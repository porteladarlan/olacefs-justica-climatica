import html

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import (
    EFS,
    Experiencia,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TipoExperiencia,
)
from .views import montar_comparativo_proposta_edicao


class ExclusaoAdminBoaPraticaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.admin = cls.User.objects.create_user(
            username="admin_fase16i",
            email="admin16i@example.org",
            password="SenhaForte123!",
            is_staff=True,
        )
        cls.usuario = cls.User.objects.create_user(
            username="usuario_fase16i",
            email="usuario16i@example.org",
            password="SenhaForte123!",
            is_staff=False,
        )
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BR16I")
        cls.efs = EFS.objects.create(
            nome="Tribunal de Contas da União do Brasil",
            nome_es="Tribunal de Cuentas de la Unión de Brasil",
            nome_en="Federal Court of Accounts of Brazil",
            sigla="TCU16I",
            pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        cls.setor = Setor.objects.create(nome="Outro", nome_es="Otro", nome_en="Other")

    def criar_experiencia(self, status=None):
        kwargs = {
            "titulo": "Boa prática para exclusão",
            "titulo_es": "Buena práctica para eliminación",
            "titulo_en": "Good practice for deletion",
            "efs": self.efs,
            "pais": self.pais,
            "tipo_experiencia": self.tipo,
            "ano_execucao": 2026,
            "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
            "setor": self.setor,
            "contato_referencia": "Contato de teste",
            "email_contato": "autor16i@example.org",
            "descricao": "Registro criado para validar exclusão administrativa.",
            "descricao_es": "Registro creado para validar eliminación administrativa.",
            "descricao_en": "Record created to validate administrative deletion.",
            "enfoque_justica_climatica": "Teste.",
            "enfoque_justica_climatica_es": "Prueba.",
            "enfoque_justica_climatica_en": "Test.",
            "status_publicacao": status or Experiencia.StatusPublicacao.PUBLICADO,
        }
        if any(field.name == "informacoes_adicionais" for field in Experiencia._meta.fields):
            kwargs["informacoes_adicionais"] = ""
        return Experiencia.objects.create(**kwargs)

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate()

    def test_usuario_comum_nao_acessa_exclusao(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="usuario_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("excluir_boa_pratica", args=[experiencia.pk]))
        self.assertIn(resposta.status_code, [302, 403])
        self.assertTrue(Experiencia.objects.filter(pk=experiencia.pk).exists())

        resposta = self.client.post(
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
            {"confirmar_exclusao": "sim"},
        )
        self.assertIn(resposta.status_code, [302, 403])
        self.assertTrue(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_staff_acessa_tela_de_confirmacao(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("excluir_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Boa prática para exclusão")
        self.assertContains(resposta, "confirmar_exclusao")
        self.assertContains(resposta, "csrfmiddlewaretoken")
        self.assertTrue(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_metodos_diferentes_de_get_e_post_sao_rejeitados(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        resposta = self.client.delete(
            reverse("excluir_boa_pratica", args=[experiencia.pk])
        )

        self.assertEqual(resposta.status_code, 405)
        self.assertTrue(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_cancelamento_descarta_next_com_esquema_inseguro(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        resposta = self.client.get(
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
            {"next": "javascript:alert(document.domain)"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "javascript:")
        self.assertContains(resposta, reverse("catalogo_experiencias"))

    def test_staff_exclui_boa_pratica_por_post_confirmado(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.post(
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
            {"confirmar_exclusao": "sim"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_catalogo_exibe_acao_de_exclusao_para_staff(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("catalogo_experiencias"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, reverse("excluir_boa_pratica", args=[experiencia.pk]))
        self.assertIn(
            "Excluir boa prática",
            html.unescape(resposta.content.decode("utf-8")),
        )

    def test_catalogo_nao_exibe_acao_de_exclusao_para_usuario_comum(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="usuario_fase16i", password="SenhaForte123!")

        resposta = self.client.get(reverse("catalogo_experiencias"))

        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(
            resposta,
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
        )

    def test_painel_de_revisao_exibe_acao_de_exclusao(self):
        experiencia = self.criar_experiencia(
            status=Experiencia.StatusPublicacao.ENVIADO
        )
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        resposta = self.client.get(reverse("painel_revisao"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
        )

    def test_mensagens_editoriais_acompanham_idioma_ativo(self):
        mensagens = {
            "pt-br": {
                "aprovar": "Experiência aprovada e publicada no catálogo público.",
                "devolver": "Experiência devolvida para ajustes.",
                "rejeitar": "Experiência rejeitada.",
            },
            "es": {
                "aprovar": "Experiencia aprobada y publicada en el catálogo público.",
                "devolver": "Experiencia devuelta para ajustes.",
                "rejeitar": "Experiencia rechazada.",
            },
            "en": {
                "aprovar": "Experience approved and published in the public catalog.",
                "devolver": "Experience returned for adjustments.",
                "rejeitar": "Experience rejected.",
            },
        }
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        for idioma, mensagens_por_acao in mensagens.items():
            for acao, mensagem in mensagens_por_acao.items():
                with self.subTest(idioma=idioma, acao=acao):
                    experiencia = self.criar_experiencia(
                        status=Experiencia.StatusPublicacao.ENVIADO
                    )
                    with translation.override(idioma):
                        url = reverse(
                            "revisar_experiencia", args=[experiencia.pk]
                        )
                    resposta = self.client.post(
                        url,
                        {"acao": acao, "comentario_revisor": "Homologação"},
                        follow=True,
                    )
                    self.assertEqual(resposta.status_code, 200)
                    self.assertContains(resposta, mensagem)

    def test_mensagem_de_exclusao_acompanha_idioma_ativo(self):
        mensagens = {
            "pt-br": "Boa prática excluída com sucesso:",
            "es": "Buena práctica eliminada correctamente:",
            "en": "Good practice deleted successfully:",
        }
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        for idioma, mensagem in mensagens.items():
            with self.subTest(idioma=idioma):
                experiencia = self.criar_experiencia()
                with translation.override(idioma):
                    url = reverse(
                        "excluir_boa_pratica", args=[experiencia.pk]
                    )
                resposta = self.client.post(
                    url,
                    {"confirmar_exclusao": "sim"},
                    follow=True,
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, mensagem)
                self.assertFalse(
                    Experiencia.objects.filter(pk=experiencia.pk).exists()
                )

    def test_label_e_ajuda_fontes_de_informacao_acompanham_idioma(self):
        textos = {
            "pt-br": (
                "Fontes de informação ou evidências",
                "Informe as principais fontes de informação ou evidências utilizadas na boa prática.",
            ),
            "es": (
                "Fuentes de Información o evidencia",
                "Informe las principales fuentes de información o evidencias utilizadas en la buena práctica.",
            ),
            "en": (
                "Sources of information or evidence",
                "Provide the main sources of information or evidence used in the good practice.",
            ),
        }
        self.client.login(username="usuario_fase16i", password="SenhaForte123!")

        for idioma, (label, ajuda) in textos.items():
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    url = reverse("adicionar_boa_pratica")
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, label)
                self.assertContains(resposta, ajuda)
                if idioma == "es":
                    self.assertNotContains(resposta, "buena prática")

    def test_comparacao_de_edicao_traduz_label_e_booleano(self):
        experiencia = self.criar_experiencia()
        experiencia.contribui_para_guia = True
        experiencia.save(update_fields=["contribui_para_guia"])
        proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=experiencia,
            email_contato=experiencia.email_contato,
            dados_json={
                "ferramentas_utilizadas": "Evidência atualizada.",
                "contribui_para_guia": False,
            },
        )
        esperados = {
            "pt-br": ("Fontes de informação ou evidências", "Sim", "Não"),
            "es": ("Fuentes de Información o evidencia", "Sí", "No"),
            "en": ("Sources of information or evidence", "Yes", "No"),
        }
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        for idioma, (rotulo, valor_sim, valor_nao) in esperados.items():
            with self.subTest(idioma=idioma):
                with translation.override(idioma):
                    comparativo = montar_comparativo_proposta_edicao(proposta)
                    url = reverse(
                        "revisar_edicao_publicada", args=[proposta.pk]
                    )
                linhas = {linha["campo"]: linha for linha in comparativo}
                self.assertEqual(
                    linhas["ferramentas_utilizadas"]["rotulo"], rotulo
                )
                self.assertEqual(
                    linhas["contribui_para_guia"]["valor_atual"], valor_sim
                )
                self.assertEqual(
                    linhas["contribui_para_guia"]["valor_proposto"], valor_nao
                )

                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, rotulo)

    def test_botoes_administrativos_usam_practica_em_espanhol(self):
        publicada = self.criar_experiencia()
        enviada = self.criar_experiencia(
            status=Experiencia.StatusPublicacao.ENVIADO
        )
        self.client.login(username="admin_fase16i", password="SenhaForte123!")

        with translation.override("es"):
            urls = [
                reverse("catalogo_experiencias"),
                reverse("painel_revisao"),
                reverse("revisar_experiencia", args=[enviada.pk]),
                reverse("detalhe_experiencia", args=[publicada.pk]),
            ]

        conteudos = []
        for url in urls:
            resposta = self.client.get(url)
            self.assertEqual(resposta.status_code, 200)
            conteudos.append(html.unescape(resposta.content.decode("utf-8")))

        self.assertIn("Eliminar buena práctica", conteudos[0])
        self.assertIn("Editar buena práctica", conteudos[1])
        self.assertIn("Eliminar buena práctica", conteudos[1])
        self.assertIn("Editar buena práctica", conteudos[2])
        self.assertIn("Eliminar buena práctica", conteudos[2])
        self.assertIn("Eliminar buena práctica", conteudos[3])
        for conteudo in conteudos:
            self.assertNotIn("buena prática", conteudo)
