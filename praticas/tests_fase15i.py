from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation
from urllib.parse import parse_qs, urlsplit

from .models import Anexo, EFS, Experiencia, Pais, PropostaEdicaoExperiencia, Setor, TipoExperiencia


class PainelFormularioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.form_count = 0
        self.in_form = False
        self.controls = []
        self.labels = []
        self.buttons = []
        self.links = []
        self._label = None
        self._button = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "form" and not self.in_form:
            self.in_form = atributos.get("data-testid") == "panel-open-search"
            if self.in_form:
                self.form_count += 1
        elif self.in_form and tag in {"input", "select", "button"}:
            self.controls.append((tag, atributos))
        if self.in_form and tag == "label":
            self._label = [atributos.get("for", ""), []]
        if self.in_form and tag == "button":
            self._button = []
        if self.in_form and tag == "a":
            self._link = []

    def handle_data(self, data):
        if self._label is not None:
            self._label[1].append(data)
        if self._button is not None:
            self._button.append(data)
        if self._link is not None:
            self._link.append(data)

    def handle_endtag(self, tag):
        if tag == "label" and self._label is not None:
            self.labels.append((self._label[0], "".join(self._label[1]).strip()))
            self._label = None
        if tag == "button" and self._button is not None:
            self.buttons.append("".join(self._button).strip())
            self._button = None
        if tag == "a" and self._link is not None:
            self.links.append("".join(self._link).strip())
            self._link = None
        if tag == "form" and self.in_form:
            self.in_form = False


class FluxoRevisaoAprovacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="revisor_fase15i",
            email="revisor_fase15i@example.org",
            password="teste123",
            is_staff=True,
        )
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="País Hispano", nome_en="Brazil", sigla="BRA")
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
            pessoa_responsavel="Pessoa Responsável",
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

    def test_painel_revisao_em_ingles_preserva_interface_e_status_historico(self):
        with translation.override("en"):
            response = self.client.get("/en/painel-revisao/")

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertIn("Good practice management", conteudo)
        self.assertIn('data-status-metric="publicado"', conteudo)
        self.assertIn('class="status-pill status-enviado"', conteudo)
        self.assertNotIn("Review published content edits", conteudo)
        self.assertNotIn("Revisar edições de conteúdos publicados", conteudo)

    def parse_painel_formulario(self, response):
        parser = PainelFormularioParser()
        parser.feed(response.content.decode("utf-8"))
        return parser

    def criar_praticas_para_busca(self):
        pais_alvo = Pais.objects.create(
            nome="ALVO_PAIS_PT_9XZ",
            nome_es="ALVO_PAIS_ES_9XZ",
            nome_en="ALVO_PAIS_EN_9XZ",
            sigla="AP9",
        )
        efs_alvo = EFS.objects.create(
            nome="ALVO_EFS_PT_9XZ",
            nome_es="ALVO_EFS_ES_9XZ",
            nome_en="ALVO_EFS_EN_9XZ",
            sigla="AE9",
            pais=pais_alvo,
        )
        pratica_alvo = Experiencia.objects.create(
            titulo="ALVO_TITULO_PT_9XZ",
            titulo_es="ALVO_TITULO_ES_9XZ",
            titulo_en="ALVO_TITULO_EN_9XZ",
            efs=efs_alvo,
            pais=pais_alvo,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            email_contato="alvo.email.9xz@example.org",
            pessoa_responsavel="ALVO_RESPONSAVEL_9XZ COMBINADO_STATUS_7LM",
            descricao="Descrição da prática alvo.",
            status_publicacao=Experiencia.StatusPublicacao.ENVIADO,
        )
        pais_controle = Pais.objects.create(
            nome="CONTROLE_PAIS_PT_4QW",
            nome_es="CONTROLE_PAIS_ES_4QW",
            nome_en="CONTROLE_PAIS_EN_4QW",
            sigla="CP4",
        )
        efs_controle = EFS.objects.create(
            nome="CONTROLE_EFS_PT_4QW",
            nome_es="CONTROLE_EFS_ES_4QW",
            nome_en="CONTROLE_EFS_EN_4QW",
            sigla="CE4",
            pais=pais_controle,
        )
        pratica_controle = Experiencia.objects.create(
            titulo="CONTROLE_TITULO_PT_4QW",
            titulo_es="CONTROLE_TITULO_ES_4QW",
            titulo_en="CONTROLE_TITULO_EN_4QW",
            efs=efs_controle,
            pais=pais_controle,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            email_contato="controle.email.4qw@example.org",
            pessoa_responsavel="CONTROLE_RESPONSAVEL_4QW COMBINADO_STATUS_7LM",
            descricao="Descrição da prática controle.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        termos = (
            "ALVO_TITULO_PT_9XZ",
            "ALVO_TITULO_ES_9XZ",
            "ALVO_TITULO_EN_9XZ",
            "ALVO_PAIS_PT_9XZ",
            "ALVO_PAIS_ES_9XZ",
            "ALVO_PAIS_EN_9XZ",
            "ALVO_EFS_PT_9XZ",
            "ALVO_EFS_ES_9XZ",
            "ALVO_EFS_EN_9XZ",
            "alvo.email.9xz@example.org",
            "ALVO_RESPONSAVEL_9XZ",
        )
        return pratica_alvo, pratica_controle, termos

    def test_painel_apresenta_busca_aberta_localizada_sem_filtro_status(self):
        casos = (
            (
                "/painel-revisao/",
                "Busca geral",
                "Nome da boa prática, país, EFS, e-mail ou responsável",
                "Buscar",
                "Limpar",
            ),
            (
                "/es/painel-revisao/",
                "Búsqueda general",
                "Nombre de la buena práctica, país, EFS, correo o responsable",
                "Buscar",
                "Limpiar",
            ),
            (
                "/en/painel-revisao/",
                "General search",
                "Good practice name, country, SAI, e-mail or responsible person",
                "Search",
                "Clear",
            ),
        )
        for caminho, label, placeholder, buscar, limpar in casos:
            with self.subTest(caminho=caminho):
                idioma = "en" if caminho.startswith("/en/") else "es" if caminho.startswith("/es/") else "pt-br"
                with translation.override(idioma):
                    response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'data-testid="panel-open-search"')
                parser = self.parse_painel_formulario(response)
                self.assertEqual(parser.form_count, 1)
                self.assertEqual(
                    [attrs.get("name") for tag, attrs in parser.controls if attrs.get("name") == "q"],
                    ["q"],
                )
                self.assertFalse([attrs for tag, attrs in parser.controls if attrs.get("name") == "status"])
                self.assertIn(("panel-search", label), parser.labels)
                campo_busca = [attrs for tag, attrs in parser.controls if attrs.get("name") == "q"][0]
                self.assertEqual(campo_busca.get("placeholder"), placeholder)
                self.assertIn(buscar, parser.buttons)
                self.assertIn(limpar, parser.links)

    def test_painel_mantem_status_historico_nos_cards_e_metricas_publicas(self):
        response = self.client.get(reverse("painel_revisao"))
        conteudo = response.content.decode("utf-8")
        self.assertIn('data-status-metric="publicado"', conteudo)
        self.assertIn('data-status-metric="arquivado"', conteudo)
        self.assertIn('class="status-pill status-enviado"', conteudo)

    def assert_busca_campo_exclusivo(self, indice_termo):
        pratica_alvo, pratica_controle, termos = self.criar_praticas_para_busca()
        with translation.override("pt-br"):
            response = self.client.get(reverse("painel_revisao"), {"q": termos[indice_termo]})
        self.assertEqual(response.status_code, 200)
        ids = {experiencia.pk for experiencia in response.context["experiencias"]}
        self.assertIn(pratica_alvo.pk, ids)
        self.assertNotIn(pratica_controle.pk, ids)

    @staticmethod
    def snapshot_model(instance):
        return {
            campo.attname: getattr(instance, campo.attname)
            for campo in instance._meta.concrete_fields
        }

    def test_painel_busca_titulo_pt(self):
        self.assert_busca_campo_exclusivo(0)

    def test_painel_busca_titulo_es(self):
        self.assert_busca_campo_exclusivo(1)

    def test_painel_busca_titulo_en(self):
        self.assert_busca_campo_exclusivo(2)

    def test_painel_busca_pais_pt(self):
        self.assert_busca_campo_exclusivo(3)

    def test_painel_busca_pais_es(self):
        self.assert_busca_campo_exclusivo(4)

    def test_painel_busca_pais_en(self):
        self.assert_busca_campo_exclusivo(5)

    def test_painel_busca_efs_pt(self):
        self.assert_busca_campo_exclusivo(6)

    def test_painel_busca_efs_es(self):
        self.assert_busca_campo_exclusivo(7)

    def test_painel_busca_efs_en(self):
        self.assert_busca_campo_exclusivo(8)

    def test_painel_busca_email(self):
        self.assert_busca_campo_exclusivo(9)

    def test_painel_busca_responsavel(self):
        self.assert_busca_campo_exclusivo(10)

    def test_painel_busca_com_status_legado_filtra_conjuntamente(self):
        pratica_alvo, pratica_controle, _ = self.criar_praticas_para_busca()
        with translation.override("pt-br"):
            response = self.client.get(
                reverse("painel_revisao"),
                {"q": "COMBINADO_STATUS_7LM", "status": "enviado"},
            )
        ids = {experiencia.pk for experiencia in response.context["experiencias"]}
        self.assertIn(pratica_alvo.pk, ids)
        self.assertNotIn(pratica_controle.pk, ids)
        self.assertNotContains(response, 'name="status"')

    def test_painel_busca_sem_escrita_compara_estado_integral_antes_e_depois(self):
        pratica_alvo, pratica_controle, termos = self.criar_praticas_para_busca()
        experiencias = [self.experiencia, pratica_alvo, pratica_controle]
        experiencias_antes = {
            experiencia.pk: self.snapshot_model(experiencia)
            for experiencia in experiencias
        }
        propostas_antes = {
            proposta.pk: self.snapshot_model(proposta)
            for proposta in PropostaEdicaoExperiencia.objects.all()
        }
        anexos_antes = {
            anexo.pk: self.snapshot_model(anexo)
            for anexo in Anexo.objects.all()
        }
        totais_antes = (
            Experiencia.objects.count(),
            PropostaEdicaoExperiencia.objects.count(),
            Anexo.objects.count(),
        )
        consultas = (
            termos[0],
            termos[0].lower(),
            f"  {termos[0]}  ",
            f"\x00{termos[0]}\x00",
            "x" * 201,
        )
        for termo in consultas:
            with self.subTest(termo=termo):
                response = self.client.get(reverse("painel_revisao"), {"q": termo})
                self.assertEqual(response.status_code, 200)
        self.client.get(
            reverse("painel_revisao"),
            {"q": "COMBINADO_STATUS_7LM", "status": "enviado"},
        )
        self.client.get(reverse("painel_revisao"), {"status": "invalido"})
        for experiencia in experiencias:
            experiencia.refresh_from_db()
        propostas_depois = {
            proposta.pk: self.snapshot_model(proposta)
            for proposta in PropostaEdicaoExperiencia.objects.all()
        }
        anexos_depois = {
            anexo.pk: self.snapshot_model(anexo)
            for anexo in Anexo.objects.all()
        }
        experiencias_depois = {
            experiencia.pk: self.snapshot_model(experiencia)
            for experiencia in experiencias
        }
        self.assertEqual(experiencias_depois, experiencias_antes)
        self.assertEqual(propostas_depois, propostas_antes)
        self.assertEqual(anexos_depois, anexos_antes)
        self.assertEqual(
            (
                Experiencia.objects.count(),
                PropostaEdicaoExperiencia.objects.count(),
                Anexo.objects.count(),
            ),
            totais_antes,
        )

    def test_painel_busca_normaliza_entrada(self):
        for termo in (" auditoria ", "AUDITORIA", "\x00Auditoria de água\x00"):
            with self.subTest(termo=termo):
                with translation.override("pt-br"):
                    response = self.client.get(reverse("painel_revisao"), {"q": termo})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Auditoria de água")
        with translation.override("pt-br"):
            response = self.client.get(reverse("painel_revisao"), {"q": " "})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Auditoria de água")
        with translation.override("pt-br"):
            response = self.client.get(reverse("painel_revisao"), {"q": "x" * 201})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["termo_busca"]), 200)

    def test_painel_busca_vazia_localizada_e_escapa_payload(self):
        casos = (
            ("/painel-revisao/", "Nenhuma boa prática encontrada para a busca informada."),
            ("/es/painel-revisao/", "No se encontraron buenas prácticas para la búsqueda informada."),
            ("/en/painel-revisao/", "No good practices were found for the search provided."),
        )
        for caminho, mensagem in casos:
            with self.subTest(caminho=caminho):
                idioma = "en" if caminho.startswith("/en/") else "es" if caminho.startswith("/es/") else "pt-br"
                with translation.override(idioma):
                    response = self.client.get(caminho, {"q": "não existe <script>alert(1)</script>"})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, mensagem)
                html = response.content.decode("utf-8")
                self.assertNotIn("<script>alert(1)</script>", html)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_painel_preserva_compatibilidade_do_status_sem_controle_visual(self):
        with translation.override("pt-br"):
            response = self.client.get(reverse("painel_revisao"), {"q": "Auditoria", "status": "enviado"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Auditoria de água")
        self.assertNotContains(response, 'name="status"')
        with translation.override("pt-br"):
            response = self.client.get(reverse("painel_revisao"), {"status": "invalido"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Auditoria de água")
        self.assertNotContains(response, 'name="status"')

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
        self.assertNotContains(response, 'name="status"')
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
