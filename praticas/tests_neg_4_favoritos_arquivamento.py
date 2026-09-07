import html
import inspect
from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from . import views
from .models import (
    Anexo,
    EFS,
    Experiencia,
    GrupoVulneravel,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TipoExperiencia,
)


class DetailActionsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_actions = False
        self.actions = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and attrs.get("data-testid") == "detail-actions":
            self.in_actions = True
        if not self.in_actions:
            return
        if tag == "form":
            self.current = {"type": "form", "method": attrs.get("method"), "action": attrs.get("action"), "text": ""}
            self.actions.append(self.current)
        elif tag == "a":
            self.current = {"type": "link", "href": attrs.get("href"), "text": ""}
            self.actions.append(self.current)

    def handle_data(self, data):
        if self.in_actions and self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag in {"form", "a"}:
            self.current = None
        elif tag == "div" and self.in_actions:
            self.in_actions = False


class FavoritosArquivamentoNeg4Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("neg4-staff", password="senha-neg4", is_staff=True)
        cls.autor = User.objects.create_user("neg4-autor", password="senha-neg4")
        cls.outro = User.objects.create_user("neg4-outro", password="senha-neg4")
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRNEG4")
        cls.pais_2 = Pais.objects.create(nome="México", nome_es="México", nome_en="Mexico", sigla="MXNEG4")
        cls.efs = EFS.objects.create(
            nome="EFS Brasil NEG-4", nome_es="EFS Brasil NEG-4", nome_en="Brazil SAI NEG-4",
            sigla="EFSNEG4", pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        cls.setor = Setor.objects.create(nome="Água NEG-4", nome_es="Agua NEG-4", nome_en="Water NEG-4")
        cls.grupo = GrupoVulneravel.objects.create(nome="Mulheres NEG-4", nome_es="Mujeres NEG-4", nome_en="Women NEG-4")

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate()

    def criar_experiencia(self, **kwargs):
        dados = {
            "autor": self.autor,
            "titulo": "Boa prática NEG-4",
            "titulo_es": "Buena práctica NEG-4",
            "titulo_en": "Good practice NEG-4",
            "efs": self.efs,
            "pais": self.pais,
            "tipo_experiencia": self.tipo,
            "ano_execucao": 2026,
            "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
            "setor": self.setor,
            "contato_referencia": "Contato NEG-4",
            "email_contato": "neg4@example.org",
            "descricao": "Descrição da boa prática NEG-4.",
            "descricao_es": "Descripción de la buena práctica NEG-4.",
            "descricao_en": "Description of good practice NEG-4.",
            "enfoque_justica_climatica": "Enfoque PT",
            "enfoque_justica_climatica_es": "Enfoque ES",
            "enfoque_justica_climatica_en": "Focus EN",
            "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
            "tipo_auditoria": Experiencia.TipoAuditoria.FINANCEIRA,
        }
        dados.update(kwargs)
        return Experiencia.objects.create(**dados)

    def snapshot(self, experiencia):
        return {
            campo.attname: getattr(experiencia, campo.attname)
            for campo in experiencia._meta.concrete_fields
        }

    def login_staff(self):
        self.client.force_login(self.staff)

    def parse_detail_actions(self, response):
        parser = DetailActionsParser()
        parser.feed(html.unescape(response.content.decode("utf-8")))
        return parser.actions

    def test_ficha_posiciona_favorito_antes_do_arquivamento_a_direita(self):
        experiencia = self.criar_experiencia()
        self.login_staff()
        response = self.client.get(reverse("detalhe_experiencia", args=[experiencia.pk]))
        self.assertEqual(response.status_code, 200)
        actions = self.parse_detail_actions(response)
        self.assertEqual([item["type"] for item in actions], ["form", "link"])
        self.assertEqual(actions[0]["method"].lower(), "post")
        self.assertIn(reverse("alternar_favorito", args=[experiencia.pk]), actions[0]["action"])
        self.assertIn(reverse("arquivar_boa_pratica", args=[experiencia.pk]), actions[1]["href"])
        self.assertContains(response, 'name="next"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "detail-actions")

    def test_favoritos_post_csrf_next_e_tres_idiomas(self):
        experiencia = self.criar_experiencia()
        self.assertEqual(self.client.get(reverse("alternar_favorito", args=[experiencia.pk])).status_code, 405)
        for idioma, incluir, remover in (
            ("pt-br", "Adicionar aos favoritos", "Remover dos favoritos"),
            ("es", "Agregar a favoritos", "Quitar de favoritos"),
            ("en", "Add to favorites", "Remove from favorites"),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                detalhe_url = reverse("detalhe_experiencia", args=[experiencia.pk])
                url = reverse("alternar_favorito", args=[experiencia.pk])
                response = self.client.get(detalhe_url)
                self.assertContains(response, incluir)
                self.client.post(url, {"next": detalhe_url})
                response = self.client.get(detalhe_url)
                self.assertContains(response, remover)
                self.client.post(url, {"next": detalhe_url})

    def test_favorito_rejeita_next_externo_e_arquivada_nao_e_alvo(self):
        experiencia = self.criar_experiencia()
        response = self.client.post(
            reverse("alternar_favorito", args=[experiencia.pk]),
            {"next": "https://evil.example/"},
        )
        self.assertRedirects(response, reverse("catalogo_experiencias"))
        experiencia.status_publicacao = Experiencia.StatusPublicacao.ARQUIVADO
        experiencia.save(update_fields=["status_publicacao"])
        response = self.client.post(reverse("alternar_favorito", args=[experiencia.pk]), {})
        self.assertEqual(response.status_code, 404)

    def test_favorito_anonimo_continua_funcionando_e_lista_ignora_arquivada(self):
        publicada = self.criar_experiencia(titulo="Favorita pública")
        arquivada = self.criar_experiencia(titulo="Favorita arquivada", status_publicacao=Experiencia.StatusPublicacao.ARQUIVADO)
        url = reverse("alternar_favorito", args=[publicada.pk])
        self.client.post(url, {"next": reverse("favoritos_experiencias")})
        self.client.post(reverse("alternar_favorito", args=[arquivada.pk]), {})
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favorita pública")
        self.assertNotContains(response, "Favorita arquivada")

    def test_arquivamento_canonico_e_legado_sao_get_post_csrf_e_idempotentes(self):
        for nome_rota in ("arquivar_boa_pratica", "excluir_boa_pratica"):
            with self.subTest(nome_rota=nome_rota):
                experiencia = self.criar_experiencia(titulo=f"{nome_rota} alvo")
                url = reverse(nome_rota, args=[experiencia.pk])
                self.login_staff()
                antes = self.snapshot(experiencia)
                self.assertEqual(self.client.get(url).status_code, 200)
                experiencia.refresh_from_db()
                self.assertEqual(self.snapshot(experiencia), antes)
                self.assertRedirects(self.client.post(url, {}), reverse("arquivar_boa_pratica", args=[experiencia.pk]))
                self.client.post(url, {"confirmar_arquivamento": "sim"})
                experiencia.refresh_from_db()
                self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ARQUIVADO)
                pk = experiencia.pk
                self.client.post(url, {"confirmar_arquivamento": "sim"})
                self.assertTrue(Experiencia.objects.filter(pk=pk).exists())

    def test_arquivamento_autorizacao_autor_staff_anonimo_e_nao_autor(self):
        propria = self.criar_experiencia(titulo="Própria")
        alheia = self.criar_experiencia(titulo="Alheia", autor=self.outro)
        url = reverse("arquivar_boa_pratica", args=[propria.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.outro)
        self.assertRedirects(self.client.get(url), reverse("meus_envios"))
        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertRedirects(self.client.get(reverse("arquivar_boa_pratica", args=[alheia.pk])), reverse("meus_envios"))
        self.login_staff()
        self.assertEqual(self.client.get(reverse("arquivar_boa_pratica", args=[alheia.pk])).status_code, 200)

    def test_arquivamento_valida_confirmacao_metodos_e_next(self):
        experiencia = self.criar_experiencia()
        self.login_staff()
        url = reverse("arquivar_boa_pratica", args=[experiencia.pk])
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.patch(url).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertRedirects(self.client.post(url, {"confirmar_arquivamento": "sim", "next": "//evil.example/"}), reverse("painel_revisao"))
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ARQUIVADO)

    def test_arquivamento_csrf_e_inexistente(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.staff)
        experiencia = self.criar_experiencia()
        url = reverse("arquivar_boa_pratica", args=[experiencia.pk])
        self.assertEqual(csrf_client.post(url, {"confirmar_arquivamento": "sim"}).status_code, 403)
        self.assertEqual(self.client.get(reverse("arquivar_boa_pratica", args=[999999])).status_code, 302)
        self.login_staff()
        self.assertEqual(self.client.get(reverse("arquivar_boa_pratica", args=[999999])).status_code, 404)

    def test_arquivamento_preserva_snapshot_anexo_m2m_proposta_e_arquivo(self):
        experiencia = self.criar_experiencia()
        experiencia.efs_participantes.add(self.efs)
        experiencia.paises_participantes.add(self.pais_2)
        experiencia.grupos_vulneraveis.add(self.grupo)
        anexo = Anexo.objects.create(
            experiencia=experiencia,
            titulo="Evidência",
            arquivo=SimpleUploadedFile("evidencia-neg4.pdf", b"%PDF-1.4 evidencia"),
        )
        proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=experiencia, email_contato="proposta@example.org", dados_json={"titulo": "proposto"}
        )
        antes = self.snapshot(experiencia)
        m2m_antes = {
            "efs": set(experiencia.efs_participantes.values_list("pk", flat=True)),
            "paises": set(experiencia.paises_participantes.values_list("pk", flat=True)),
            "grupos": set(experiencia.grupos_vulneraveis.values_list("pk", flat=True)),
        }
        self.login_staff()
        self.client.post(reverse("arquivar_boa_pratica", args=[experiencia.pk]), {"confirmar_arquivamento": "sim"})
        experiencia.refresh_from_db()
        self.assertEqual(Experiencia.objects.count(), 1)
        self.assertEqual({k: v for k, v in self.snapshot(experiencia).items() if k not in {"status_publicacao", "atualizado_em"}}, {k: v for k, v in antes.items() if k not in {"status_publicacao", "atualizado_em"}})
        self.assertEqual(set(experiencia.efs_participantes.values_list("pk", flat=True)), m2m_antes["efs"])
        self.assertEqual(set(experiencia.paises_participantes.values_list("pk", flat=True)), m2m_antes["paises"])
        self.assertEqual(set(experiencia.grupos_vulneraveis.values_list("pk", flat=True)), m2m_antes["grupos"])
        self.assertTrue(Anexo.objects.filter(pk=anexo.pk, experiencia=experiencia).exists())
        self.assertEqual(PropostaEdicaoExperiencia.objects.get(pk=proposta.pk).experiencia_id, experiencia.pk)
        self.assertTrue(Anexo.objects.get(pk=anexo.pk).arquivo.name.startswith("anexos/evidencia-neg4"))
        self.assertTrue(Anexo.objects.get(pk=anexo.pk).arquivo.name.endswith(".pdf"))

    def test_arquivamento_remove_catalogo_detalhe_home_comparacao_e_favoritos(self):
        experiencia = self.criar_experiencia(titulo="Sai das consultas")
        self.client.post(reverse("alternar_favorito", args=[experiencia.pk]), {})
        self.login_staff()
        self.client.post(reverse("arquivar_boa_pratica", args=[experiencia.pk]), {"confirmar_arquivamento": "sim"})
        self.assertNotContains(self.client.get(reverse("catalogo_experiencias")), "Sai das consultas")
        self.assertNotContains(self.client.get(reverse("pagina_inicial")), "Sai das consultas")
        self.assertNotContains(self.client.get(reverse("comparar_experiencias"), {"experiencias": [experiencia.pk]}), "Sai das consultas")
        self.assertNotContains(self.client.get(reverse("favoritos_experiencias")), "Sai das consultas")
        self.assertEqual(self.client.get(reverse("detalhe_experiencia", args=[experiencia.pk])).status_code, 404)
        self.assertContains(self.client.get(reverse("painel_revisao")), "Sai das consultas")

    def test_arquivada_permanece_em_meus_envios_e_nao_exibe_acao_arquivar(self):
        experiencia = self.criar_experiencia(titulo="Permanece interna", status_publicacao=Experiencia.StatusPublicacao.ARQUIVADO)
        self.client.force_login(self.autor)
        response = self.client.get(reverse("meus_envios"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Permanece interna")
        self.assertNotContains(response, reverse("arquivar_boa_pratica", args=[experiencia.pk]))

    def test_interface_nao_exibe_textos_de_exclusao_nas_acoes_ativas(self):
        experiencia = self.criar_experiencia()
        self.login_staff()
        urls = [
            reverse("catalogo_experiencias"),
            reverse("painel_revisao"),
            reverse("detalhe_experiencia", args=[experiencia.pk]),
            reverse("revisar_experiencia", args=[experiencia.pk]),
            reverse("arquivar_boa_pratica", args=[experiencia.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                conteudo = html.unescape(self.client.get(url).content.decode("utf-8"))
                self.assertNotIn("Delete good practice", conteudo)
                self.assertNotIn("Eliminar buena práctica", conteudo)
                self.assertNotIn("Excluir boa prática", conteudo)

    def test_fluxo_ativo_nao_possui_delete_na_view_canonica(self):
        fonte = inspect.getsource(views.arquivar_boa_pratica)
        self.assertNotIn("experiencia.delete(", fonte)
        self.assertNotIn("anexo.delete(", fonte)
        self.assertNotIn("anexo.arquivo.delete", fonte)
