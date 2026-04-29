from django.urls import path

from . import views

urlpatterns = [
    path("generar_codigo/", views.generar_codigo, name="generar_codigo"),
    path("Codigos/", views.lista_codigos, name="lista_codigos"),
    path("BuscarCodigo/", views.buscar_codigo, name="buscar_codigo"),
    path("anular_codigo/<int:codigo_id>/", views.anular_codigo, name="anular_codigo"),
    path("historial_anulaciones/", views.historial_anulaciones, name="historial_anulaciones"),
    path("solicitar_anulacion/<int:codigo_id>/", views.solicitar_anulacion, name="solicitar_anulacion"),
    path("solicitudes_anulacion/", views.solicitudes_anulacion_view, name="solicitudes_anulacion"),
]
