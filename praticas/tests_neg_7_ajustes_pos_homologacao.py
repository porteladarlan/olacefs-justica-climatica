from html import unescape
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from .models import EFS, Experiencia, Ferramenta, NormaInternacional, NormaInternacionalPais, Pais, Setor, TipoExperiencia
from .views import _ids_comparacao_seguros


class Neg7AjustesPosHomologacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("neg7-staff", password="senha", is_staff=True)
        cls.autor = User.objects.create_user("neg7-autor", password="senha")
        cls.outro = User.objects.create_user("neg7-outro", password="senha")
        cls.pais = Pais.objects.create(nome="Brasil NEG7", nome_es="Brasil NEG7", nome_en="Brazil NEG7", sigla="BRA")
        cls.efs = EFS.objects.create(nome="EFS NEG7", nome_es="EFS NEG7 ES", nome_en="NEG7 SAI", sigla="EFS7", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria NEG7", nome_es="Auditoría NEG7", nome_en="NEG7 Audit")
        cls.setor = Setor.objects.create(nome="Água", nome_es="Agua", nome_en="Water", codigo="neg7-agua")

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.activate("pt-br")

    def ferramenta(self, situacao=Ferramenta.Situacao.PUBLICADA, autor=None, **alteracoes):
        dados = {
            "autor": autor or self.autor,
            "codigo": f"neg7-{Ferramenta.objects.count()}",
            "titulo": "Título PT",
            "titulo_es": "Título ES",
            "titulo_en": "Title EN",
            "descricao": "Descrição PT",
            "descricao_es": "Descripción ES",
            "descricao_en": "Description EN",
            "idioma_submissao": Ferramenta.IdiomaSubmissao.PORTUGUES,
            "responsavel": "Responsável",
            "pais_ou_instancia": "EFS",
            "setor": self.setor,
            "url": "https://example.org/neg7",
            "ano": 2026,
            "periodo": "2026",
            "ordem": Ferramenta.objects.count() + 1,
            "situacao": situacao,
        }
        dados.update(alteracoes)
        ferramenta = Ferramenta.objects.create(**dados)
        return ferramenta

    def experiencia(self, status, autor=None, titulo="Boa prática NEG7"):
        return Experiencia.objects.create(
            autor=autor or self.autor,
            titulo=titulo,
            titulo_es=f"{titulo} ES",
            titulo_en=f"{titulo} EN",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=self.setor,
            contato_referencia="Contato NEG7",
            email_contato="neg7@example.org",
            descricao="Descrição NEG7",
            descricao_es="Descripción NEG7",
            descricao_en="Description NEG7",
            enfoque_justica_climatica="Enfoque PT",
            enfoque_justica_climatica_es="Enfoque ES",
            enfoque_justica_climatica_en="Focus EN",
            status_publicacao=status,
        )

    def test_staff_recupera_ferramenta_arquivada_e_catalogo_a_omite(self):
        ferramenta = self.ferramenta(Ferramenta.Situacao.ARQUIVADA)
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("arquivar_ferramenta", args=[ferramenta.pk]),
            {"confirmar_arquivamento": "sim", "acao_status": "recuperar"},
        )
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_recuperacao_incompleta_mantem_ferramenta_arquivada(self):
        ferramenta = self.ferramenta(Ferramenta.Situacao.ARQUIVADA)
        Ferramenta.objects.filter(pk=ferramenta.pk).update(titulo="", descricao="", ano=None, setor=None, url="")
        self.client.force_login(self.staff)
        for idioma, aviso in (
            ("pt-br", "Preencha todos os campos obrigatórios"),
            ("es", "Complete todos los campos obligatorios"),
            ("en", "Complete all required fields"),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                pagina = self.client.get(reverse("arquivar_ferramenta", args=[ferramenta.pk]))
                self.assertEqual(pagina.status_code, 200)
                html = pagina.content.decode("utf-8")
                self.assertIn('name="acao_status" value="recuperar"', html)
                self.assertIn(aviso, html)
                self.assertIn('name="confirmar_arquivamento" value="sim" disabled', html)
        response = self.client.post(
            reverse("arquivar_ferramenta", args=[ferramenta.pk]),
            {"confirmar_arquivamento": "sim", "acao_status": "recuperar"},
        )
        self.assertEqual(response.status_code, 400)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.ARQUIVADA)

    def test_acao_de_status_desconhecida_nao_altera_ferramenta(self):
        ferramenta = self.ferramenta(Ferramenta.Situacao.PUBLICADA)
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("arquivar_ferramenta", args=[ferramenta.pk]),
            {"confirmar_arquivamento": "sim", "acao_status": "desconhecida"},
        )
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_ferramenta_publicada_sem_acao_nao_e_arquivada(self):
        ferramenta = self.ferramenta(Ferramenta.Situacao.PUBLICADA)
        atualizado_em = ferramenta.atualizado_em
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("arquivar_ferramenta", args=[ferramenta.pk]),
            {"confirmar_arquivamento": "sim"},
        )
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)
        self.assertEqual(ferramenta.atualizado_em, atualizado_em)

    def test_acao_de_status_incompativel_nao_grava(self):
        casos = (
            (Ferramenta.Situacao.PUBLICADA, "recuperar"),
            (Ferramenta.Situacao.ARQUIVADA, "arquivar"),
        )
        self.client.force_login(self.staff)
        for situacao, acao in casos:
            with self.subTest(situacao=situacao, acao=acao):
                ferramenta = self.ferramenta(situacao)
                atualizado_em = ferramenta.atualizado_em
                response = self.client.post(
                    reverse("arquivar_ferramenta", args=[ferramenta.pk]),
                    {"confirmar_arquivamento": "sim", "acao_status": acao},
                )
                self.assertRedirects(response, reverse("painel_revisao"))
                ferramenta.refresh_from_db()
                self.assertEqual(ferramenta.situacao, situacao)
                self.assertEqual(ferramenta.atualizado_em, atualizado_em)

    def test_meus_envios_so_exibe_acoes_de_arquivamento_validas(self):
        experiencias = {
            status: self.experiencia(status, titulo=f"Envio {status}", autor=self.autor)
            for status in (
                Experiencia.StatusPublicacao.RASCUNHO,
                Experiencia.StatusPublicacao.ENVIADO,
                Experiencia.StatusPublicacao.EM_REVISAO,
                Experiencia.StatusPublicacao.APROVADO,
                Experiencia.StatusPublicacao.REJEITADO,
                Experiencia.StatusPublicacao.PUBLICADO,
                Experiencia.StatusPublicacao.ARQUIVADO,
            )
        }
        self.client.force_login(self.autor)
        for idioma, arquivar, recuperar in (
            ("pt-br", "Arquivar", "Recuperar"),
            ("es", "Archivar", "Restaurar"),
            ("en", "Archive", "Restore"),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                response = self.client.get(reverse("meus_envios"))
                html = response.content.decode("utf-8")
                self.assertEqual(html.count(f">{arquivar}<"), 1)
                self.assertEqual(html.count(f">{recuperar}<"), 1)

    def test_confirmacao_de_arquivamento_localiza_status_nos_tres_idiomas(self):
        self.client.force_login(self.staff)
        for status, labels in (
            (Experiencia.StatusPublicacao.PUBLICADO, {"pt-br": "Publicado", "es": "Publicado", "en": "Published"}),
            (Experiencia.StatusPublicacao.ARQUIVADO, {"pt-br": "Arquivado", "es": "Archivado", "en": "Archived"}),
        ):
            experiencia = self.experiencia(status, titulo=f"Status confirmação {status}")
            for idioma, esperado in labels.items():
                with self.subTest(status=status, idioma=idioma), translation.override(idioma):
                    response = self.client.get(reverse("arquivar_boa_pratica", args=[experiencia.pk]))
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(esperado, response.content.decode("utf-8"))
            experiencia.delete()

    def test_get_de_status_nao_grava(self):
        ferramenta = self.ferramenta()
        antes = ferramenta.situacao
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("arquivar_ferramenta", args=[ferramenta.pk])).status_code, 200)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, antes)

    def test_usuario_comum_nao_edita_publicada_propria(self):
        ferramenta = self.ferramenta(autor=self.autor)
        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(reverse("editar_ferramenta", args=[ferramenta.pk])).status_code, 302)

    def test_post_de_usuario_comum_nao_edita_publicada(self):
        ferramenta = self.ferramenta(autor=self.autor)
        original = (ferramenta.titulo, ferramenta.atualizado_em)
        self.client.force_login(self.autor)
        response = self.client.post(
            reverse("editar_ferramenta", args=[ferramenta.pk]),
            {"nome": "Tentativa indevida", "acao_envio": "enviar"},
        )
        self.assertRedirects(response, reverse("meus_envios"), fetch_redirect_response=False)
        ferramenta.refresh_from_db()
        self.assertEqual((ferramenta.titulo, ferramenta.atualizado_em), original)

    def test_usuario_comum_nao_edita_ferramenta_alheia(self):
        ferramenta = self.ferramenta(autor=self.outro)
        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(reverse("editar_ferramenta", args=[ferramenta.pk])).status_code, 302)

    def test_painel_agrega_publicadas_e_arquivadas(self):
        self.ferramenta(Ferramenta.Situacao.PUBLICADA)
        self.ferramenta(Ferramenta.Situacao.ARQUIVADA)
        self.client.force_login(self.staff)
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gerenciamento de submissões")
        self.assertContains(response, 'data-testid="panel-open-search"')

    def test_status_do_painel_de_boas_praticas_e_localizado_sem_mistura(self):
        for status in (
            Experiencia.StatusPublicacao.RASCUNHO,
            Experiencia.StatusPublicacao.ENVIADO,
            Experiencia.StatusPublicacao.EM_REVISAO,
            Experiencia.StatusPublicacao.APROVADO,
            Experiencia.StatusPublicacao.PUBLICADO,
            Experiencia.StatusPublicacao.ARQUIVADO,
            Experiencia.StatusPublicacao.REJEITADO,
        ):
            self.experiencia(status, titulo=f"Status {status}")
        self.client.force_login(self.staff)
        rotulos = {
            "pt-br": ("Rascunho", "Enviado", "Em revisão", "Aprovado", "Publicado", "Arquivado", "Rejeitado"),
            "es": ("Borrador", "Enviado", "En revisión", "Aprobado", "Publicado", "Archivado", "Rechazado"),
            "en": ("Draft", "Submitted", "Under review", "Approved", "Published", "Archived", "Rejected"),
        }
        for idioma, esperados in rotulos.items():
            with self.subTest(idioma=idioma), translation.override(idioma):
                response = self.client.get(reverse("painel_revisao"))
                conteudo = unescape(response.content.decode("utf-8"))
                painel = conteudo.split('data-testid="panel-good-practices"', 1)[1].split("</section>", 1)[0]
                for rotulo in esperados:
                    self.assertIn(rotulo, painel)
                proibidos = set({"Rascunho", "Em revisão", "Aprovado", "Publicado", "Arquivado", "Rejeitado"}) - set(esperados)
                for rotulo in proibidos:
                    self.assertNotIn(rotulo, painel)

    def test_busca_de_ferramenta_cobre_codigo_responsavel_e_autoria(self):
        ferramenta = self.ferramenta()
        ferramenta.codigo = "codigo-neg7-especial"
        ferramenta.responsavel = "Pessoa Neg7"
        ferramenta.save(update_fields=["codigo", "responsavel"])
        self.client.force_login(self.staff)
        for termo in ("codigo-neg7", "Pessoa Neg7", "neg7-autor"):
            response = self.client.get(reverse("painel_revisao"), {"q": termo})
            self.assertContains(response, ferramenta.titulo_exibicao)

    def test_formulario_ingles_usa_responsible(self):
        self.client.force_login(self.autor)
        response = self.client.get("/en/adicionar-boa-pratica/?tipo=ferramenta")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Responsible")
        self.assertNotContains(response, "Responsible party")

    def test_usuario_publica_ferramenta_diretamente(self):
        self.client.force_login(self.autor)
        response = self.client.post(
            reverse("adicionar_boa_pratica"),
            {
                "tipo_compartilhamento": "ferramenta",
                "acao_envio": "enviar",
                "nome": "Ferramenta publicada NEG7",
                "ano": "2026",
                "descricao": "Descrição completa",
                "setor": str(self.setor.pk),
                "link_acesso": "https://example.org/neg7-publicada",
                "pais_ou_instancia": "EFS NEG7",
            },
        )
        self.assertEqual(response.status_code, 302)
        ferramenta = Ferramenta.objects.get(codigo="ferramenta-publicada-neg7")
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_publicacao_de_ferramentas_gera_traducoes_pt_es_en(self):
        casos = (
            ("/adicionar-boa-pratica/", "pt", "Título PT novo", "Descrição PT nova"),
            ("/es/adicionar-boa-pratica/", "es", "Título ES novo", "Descripción ES nueva"),
            ("/en/adicionar-boa-pratica/", "en", "New EN title", "New EN description"),
        )
        with patch(
            "praticas.services.traducao._traduzir_lote",
            side_effect=lambda campos, origem, destino: {
                "titulo": f"titulo-{destino}",
                "descricao": f"descricao-{destino}",
            },
        ):
            for caminho, idioma, titulo, descricao in casos:
                with self.subTest(idioma=idioma):
                    with translation.override(idioma):
                        self.client.force_login(self.autor)
                        dados = {
                            "tipo_compartilhamento": "ferramenta",
                            "acao_envio": "enviar",
                            "nome": titulo,
                            "ano": "2026",
                            "descricao": descricao,
                            "setor": str(self.setor.pk),
                            "link_acesso": f"https://example.org/{idioma}-neg7",
                            "pais_ou_instancia": "EFS NEG7",
                        }
                        with self.captureOnCommitCallbacks(execute=True):
                            response = self.client.post(caminho, dados)
                    self.assertEqual(response.status_code, 302)
                    ferramenta = Ferramenta.objects.order_by("-pk").first()
                    self.assertEqual(ferramenta.idioma_submissao, idioma)
                    campo_origem = {"pt": "titulo", "es": "titulo_es", "en": "titulo_en"}[idioma]
                    self.assertEqual(getattr(ferramenta, campo_origem), titulo)
                    self.assertTrue(ferramenta.titulo)
                    self.assertTrue(ferramenta.titulo_es)
                    self.assertTrue(ferramenta.titulo_en)
                    self.assertNotEqual(len({ferramenta.titulo, ferramenta.titulo_es, ferramenta.titulo_en}), 1)

    def test_indisponibilidade_da_traducao_nao_impede_publicacao_da_ferramenta(self):
        with patch(
            "praticas.services.traducao._traduzir_lote",
            side_effect=TimeoutError,
        ):
            self.client.force_login(self.autor)
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    reverse("adicionar_boa_pratica"),
                    {
                        "tipo_compartilhamento": "ferramenta",
                        "acao_envio": "enviar",
                        "nome": "Ferramenta sem provedor",
                        "ano": "2026",
                        "descricao": "Descrição original",
                        "setor": str(self.setor.pk),
                        "link_acesso": "https://example.org/sem-provedor",
                        "pais_ou_instancia": "EFS NEG7",
                    },
                )
        self.assertEqual(response.status_code, 302)
        ferramenta = Ferramenta.objects.get(codigo="ferramenta-sem-provedor")
        self.assertEqual(ferramenta.titulo, "Ferramenta sem provedor")
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_usuario_comum_nao_edita_publicada_nem_oferece_rascunho(self):
        ferramenta = self.ferramenta()
        self.client.force_login(self.autor)
        response = self.client.get(reverse("editar_ferramenta", args=[ferramenta.pk]))
        self.assertEqual(response.status_code, 302)
        original = ferramenta.titulo
        response = self.client.post(
            reverse("editar_ferramenta", args=[ferramenta.pk]),
            {"nome": "", "descricao": "Descrição atualizada"},
        )
        self.assertEqual(response.status_code, 302)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.titulo, original)
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_publicacao_administrativa_rejeita_ferramenta_incompleta(self):
        ferramenta = self.ferramenta(situacao=Ferramenta.Situacao.RASCUNHO)
        Ferramenta.objects.filter(pk=ferramenta.pk).update(
            titulo="",
            descricao="",
            ano=None,
            setor=None,
            url="",
            pais_ou_instancia="",
        )
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("arquivar_ferramenta", args=[ferramenta.pk]),
            {"confirmar_arquivamento": "sim", "acao_status": "publicar"},
        )
        self.assertEqual(response.status_code, 400)
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.RASCUNHO)

    def test_arquivamento_exige_staff_e_csrf(self):
        ferramenta = self.ferramenta()
        self.assertEqual(self.client.get(reverse("arquivar_ferramenta", args=[ferramenta.pk])).status_code, 302)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.staff)
        self.assertEqual(csrf_client.post(reverse("arquivar_ferramenta", args=[ferramenta.pk]), {"confirmar_arquivamento": "sim"}).status_code, 403)

    def test_staff_pode_publicar_estados_legados_sem_deletar(self):
        self.client.force_login(self.staff)
        for indice, situacao in enumerate((Ferramenta.Situacao.ENVIADA, Ferramenta.Situacao.EM_REVISAO, Ferramenta.Situacao.APROVADA, Ferramenta.Situacao.REJEITADA), start=1):
            with self.subTest(situacao=situacao):
                ferramenta = self.ferramenta(situacao)
                response = self.client.get(reverse("arquivar_ferramenta", args=[ferramenta.pk]))
                self.assertContains(response, "Publicar ferramenta")
                response = self.client.post(reverse("arquivar_ferramenta", args=[ferramenta.pk]), {"confirmar_arquivamento": "sim", "acao_status": "publicar"})
                self.assertRedirects(response, reverse("painel_revisao"))
                ferramenta.refresh_from_db()
                self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

    def test_publicacao_administrativa_gera_traducoes_ausentes_e_preserva_curada(self):
        ferramenta = self.ferramenta(
            Ferramenta.Situacao.ENVIADA,
            titulo_es="Tradução curada",
            titulo_en="",
            descricao_es="Descrição curada",
            descricao_en="",
        )
        self.client.force_login(self.staff)
        with patch(
            "praticas.services.traducao._traduzir_lote",
            side_effect=lambda campos, origem, destino: {
                "titulo": f"Título gerado {destino}",
                "descricao": f"Descrição gerada {destino}",
            },
        ):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    reverse("arquivar_ferramenta", args=[ferramenta.pk]),
                    {"confirmar_arquivamento": "sim", "acao_status": "publicar"},
                )
        self.assertRedirects(response, reverse("painel_revisao"))
        ferramenta.refresh_from_db()
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)
        self.assertEqual(ferramenta.titulo_es, "Tradução curada")
        self.assertEqual(ferramenta.descricao_es, "Descrição curada")
        self.assertEqual(ferramenta.titulo_en, "Título gerado en")
        self.assertEqual(ferramenta.descricao_en, "Descrição gerada en")

    def test_proprietario_nao_enxerga_edicao_de_ferramenta_publicada(self):
        ferramenta = self.ferramenta(autor=self.autor)
        self.client.force_login(self.autor)
        response = self.client.get(reverse("status_envio"))
        self.assertNotContains(response, reverse("editar_ferramenta", args=[ferramenta.pk]))

    def test_comparacao_invalida_nao_renderiza_resultado_parcial(self):
        experiencia_1 = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Favorita 1")
        experiencia_2 = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Favorita 2")
        self.client.force_login(self.autor)
        for experiencia in (experiencia_1, experiencia_2):
            self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        response = self.client.get(reverse("favoritos_experiencias"), {"comparar": [str(experiencia_1.pk), "999999"]})
        self.assertContains(response, "Selecione duas ou três")
        self.assertNotContains(response, 'id="quadro-comparativo"')
        response = self.client.get(reverse("favoritos_experiencias"), {"comparar": ["invalido", str(experiencia_1.pk)]})
        self.assertContains(response, "Selecione duas ou três")
        self.assertNotContains(response, 'id="quadro-comparativo"')

    def test_comparacao_com_um_ou_quatro_ids_sem_submit_e_rejeitada(self):
        experiencias = [
            self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo=f"Comparável {indice}")
            for indice in range(1, 5)
        ]
        self.client.force_login(self.autor)
        for experiencia in experiencias:
            self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        for ids in ([experiencias[0].pk], [experiencia.pk for experiencia in experiencias]):
            with self.subTest(ids=ids):
                response = self.client.get(reverse("favoritos_experiencias"), {"comparar": ids})
                self.assertContains(response, "Selecione duas ou três")
                self.assertNotContains(response, 'id="quadro-comparativo"')

    def test_formulario_de_comparacao_inicial_aponta_para_o_resultado(self):
        experiencia = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO)
        self.client.force_login(self.autor)
        self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'action="/favoritos/#quadro-comparativo"')
        self.assertNotContains(response, "Selecione duas ou três")

    def test_comparacao_completa_exibe_campos_existentes(self):
        experiencias = [
            self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Comparável 1"),
            self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Comparável 2"),
        ]
        self.client.force_login(self.autor)
        for experiencia in experiencias:
            self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        response = self.client.get(reverse("favoritos_experiencias"), {"comparar": [str(item.pk) for item in experiencias]})
        self.assertContains(response, "Perguntas de auditoria")
        self.assertContains(response, "Critérios")
        self.assertContains(response, "Metodologias e instrumentos")
        self.assertContains(response, "Replicabilidade")
        self.assertContains(response, "Normas internacionais")
        self.assertContains(response, "#quadro-comparativo")

        html = response.content.decode("utf-8")
        for experiencia in experiencias:
            self.assertIn(f'value="{experiencia.pk}" class="me-1" checked', html)

        terceira = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Comparável 3")
        nao_selecionada = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Comparável não selecionada")
        for item in (terceira, nao_selecionada):
            self.client.post(reverse("alternar_favorito", args=[item.pk]))
        resposta_com_tres = self.client.get(
            reverse("favoritos_experiencias"),
            {"comparar": [str(item.pk) for item in experiencias] + [str(terceira.pk)]},
        )
        html = resposta_com_tres.content.decode("utf-8")
        self.assertIn(f'value="{terceira.pk}" class="me-1" checked', html)
        self.assertIn(f'value="{nao_selecionada.pk}" class="me-1"', html)
        self.assertNotIn(f'value="{nao_selecionada.pk}" class="me-1" checked', html)

    def test_comparacao_sem_selecao_mostra_aviso_sem_comparacao(self):
        experiencia = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO)
        self.client.force_login(self.autor)
        self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        response = self.client.get(
            reverse("favoritos_experiencias"),
            {"comparar_submit": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecione duas ou três")
        self.assertNotContains(response, "id=\"quadro-comparativo\"")

    def test_comparacao_com_duplicata_ou_nao_favorito_nao_e_parcial(self):
        experiencia = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO)
        outra = self.experiencia(Experiencia.StatusPublicacao.PUBLICADO)
        self.client.force_login(self.autor)
        self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        for ids in ([str(experiencia.pk), str(experiencia.pk)], [str(experiencia.pk), str(outra.pk)]):
            with self.subTest(ids=ids):
                response = self.client.get(
                    reverse("favoritos_experiencias"),
                    {"comparar": ids, "comparar_submit": "1"},
                )
                self.assertContains(response, "Selecione duas ou três")
                self.assertNotContains(response, "id=\"quadro-comparativo\"")

    def test_parser_de_comparacao_rejeita_ids_malformados_sem_http_500(self):
        limite, limite_invalido = _ids_comparacao_seguros(["9223372036854775807"])
        acima, acima_invalido = _ids_comparacao_seguros(["9223372036854775808"])
        self.assertEqual(limite, [9223372036854775807])
        self.assertFalse(limite_invalido)
        self.assertEqual(acima, [])
        self.assertTrue(acima_invalido)
        experiencias = [
            self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo=f"Parser {indice}")
            for indice in range(1, 4)
        ]
        self.client.force_login(self.autor)
        for experiencia in experiencias:
            self.client.post(reverse("alternar_favorito", args=[experiencia.pk]))
        validos = self.client.get(
            reverse("favoritos_experiencias"),
            {"comparar": [str(item.pk) for item in experiencias]},
        )
        self.assertEqual(validos.status_code, 200)
        self.assertContains(validos, 'id="quadro-comparativo"')
        for valor in ("5" * 5000, "²", "-1", "0", "texto", "999999"):
            with self.subTest(valor=valor):
                response = self.client.get(
                    reverse("favoritos_experiencias"),
                    {"comparar": [str(experiencias[0].pk), valor]},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Selecione duas ou três")
                self.assertNotContains(response, 'id="quadro-comparativo"')

    def test_contadores_do_painel_sao_agregados_com_valores_reais(self):
        self.experiencia(Experiencia.StatusPublicacao.PUBLICADO, titulo="Publicada NEG7")
        self.experiencia(Experiencia.StatusPublicacao.ARQUIVADO, titulo="Arquivada NEG7")
        self.ferramenta(Ferramenta.Situacao.PUBLICADA)
        self.ferramenta(Ferramenta.Situacao.ARQUIVADA)
        self.client.force_login(self.staff)
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.context["contadores"]["publicado"], 2)
        self.assertEqual(response.context["contadores"]["arquivado"], 2)
        self.assertContains(response, '<p class="metric-value">2</p>', count=2)

    def test_recuperacao_de_pratica_do_autor_tem_texto_e_fluxo_corretos(self):
        experiencia = self.experiencia(Experiencia.StatusPublicacao.ARQUIVADO, autor=self.autor)
        self.client.force_login(self.autor)
        with translation.override("pt-br"):
            response = self.client.get(reverse("arquivar_boa_pratica", args=[experiencia.pk]))
            self.assertContains(response, "Recuperar boa prática")
            self.assertContains(response, "Esta ação recupera a boa prática")
            self.assertNotContains(response, "retira a prática")
            response = self.client.post(reverse("arquivar_boa_pratica", args=[experiencia.pk]), {"confirmar_arquivamento": "sim", "acao_status": "recuperar"})
            self.assertRedirects(response, reverse("meus_envios"))
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)

    def test_transicoes_de_arquivamento_de_boas_praticas_rejeitam_acoes_ausentes_ou_incompativeis(self):
        casos = (
            (Experiencia.StatusPublicacao.PUBLICADO, "desconhecida"),
            (Experiencia.StatusPublicacao.PUBLICADO, None),
            (Experiencia.StatusPublicacao.PUBLICADO, "recuperar"),
            (Experiencia.StatusPublicacao.ARQUIVADO, "arquivar"),
        )
        self.client.force_login(self.staff)
        for status, acao in casos:
            with self.subTest(status=status, acao=acao):
                experiencia = self.experiencia(status)
                dados = {"confirmar_arquivamento": "sim"}
                if acao is not None:
                    dados["acao_status"] = acao
                antes = experiencia.atualizado_em
                response = self.client.post(reverse("arquivar_boa_pratica", args=[experiencia.pk]), dados)
                self.assertEqual(response.status_code, 302)
                experiencia.refresh_from_db()
                self.assertEqual(experiencia.status_publicacao, status)
                self.assertEqual(experiencia.atualizado_em, antes)

    def test_mapa_e_listagem_normativa_usam_o_mesmo_universo(self):
        normas = [
            NormaInternacional.objects.create(nome=f"Norma NEG7 {indice}", nome_es=f"Norma ES {indice}", nome_en=f"Norma EN {indice}")
            for indice in range(1, 3)
        ]
        NormaInternacionalPais.objects.bulk_create([
            NormaInternacionalPais(norma=norma, pais=self.pais, status="Aplicável")
            for norma in normas
        ])
        with translation.override("pt-br"):
            from . import views
            payload = views._payload_mapa_regional()
        brasil = next(item for item in payload["paises"] if item["id"] == self.pais.pk)
        with translation.override("pt-br"):
            response = self.client.get(reverse("normas_internacionais"), {"pais": self.pais.pk})
            self.assertEqual(brasil["criterios_normativos"], 2)
            self.assertEqual(len(brasil["criterios_normativos_ids"]), 2)
            self.assertContains(response, "Norma NEG7 1")
            self.assertContains(response, "Norma NEG7 2")

    def test_ferramentas_publicadas_respeitam_o_idioma_da_interface(self):
        ferramenta = self.ferramenta()
        self.client.force_login(self.autor)
        for idioma, titulo in (("pt-br", "Título PT"), ("es", "Título ES"), ("en", "Title EN")):
            with self.subTest(idioma=idioma), translation.override(idioma):
                response = self.client.get(reverse("ferramentas"))
                self.assertContains(response, titulo)

    def test_confirmacao_de_ferramenta_aponta_para_catalogo_de_ferramentas(self):
        response = self.client.get(reverse("confirmacao_envio"), {"tipo": "ferramenta"})
        self.assertContains(response, f'href="{reverse("ferramentas")}"')

    def test_confirmacao_de_boa_pratica_indica_publicacao_sem_revisao(self):
        response = self.client.get(reverse("confirmacao_envio"))
        conteudo = unescape(response.content.decode("utf-8"))
        conteudo = conteudo.split('<section class="page-hero">', 1)[1].split("</section>", 1)[0]
        self.assertIn("Sua boa prática foi publicada", conteudo)
        self.assertIn("disponível no catálogo público", conteudo)
        self.assertNotIn("aprovado", conteudo)
        self.assertNotIn("revisão", conteudo)

    def test_orientacao_do_mapa_e_localizada_e_acessivel(self):
        for idioma, trechos in (
            ("pt-br", ("Use Tab", "Enter ou Espaço", "nova seleção")),
            ("es", ("Usa Tab", "Enter o Espacio", "nueva selección")),
            ("en", ("Use Tab", "Enter or Space", "new selection")),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                response = self.client.get(reverse("pagina_inicial"))
                conteudo = unescape(response.content.decode("utf-8"))
                self.assertIn('id="home-map-keyboard-help"', conteudo)
                for trecho in trechos:
                    self.assertIn(trecho, conteudo)
                self.assertIn('aria-describedby="home-map-description home-map-keyboard-help"', conteudo)
