from django.conf import settings
from django.db import models

from .constants import TABLA


class ContadorCodigo(models.Model):
    anio = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)

    class Meta:
        db_table = TABLA("contador_codigo")


class Empresa(models.Model):
    sigla = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    correo_notificacion = models.EmailField()

    class Meta:
        db_table = TABLA("empresa")

    def __str__(self):
        return f"{self.sigla} - {self.nombre}"


class CodigoGenerado(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    año = models.CharField(max_length=4)
    numero_proyecto = models.CharField(max_length=2)
    subproyecto = models.CharField(max_length=1)
    departamento = models.CharField(max_length=2)
    disciplina = models.CharField(max_length=2)
    tipo_documento = models.CharField(max_length=4)
    consecutivo = models.PositiveIntegerField()
    codigo = models.CharField(max_length=50, unique=True)
    motivo = models.TextField(verbose_name="Motivo / Asunto")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="codigos_generados",
    )
    anulado = models.BooleanField(default=False)
    usuario_anulacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="codigos_anulados",
    )
    fecha_anulacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = TABLA("codigo_generado")
        indexes = [
            models.Index(fields=["-fecha_creacion"], name="codigos_fecha_creacion_idx"),
            models.Index(fields=["anulado", "-fecha_anulacion"], name="codigos_anulado_fecha_idx"),
            models.Index(
                fields=[
                    "empresa",
                    "año",
                    "numero_proyecto",
                    "subproyecto",
                    "departamento",
                    "disciplina",
                    "tipo_documento",
                ],
                name="codigos_consecutivo_lookup_idx",
            ),
        ]

    def __str__(self):
        return self.codigo + " by " + str(self.usuario)


class SolicitudAnulacion(models.Model):
    codigo = models.ForeignKey(CodigoGenerado, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes_anulacion_codigo",
    )
    motivo = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField(default=False)

    class Meta:
        db_table = TABLA("solicitud_anulacion")
        indexes = [
            models.Index(
                fields=["solicitante", "procesada"],
                name="codigos_sol_pendiente_idx",
            ),
            models.Index(fields=["procesada", "-fecha_solicitud"], name="codigos_sol_fecha_idx"),
        ]
        permissions = [
            ("puede_anular_codigo", "Puede anular códigos"),
        ]

    def __str__(self):
        return f"Solicitud de {self.solicitante} para {self.codigo}"
