# BUSINESS_RULES.md — Repositorio Códigos

> Solo reglas de negocio identificadas en el código. Cada regla indica dónde se implementa.  
> Si una regla no está codificada de forma inequívoca, se marca como **parcial** o **inconsistencia**.

---

## 1. Acceso al módulo

### BR-01 — Acceso restringido al módulo `codigos`

- **Regla:** Un usuario autenticado solo puede usar las vistas de negocio si tiene acceso al módulo con código `"codigos"` (o es superusuario con el módulo activo en catálogo).
- **Implementación:**
  - `documentos/decorators.py` → `requiere_modulo_paldaca` + `_usuario_tiene_acceso`
  - `core/models.py` → `UsuarioPaldaca.tiene_acceso_modulo`
  - Constante: `documentos/constants.py` → `MODULO_CODIGO = "codigos"`
- **Efecto:** sin acceso → HTTP 403 `"No tienes acceso a este programa."`; sin login → redirect a SSO.

### BR-02 — Autenticación solo vía SSO del Portal

- **Regla:** Este repositorio no autentica usuarios localmente. Login, registro y logout redirigen a URLs SSO configuradas.
- **Implementación:** `core/views.py` (`login_redirect`, `signup_redirect`, `signout`); `settings.LOGIN_URL = PALDACA_SSO_LOGIN_URL`.

### BR-03 — Invalidación de sesión ante cambio de permisos

- **Regla:** Si cambian rol, disciplina, perfil, activo o módulos asignados (hash `get_auth_revision`), la sesión se cierra cuando `PALDACA_STRICT_SESSION_CONSISTENCY` es verdadero (default).
- **Implementación:** `core/middleware.py` → `PaldacaSessionMiddleware`; `core/models.py` → `get_auth_revision`.

---

## 2. Generación de códigos

### BR-04 — Estructura obligatoria del código

- **Regla:** El código se compone de segmentos fijos:

  `{sigla_empresa}-{año_2_dígitos}-{numero_proyecto}-{subproyecto}-{departamento}-{disciplina}-{tipo_documento}-{consecutivo:03}`

- **Implementación:** `documentos/views.py` → `_calcular_codigo_y_consecutivo`.
- **Origen de segmentos:** `documentos/forms.py` → `CodigoForm` (choices de años, proyectos, subproyectos, departamentos, disciplinas, tipos de documento) + `Empresa.sigla`.

### BR-05 — Consecutivo por combinación de segmentos

- **Regla:** El consecutivo es `N + 1`, donde `N` es el número de `CodigoGenerado` existentes con la misma combinación de: empresa, año completo, número de proyecto, subproyecto, departamento, disciplina y tipo de documento.
- **Implementación:** `documentos/views.py` → `_calcular_codigo_y_consecutivo` (`filtro_existente.count() + 1`).
- **Nota:** El modelo `ContadorCodigo` **no participa** en este cálculo en el código actual.

### BR-06 — Unicidad del código

- **Regla:** El campo `codigo` es único en base de datos.
- **Implementación:** `documentos/models.py` → `CodigoGenerado.codigo` (`unique=True`); captura de `IntegrityError` en `generar_codigo`.

### BR-07 — Motivo/asunto obligatorio al confirmar

- **Regla:** No se puede persistir un código sin `motivo` no vacío.
- **Implementación:** `documentos/views.py` (rama `paso == 'confirmar'`); campo `CodigoGenerado.motivo`.

### BR-08 — Flujo en dos pasos (vista previa → confirmación)

- **Regla:** Primero se valida el formulario y se guarda preview en sesión; solo en confirmación se persiste.
- **Implementación:** `documentos/views.py` (`GENERADOR_SESSION_PREVIEW`, pasos `datos` / `confirmar` / `cancelar`).

### BR-09 — Asociación al usuario creador

- **Regla:** Todo código generado se asocia al usuario autenticado (`usuario=request.user`).
- **Implementación:** `documentos/views.py` → `CodigoGenerado.objects.create(...)`.

### BR-10 — Empresa protegida ante borrado

- **Regla:** No se puede eliminar una `Empresa` si tiene códigos asociados (`on_delete=PROTECT`).
- **Implementación:** `documentos/models.py` → `CodigoGenerado.empresa`.

### BR-11 — Catálogos de negocio en el formulario

- **Regla:** Departamentos, disciplinas técnicas y tipos de documento permitidos están fijados en choices del formulario (no en tablas).
- **Implementación:** `documentos/forms.py` → `DEPARTAMENTOS`, `DISCIPLINAS`, `TIPOS_DOCUMENTO`.
- **Alcance detectado:**
  - Años: 2020 … año actual + 1.
  - Número de proyecto: `00`–`99`.
  - Subproyecto: `A`–`Z` o `0`.

### BR-12 — Notificación por correo al generar

- **Regla:** Tras guardar un código, se envía correo a `empresa.correo_notificacion` con asunto `"Nuevo Código generado"`.
- **Implementación:** `documentos/views.py` (bloque email tras `create`); plantilla `documentos/templates/emails/nuevo_codigo.html`.
- **Comportamiento ante fallo:** el código **sí queda guardado**; se muestra advertencia al usuario (`email_warning`).
- **Logo por nombre de empresa:** mapeo hardcodeado de nombres (`SSAPI`, `Paldaca`, `Orinoco Energy`, `Kinetic Scale Projectos`) a archivos de imagen; default `PaldacalogoyRif.png`.

---

## 3. Consulta e historial

### BR-13 — Listado reciente por defecto

- **Regla:** `/Codigos/` muestra los 15 más recientes salvo `?todos=1`.
- **Implementación:** `documentos/views.py` → `lista_codigos`.

### BR-14 — Búsqueda con filtros opcionales

- **Regla:** Se puede filtrar por código (icontains), usuario, rango de fechas; por defecto se excluyen anulados salvo checkbox `ver_anulados`.
- **Implementación:** `documentos/views.py` → `buscar_codigo`; `BusquedaCodigoForm`.

### BR-15 — Historial de anulaciones

- **Regla:** `/historial_anulaciones/` lista solo códigos con `anulado=True`, ordenados por fecha de anulación descendente.
- **Implementación:** `documentos/views.py` → `historial_anulaciones`.

---

## 4. Anulación y solicitudes

### BR-16 — Quién puede anular directamente (backend)

- **Regla:** Puede anular vía `POST /anular_codigo/<id>/` si:
  1. es el usuario creador del código, **o**
  2. `es_aprobador_codigos(user)` es verdadero.
- **Implementación:** `documentos/views.py` → `anular_codigo`.

### BR-17 — Definición de aprobador

- **Regla:** Un usuario es aprobador si:
  1. `es_administrador_en_modulo("codigos")` (acceso al módulo + rol administrador, o superuser), **o**
  2. tiene el permiso Django `documentos.puede_anular_codigo`.
- **Implementación:** `documentos/permissions.py` → `es_aprobador_codigos`.

### BR-18 — Anulación es irreversible en el flujo actual

- **Regla:** Un código ya anulado no puede anularse de nuevo; se marca `anulado=True`, se registra `usuario_anulacion` y `fecha_anulacion`.
- **Implementación:** `documentos/views.py` → `anular_codigo` / `solicitudes_anulacion_view`; modelo `CodigoGenerado`.
- **Nota:** No hay endpoint de “des-anular” en el código.

### BR-19 — Solicitud de anulación con motivo

- **Regla:** Cualquier usuario con acceso al módulo puede solicitar anulación enviando motivo no vacío.
- **Implementación:** `documentos/views.py` → `solicitar_anulacion`.

### BR-20 — Una sola solicitud pendiente por usuario y código

- **Regla:** No se permite crear otra `SolicitudAnulacion` si ya existe una del mismo solicitante, mismo código y `procesada=False`.
- **Implementación:** `documentos/views.py` → `solicitar_anulacion` (y chequeo JS adicional en `lista_codigos.html`).

### BR-21 — Procesamiento de solicitudes solo por aprobadores

- **Regla:** La vista `/solicitudes_anulacion/` exige `es_aprobador_codigos`; acciones:
  - `anular`: marca solicitud procesada + anula el código.
  - `rechazar`: marca solicitud procesada sin anular.
- **Implementación:** `documentos/views.py` → `solicitudes_anulacion_view`.

### BR-22 — Anulación directa cierra solicitudes pendientes del código

- **Regla:** Al anular directamente, todas las solicitudes pendientes de ese código pasan a `procesada=True`.
- **Implementación:** `documentos/views.py` → `anular_codigo`.

---

## 5. Roles globales de Suite (compartidos)

### BR-23 — Roles de usuario Suite

- **Regla:** `UsuarioPaldaca.rol` solo admite `usuario` o `administrador` (default `usuario`).
- **Implementación:** `core/models.py` → `ROL_CHOICES`.
- **Uso en Códigos:** el rol administrador, junto con acceso al módulo, habilita aprobación (`es_administrador_en_modulo`).

### BR-24 — Superusuario = acceso a todos los módulos activos

- **Regla:** `is_superuser` implica acceso a cualquier módulo activo sin filas en `core_usuario_modulo`.
- **Implementación:** `UsuarioPaldaca.tiene_acceso_modulo` / `modulos_habilitados` / `es_superadmin`.

---

## 6. Inconsistencias detectadas (no inventar resolución)

### INC-01 — UI de anulación vs regla backend

- **Plantilla** `lista_codigos.html` muestra “Anular código” solo si `perms.documentos.puede_anular_codigo`.
- **Backend** `anular_codigo` también permite al **creador** del código y a administradores de módulo (`es_aprobador_codigos`).
- **Consecuencia:** un creador sin el permiso Django verá “Solicitar anulación” en UI, aunque el endpoint de anulación directa lo autorizaría.

### INC-02 — Etiqueta del home vs permiso real

- En `home.html`, el enlace a `solicitudes_anulacion` se etiqueta “Solicitar Anulacion”, pero la vista es la bandeja de **aprobación** (solo aprobadores). La solicitud se hace desde el menú contextual de la lista.

### INC-03 — `ContadorCodigo` vs cálculo real

- Existe modelo/tabla `codigos_contador_codigo` y scripts de migración en `GUIA.md`, pero el generador actual **no** actualiza ni lee ese contador.

---

## 7. Reglas NO encontradas en el código

No hay evidencia en este repositorio de:

- Validación de que el código anulado “libere” el consecutivo para reutilización (los anulados siguen contando en el `COUNT` del consecutivo).
- Workflow de aprobación multi-nivel.
- API pública de generación de códigos para otros módulos.
- Reglas de negocio que usen `Role` / `UserRole` / `GoogleDriveToken` de Calidad.
- Reglas de negocio que usen campos de timesheet en `UsuarioPaldaca`.
