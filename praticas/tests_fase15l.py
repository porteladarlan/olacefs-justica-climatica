from django.test import TestCase
from django.utils.translation import activate, deactivate


class UsabilidadeAcessibilidadeTests(TestCase):
    def tearDown(self):
        deactivate()

    def test_base_inclui_regras_de_toque_e_mobile(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn("Fase 15L: usabilidade e acessibilidade", conteudo)
        self.assertIn("min-height: 44px", conteudo)
        self.assertIn("prefers-contrast: more", conteudo)
        self.assertIn("overflow-wrap: anywhere", conteudo)

    def test_skip_link_e_main_permanecem_acessiveis(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn('class="skip-link"', conteudo)
        self.assertIn('id="conteudo-principal"', conteudo)
        self.assertIn('tabindex="-1"', conteudo)

    def test_paginas_publicas_carregam_com_regras_mobile_em_ingles_e_espanhol(self):
        for idioma in ["en", "es"]:
            activate(idioma)
            response = self.client.get(f"/{idioma}/catalogo/")
            self.assertEqual(response.status_code, 200)
            conteudo = response.content.decode("utf-8")
            self.assertIn("Fase 15L: usabilidade e acessibilidade", conteudo)
            self.assertIn("max-width: 575.98px", conteudo)
