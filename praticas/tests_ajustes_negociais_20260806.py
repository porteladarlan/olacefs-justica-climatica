from django.test import TestCase


class AjustesNegociaisHome20260806Tests(TestCase):
    def test_home_pt_exibe_textos_aprovados(self):
        resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Palavras das Presid&ecirc;ncias da CGID e da COMTEMA",
        )

        self.assertContains(
            resposta,
            "a Plataforma de Justi&ccedil;a Clim&aacute;tica oferece um canal "
            "para o interc&acirc;mbio de boas pr&aacute;ticas e visualiza&ccedil;&atilde;o de normas e "
            "ferramentas de auditoria",
        )

        self.assertNotContains(
            resposta,
            "com o apoio da GIZ",
        )

        self.assertContains(
            resposta,
            'class="jc-hero-title-line jc-hero-title-nowrap"',
        )
