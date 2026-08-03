from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect

from .embed import embed_signal_response, is_embedded
from .session_logout import apply_paldaca_cookie_clearance, close_paldaca_session


class PaldacaSessionMiddleware:
    SESSION_REVISION_KEY = "paldaca_auth_revision"
    SESSION_ROL_KEY = "paldaca_rol"
    SESSION_DISCIPLINA_KEY = "paldaca_disciplina_id"
    SESSION_PERFIL_KEY = "paldaca_perfil_id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        if not hasattr(request, "session"):
            return self.get_response(request)

        current_user = self._get_current_user(user.pk)
        if not current_user or not current_user.is_active:
            return self._close_session(request)

        current_revision = current_user.get_auth_revision()
        session_revision = request.session.get(self.SESSION_REVISION_KEY)

        if not session_revision:
            self._store_snapshot(request, current_user, current_revision)
            return self.get_response(request)

        if session_revision != current_revision:
            strict_mode = (
                str(
                    getattr(settings, "PALDACA_STRICT_SESSION_CONSISTENCY", "true")
                ).lower()
                == "true"
            )
            if strict_mode:
                return self._close_session(request)
            self._store_snapshot(request, current_user, current_revision)

        return self.get_response(request)

    def _get_current_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.select_related("disciplina", "perfil").get(
                pk=user_id
            )
        except user_model.DoesNotExist:
            return None

    def _store_snapshot(self, request, user, revision):
        request.session[self.SESSION_REVISION_KEY] = revision
        request.session[self.SESSION_ROL_KEY] = user.rol
        request.session[self.SESSION_DISCIPLINA_KEY] = user.disciplina_id
        request.session[self.SESSION_PERFIL_KEY] = user.perfil_id

    def _close_session(self, request):
        close_paldaca_session(request)

        login_url = getattr(settings, "PALDACA_SSO_LOGIN_URL", "/login/")
        accept_header = request.headers.get("Accept", "").lower()
        is_api_request = (
            request.path.startswith("/api/")
            or "application/json" in accept_header
        )

        if is_api_request:
            response = JsonResponse(
                {"detail": "La sesion se cerro porque cambiaron tus permisos."},
                status=401,
            )
            return apply_paldaca_cookie_clearance(response)

        # Dentro del shell, un redirect al login navegaria el propio iframe y el
        # usuario veria el formulario de login incrustado en el area de trabajo.
        if is_embedded(request):
            response = embed_signal_response(request, "session-expired")
            return apply_paldaca_cookie_clearance(response)

        response = redirect(login_url)
        return apply_paldaca_cookie_clearance(response)
