from django.test import TestCase


class PolimentoHomeApresentacaoTests(TestCase):
    TERMOS_PROIBIDOS = [
        "Link pendente",
        "Link pending",
        "Link pendiente",
        "Link to be inserted",
        "V&iacute;nculo pendiente",
        "MVP local",
        "Marcadores de logo",
        "Ambiente de demonstração",
        "LGBTQIAPN+",
    ]

    def test_home_nao_exibe_residuos_de_conteudo_incompleto(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        for termo in self.TERMOS_PROIBIDOS:
            self.assertNotIn(termo, conteudo)

    def test_home_padroniza_conteudo_em_portugues(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn("Fundamentos e estratégias", conteudo)
        self.assertNotIn("ODS 13, 16 y 17", conteudo)

    def test_home_ingles_e_espanhol_nao_exibem_link_pendente(self):
        for prefixo in ["/en/", "/es/"]:
            response = self.client.get(prefixo)
            self.assertEqual(response.status_code, 200)
            conteudo = response.content.decode("utf-8")
            self.assertNotIn("Link pending", conteudo)
            self.assertNotIn("Link pendiente", conteudo)
            self.assertNotIn("Link pendente", conteudo)
            self.assertNotIn("LGBTQIAPN+", conteudo)
