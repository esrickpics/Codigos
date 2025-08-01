from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db import models

class ContadorCodigo(models.Model):
    anio = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)


class Empresa(models.Model):
    sigla = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    correo_notificacion = models.EmailField()

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    anulado = models.BooleanField(default=False)
    usuario_anulacion = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='anulaciones')
    fecha_anulacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo + ' by ' + str(self.usuario)
    