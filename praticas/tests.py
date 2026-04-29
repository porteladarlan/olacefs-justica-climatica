from django.test import TestCase
from django.urls import reverse

from .models import (
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    Pais,
    Setor,
    TipoExperiencia,
)


class RotasPublicasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(
            nome="Brasil",
            nome_es="Brasil",
            nome_en="Brazil",
            sigla="BRA",
        )
        efs = EFS.objects.create(
            nome="Tribunal de Contas da Uniao",
            nome_es="Tribunal de Cuentas de la Union",
            nome_en="Federal Court of Accounts",
            sigla="TCU",
            pais=pais,
        )
        tipo = TipoExperiencia.objects.create(
            nome="Auditoria de desempenho",
            nome_es="Auditoria de desempeno",
            nome_en="Performance audit",
        )
        setor = Setor.objects.create(
            nome="Recursos hidricos",
            nome_es="Recursos hidricos",
            nome_en="Water resources",
        )
        dimensao = DimensaoJusticaClimatica.objects.create(
            nome="Distributiva",
            nome_es="Distributiva",
            nome_en="Distributive",
        )
        grupo = GrupoVulneravel.objects.create(
            nome="Populacao rural",
            nome_es="Poblacion rural",
            nome_en="Rural population",
        )

        experiencia = Experiencia.objects.create(
            titulo="Avaliacao da equidade no acesso a agua",
            titulo_es="Evaluacion de la equidad en el acceso al agua",
            titulo_en="Assessment of equity in access to water",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2025,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            descricao="Experiencia de demonstracao sobre agua e justica climatica.",
            descricao_es="Experiencia de demostracion sobre agua y justicia climatica.",
            descricao_en="Demonstration experience on water and climate justice.",
            problema_climatico="Seca e escassez de agua.",
            problema_climatico_es="Sequia y escasez de agua.",
            problema_climatico_en="Drought and water scarcity.",
            objetivo="Avaliar politicas publicas.",
            objetivo_es="Evaluar politicas publicas.",
            objetivo_en="Assess public policies.",
            resultados="Resultados de demonstracao.",
            resultados_es="Resultados de demostracion.",
            resultados_en="Demonstration results.",
            recomendacoes="Recomendacoes de demonstracao.",
            recomendacoes_es="Recomendaciones de demostracion.",
            recomendacoes_en="Demonstration recommendations.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        experiencia.dimensoes_consideradas.add(dimensao)
        experiencia.grupos_vulneraveis.add(grupo)

        recurso = BancoTecnico.objects.create(
            titulo="Checklist para avaliar planos de adaptacao",
            titulo_es="Checklist para evaluar planes de adaptacion",
            titulo_en="Checklist for assessing adaptation plans",
            descricao="Recurso tecnico de demonstracao.",
            descricao_es="Recurso tecnico de demostracion.",
            descricao_en="Demonstration technical resource.",
            tipo_recurso="Checklist",
            tipo_recurso_es="Checklist",
            tipo_recurso_en="Checklist",
            setor=setor,
        )
        recurso.dimensoes.add(dimensao)

    def assert_busca_tem_resultado(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TCU")
        self.assertContains(response, "2025")

    def test_pagina_inicial_retorna_200(self):
        response = self.client.get(reverse("pagina_inicial"))
        self.assertEqual(response.status_code, 200)

    def test_catalogo_retorna_200(self):
        response = self.client.get(reverse("catalogo_experiencias"))
        self.assertEqual(response.status_code, 200)

    def test_banco_tecnico_retorna_200(self):
        response = self.client.get(reverse("banco_tecnico"))
        self.assertEqual(response.status_code, 200)

    def test_sobre_retorna_200(self):
        response = self.client.get(reverse("sobre_plataforma"))
        self.assertEqual(response.status_code, 200)

    def test_rota_es_retorna_200(self):
        response = self.client.get("/es/")
        self.assertEqual(response.status_code, 200)

    def test_rota_en_retorna_200(self):
        response = self.client.get("/en/")
        self.assertEqual(response.status_code, 200)

    def test_busca_em_portugues_retorna_resultado(self):
        response = self.client.get("/catalogo/", {"q": "agua"})
        self.assert_busca_tem_resultado(response)

    def test_busca_em_espanhol_retorna_resultado(self):
        response = self.client.get("/es/catalogo/", {"q": "agua"})
        self.assert_busca_tem_resultado(response)

    def test_busca_em_ingles_retorna_resultado(self):
        response = self.client.get("/en/catalogo/", {"q": "water"})
        self.assert_busca_tem_resultado(response)
