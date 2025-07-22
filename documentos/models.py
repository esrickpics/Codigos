from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db import models

class ContadorCodigo(models.Model):
    anio = models.IntegerField(unique=True)
    ultimo_numero = models.IntegerField(default=0)


class CodigoGenerado(models.Model):
    empresa = models.CharField(max_length=3, default='PAL')
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

    def __str__(self):
        return self.codigo + ' by ' + str(self.usuario)