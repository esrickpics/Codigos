"""Query budgets for the pages most often loaded inside the Portal iframe."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from core.models import Modulo, UsuarioModulo
from documentos.models import CodigoGenerado, Empresa
from documentos.views import LIST_PAGE_SIZE

IFRAME = {"sec-fetch-dest": "iframe"}


class QueryBudgetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="perf_codigos",
            email="perf-codigos@example.com",
            password="test-pass-123",
        )
        modulo, _ = Modulo.objects.get_or_create(
            codigo="codigos", defaults={"nombre": "Codigos"}
        )
        UsuarioModulo.objects.get_or_create(usuario=cls.user, modulo=modulo)
        empresa = Empresa.objects.create(
            sigla="PAL",
            nombre="Paldaca",
            correo_notificacion="perf@example.com",
        )
        CodigoGenerado.objects.bulk_create(
            [
                CodigoGenerado(
                    empresa=empresa,
                    año="2026",
                    numero_proyecto="01",
                    subproyecto="A",
                    departamento="IT",
                    disciplina="ME",
                    tipo_documento="REP",
                    consecutivo=index,
                    codigo=f"PAL-26-01-A-IT-ME-REP-{index:04d}",
                    motivo="presupuesto",
                    usuario=cls.user,
                )
                for index in range(40)
            ]
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        self.client.get("/", headers=IFRAME)

    def _assert_budget(self, url, maximum):
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(url, headers=IFRAME)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            len(captured),
            maximum,
            f"{url} ejecutó {len(captured)} queries; presupuesto: {maximum}\n"
            + "\n".join(query["sql"] for query in captured.captured_queries),
        )
        return response

    def test_presupuesto_home(self):
        self._assert_budget("/", 16)

    def test_presupuesto_listado_codigos(self):
        response = self._assert_budget("/Codigos/", 16)
        page = response.context["codigos"]
        self.assertLessEqual(len(page.object_list), 15)
        self.assertGreater(page.paginator.count, 15)

    def test_listado_todos_esta_paginado(self):
        response = self.client.get("/Codigos/", {"todos": "1"}, headers=IFRAME)
        self.assertEqual(response.status_code, 200)
        page = response.context["codigos"]
        self.assertLessEqual(len(page.object_list), LIST_PAGE_SIZE)

    def test_presupuesto_buscador(self):
        self._assert_budget("/BuscarCodigo/", 18)

    def test_smtp_tiene_timeout_explicito(self):
        self.assertEqual(settings.EMAIL_TIMEOUT, 8)
