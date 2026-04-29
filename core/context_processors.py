def navigation_context(request):
    if not request.user.is_authenticated:
        return {"is_aprobador": False}

    is_aprobador = request.user.groups.filter(name__iexact="aprobadores").exists()
    return {"is_aprobador": is_aprobador}
