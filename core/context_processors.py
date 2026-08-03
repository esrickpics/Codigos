from django.conf import settings

from documentos.permissions import es_aprobador_codigos

from .embed import is_embedded


def _nav_asset_base():
    if settings.DEBUG:
        return "http://127.0.0.1:8000"
    return "https://cpaldaca.com"


def paldaca_urls(request):
    asset_base = _nav_asset_base()
    # Fuente unica: el mismo valor que usa core/embed.py como targetOrigin de
    # postMessage. Si divergieran, el shell descartaria en silencio todos los
    # mensajes del satelite y el overlay de carga se quedaria colgado.
    portal_url = settings.PALDACA_PORTAL_URL
    api_base = (
        "http://127.0.0.1:8000/api"
        if settings.DEBUG
        else "https://api.cpaldaca.com/api"
    )
    return {
        "paldaca_sso_login_url": settings.PALDACA_SSO_LOGIN_URL,
        "paldaca_sso_logout_url": settings.PALDACA_SSO_LOGOUT_URL,
        "paldaca_nav_css": f"{asset_base}/static/paldaca-nav.css",
        "paldaca_nav_js": f"{asset_base}/static/paldaca-nav.js",
        "paldaca_embed_css": f"{asset_base}/static/paldaca-embed.css",
        "paldaca_nav_api_base": api_base,
        "paldaca_nav_portal_url": portal_url,
        "paldaca_nav_logo_full": f"{portal_url}/images/logo%20blanco.png",
        "paldaca_nav_logo_compact": f"{portal_url}/images/logo%20blanco%20recortado.png",
        "paldaca_nav_current_app": settings.PALDACA_MODULO_CODIGO,
        "paldaca_embedded": is_embedded(request),
    }


def navigation_context(request):
    return {
        "is_aprobador": es_aprobador_codigos(request.user),
    }
