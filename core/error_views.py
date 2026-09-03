import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def custom_500(request):
    logger.error("500 | path=%s", request.path)
    return render(request, "errors/500.html", status=500)


def custom_404(request, exception=None):
    logger.warning("404 | path=%s", request.path)
    return render(request, "errors/404.html", status=404)


def custom_403(request, exception=None):
    logger.warning("403 | path=%s", request.path)
    return render(request, "errors/403.html", status=403)
