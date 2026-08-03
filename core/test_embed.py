"""
Contrato de embebido en el shell del Portal (`paldaca-embed` v1).

Cubre lo que se rompe en silencio: si alguien repone `XFrameOptionsMiddleware`
o `X_FRAME_OPTIONS`, el modulo deja de cargar dentro de cpaldaca.com y el unico
sintoma es un area de trabajo en blanco, sin error en el servidor.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from core.models import Modulo, UsuarioModulo


class EmbedContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="pytest_user",
            email="pytest@example.com",
            password="test-pass-123",
        )
        modulo, _ = Modulo.objects.get_or_create(
            codigo="codigos", defaults={"nombre": "Codigos"}
        )
        UsuarioModulo.objects.get_or_create(usuario=cls.user, modulo=modulo)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_dentro_del_iframe_emite_csp_y_no_bloquea_el_framing(self):
        res = self.client.get("/", headers={"sec-fetch-dest": "iframe"})

        self.assertEqual(res.status_code, 200)
        self.assertIn("frame-ancestors", res.headers.get("Content-Security-Policy", ""))
        self.assertIsNone(res.headers.get("X-Frame-Options"))

    def test_dentro_del_iframe_no_monta_el_nav_duplicado(self):
        body = self.client.get("/", headers={"sec-fetch-dest": "iframe"}).content.decode()

        self.assertNotIn("paldaca-nav-root", body)
        self.assertIn("paldaca-embed.css", body)

    def test_navegacion_top_level_conserva_el_nav_propio(self):
        body = self.client.get(
            "/", headers={"sec-fetch-dest": "document"}
        ).content.decode()

        self.assertIn("paldaca-nav-root", body)
        self.assertNotIn("paldaca-embed.css", body)

    def test_cookie_de_respaldo_mantiene_el_estado_sin_sec_fetch(self):
        """Navegadores sin cabeceras `Sec-Fetch-*` (capa 2 de la deteccion)."""
        self.client.get("/", headers={"sec-fetch-dest": "iframe"})

        body = self.client.get("/").content.decode()

        self.assertIn("paldaca-embed.css", body)

    def test_una_navegacion_top_level_invalida_la_cookie_de_respaldo(self):
        """Sin esto, abrir el subdominio en una pestana seguiria pareciendo embebido."""
        self.client.get("/", headers={"sec-fetch-dest": "iframe"})

        res = self.client.get("/", headers={"sec-fetch-dest": "document"})

        self.assertEqual(res.cookies["paldaca_embed"]["max-age"], 0)
        self.assertIn("paldaca-nav-root", res.content.decode())

    @override_settings(PALDACA_EMBED_REDIRECT_TO_SHELL=True)
    def test_acceso_directo_al_subdominio_redirige_al_shell(self):
        res = self.client.get("/Codigos/", headers={"sec-fetch-dest": "document"})

        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["Location"].endswith("/codigos/Codigos/"))

    @override_settings(PALDACA_EMBED_REDIRECT_TO_SHELL=True)
    def test_el_redirect_al_shell_no_aplica_dentro_del_iframe(self):
        """Redirigir aqui meteria el shell dentro del shell."""
        res = self.client.get("/", headers={"sec-fetch-dest": "iframe"})

        self.assertEqual(res.status_code, 200)

    @override_settings(PALDACA_EMBED_REDIRECT_TO_SHELL=True)
    def test_valvula_de_escape_sirve_el_satelite_suelto(self):
        res = self.client.get(
            "/?paldaca_standalone=1", headers={"sec-fetch-dest": "document"}
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("paldaca-nav-root", res.content.decode())
