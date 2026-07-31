from django.test import TestCase
from django.urls import reverse


class HomePrimeiraEvolucaoTests(TestCase):
    def test_home_destaca_acessos_principais_com_destinos_reais(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Boas Pr&aacute;ticas", html=False)
        self.assertContains(response, "Banco T&eacute;cnico", html=False)
        self.assertContains(
            response,
            "Dimens&otilde;es de Justi&ccedil;a Clim&aacute;tica",
            html=False,
        )
        self.assertContains(response, f'href="{reverse("catalogo_experiencias")}"')
        self.assertContains(response, f'href="{reverse("banco_tecnico")}"')
        self.assertContains(response, 'data-home-tab-target="#concepto-tab"')

    def test_home_preserva_acessos_nos_tres_idiomas(self):
        casos = [
            ("/", "Boas Pr&aacute;ticas", "Dimens&otilde;es de Justi&ccedil;a Clim&aacute;tica"),
            ("/es/", "Buenas Pr&aacute;cticas", "Dimensiones de Justicia Clim&aacute;tica"),
            ("/en/", "Good Practices", "Climate Justice Dimensions"),
        ]

        for caminho, praticas, dimensoes in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, praticas, html=False)
                self.assertContains(response, dimensoes, html=False)

    def test_bloco_de_acessos_tem_estrutura_semantica(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(
            response,
            '<section class="home-primary-access mb-5" '
            'aria-labelledby="home-primary-access-title">',
            html=False,
        )
        self.assertContains(response, 'id="home-primary-access-title"')
        self.assertEqual(
            response.content.decode("utf-8").count(
                '<article class="home-primary-access-card">'
            ),
            3,
        )
