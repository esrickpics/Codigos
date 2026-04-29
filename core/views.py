from django.contrib.auth import authenticate, login, logout
import logging
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

logger = logging.getLogger('core')


@login_required
def home(request):
    nombre_usuario = request.user.get_full_name() or request.user.username
    logger.info("Acceso a home usuario=%s", request.user.username)
    return render(request, "Home/home.html", {"nombre_usuario": nombre_usuario})


def signup(request):
    if request.method == "GET":
        logger.info("Vista signup GET")
        return render(
            request,
            "Acceso/signup.html",
            {"form": UserCreationForm()},
        )

    if request.POST["password1"] == request.POST["password2"]:
        try:
            user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password1"],
            )
            user.save()
            login(request, user)
            logger.info("Usuario registrado y autenticado username=%s", user.username)
            return redirect("home")
        except IntegrityError:
            logger.warning("Intento de registro duplicado username=%s", request.POST.get("username"))
            return render(
                request,
                "Acceso/signup.html",
                {
                    "form": UserCreationForm(),
                    "error": "El usuario ya existe",
                },
            )

    logger.warning("Registro fallido por contrasenas distintas username=%s", request.POST.get("username"))
    return render(
        request,
        "Acceso/signup.html",
        {
            "form": UserCreationForm(),
            "error": "Las contraseñas no coinciden.",
        },
    )


@login_required
def signout(request):
    logger.info("Cierre de sesion usuario=%s", request.user.username)
    logout(request)
    return redirect("login")


def iniciar_sesion(request):
    if request.method == "GET":
        logger.info("Vista login GET")
        return render(
            request,
            "Acceso/login.html",
            {"form": AuthenticationForm()},
        )

    user = authenticate(
        request,
        username=request.POST["username"],
        password=request.POST["password"],
    )
    if user is None:
        logger.warning("Login fallido username=%s", request.POST.get("username"))
        return render(
            request,
            "Acceso/login.html",
            {
                "form": AuthenticationForm(),
                "error": "Usuario o contraseña incorrectos.",
            },
        )

    login(request, user)
    logger.info("Login exitoso username=%s", user.username)
    return redirect("home")
