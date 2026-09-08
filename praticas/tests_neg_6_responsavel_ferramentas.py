from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import override

from .forms import FerramentaSubmissaoForm
from .models import Experiencia, Ferramenta, Setor


class Neg6ResponsavelFerramentasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="neg6-autora",
            email="neg6@example.org",
            password="SenhaForte123!",
        )
        cls.setor = Setor.objects.create(
            codigo="neg6-setor",
            nome="Infraestrutura",
            nome_es="Infraestructura",
            nome_en="Infrastructure",
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def _formulario_html(self, caminho="/adicionar-boa-pratica/?tipo=ferramenta"):
        resposta = self.client.get(caminho)
        self.assertEqual(resposta.status_code, 200)
        html = resposta.content.decode("utf-8")
        return html.split('<form method="post" class="submission-form">', 1)[1].split(
            "</form>", 1
        )[0]

    def test_formulario_preserva_campos_tecnicos_e_nao_cria_responsavel(self):
        form = FerramentaSubmissaoForm()

        self.assertEqual(
            list(form.fields),
            ["nome", "ano", "descricao", "setor", "link_acesso", "pais_ou_instancia"],
        )
        self.assertIn("pais_ou_instancia", form.fields)
        self.assertNotIn("responsavel", form.fields)

    def test_rotulos_e_help_text_sao_trilingues_no_formulario(self):
        casos = (
            (
                "pt-br",
                "Responsável",
                "Atores responsáveis pelo desenvolvimento da ferramenta. Ex: TCU-Brasil, CGR-Paraguay, COMTEMA - OLACEFS, IDI, GIZ.",
                "País ou Instância",
            ),
            (
                "es",
                "Responsable",
                "Actores responsables del desarrollo de la herramienta. Ej.: TCU-Brasil, CGR-Paraguay, COMTEMA - OLACEFS, IDI, GIZ.",
                "País o Instancia",
            ),
            (
                "en",
                "Responsible party",
                "Actors responsible for developing the tool. E.g.: TCU-Brasil, CGR-Paraguay, COMTEMA - OLACEFS, IDI, GIZ.",
                "Country or Body",
            ),
        )

        for idioma, rotulo, ajuda, antigo in casos:
            with self.subTest(idioma=idioma):
                with override(idioma):
                    form = FerramentaSubmissaoForm()
                    self.assertEqual(form.fields["pais_ou_instancia"].label, rotulo)
                    self.assertEqual(form.fields["pais_ou_instancia"].help_text, ajuda)

                html = self._formulario_html(
                    "/es/adicionar-boa-pratica/?tipo=ferramenta"
                    if idioma == "es"
                    else "/en/adicionar-boa-pratica/?tipo=ferramenta"
                    if idioma == "en"
                    else "/adicionar-boa-pratica/?tipo=ferramenta"
                )
                self.assertIn(rotulo, html)
                self.assertIn(ajuda, html)
                self.assertNotIn(antigo, html)
                self.assertIn('name="pais_ou_instancia"', html)
                self.assertIn('id="id_pais_ou_instancia"', html)
                self.assertIn(f'aria-label="{ajuda}"', html)
                self.assertIn(f'title="{ajuda}"', html)

    def test_post_cria_ferramenta_preserva_responsavel_idioma_e_nao_cria_experiencia(self):
        casos = (
            ("/adicionar-boa-pratica/", "pt", "Responsável PT"),
            ("/es/adicionar-boa-pratica/", "es", "Responsable ES"),
            ("/en/adicionar-boa-pratica/", "en", "Responsible party EN"),
        )
        experiencias_antes = Experiencia.objects.count()

        for indice, (caminho, idioma, valor) in enumerate(casos):
            with self.subTest(idioma=idioma):
                resposta = self.client.post(
                    caminho,
                    {
                        "tipo_compartilhamento": "ferramenta",
                        "acao_envio": "enviar",
                        "nome": f"Ferramenta NEG6 {idioma}",
                        "ano": "2026",
                        "descricao": "Descrição da ferramenta.",
                        "setor": str(self.setor.pk),
                        "link_acesso": f"https://example.org/neg6-{indice}",
                        "pais_ou_instancia": valor,
                    },
                )
                self.assertEqual(resposta.status_code, 302)
                ferramenta = Ferramenta.objects.get(url=f"https://example.org/neg6-{indice}")
                self.assertEqual(ferramenta.pais_ou_instancia, valor)
                self.assertEqual(ferramenta.responsavel, valor)
                self.assertEqual(ferramenta.idioma_submissao, idioma)
                self.assertNotEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

        self.assertEqual(Experiencia.objects.count(), experiencias_antes)

    def test_get_do_formulario_nao_grava_dados(self):
        antes = (Ferramenta.objects.count(), Experiencia.objects.count())

        for caminho in (
            "/adicionar-boa-pratica/?tipo=ferramenta",
            "/es/adicionar-boa-pratica/?tipo=ferramenta",
            "/en/adicionar-boa-pratica/?tipo=ferramenta",
        ):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 200)

        self.assertEqual((Ferramenta.objects.count(), Experiencia.objects.count()), antes)

    def test_edicao_usa_novo_rotulo_e_sincroniza_os_dois_campos(self):
        ferramenta = Ferramenta.objects.create(
            autor=self.usuario,
            codigo="neg6-edicao",
            titulo="Ferramenta editável",
            descricao="Descrição original",
            idioma_submissao=Ferramenta.IdiomaSubmissao.PORTUGUES,
            pais_ou_instancia="Valor antigo",
            responsavel="Valor antigo",
            ano=2025,
            setor=self.setor,
            url="https://example.org/neg6-edicao",
            situacao=Ferramenta.Situacao.RASCUNHO,
            ordem=1,
        )

        resposta = self.client.get(reverse("editar_ferramenta", args=[ferramenta.pk]))
        self.assertEqual(resposta.status_code, 200)
        html = resposta.content.decode("utf-8")
        formulario = html.split('<form method="post" class="submission-form">', 1)[1].split(
            "</form>", 1
        )[0]
        self.assertIn("Responsável", formulario)
        self.assertIn('name="pais_ou_instancia"', formulario)
        self.assertNotIn("País ou Instância", formulario)

        resposta = self.client.post(
            reverse("editar_ferramenta", args=[ferramenta.pk]),
            {
                "acao_envio": "rascunho",
                "nome": "Ferramenta editada",
                "ano": "2026",
                "descricao": "Descrição atualizada",
                "setor": str(self.setor.pk),
                "link_acesso": "https://example.org/neg6-edicao-atualizada",
                "pais_ou_instancia": "Novo responsável",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.pais_ou_instancia, "Novo responsável")
        self.assertEqual(ferramenta.responsavel, "Novo responsável")

    def test_rascunho_parcial_continua_permitido(self):
        resposta = self.client.post(
            reverse("adicionar_boa_pratica"),
            {
                "tipo_compartilhamento": "ferramenta",
                "acao_envio": "rascunho",
                "nome": "Ferramenta parcial NEG6",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        ferramenta = Ferramenta.objects.filter(autor=self.usuario).order_by("-pk").first()
        self.assertIsNotNone(ferramenta)
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.RASCUNHO)
        self.assertEqual(ferramenta.pais_ou_instancia, "")
        self.assertEqual(ferramenta.responsavel, "")

    def test_post_continua_exigindo_autenticacao_e_csrf(self):
        anonimo = Client()
        resposta = anonimo.post(
            reverse("adicionar_boa_pratica"),
            {"tipo_compartilhamento": "ferramenta", "pais_ou_instancia": "OLACEFS"},
        )
        self.assertEqual(resposta.status_code, 302)

        protegido = Client(enforce_csrf_checks=True)
        protegido.force_login(self.usuario)
        resposta = protegido.post(
            reverse("adicionar_boa_pratica"),
            {
                "tipo_compartilhamento": "ferramenta",
                "acao_envio": "enviar",
                "nome": "Sem CSRF",
                "ano": "2026",
                "descricao": "Descrição",
                "setor": str(self.setor.pk),
                "link_acesso": "https://example.org/sem-csrf",
                "pais_ou_instancia": "OLACEFS",
            },
        )
        self.assertEqual(resposta.status_code, 403)
