from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation
from urllib.parse import parse_qs, urlsplit

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
        self.assertNotIn("Review published content edits", conteudo)
        self.assertNotIn("Revisar edições de conteúdos publicados", conteudo)

    def test_painel_exibe_somente_publicado_e_arquivado_nos_tres_idiomas(self):
        casos = (
            ("/painel-revisao/", ("Publicado", "Arquivado")),
            ("/es/painel-revisao/", ("Publicado", "Archivado")),
            ("/en/painel-revisao/", ("Published", "Archived")),
        )
        for caminho, labels in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode("utf-8")
                inicio = html.index('data-testid="panel-status-metrics"')
                fim = html.index("</section>", inicio)
                container = html[inicio:fim]
                self.assertEqual(container.count("data-status-metric="), 2)
                self.assertIn('data-status-metric="publicado"', container)
                self.assertIn('data-status-metric="arquivado"', container)
                self.assertEqual(sum(label in container for label in labels), 2)
                for label in ("Enviado", "Em revisão", "Aprovado", "Edições pendentes", "En revisión", "Aprobado", "Ediciones pendientes", "Submitted", "Under review", "Approved", "Pending edits"):
                    self.assertNotIn(label, container)

    def test_painel_preserva_contadores_reais_estados_historicos_e_get_sem_escrita(self):
        publicado = Experiencia.objects.create(
            titulo="Publicada para contagem", efs=self.efs, pais=self.pais,
            tipo_experiencia=self.tipo, setor=self.setor, ano_execucao=2026,
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        arquivado = Experiencia.objects.create(
            titulo="Arquivada para contagem", efs=self.efs, pais=self.pais,
            tipo_experiencia=self.tipo, setor=self.setor, ano_execucao=2026,
            status_publicacao=Experiencia.StatusPublicacao.ARQUIVADO,
        )
        em_revisao = Experiencia.objects.create(
            titulo="Em revisão para contagem", efs=self.efs, pais=self.pais,
            tipo_experiencia=self.tipo, setor=self.setor, ano_execucao=2026,
            status_publicacao=Experiencia.StatusPublicacao.EM_REVISAO,
        )
        aprovado = Experiencia.objects.create(
            titulo="Aprovada para contagem", efs=self.efs, pais=self.pais,
            tipo_experiencia=self.tipo, setor=self.setor, ano_execucao=2026,
            status_publicacao=Experiencia.StatusPublicacao.APROVADO,
        )
        estados = {
            self.experiencia.pk: self.experiencia.status_publicacao,
            publicado.pk: publicado.status_publicacao,
            arquivado.pk: arquivado.status_publicacao,
            em_revisao.pk: em_revisao.status_publicacao,
            aprovado.pk: aprovado.status_publicacao,
        }
        total_experiencias = Experiencia.objects.count()
        total_propostas = PropostaEdicaoExperiencia.objects.count()
        total_anexos = Anexo.objects.count()
        status_proposta = self.proposta.status
        anexo_existente = Anexo.objects.filter(pk=self.anexo.pk).exists()
        response = self.client.get("/painel-revisao/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["contadores"]["publicado"], 1)
        self.assertEqual(response.context["contadores"]["arquivado"], 1)
        self.assertEqual({pk: Experiencia.objects.get(pk=pk).status_publicacao for pk in estados}, estados)
        self.assertEqual(Experiencia.objects.count(), total_experiencias)
        self.assertEqual(PropostaEdicaoExperiencia.objects.count(), total_propostas)
        self.assertEqual(Anexo.objects.count(), total_anexos)
        self.assertTrue(PropostaEdicaoExperiencia.objects.filter(pk=self.proposta.pk).exists())
        self.assertEqual(self.proposta.refresh_from_db(), None)
        self.assertEqual(self.proposta.status, status_proposta)
        self.assertEqual(self.proposta.status, PropostaEdicaoExperiencia.Status.PENDENTE)
        self.assertTrue(Anexo.objects.filter(pk=self.anexo.pk).exists())
        self.assertEqual(Anexo.objects.filter(pk=self.anexo.pk).exists(), anexo_existente)

    def test_rota_de_edicoes_legada_preserva_permissao_para_staff_anonimo_e_nao_staff(self):
        resposta_staff = self.client.get(reverse("painel_revisao_edicoes"))
        self.assertEqual(resposta_staff.status_code, 302)
        self.assertEqual(urlsplit(resposta_staff.url).path, reverse("painel_revisao"))

        anonimo = self.client_class()
        resposta_anonimo = anonimo.get(reverse("painel_revisao_edicoes"))
        self.assertEqual(resposta_anonimo.status_code, 302)
        partes_anonimo = urlsplit(resposta_anonimo.url)
        self.assertEqual(partes_anonimo.path, "/admin/login/")
        self.assertEqual(parse_qs(partes_anonimo.query).get("next"), [reverse("painel_revisao_edicoes")])

        nao_staff = get_user_model().objects.create_user(
            username="nao_staff_fase15i", password="teste123"
        )
        cliente_nao_staff = self.client_class()
        cliente_nao_staff.force_login(nao_staff)
        resposta_nao_staff = cliente_nao_staff.get(reverse("painel_revisao_edicoes"))
        self.assertEqual(resposta_nao_staff.status_code, 302)
        partes_nao_staff = urlsplit(resposta_nao_staff.url)
        self.assertEqual(partes_nao_staff.path, "/admin/login/")
        self.assertEqual(parse_qs(partes_nao_staff.query).get("next"), [reverse("painel_revisao_edicoes")])

    def test_rota_de_edicoes_legada_e_busca_do_painel_permanecem_disponiveis(self):
        response = self.client.get(reverse("painel_revisao_edicoes"))
        self.assertRedirects(response, reverse("painel_revisao"))
        response = self.client.get(reverse("painel_revisao"), {"q": "Auditoria", "status": "enviado"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'name="status"')
        self.assertNotContains(response, "Revisar edições de conteúdos publicados")

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

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith("/en/painel-revisao/"))
