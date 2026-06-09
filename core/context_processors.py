from django.conf import settings

from documentos.permissions import es_aprobador_codigos


def paldaca_urls(request):
    return {
        "paldaca_sso_login_url": settings.PALDACA_SSO_LOGIN_URL,
        "paldaca_sso_logout_url": settings.PALDACA_SSO_LOGOUT_URL,
    }


def navigation_context(request):
    return {
        "is_aprobador": es_aprobador_codigos(request.user),
    }
