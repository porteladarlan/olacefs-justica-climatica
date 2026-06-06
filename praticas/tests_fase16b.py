from django.test import TestCase


class ValidacaoRenderPublicoTests(TestCase):
    TERMOS_PROIBIDOS = [
        "MVP local",
        "Marcadores de logo",
        "Marcadores de logo para o MVP",
        "Ambiente de demonstração",
    ]

    def test_home_local_nao_exibe_termos_antigos_de_mvp(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        for termo in self.TERMOS_PROIBIDOS:
            self.assertNotIn(termo, conteudo)

    def test_paginas_principais_locais_carregam_sem_termos_antigos(self):
        for caminho in ["/", "/catalogo/", "/banco-tecnico/", "/normas-internacionais/", "/sobre/"]:
            response = self.client.get(caminho)
            self.assertEqual(response.status_code, 200)
            conteudo = response.content.decode("utf-8")
            for termo in self.TERMOS_PROIBIDOS:
                self.assertNotIn(termo, conteudo)
