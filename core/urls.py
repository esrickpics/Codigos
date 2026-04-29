from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("Register/", views.signup, name="signup"),
    path("Logout/", views.signout, name="logout"),
    path("Login/", views.iniciar_sesion, name="login"),
]
