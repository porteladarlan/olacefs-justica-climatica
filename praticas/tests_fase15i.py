from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import Anexo, EFS, Experiencia, Pais, PropostaEdicaoExperiencia, Setor, TipoExperiencia


class FluxoRevisaoAprovacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="revisor_fase15i",
            email="revisor_fase15i@example.org",
            password="teste123",
            is_staff=True,
        )
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA")
        cls.efs = EFS.objects.create(nome="Tribunal de Contas", nome_es="Tribunal de Cuentas", nome_en="Court of Accounts", sigla="TC", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        cls.setor = Setor.objects.create(nome="Água", nome_es="Agua", nome_en="Water")
        cls.experiencia = Experiencia.objects.create(
            titulo="Auditoria de água",
            titulo_es="Auditoría de agua",
            titulo_en="Water audit",
            efs=cls.efs,
            pais=cls.pais,
            tipo_experiencia=cls.tipo,
            setor=cls.setor,
            ano_execucao=2026,
            contato_referencia="Contato",
            email_contato="contato@example.org",
            descricao="Descrição",
            descricao_es="Descripción",
            descricao_en="Description",
            enfoque_justica_climatica="Equidade",
            enfoque_justica_climatica_es="Equidad",
            enfoque_justica_climatica_en="Equity",
            status_publicacao=Experiencia.StatusPublicacao.ENVIADO,
        )
        cls.proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=cls.experiencia,
            email_contato="contato@example.org",
            comentario_autor="Atualização de teste",
            dados_json={
                "titulo": "Auditoria de água atualizada",
                "resultados": "Resultados atualizados para revisão.",
            },
            status=PropostaEdicaoExperiencia.Status.PENDENTE,
        )
        cls.anexo = Anexo.objects.create(
            experiencia=cls.experiencia,
            titulo="Referência externa",
            titulo_es="Referencia externa",
            titulo_en="External reference",
            url_externa="https://example.org/reference",
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_painel_revisao_em_ingles_nao_exibe_rotulos_principais_em_portugues(self):
        with translation.override("en"):
            response = self.client.get("/en/painel-revisao/")

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertIn("Good practice management", conteudo)
        self.assertIn("Submitted", conteudo)
        self.assertIn("Under review", conteudo)
        self.assertIn("Approved", conteudo)
        self.assertIn("Review published content edits", conteudo)
        self.assertNotIn("Revisar edições de conteúdos publicados", conteudo)

    def test_rota_legada_de_revisao_redireciona_para_edicao(self):
        response = self.client.get(reverse("revisar_experiencia", args=[self.experiencia.pk]))
        self.assertRedirects(response, reverse("editar_boa_pratica", args=[self.experiencia.pk]))

    def test_rota_legada_nao_processa_decisao(self):
        status_anterior = self.experiencia.status_publicacao
        response = self.client.post(
            reverse("revisar_experiencia", args=[self.experiencia.pk]),
            {"acao": "aprovar", "comentario_revisor": "Não deve ser processado."},
        )
        self.assertRedirects(response, reverse("editar_boa_pratica", args=[self.experiencia.pk]))
        self.experiencia.refresh_from_db()
        self.assertEqual(self.experiencia.status_publicacao, status_anterior)
        self.assertEqual(self.experiencia.comentario_revisor, "")

    def test_painel_edicoes_em_ingles_exibe_textos_traduzidos(self):
        with translation.override("en"):
            response = self.client.get("/en/painel-revisao-edicoes/")

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertIn("Edit proposals", conteudo)
        self.assertIn("The published version remains active", conteudo)
        self.assertIn("Open proposal", conteudo)
        self.assertNotIn("Propostas de edição", conteudo)
