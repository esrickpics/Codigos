# ARCHITECTURE.md — Repositorio Códigos

> Documentación derivada del código existente. Última revisión basada en el estado del repositorio en el momento de generación.  
> Stack: Django 5.2.4 · MySQL · plantillas Django + Bootstrap 5 · sin frontend SPA propio.

---

## 1. Propósito del repositorio

**Códigos** es el módulo de la **PALDACA Suite** encargado de **generar, consultar y anular códigos documentales** corporativos (identificadores estructurados por empresa, año, proyecto, departamento, disciplina y tipo de documento).

Responsabilidades confirmadas en el código:

- Generar códigos con formato predefinido y consecutivo calculado.
- Notificar por correo a la empresa asociada al generar un código.
- Listar y buscar códigos históricos.
- Anular códigos (directamente o mediante solicitud/aprobación).
- Integrarse al SSO y a la navegación compartida de PALDACA Suite.
- Operar sobre la base de datos MySQL unificada de la Suite (`ssapmcco_PALDACA_DB` / `paldaca_db` según entorno).

No es el Portal Shell, ni gestiona autenticación de usuarios (login/registro se redirigen al Portal).

---

## 2. Arquitectura general

```
┌─────────────────────────────────────────────────────────────────┐
│                     PALDACA Suite (BD MySQL única)               │
│  core_* · django_session · codigos_* · calidad_* · (otros)      │
└─────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
┌────────┴────────┐  ┌────────┴────────┐  ┌───────┴────────┐
│ Portal-Paldaca  │  │    Códigos      │  │ Activos/Calidad│
│ (SSO + Nav API) │  │  (este repo)    │  │ / HDT / ...    │
└────────┬────────┘  └────────┬────────┘  └────────────────┘
         │                    │
         │  cookie            │  consume nav CSS/JS + API
         │  paldaca_sessionid │  redirige login/logout SSO
         └────────────────────┘
```

### Estilo arquitectónico

- **Aplicación Django monolítica por módulo** (server-rendered).
- **Dos apps Django** dentro del proyecto: `core` (identidad/SSO compartida) y `documentos` (dominio de negocio).
- **Autenticación externalizada**: no hay login local; se valida sesión Django compartida (`SESSION_COOKIE_NAME=paldaca_sessionid`).
- **Autorización por módulo**: acceso gated por `UsuarioPaldaca.tiene_acceso_modulo("codigos")`.
- **Sin capa API REST propia** en este repositorio (las vistas JSON son endpoints puntuales de anulación, no una API pública).

---

## 3. Estructura del repositorio

```
Codigos/
├── codigos/                 # Proyecto Django (settings, urls, wsgi, db)
│   ├── settings.py
│   ├── urls.py
│   ├── db.py                # Configuración MySQL
│   ├── wsgi.py / asgi.py
├── core/                    # Identidad Suite + middleware SSO + home
│   ├── models.py            # UsuarioPaldaca, Modulo, Disciplina, Perfil, …
│   ├── middleware.py        # PaldacaSessionMiddleware
│   ├── session_logout.py
│   ├── context_processors.py
│   ├── views.py / urls.py / admin.py
│   ├── templates/           # layout, home, login/signup redirects
│   ├── management/commands/seed_core_modulos.py
│   └── migrations/
├── documentos/              # Dominio: generación y anulación de códigos
│   ├── models.py
│   ├── views.py / forms.py / urls.py
│   ├── permissions.py / decorators.py / constants.py
│   ├── templates/
│   ├── static/
│   └── migrations/
├── scripts/cpanel_deploy_check.py
├── .github/workflows/main.yml
├── .cpanel.yml
├── key.env.example
├── requirements.txt
├── manage.py
└── GUIA.md                  # SQL de migración legacy → BD unificada
```

---

## 4. Aplicaciones Django

### 4.1 `core`

**Rol:** capa de identidad y sesión compartida con el resto de la Suite.

| Componente | Responsabilidad |
|---|---|
| `UsuarioPaldaca` | `AUTH_USER_MODEL`; roles `usuario` / `administrador`; acceso a módulos |
| `Modulo` / `UsuarioModulo` | Catálogo de programas de la Suite y asignación por usuario |
| `Disciplina` / `Perfil` | Catálogos de contexto de usuario |
| `Role` / `UserRole` / `GoogleDriveToken` | Modelos espejo de **Calidad** (`calidad_*`); no usados por la lógica de Códigos |
| `PaldacaSessionMiddleware` | Invalida sesión si cambia la “auth revision” del usuario |
| `context_processors` | URLs SSO + assets de navegación Portal; flag `is_aprobador` |
| Vistas `Login/` `Register/` `Logout/` | Solo redirección a URLs SSO del Portal |

Campos en `UsuarioPaldaca` orientados a **Hoja de Tiempo** (`date_last_hour_entry`, `auto_timesheet_generation_*`) existen por compatibilidad de esquema compartido; este repositorio no los consume en vistas.

### 4.2 `documentos`

**Rol:** dominio funcional de códigos documentales.

| Modelo | Tabla física | Uso |
|---|---|---|
| `Empresa` | `codigos_empresa` | Sigla, nombre, correo de notificación |
| `CodigoGenerado` | `codigos_codigo_generado` | Registro del código emitido |
| `SolicitudAnulacion` | `codigos_solicitud_anulacion` | Flujo de solicitud → aprobación |
| `ContadorCodigo` | `codigos_contador_codigo` | **Modelo presente; no referenciado en vistas actuales** |

Prefijo de tablas: `documentos.constants.TABLA()` → `codigos_<nombre>` (`MODULO_CODIGO = "codigos"`).

---

## 5. Flujo principal de ejecución

### 5.1 Arranque de request

1. Middleware de seguridad / sesión / CSRF / auth de Django.
2. `PaldacaSessionMiddleware`: si hay usuario autenticado, compara `paldaca_auth_revision` en sesión con `UsuarioPaldaca.get_auth_revision()`.
3. Si la revisión no coincide y `PALDACA_STRICT_SESSION_CONSISTENCY=true` → cierra sesión y redirige a SSO login (o 401 JSON si parece API).
4. Vista decorada con `@requiere_modulo_paldaca` → exige login + `tiene_acceso_modulo("codigos")`.

### 5.2 Generación de código

```
GET/POST /generar_codigo/
  ├─ POST paso=datos     → valida CodigoForm → guarda preview en sesión → redirect ?vista_previa=1
  ├─ GET  ?vista_previa=1 → muestra código calculado + resumen
  └─ POST paso=confirmar → exige motivo → crea CodigoGenerado → envía email → redirect ?guardado=1
```

Cálculo del código (`_calcular_codigo_y_consecutivo`):

```
{SIGLA}-{AA}-{NN}-{S}-{DEPT}-{DISC}-{TIPO}-{CCC}
```

donde `CCC` = cantidad de registros existentes con la misma combinación de segmentos + 1 (formato 3 dígitos).

### 5.3 Anulación

- **Directa** (`POST /anular_codigo/<id>/`): permitido si el usuario es el creador **o** `es_aprobador_codigos`.
- **Solicitud** (`POST /solicitar_anulacion/<id>/`): crea `SolicitudAnulacion` con motivo; no permite duplicados pendientes del mismo solicitante.
- **Aprobación** (`/solicitudes_anulacion/`): solo aprobadores; acciones `anular` o `rechazar`.

### 5.4 Autenticación (sin login local)

```
/Login/  → redirect PALDACA_SSO_LOGIN_URL
/Register/ → redirect PALDACA_SSO_LOGIN_URL
/Logout/ → redirect PALDACA_SSO_LOGOUT_URL
```

La sesión válida llega vía cookie compartida emitida por el Portal / backend SSO.

---

## 6. Decisiones arquitectónicas detectadas

| Decisión | Evidencia | Implicación |
|---|---|---|
| `AUTH_USER_MODEL = core.UsuarioPaldaca` | `settings.py` | Misma identidad que el resto de la Suite |
| Tablas de dominio con prefijo `codigos_` | migración `0006` + `constants.TABLA` | Evita colisión en BD compartida |
| Modelos `calidad_*` y campos HDT en `core` | migraciones `0011`, `0013` | Esquema unificado; este app no los usa funcionalmente |
| Consecutivo por `COUNT` + 1, no por `ContadorCodigo` | `documentos/views.py` | Modelo `ContadorCodigo` legacy / no activo en flujo actual |
| Preview en sesión antes de persistir | claves `generador_preview_*` | Evita guardar códigos incompletos |
| Navegación embebida del Portal | `paldaca_nav.html` + context processors | UX unificada; dependencia runtime de assets/API Portal |
| Server-rendered (sin DRF/React propio) | templates + Bootstrap CDN | Despliegue simple; no expone API de dominio documentada |

---

## 7. Dependencias internas

```
codigos (proyecto)
 ├── core
 │    ├── usa documentos.decorators (home)
 │    └── usa documentos.permissions (context processor)
 └── documentos
      ├── usa core.UsuarioPaldaca (FK AUTH_USER_MODEL)
      └── usa settings SSO / LOGIN_URL
```

Dependencia circular suave: `core` importa permisos/decoradores de `documentos`. Funciona porque son importaciones en tiempo de uso (vistas/context processors), no a nivel de modelos.

---

## 8. Configuración y despliegue

| Aspecto | Detalle en código |
|---|---|
| Settings | `codigos/settings.py`; secretos desde `key.env` / `.env/key.env` + `correo.env` |
| BD | `codigos/db.py` (actualmente hardcodeada a producción en el archivo activo) |
| Locale | `es-ve`, `America/Caracas` |
| Estáticos | `STATIC_ROOT=staticfiles`; `STATICFILES_DIRS` apunta a `documentos/static` |
| Deploy CI | `.github/workflows/main.yml` → SSH, migrate, collectstatic, Passenger |
| Deploy cPanel | `.cpanel.yml` → rsync a `/home/ssapmcco/PaldacaCodigos` |
| Host productivo | `codigos.cpaldaca.com` |

---

## 9. Riesgos técnicos (arquitectura)

1. **`DEBUG = True` hardcodeado** en `settings.py` — inadecuado para producción.
2. **Credenciales MySQL en texto plano** en `codigos/db.py` (no lee `MYSQL_*` de `key.env.example`).
3. **`ALLOWED_HOSTS` incluye URL con esquema** (`https://codigos.cpaldaca.com/`) — formato incorrecto para Django.
4. **Concurrencia en consecutivos**: el cálculo `count()+1` no usa transacción/bloqueo; riesgo de colisión bajo carga concurrente (mitigado parcialmente por `unique=True` en `codigo` + `IntegrityError`).
5. **Desalineación UI vs backend en anulación**: la plantilla decide “Anular” vs “Solicitar” con `perms.documentos.puede_anular_codigo`; el backend permite anular también al creador o a administradores de módulo vía `es_aprobador_codigos`.
6. **Dos rutas de despliegue** (GitHub Actions vs `.cpanel.yml`) con paths distintos — riesgo de divergencia operativa.
7. **Modelos ajenos en `core`**: migraciones de Códigos pueden crear/alterar tablas `calidad_*` o columnas HDT en BD compartida.

---

## 10. Archivos críticos

| Archivo | Por qué |
|---|---|
| `codigos/settings.py` | SSO, cookies, apps, email, logging |
| `codigos/db.py` | Conexión a BD compartida |
| `core/models.py` | Identidad Suite |
| `core/middleware.py` | Consistencia de sesión SSO |
| `documentos/views.py` | Todo el flujo de negocio |
| `documentos/forms.py` | Catálogos de segmentos del código |
| `documentos/permissions.py` / `decorators.py` | Gate de acceso y aprobación |
| `core/context_processors.py` | Integración visual/API con Portal |
