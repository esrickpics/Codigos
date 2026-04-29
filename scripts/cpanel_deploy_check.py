#!/usr/bin/env python3
"""
Comprueba requisitos típicos de cPanel Git™ Deployment antes de desplegar:

  - Existe un .cpanel.yml reconocible (estructura deployment.tasks).
  - No hay cambios sin commitear en la rama actual (requisito de cPanel).

Escribe un registro en: logs/cpanel-deployment-check.log

Uso (desde la raíz del repo):
  python scripts/cpanel_deploy_check.py
  python scripts/cpanel_deploy_check.py --strict   # sale con código 1 si hay errores

cPanel muestra errores genéricos como "The system cannot deploy"; este script
deja trazas concretas en el log local para diagnosticar.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CPANEL_FILE = REPO_ROOT / ".cpanel.yml"
LOG_PATH = REPO_ROOT / "logs" / "cpanel-deployment-check.log"


def log_line(fp, level: str, message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts}\t{level}\t{message}\n"
    fp.write(line)
    fp.flush()
    print(line.rstrip())


def ensure_log_dir() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_yaml_document(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if data is None:
            return {"__parse_error__": "YAML vacío o solo comentarios"}
        return data if isinstance(data, dict) else {"__parse_error__": "Raíz YAML no es un mapa"}
    except ImportError:
        return None
    except Exception as e:
        return {"__parse_error__": str(e)}


def validate_cpanel_structure(data: dict) -> list[str]:
    errors: list[str] = []
    if "deployment" not in data:
        errors.append("Falta la clave raíz 'deployment'.")
        return errors
    dep = data["deployment"]
    if not isinstance(dep, dict):
        errors.append("'deployment' debe ser un mapa (objeto YAML).")
        return errors
    if "tasks" not in dep:
        errors.append("Falta 'deployment.tasks'.")
        return errors
    tasks = dep["tasks"]
    if not isinstance(tasks, list):
        errors.append("'deployment.tasks' debe ser una lista de comandos.")
        return errors
    if len(tasks) == 0:
        errors.append("'deployment.tasks' está vacío.")
        return errors
    for i, item in enumerate(tasks):
        if not isinstance(item, str):
            errors.append(f"Tarea índice {i} no es texto (tipo {type(item).__name__}).")
        elif not item.strip():
            errors.append(f"Tarea índice {i} es una cadena vacía.")
    return errors


def heuristic_yaml_check(path: Path) -> list[str]:
    """Si no hay PyYAML, comprobaciones mínimas por contenido."""
    errors: list[str] = []
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("El archivo tiene BOM UTF-8; conviene guardarlo como UTF-8 sin BOM.")
    text = path.read_text(encoding="utf-8")
    if "\t" in text:
        for n, line in enumerate(text.splitlines(), 1):
            if line.startswith("\t"):
                errors.append(f"Línea {n}: indentación con TAB; cPanel/YAML suelen esperar espacios.")
                break
    if "deployment:" not in text:
        errors.append("No se encontró la línea 'deployment:'.")
    if "tasks:" not in text:
        errors.append("No se encontró 'tasks:' bajo deployment.")
    lines = text.splitlines()
    task_lines = [ln for ln in lines if ln.strip().startswith("- ") and not ln.strip().startswith("#")]
    if not task_lines:
        errors.append("No se detectaron líneas de tarea con guión ('- comando').")
    return errors


def git_porcelain(repo: Path) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except FileNotFoundError:
        return 127, "", "git no está en PATH"
    except subprocess.TimeoutExpired:
        return 124, "", "git status excedió el tiempo"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar .cpanel.yml y estado Git para despliegue cPanel.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Tratar advertencias como error (código de salida 1).",
    )
    args = parser.parse_args()

    ensure_log_dir()
    errors: list[str] = []
    warnings: list[str] = []

    with LOG_PATH.open("a", encoding="utf-8") as fp:
        log_line(fp, "INFO", "======== Inicio comprobación despliegue cPanel ========")

        if not CPANEL_FILE.is_file():
            msg = f"No existe {CPANEL_FILE.relative_to(REPO_ROOT)}"
            log_line(fp, "ERROR", msg)
            errors.append(msg)
        else:
            log_line(fp, "INFO", f"Archivo encontrado: {CPANEL_FILE.name}")
            try:
                data = load_yaml_document(CPANEL_FILE)
            except OSError as e:
                log_line(fp, "ERROR", f"No se pudo leer .cpanel.yml: {e}")
                errors.append(str(e))
                data = None

            if data is None:
                log_line(fp, "WARN", "PyYAML no instalado; usando comprobación heurística.")
                heur = heuristic_yaml_check(CPANEL_FILE)
                for h in heur:
                    log_line(fp, "WARN", h)
                warnings.extend(heur)
                if not heur:
                    log_line(fp, "INFO", "Heurística básica: .cpanel.yml parece coherente.")
            elif isinstance(data, dict) and "__parse_error__" in data:
                log_line(fp, "ERROR", f"YAML inválido: {data['__parse_error__']}")
                errors.append(data["__parse_error__"])
                heur = heuristic_yaml_check(CPANEL_FILE)
                for h in heur:
                    log_line(fp, "WARN", h)
                warnings.extend(heur)
            elif isinstance(data, dict):
                struct_errors = validate_cpanel_structure(data)
                if struct_errors:
                    for e in struct_errors:
                        log_line(fp, "ERROR", e)
                    errors.extend(struct_errors)
                else:
                    log_line(fp, "INFO", "Estructura deployment.tasks válida.")
            else:
                log_line(fp, "ERROR", "Resultado YAML inesperado.")
                errors.append("YAML inesperado")

        # Git: cambios sin commit (bloquea despliegue en cPanel)
        code, out, err = git_porcelain(REPO_ROOT)
        if code == 127:
            log_line(fp, "WARN", "Git no disponible; no se pudo comprobar el árbol de trabajo.")
            warnings.append(err)
        elif code != 0:
            log_line(fp, "ERROR", f"git status falló (código {code}): {err.strip()}")
            errors.append("git status falló")
        else:
            dirty = [ln for ln in out.splitlines() if ln.strip()]
            if dirty:
                log_line(
                    fp,
                    "ERROR",
                    "Hay cambios sin commitear (cPanel no despliega con working tree sucio): "
                    + json.dumps(dirty, ensure_ascii=False),
                )
                errors.append("Cambios sin commit en el repositorio.")
            else:
                log_line(fp, "INFO", "Git: working tree limpio (sin cambios sin commit).")

        if errors:
            log_line(fp, "ERROR", f"Resultado: FALLO ({len(errors)} error(es)).")
        elif warnings:
            log_line(fp, "WARN", f"Resultado: OK con advertencias ({len(warnings)}).")
        else:
            log_line(fp, "INFO", "Resultado: OK.")
        log_line(fp, "INFO", "======== Fin comprobación ========")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
