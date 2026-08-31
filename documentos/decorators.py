from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from core.embed import embed_signal_response, is_embedded

from .constants import MODULO_CODIGO


def _usuario_tiene_acceso(request):
    user = request.user
    module_codes = getattr(request, "paldaca_module_codes", None)
    if module_codes is not None:
        return user.is_authenticated and MODULO_CODIGO in module_codes
    return (
        user.is_authenticated
        and hasattr(user, "tiene_acceso_modulo")
        and user.tiene_acceso_modulo(MODULO_CODIGO)
    )


def _deny_access(request):
    if not request.user.is_authenticated:
        if is_embedded(request):
            return embed_signal_response(request, "session-expired")
        return redirect(settings.PALDACA_SSO_LOGIN_URL)
    if is_embedded(request):
        return embed_signal_response(request, "forbidden")
    return HttpResponseForbidden("No tienes acceso a este programa.")


def requiere_modulo_paldaca(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if _usuario_tiene_acceso(request):
            return view_func(request, *args, **kwargs)
        return _deny_access(request)

    return _wrapped
