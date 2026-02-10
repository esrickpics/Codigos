 # codigos/forms.py
from django import forms
from datetime import datetime
from django.contrib.auth.models import User
from .models import Empresa

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
    ('GN', 'General'), ('GP', 'Gerencia de Proyectos'), ('OF', 'Ofertas'),
    ('IT', 'Informática y Tecnología')
    ]

    DISCIPLINAS = [
        ('M', 'Mecánica'), ('A', 'Arquitectura'), ('C', 'Civil'),
        ('I', 'Instrumentación'), ('E', 'Electricidad'), ('P', 'Procesos'),
        ('T', 'Telecomunicaciones'), ('G', 'General')
    ]

    TIPOS_DOCUMENTO = [
    ('ACC', 'Acción Correctiva'),
    ('CAR', 'Carta'),
    ('CEN', 'Centro de Costos'),
    ('CON', 'Contrato'),
    ('CRO', 'Cronograma'),
    ('DPT', 'Descripción de Puesto de Trabajo'),
    ('GEN', 'Documentos Generales'),
    ('DOC', 'Documentos de Ingeniería'),
    ('ESC', 'Estimado de Costos'),
    ('ESP', 'Especificación Técnica'),
    ('EST', 'Estudio'),
    ('FPR', 'Ficha de Proceso'),
    ('FLU', 'Flujograma'),
    ('FOR', 'Formulario'),
    ('HDC', 'Hoja de Control'),
    ('HDD', 'Hoja de Datos'),
    ('INF', 'Informe'),
    ('INS', 'Instrucción de Sitio'),
    ('LIS', 'Lista'),
    ('MDC', 'Manejo del Cambio'),
    ('MAN', 'Manual'),
    ('MAC', 'Manual de la Calidad'),
    ('MDP', 'Mapa de Procesos'),
    ('MAT', 'Matriz de Riesgo'),
    ('MRO', 'Matriz de Riesgo y Oportunidades'),
    ('MNT', 'Minuta'),
    ('MVV', 'Misión y Visión y Valores'),
    ('NCN', 'No Conformidad'),
    ('ODC', 'Objetivos de la Calidad'),
    ('OFE', 'Oferta'),
    ('ODM', 'Oportunidad de Mejora'),
    ('PLN', 'Plan'),
    ('PIE', 'Plan de Inspección y Ensayo'),
    ('PQC', 'Plan de la Calidad'),
    ('PLA', 'Plano'),
    ('PDC', 'Política de la Calidad'),
    ('PRE', 'Presentación'),
    ('PRO', 'Procedimiento'),
    ('PNC', 'Producto No Conforme'),
    ('PGM', 'Programa'),
    ('RGA', 'Relación de Gastos'),
    ('REQ', 'Requisición de Materiales'),
    ('SVI', 'Solicitud de Viáticos'),
    ('TRN', 'Transmittal')
]
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(), label='Empresa')
    año = forms.ChoiceField(choices=AÑOS)
    numero_proyecto = forms.ChoiceField(choices=NUM_PROYECTO)
    subproyecto = forms.ChoiceField(choices=SUBPROYECTOS)
    departamento = forms.ChoiceField(choices=DEPARTAMENTOS)
    disciplina = forms.ChoiceField(choices=DISCIPLINAS)
    tipo_documento = forms.ChoiceField(choices=TIPOS_DOCUMENTO)
