"""
URL configuration for codigos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from documentos import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generar_codigo/', views.generar_codigo, name='generar_codigo'),
    path('', views.home, name='home'),
    path('Register/', views.signup, name='signup'),
    path('Logout/', views.signout, name='logout'),
    path('Login/', views.IniciarSesion, name='login'),
    path('Codigos/', views.lista_codigos, name='lista_codigos'),
    path('BuscarCodigo/', views.buscar_codigo, name='buscar_codigo'),
    path('anular_codigo/<int:codigo_id>/', views.anular_codigo, name='anular_codigo'),
    path('historial_anulaciones/', views.historial_anulaciones, name='historial_anulaciones'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])