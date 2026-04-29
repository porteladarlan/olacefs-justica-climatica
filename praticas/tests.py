from django.contrib.auth import get_user_model
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
            nome="Auditoria",
            nome_es="Auditoria",
            nome_en="Audit",
        )
        setor = Setor.objects.create(
            nome="Agua",
            nome_es="Agua",
            nome_en="Water",
        )
        tema = TemaTransversal.objects.create(
            nome="Direitos humanos",
            nome_es="Derechos humanos",
            nome_en="Human rights",
        )
        norma = NormaInternacional.objects.create(
            nome="Acordo de Paris",
            nome_es="Acuerdo de Paris",
            nome_en="Paris Agreement",
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

        pendente = Experiencia.objects.create(
            titulo="Boa pratica pendente",
            titulo_es="Buena practica pendiente",
            titulo_en="Pending good practice",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            contato_referencia="Contato Pendente",
            email_contato="autor@example.org",
            descricao="Experiencia aguardando revisao.",
            descricao_es="Experiencia esperando revision.",
            descricao_en="Experience awaiting review.",
            enfoque_justica_climatica="Equidade.",
            enfoque_justica_climatica_es="Equidad.",
            enfoque_justica_climatica_en="Equity.",
            status_publicacao=Experiencia.StatusPublicacao.ENVIADO,
        )
        pendente.temas_transversais.add(tema)
        pendente.normas_internacionais.add(norma)

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

    def test_comparar_experiencias_retorna_200(self):
        self.assertEqual(self.client.get(reverse("comparar_experiencias")).status_code, 200)

    def test_comparar_experiencias_com_item(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        response = self.client.get(reverse("comparar_experiencias"), {"experiencias": [experiencia.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TCU")

    def test_normas_retorna_200(self):
        self.assertEqual(self.client.get(reverse("normas_internacionais")).status_code, 200)

    def test_adicionar_boa_pratica_retorna_200(self):
        self.assertEqual(self.client.get(reverse("adicionar_boa_pratica")).status_code, 200)

    def test_status_envio_retorna_200(self):
        self.assertEqual(self.client.get(reverse("status_envio")).status_code, 200)

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

    def test_painel_revisao_exige_login_staff(self):
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.status_code, 302)

    def test_painel_revisao_staff_retorna_200(self):
        usuario = get_user_model().objects.create_user(
            username="revisor",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending good practice")
        self.assertContains(response, "autor@example.org")
        self.assertContains(response, "2026")

    def test_revisor_publica_experiencia(self):
        usuario = get_user_model().objects.create_user(
            username="revisor2",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {
                "acao": "publicar",
                "comentario_revisor": "Aprovada para publicação.",
            },
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(
            experiencia.status_publicacao,
            Experiencia.StatusPublicacao.PUBLICADO,
        )

    def test_consulta_status_por_email(self):
        response = self.client.get(
            reverse("status_envio"),
            {"email_contato": "autor@example.org"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending good practice")
        self.assertContains(response, "autor@example.org")
        self.assertContains(response, "2026")

    def test_edicao_exige_email_valido(self):
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        response = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(response.status_code, 302)

    def test_autor_edita_e_reenvia(self):
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        response = self.client.post(
            f"{reverse('editar_boa_pratica', args=[experiencia.pk])}?email=autor@example.org",
            {
                "efs": experiencia.efs_id,
                "pais": experiencia.pais_id,
                "titulo": "Boa pratica ajustada",
                "tipo_experiencia": experiencia.tipo_experiencia_id,
                "setor": experiencia.setor_id,
                "temas_transversais": [str(item.id) for item in experiencia.temas_transversais.all()],
                "normas_internacionais": [str(item.id) for item in experiencia.normas_internacionais.all()],
                "contato_referencia": "Contato Ajustado",
                "email_contato": "autor@example.org",
                "pessoa_responsavel": "Pessoa Ajustada",
                "descricao": "Descricao ajustada.",
                "enfoque_justica_climatica": "Enfoque ajustado.",
                "objetivo": "Objetivo ajustado.",
                "perguntas_chave": "Pergunta ajustada.",
                "criterios_utilizados": "Criterio ajustado.",
                "metodologia": "Metodologia ajustada.",
                "ferramentas_utilizadas": "Ferramenta ajustada.",
                "resultados": "Resultado ajustado.",
                "recomendacoes": "Recomendacao ajustada.",
                "replicabilidade": "Replicabilidade ajustada.",
                "ano_execucao": 2026,
                "contribui_para_guia": "on",
                "acao_envio": "enviar",
                "email_contato_original": "autor@example.org",
            },
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.titulo, "Boa pratica ajustada")
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ENVIADO)

    def test_catalogo_tem_selecao_para_comparacao(self):
        response = self.client.get(reverse("catalogo_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "catalog-compare-checkbox")
        self.assertContains(response, "catalogoCompararSelecionadas")


    def test_favoritos_retorna_200(self):
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)

    def test_alternar_favorito_adiciona_na_sessao(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        response = self.client.post(
            reverse("alternar_favorito", args=[experiencia.pk]),
            {"next": reverse("favoritos_experiencias")},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(experiencia.pk, self.client.session.get("favoritos_experiencias", []))

    def test_favoritos_exibe_experiencia_salva(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        session = self.client.session
        session["favoritos_experiencias"] = [experiencia.pk]
        session.save()

        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Assessment of equity in access to water")

