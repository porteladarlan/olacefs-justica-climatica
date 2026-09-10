import inspect
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import Ferramenta, LoteImportacaoConteudo, Setor
from . import views


class FerramentaPainelParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_section = False
        self.in_card = False
        self.in_form = False
        self.cards = []
        self.forms = []
        self.classes = []
        self.texto = []
        self._card = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        classes = set((atributos.get("class") or "").split())
        if tag == "section" and atributos.get("data-testid") == "panel-tools":
            self.in_section = True
        if not self.in_section:
            return
        if classes:
            self.classes.append(classes)
        if tag == "article" and "submission-item" in classes:
            self.in_card = True
            self._card = {"classes": [], "text": []}
        if self.in_card and classes:
            self._card["classes"].append(classes)
        if tag == "form":
            self.in_form = True
            self.forms.append(atributos)
        if self.in_card and atributos.get("href"):
            self._card.setdefault("links", []).append(atributos["href"])

    def handle_data(self, data):
        if self.in_section:
            self.texto.append(data)
        if self.in_card and self._card is not None:
            self._card["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "article" and self.in_card:
            self.cards.append(self._card)
            self._card = None
            self.in_card = False
        if tag == "form" and self.in_form:
            self.in_form = False
        if tag == "section" and self.in_section:
            self.in_section = False


class GestaoFerramentasNeg3Tests(TestCase):
    def setUp(self):
        translation.activate("pt-br")
        self.addCleanup(translation.deactivate)

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(
            username="staff-neg3", password="senha-neg3", is_staff=True
        )
        cls.usuario = User.objects.create_user(
            username="usuario-neg3", password="senha-neg3"
        )
        cls.outro_usuario = User.objects.create_user(
            username="outro-neg3", password="senha-neg3"
        )
        cls.setor = Setor.objects.create(
            nome="Água", nome_es="Agua", nome_en="Water", codigo="agua"
        )
        cls.lote = LoteImportacaoConteudo.objects.create(
            fonte="teste-neg3",
            sha256="0" * 64,
            versao_fonte="neg3",
            executado_por=cls.staff,
        )

    def criar_ferramenta(self, **alteracoes):
        ordem = Ferramenta.objects.count() + 1
        dados = {
            "autor": self.usuario,
            "codigo": f"ferramenta-neg3-{ordem}",
            "titulo": "Ferramenta PT",
            "titulo_es": "Herramienta ES",
            "titulo_en": "Tool EN",
            "descricao": "Descrição PT da ferramenta.",
            "descricao_es": "Descripción ES de la herramienta.",
            "descricao_en": "Tool EN description.",
            "idioma_submissao": Ferramenta.IdiomaSubmissao.PORTUGUES,
            "responsavel": "Responsável NEG-3",
            "periodo": "2025-2026",
            "ano": 2026,
            "pais_ou_instancia": "EFS Brasil",
            "setor": self.setor,
            "url": "https://example.org/neg3",
            "situacao": Ferramenta.Situacao.PUBLICADA,
            "ordem": ordem,
            "lote_origem": self.lote,
        }
        dados.update(alteracoes)
        return Ferramenta.objects.create(**dados)

    def login_staff(self):
        self.client.force_login(self.staff)

    def parse_painel(self, response):
        parser = FerramentaPainelParser()
        parser.feed(response.content.decode("utf-8"))
        return parser

    def snapshot(self, ferramenta):
        return {
            campo.attname: getattr(ferramenta, campo.attname)
            for campo in ferramenta._meta.concrete_fields
        }

    def test_painel_restringe_acesso_a_staff(self):
        ferramenta = self.criar_ferramenta()
        for usuario in (None, self.usuario):
            self.client.logout()
            if usuario:
                self.client.force_login(usuario)
            response = self.client.get(reverse("painel_revisao"))
            self.assertEqual(response.status_code, 302)
            self.assertIn("login", response["Location"])
        self.login_staff()
        self.assertEqual(self.client.get(reverse("painel_revisao")).status_code, 200)
        self.assertTrue(ferramenta.pk)

    def test_painel_exibe_ferramentas_em_pt_es_en_com_cartao_compacto(self):
        ferramenta = self.criar_ferramenta()
        for idioma, rotulo in (("pt-br", "Ferramentas"), ("es", "Herramientas"), ("en", "Tools")):
            with self.subTest(idioma=idioma), translation.override(idioma):
                self.login_staff()
                response = self.client.get(reverse("painel_revisao"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'data-testid="panel-tools"')
                self.assertContains(response, rotulo)
                parser = self.parse_painel(response)
                self.assertEqual(len(parser.cards), 1)
                classes = set().union(*parser.cards[0]["classes"])
                self.assertTrue({"submission-item", "submission-item-main", "submission-item-meta", "submission-item-action"} <= classes)
                self.assertIn("Ferramenta PT" if idioma == "pt-br" else "Herramienta ES" if idioma == "es" else "Tool EN", "".join(parser.cards[0]["text"]))

    def test_painel_status_acoes_staff_e_arquivada_sem_novo_arquivar(self):
        publicada = self.criar_ferramenta(codigo="neg3-publicada")
        arquivada = self.criar_ferramenta(codigo="neg3-arquivada", situacao=Ferramenta.Situacao.ARQUIVADA)
        self.login_staff()
        response = self.client.get(reverse("painel_revisao"))
        self.assertContains(response, "Publicada")
        self.assertContains(response, "Arquivada")
        self.assertContains(response, reverse("editar_ferramenta", args=[publicada.pk]))
        self.assertContains(response, reverse("arquivar_ferramenta", args=[publicada.pk]))
        self.assertContains(response, reverse("editar_ferramenta", args=[arquivada.pk]))
        self.assertContains(response, f"{reverse('arquivar_ferramenta', args=[arquivada.pk])}?next")
        self.assertNotContains(response, "Excluir ferramenta")

    def test_painel_preserva_busca_neg2_e_lista_de_boas_praticas(self):
        self.criar_ferramenta()
        self.login_staff()
        response = self.client.get(reverse("painel_revisao"), {"q": "sem resultado"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("experiencias", response.context)
        self.assertIn("ferramentas_enviadas", response.context)

    def test_edicao_staff_publicada_preserva_situacao_e_dados_imutaveis(self):
        ferramenta = self.criar_ferramenta()
        original = self.snapshot(ferramenta)
        self.login_staff()
        response = self.client.get(reverse("editar_ferramenta", args=[ferramenta.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Salvar alterações")
        self.assertNotContains(response, "Salvar rascunho")
        self.assertNotContains(response, "Enviar para revisão")
        response = self.client.post(
            reverse("editar_ferramenta", args=[ferramenta.pk]),
            {"nome": "Ferramenta PT atualizada", "descricao": "Descrição atualizada", "next": reverse("painel_revisao")},
        )
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)
        self.assertEqual(ferramenta.codigo, original["codigo"])
        self.assertEqual(ferramenta.ordem, original["ordem"])
        self.assertEqual(ferramenta.lote_origem_id, original["lote_origem_id"])
        self.assertEqual(ferramenta.titulo_es, original["titulo_es"])
        self.assertEqual(ferramenta.titulo_en, original["titulo_en"])

    def test_edicao_staff_arquivada_e_outros_estados_preserva_situacao(self):
        self.login_staff()
        for indice, situacao in enumerate(Ferramenta.Situacao.values, start=10):
            with self.subTest(situacao=situacao):
                ferramenta = self.criar_ferramenta(codigo=f"neg3-estado-{indice}", situacao=situacao)
                response = self.client.post(
                    reverse("editar_ferramenta", args=[ferramenta.pk]),
                    {"nome": "Título administrativo", "next": reverse("painel_revisao")},
                )
                self.assertRedirects(response, reverse("painel_revisao"))
                ferramenta.refresh_from_db()
                self.assertEqual(ferramenta.situacao, situacao)

    def test_edicao_staff_preserva_traducoes_nao_editadas_e_campos_ausentes(self):
        ferramenta = self.criar_ferramenta(
            idioma_submissao=Ferramenta.IdiomaSubmissao.INGLES,
            situacao=Ferramenta.Situacao.ARQUIVADA,
        )
        original = self.snapshot(ferramenta)
        self.login_staff()
        self.client.post(reverse("editar_ferramenta", args=[ferramenta.pk]), {"nome": "Updated EN"})
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.titulo_en, "Updated EN")
        self.assertEqual(ferramenta.titulo, original["titulo"])
        self.assertEqual(ferramenta.titulo_es, original["titulo_es"])
        self.assertEqual(ferramenta.url, original["url"])
        self.assertEqual(ferramenta.situacao, original["situacao"])

    def test_usuario_comum_so_edita_rascunho_proprio(self):
        rascunho = self.criar_ferramenta(codigo="neg3-rascunho", situacao=Ferramenta.Situacao.RASCUNHO)
        publicada = self.criar_ferramenta(codigo="neg3-publicada-user", situacao=Ferramenta.Situacao.PUBLICADA)
        alheia = self.criar_ferramenta(codigo="neg3-alheia", autor=self.outro_usuario, situacao=Ferramenta.Situacao.RASCUNHO)
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("editar_ferramenta", args=[rascunho.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("editar_ferramenta", args=[publicada.pk])).status_code, 302)
        self.assertEqual(self.client.get(reverse("editar_ferramenta", args=[alheia.pk])).status_code, 302)
        self.assertFalse(self.client.get(reverse("painel_revisao")).status_code == 200)

    def test_fluxo_de_usuario_comum_de_rascunho_continua_funcional(self):
        rascunho = self.criar_ferramenta(codigo="neg3-fluxo-rascunho", situacao=Ferramenta.Situacao.RASCUNHO)
        self.client.force_login(self.usuario)
        dados = {"nome": "Rascunho salvo", "ano": "2026", "descricao": "Descrição", "setor": str(self.setor.pk), "link_acesso": "https://example.org/rascunho", "pais_ou_instancia": "EFS"}
        response = self.client.post(reverse("editar_ferramenta", args=[rascunho.pk]), {**dados, "acao_envio": "rascunho"})
        self.assertRedirects(response, reverse("meus_envios"))
        rascunho.refresh_from_db()
        self.assertEqual(rascunho.situacao, Ferramenta.Situacao.RASCUNHO)

    def test_get_arquivamento_nao_escreve(self):
        ferramenta = self.criar_ferramenta()
        antes = self.snapshot(ferramenta)
        self.login_staff()
        response = self.client.get(reverse("arquivar_ferramenta", args=[ferramenta.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Arquivar ferramenta")
        ferramenta.refresh_from_db()
        self.assertEqual(self.snapshot(ferramenta), antes)

    def test_post_sem_confirmacao_nao_escreve(self):
        ferramenta = self.criar_ferramenta()
        antes = self.snapshot(ferramenta)
        self.login_staff()
        response = self.client.post(reverse("arquivar_ferramenta", args=[ferramenta.pk]), {})
        self.assertRedirects(response, reverse("arquivar_ferramenta", args=[ferramenta.pk]))
        ferramenta.refresh_from_db()
        self.assertEqual(self.snapshot(ferramenta), antes)

    def test_post_valido_arquiva_sem_excluir_e_preserva_registro(self):
        ferramenta = self.criar_ferramenta()
        antes = self.snapshot(ferramenta)
        total = Ferramenta.objects.count()
        self.login_staff()
        response = self.client.post(reverse("arquivar_ferramenta", args=[ferramenta.pk]), {"confirmar_arquivamento": "sim", "acao_status": "arquivar"})
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        depois = self.snapshot(ferramenta)
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.ARQUIVADA)
        self.assertEqual(Ferramenta.objects.count(), total)
        self.assertEqual({k: v for k, v in depois.items() if k not in {"situacao", "atualizado_em"}}, {k: v for k, v in antes.items() if k not in {"situacao", "atualizado_em"}})

    def test_arquivamento_e_idempotente_e_catalogo_exige_publicada(self):
        ferramenta = self.criar_ferramenta(codigo="neg3-idempotente")
        self.login_staff()
        url = reverse("arquivar_ferramenta", args=[ferramenta.pk])
        self.client.post(url, {"confirmar_arquivamento": "sim", "acao_status": "arquivar"})
        self.client.post(url, {"confirmar_arquivamento": "sim", "acao_status": "arquivar"})
        self.assertEqual(Ferramenta.objects.get(pk=ferramenta.pk).situacao, Ferramenta.Situacao.ARQUIVADA)
        with translation.override("pt-br"):
            self.assertNotContains(self.client.get(reverse("ferramentas")), "neg3-idempotente")

    def test_arquivamento_restringe_usuario_anonimo_nao_staff_e_csrf(self):
        ferramenta = self.criar_ferramenta(codigo="neg3-seguranca")
        url = reverse("arquivar_ferramenta", args=[ferramenta.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.post(url, {"confirmar_arquivamento": "sim"}).status_code, 302)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.staff)
        self.assertEqual(csrf_client.post(url, {"confirmar_arquivamento": "sim"}).status_code, 403)
        self.assertEqual(Ferramenta.objects.get(pk=ferramenta.pk).situacao, Ferramenta.Situacao.PUBLICADA)

    def test_arquivamento_valida_next_interno_e_rejeita_externo(self):
        ferramenta = self.criar_ferramenta(codigo="neg3-next")
        self.login_staff()
        url = reverse("arquivar_ferramenta", args=[ferramenta.pk])
        response = self.client.post(url, {"confirmar_arquivamento": "sim", "acao_status": "arquivar", "next": "https://evil.example/"})
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.situacao = Ferramenta.Situacao.PUBLICADA
        ferramenta.save(update_fields=["situacao"])
        response = self.client.post(url, {"confirmar_arquivamento": "sim", "acao_status": "arquivar", "next": reverse("meus_envios")})
        self.assertRedirects(response, reverse("meus_envios"))

    def test_arquivamento_aceita_somente_get_e_post_e_nao_chama_delete(self):
        ferramenta = self.criar_ferramenta(codigo="neg3-metodo")
        self.login_staff()
        response = self.client.put(reverse("arquivar_ferramenta", args=[ferramenta.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertNotIn(".delete(", inspect.getsource(views.arquivar_ferramenta))

    def test_ferramenta_arquivada_permanece_no_painel_e_nao_no_catalogo(self):
        ferramenta = self.criar_ferramenta(codigo="neg3-painel", situacao=Ferramenta.Situacao.ARQUIVADA)
        self.login_staff()
        self.assertContains(self.client.get(reverse("painel_revisao")), "Ferramenta PT")
        with translation.override("pt-br"):
            self.assertNotContains(self.client.get(reverse("ferramentas")), "Ferramenta PT")
