import logging

from django.conf import settings
from django.shortcuts import redirect, render

from documentos.decorators import requiere_modulo_paldaca

logger = logging.getLogger("core")


@requiere_modulo_paldaca
def home(request):
    nombre_usuario = request.user.get_full_name() or request.user.username
    logger.info("Acceso a home usuario=%s", request.user.username)
    return render(request, "Home/home.html", {"nombre_usuario": nombre_usuario})


def login_redirect(request):
    return redirect(settings.PALDACA_SSO_LOGIN_URL)


def signup_redirect(request):
    return redirect(settings.PALDACA_SSO_LOGIN_URL)


def signout(request):
    return redirect(settings.PALDACA_SSO_LOGOUT_URL)
