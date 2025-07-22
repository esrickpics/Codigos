# codigos/forms.py
from django import forms
from datetime import datetime
from django.contrib.auth.models import User

class BusquedaCodigoForm(forms.Form):
    codigo = forms.CharField(label='Código', required=False)
    usuario = forms.ModelChoiceField(label='Usuario', queryset=User.objects.all(), required=False)
    fecha_inicio = forms.DateField(label='Desde', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(label='Hasta', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class CodigoForm(forms.Form):
    AÑOS = [(str(a), str(a)) for a in range(2020, datetime.now().year + 2)]
    NUM_PROYECTO = [(f"{i:02}", f"{i:02}") for i in range(0, 100)]
    SUBPROYECTOS = [(chr(i), chr(i)) for i in range(ord('A'), ord('Z') + 1)] + [('0', '0')]
    DEPARTAMENTOS = [
        ('GG', 'Gerencia General'), ('GO', 'Gerencia de Operaciones'),
        ('MN', 'Mantenimiento'), ('CO', 'Construcción'), ('IN', 'Ingeniería'),
        ('CA', 'Calidad'), ('RH', 'Recursos Humanos'), ('SH', 'Seguridad'),
        ('AM', 'Ambiente'), ('PR', 'Procura'), ('CT', 'Contratos'),
        ('AF', 'Administración y Finanzas'), ('PL', 'Planificación'),
        ('EC', 'Estimación de Costos'), ('CD', 'Control de Documentos'),
        ('GN', 'General'),
    ]
    DISCIPLINAS = [
        ('M', 'Mecánica'), ('A', 'Arquitectura'), ('C', 'Civil'),
        ('I', 'Instrumentación'), ('E', 'Electricidad'), ('P', 'Procesos'),
        ('T', 'Telecomunicaciones'), ('G', 'General')
    ]
    TIPOS_DOCUMENTO = [
        ('MVV', 'Misión y Visión y Valores'), ('PDC', 'Política de la Calidad'),
        ('ODC', 'Objetivos de la Calidad'), ('MDP', 'Mapa de Procesos'),
        ('MAC', 'Manual de la Calidad'), ('PRO', 'Procedimiento'),
        ('CAR', 'Carta'), ('FOR', 'Formulario'), ('ESP', 'Especificación Técnica'),
        ('HDD', 'Hoja de Datos'), ('LIS', 'Lista'), ('MAT', 'Matriz de Riesgo'),
        ('MRP', 'Matriz de Riesgo de los Procesos'), ('FPR', 'Ficha de Proceso'),
        ('FLU', 'Flujograma'), ('CRO', 'Cronograma'), ('MDC', 'Manejo del Cambio'),
        ('INS', 'Instrucción de Sitio'), ('NCN', 'No Conformidad'),
        ('DOC', 'Documentos de Ingeniería'), ('PLA', 'Plano'), ('PLN', 'Plan'),
        ('PIE', 'Plan de Inspección y Ensayo'), ('MAN', 'Manual'),
        ('REQ', 'Requisición de Materiales'), ('EST', 'Estudio'), ('OFE', 'Oferta'),
        ('CON', 'Contrato'), ('ESC', 'Estimado de Costos'), ('PRE', 'Presentación'),
        ('INF', 'Informe'), ('MNT', 'Minuta'), ('SVI', 'Solicitud de Viáticos'),
        ('RGA', 'Relación de Gastos'), ('CEN', 'Centro de Costos'),
        ('DPT', 'Descripción de Puesto de Trabajo'), ('TRN', 'Transmittal'),
        ('GEN', 'Documentos Generales'),
    ]
    EMPRESAS = [
    ('PAL', 'Paldaca'),
    ('SSA', 'SSAPICO'),
    ('KSP', 'Kinetic Scale Proyectos LDA'),
    ('OEC', 'Orinoco Energy CA'),
    ]


    empresa = forms.ChoiceField(choices=EMPRESAS, label='Empresa')
    año = forms.ChoiceField(choices=AÑOS)
    numero_proyecto = forms.ChoiceField(choices=NUM_PROYECTO)
    subproyecto = forms.ChoiceField(choices=SUBPROYECTOS)
    departamento = forms.ChoiceField(choices=DEPARTAMENTOS)
    disciplina = forms.ChoiceField(choices=DISCIPLINAS)
    tipo_documento = forms.ChoiceField(choices=TIPOS_DOCUMENTO)
