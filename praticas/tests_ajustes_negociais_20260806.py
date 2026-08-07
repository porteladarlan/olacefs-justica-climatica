from django.test import TestCase


class AjustesNegociaisHome20260806Tests(TestCase):
    def test_home_pt_exibe_textos_aprovados(self):
        resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Palavras das Presid&ecirc;ncias da COMTEMA e da CGID",
        )

        self.assertContains(
            resposta,
            "a Plataforma promove um canal para o intercambio de boas "
            "pr&aacute;ticas e visualiza&ccedil;&atilde;o de normas e "
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
