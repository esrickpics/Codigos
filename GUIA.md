-- 1) Empresas
INSERT INTO paldaca_db.codigos_empresa (id, sigla, nombre, correo_notificacion)
SELECT id, sigla, nombre, correo_notificacion
FROM codigos_db.documentos_empresa;

-- 2) Contadores
INSERT INTO paldaca_db.codigos_contador_codigo (id, anio, ultimo_numero)
SELECT id, anio, ultimo_numero
FROM codigos_db.documentos_contadorcodigo;

-- 3) Códigos (usuario fijo)
INSERT INTO paldaca_db.codigos_codigo_generado (
  id, empresa_id, año, numero_proyecto, subproyecto, departamento,
  disciplina, tipo_documento, consecutivo, codigo, motivo, fecha_creacion,
  usuario_id, anulado, usuario_anulacion_id, fecha_anulacion
)
SELECT
  c.id, c.empresa_id, c.año, c.numero_proyecto, c.subproyecto, c.departamento,
  c.disciplina, c.tipo_documento, c.consecutivo, c.codigo,
  COALESCE(c.motivo, ''), c.fecha_creacion,
  @legacy_user_id,
  COALESCE(c.anulado, 0),
  CASE WHEN c.anulado THEN @legacy_user_id ELSE NULL END,
  c.fecha_anulacion
FROM codigos_db.documentos_codigogenerado c;


SELECT COUNT(*) FROM codigos_db.documentos_codigogenerado;
SELECT COUNT(*) FROM paldaca_db.codigos_codigo_generado;

SELECT codigo, COUNT(*) FROM paldaca_db.codigos_codigo_generado
GROUP BY codigo HAVING COUNT(*) > 1;

Cambiar a ssmapico_codigos