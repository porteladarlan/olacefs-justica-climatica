from django.test import TestCase
from django.urls import reverse

from .models import (
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class RotasPublicasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA")
        efs = EFS.objects.create(nome="Tribunal de Contas da Uniao", nome_es="Tribunal de Cuentas de la Union", nome_en="Federal Court of Accounts", sigla="TCU", pais=pais)
        tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoria", nome_en="Audit")
        setor = Setor.objects.create(nome="Agua", nome_es="Agua", nome_en="Water")
        tema = TemaTransversal.objects.create(nome="Direitos humanos", nome_es="Derechos humanos", nome_en="Human rights")
        norma = NormaInternacional.objects.create(nome="Acordo de Paris", nome_es="Acuerdo de Paris", nome_en="Paris Agreement")
        dimensao = DimensaoJusticaClimatica.objects.create(nome="Distributiva", nome_es="Distributiva", nome_en="Distributive")
        grupo = GrupoVulneravel.objects.create(nome="Populacao rural", nome_es="Poblacion rural", nome_en="Rural population")

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
            contato_referencia="Contato TCU",
            email_contato="contato@example.org",
            descricao="Experiencia de demonstracao sobre agua e justica climatica.",
            descricao_es="Experiencia de demostracion sobre agua y justicia climatica.",
            descricao_en="Demonstration experience on water and climate justice.",
            enfoque_justica_climatica="Direitos humanos e equidade.",
            enfoque_justica_climatica_es="Derechos humanos y equidad.",
            enfoque_justica_climatica_en="Human rights and equity.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        experiencia.temas_transversais.add(tema)
        experiencia.normas_internacionais.add(norma)
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

    def test_pagina_inicial_retorna_200(self):
        self.assertEqual(self.client.get(reverse("pagina_inicial")).status_code, 200)

    def test_catalogo_retorna_200(self):
        self.assertEqual(self.client.get(reverse("catalogo_experiencias")).status_code, 200)

    def test_normas_retorna_200(self):
        self.assertEqual(self.client.get(reverse("normas_internacionais")).status_code, 200)

    def test_adicionar_boa_pratica_retorna_200(self):
        self.assertEqual(self.client.get(reverse("adicionar_boa_pratica")).status_code, 200)

    def test_banco_tecnico_retorna_200(self):
        self.assertEqual(self.client.get(reverse("banco_tecnico")).status_code, 200)

    def test_sobre_retorna_200(self):
        self.assertEqual(self.client.get(reverse("sobre_plataforma")).status_code, 200)

    def test_rota_es_retorna_200(self):
        self.assertEqual(self.client.get("/es/").status_code, 200)

    def test_rota_en_retorna_200(self):
        self.assertEqual(self.client.get("/en/").status_code, 200)

    def test_busca_em_ingles_retorna_resultado(self):
        response = self.client.get("/en/catalogo/", {"q": "water"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TCU")

    def test_filtro_por_norma_retorna_resultado(self):
        norma = NormaInternacional.objects.get(nome="Acordo de Paris")
        response = self.client.get(reverse("catalogo_experiencias"), {"norma": norma.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TCU")
