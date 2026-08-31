# Rendimiento de Códigos

## Instrumentación

Con `DEBUG=True`, cada respuesta incluye `Server-Timing` y registra:

- tiempo total y tiempo SQL;
- cantidad de consultas;
- tamaño de la respuesta;
- ruta, método y estado HTTP.

El log usa el nombre `paldaca.performance`. No se registra SQL ni contenido
de usuario y el middleware queda inactivo fuera de desarrollo.

## Línea base (desarrollo)

| Ruta | Presupuesto de consultas | Notas |
|------|--------------------------|--------|
| `/` | 16 | Home autenticada |
| `/Codigos/` | 16 | Listado paginado |
| `/BuscarCodigo/` | 18 | Formulario; el queryset se pagina al buscar |

## Cambios estructurales

- SSO reutiliza el usuario autenticado y un snapshot de módulos por petición.
- Historial, búsqueda, solicitudes y vista «todos» están paginados.
- `select_related` cubre `usuario` y `usuario_anulacion`.
- El SMTP tiene timeout explícito: el código se guarda aunque el correo tarde.
- jQuery y Popper sin uso se retiraron; Bootstrap carga un solo bundle.
- El menú contextual usa `is_aprobador` y una sola función JS de solicitud.

## Iframe

El Portal avisa a los 15 s y trata los 30 s como espera recuperable.

## Riesgos pendientes

- El correo de confirmación sigue siendo síncrono, acotado por `EMAIL_TIMEOUT`.
- No hay cola. Esta fase no introduce Redis ni Celery.
