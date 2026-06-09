from .constants import MODULO_CODIGO


def es_aprobador_codigos(user):
    if not user.is_authenticated:
        return False
    if hasattr(user, "es_administrador_en_modulo"):
        if user.es_administrador_en_modulo(MODULO_CODIGO):
            return True
    return user.has_perm("documentos.puede_anular_codigo")
