from .constants import MODULO_CODIGO


def es_aprobador_codigos(user, request=None):
    if request is not None:
        cached = getattr(request, "paldaca_es_aprobador", None)
        if cached is not None:
            return cached

    if not user.is_authenticated:
        result = False
    elif hasattr(user, "es_administrador_en_modulo") and user.es_administrador_en_modulo(
        MODULO_CODIGO
    ):
        result = True
    else:
        result = user.has_perm("documentos.puede_anular_codigo")

    if request is not None:
        request.paldaca_es_aprobador = result
    return result
