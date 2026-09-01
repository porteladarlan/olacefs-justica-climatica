from smtplib import SMTPException
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import (
    EFS,
    Experiencia,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="plataforma@example.org",
)
class NotificacoesFluxoEditorialTests(TestCase):
    senha = "SenhaForte123!"

    @classmethod
    def setUpTestData(cls):
        cls.pais = Pais.objects.create(
            nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA"
        )
        cls.efs = EFS.objects.create(
            nome="Tribunal de Contas",
            nome_es="Tribunal de Cuentas",
            nome_en="Court of Accounts",
            sigla="TC",
            pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(
            nome="Auditoria", nome_es="Auditoría", nome_en="Audit"
        )
        cls.setor = Setor.objects.create(
            nome="Água", nome_es="Agua", nome_en="Water"
        )
        cls.tema = TemaTransversal.objects.create(
            nome="Equidade", nome_es="Equidad", nome_en="Equity"
        )
        cls.norma = NormaInternacional.objects.create(
            nome="Norma climática",
            nome_es="Norma climática ES",
            nome_en="Climate standard",
        )
        cls.autor = get_user_model().objects.create_user(
            username="autora",
            email="autora@example.org",
            password=cls.senha,
            first_name="Ana",
            last_name="Silva",
        )
        cls.revisor = get_user_model().objects.create_user(
            username="revisor",
            email="revisor@example.org",
            password=cls.senha,
            is_staff=True,
        )

    def setUp(self):
        translation.activate("pt-br")
        self.client.force_login(self.autor)

    def tearDown(self):
        translation.deactivate_all()

    def dados_formulario(self, titulo="Boa prática notificada", acao="enviar"):
        return {
            "efs": self.efs.pk,
            "pais": self.pais.pk,
            "titulo": titulo,
            "tipo_experiencia": self.tipo.pk,
            "setor": self.setor.pk,
            "temas_transversais": [self.tema.pk],
            "normas_internacionais": [self.norma.pk],
            "email_contato": self.autor.email,
            "pessoa_responsavel": "Ana Silva",
            "descricao": "Descrição da boa prática.",
            "enfoque_justica_climatica": "Enfoque de justiça climática.",
            "objetivo": "Objetivo climático.",
            "perguntas_chave": "Pergunta de auditoria.",
            "criterios_utilizados": "Critério climático.",
            "metodologia": "Metodologia aplicada.",
            "ferramentas_utilizadas": "Ferramenta utilizada.",
            "resultados": "Resultados alcançados.",
            "recomendacoes": "Recomendações.",
            "replicabilidade": "Replicável.",
            "informacoes_adicionais": "Informações adicionais.",
            "ano_execucao": 2026,
            "acao_envio": acao,
        }

    def criar_experiencia(self, titulo, status, autor=None):
        return Experiencia.objects.create(
            autor=autor or self.autor,
            titulo=titulo,
            titulo_es=f"{titulo} ES",
            titulo_en=f"{titulo} EN",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            ano_execucao=2026,
            setor=self.setor,
            email_contato=(autor or self.autor).email,
            pessoa_responsavel="Ana Silva",
            descricao="Descrição.",
            status_publicacao=status,
        )

    def mensagem_para(self, email):
        return next(mensagem for mensagem in mail.outbox if mensagem.to == [email])

    def test_rascunho_e_formulario_invalido_nao_enviam_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            rascunho = self.client.post(
                reverse("adicionar_boa_pratica"),
                self.dados_formulario(acao="rascunho"),
            )
        self.assertEqual(rascunho.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

        dados_invalidos = self.dados_formulario(titulo="")
        with self.captureOnCommitCallbacks(execute=True):
            invalido = self.client.post(reverse("adicionar_boa_pratica"), dados_invalidos)
        self.assertEqual(invalido.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_envio_notifica_autor_e_apenas_revisores_staff_ativos_unicos(self):
        get_user_model().objects.create_user(
            username="revisor-duplicado",
            email="REVISOR@example.org",
            password=self.senha,
            is_staff=True,
        )
        get_user_model().objects.create_user(
            username="revisor-inativo",
            email="inativo@example.org",
            password=self.senha,
            is_staff=True,
            is_active=False,
        )
        get_user_model().objects.create_user(
            username="revisor-sem-email",
            email="",
            password=self.senha,
            is_staff=True,
        )
        get_user_model().objects.create_user(
            username="superuser-sem-staff",
            email="superuser@example.org",
            password=self.senha,
            is_superuser=True,
            is_staff=False,
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("adicionar_boa_pratica"),
                self.dados_formulario(),
                secure=True,
            )
        experiencia = Experiencia.objects.get(titulo="Boa prática notificada")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)
        self.assertCountEqual(
            [mensagem.to for mensagem in mail.outbox],
            [["autora@example.org"], ["revisor@example.org"]],
        )

        autor = self.mensagem_para("autora@example.org")
        self.assertEqual(autor.subject, "Boa prática publicada")
        self.assertIn("Publicado", autor.body)
        self.assertIn("https://testserver/meus-envios/", autor.body)
        self.assertIn("foi publicada com sucesso", autor.body)
        revisor = self.mensagem_para("revisor@example.org")
        self.assertIn(experiencia.titulo, revisor.body)
        self.assertIn("publicada automaticamente", revisor.body)
        for mensagem in mail.outbox:
            self.assertNotIn(self.senha, mensagem.body)
            self.assertNotIn("token", mensagem.body.lower())

    def test_notificacao_permanece_pendente_ate_commit(self):
        with patch("praticas.views.tentar_traduzir_experiencia") as traduzir:
            with self.captureOnCommitCallbacks(execute=False) as callbacks:
                response = self.client.post(
                    reverse("adicionar_boa_pratica"), self.dados_formulario()
                )
                self.assertEqual(len(mail.outbox), 0)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(len(callbacks), 2)
            for callback in callbacks:
                callback()

            self.assertEqual(len(mail.outbox), 2)
            traduzir.assert_called_once()

    def test_editar_sem_transicao_para_enviado_nao_duplica_notificacao(self):
        experiencia = self.criar_experiencia(
            "Já enviada", Experiencia.StatusPublicacao.ENVIADO
        )
        dados = self.dados_formulario(titulo="Já enviada")

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("editar_boa_pratica", args=[experiencia.pk]), dados
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)

    def test_rota_legada_nao_aprova_nem_notifica(self):
        experiencia = self.criar_experiencia(
            "Prática aprovada", Experiencia.StatusPublicacao.ENVIADO
        )
        self.client.force_login(self.revisor)

        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {"acao": "aprovar", "comentario_revisor": "Aprovada."},
            secure=True,
        )
        experiencia.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ENVIADO)
        self.assertEqual(len(mail.outbox), 0)

    def test_rota_legada_nao_publica_nem_notifica(self):
        experiencia = self.criar_experiencia(
            "Prática publicada", Experiencia.StatusPublicacao.APROVADO
        )
        self.client.force_login(self.revisor)

        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {"acao": "publicar", "comentario_revisor": "Publicada."},
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.APROVADO)
        self.assertEqual(len(mail.outbox), 0)

    def test_decisoes_legadas_nao_alteram_status_nem_notificam(self):
        casos = ("devolver", "rejeitar")
        self.client.force_login(self.revisor)
        for indice, acao in enumerate(casos):
            with self.subTest(acao=acao):
                mail.outbox.clear()
                experiencia = self.criar_experiencia(
                    f"Decisão {indice}", Experiencia.StatusPublicacao.EM_REVISAO
                )
                response = self.client.post(
                    reverse("revisar_experiencia", args=[experiencia.pk]),
                    {"acao": acao, "comentario_revisor": "Justificativa institucional."},
                )
                experiencia.refresh_from_db()

                self.assertEqual(response.status_code, 302)
                self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.EM_REVISAO)
                self.assertEqual(len(mail.outbox), 0)

    def test_revisao_sem_mudanca_real_de_status_nao_notifica(self):
        experiencia = self.criar_experiencia(
            "Permanece publicada", Experiencia.StatusPublicacao.PUBLICADO
        )
        self.client.force_login(self.revisor)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("revisar_experiencia", args=[experiencia.pk]),
                {"acao": "publicar", "comentario_revisor": "Sem alteração."},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_solicitacao_edicao_notifica_solicitante_e_revisores(self):
        experiencia = self.criar_experiencia(
            "Prática para editar", Experiencia.StatusPublicacao.PUBLICADO
        )
        experiencia.email_contato = "contato-da-pratica@example.org"
        experiencia.save(update_fields=["email_contato"])
        dados = self.dados_formulario(titulo="Prática editada")
        dados["email_contato"] = experiencia.email_contato
        dados["comentario_autor"] = "Atualização necessária."

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("solicitar_edicao_publicada", args=[experiencia.pk]),
                dados,
                secure=True,
            )
        self.assertRedirects(response, reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertFalse(PropostaEdicaoExperiencia.objects.filter(experiencia=experiencia).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_solicitante_autorizado_recebe_confirmacao_e_decisao_no_lugar_do_autor(self):
        solicitante = get_user_model().objects.create_user(
            username="solicitante-autorizado",
            email="solicitante@example.org",
            password=self.senha,
            is_staff=True,
        )
        experiencia = self.criar_experiencia(
            "Prática solicitada por outro usuário",
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        dados = self.dados_formulario(titulo="Prática atualizada pelo solicitante")
        self.client.force_login(solicitante)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("solicitar_edicao_publicada", args=[experiencia.pk]),
                dados,
                secure=True,
            )

        self.assertRedirects(response, reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertFalse(PropostaEdicaoExperiencia.objects.filter(experiencia=experiencia).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_decisao_de_proposta_antiga_com_email_invalido_usa_email_do_autor(self):
        experiencia = self.criar_experiencia(
            "Proposta antiga sem contato válido",
            Experiencia.StatusPublicacao.PUBLICADO,
        )
        proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=experiencia,
            email_contato="contato inválido",
            dados_json={},
        )
        self.client.force_login(self.revisor)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("revisar_edicao_publicada", args=[proposta.pk]),
                {
                    "acao": "rejeitar",
                    "comentario_revisor": "Decisão sobre registro antigo.",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(mail.outbox, [])

    def test_decisao_edicao_notifica_solicitante(self):
        self.client.force_login(self.revisor)
        casos = (("aprovar", PropostaEdicaoExperiencia.Status.PENDENTE), ("rejeitar", PropostaEdicaoExperiencia.Status.PENDENTE))
        for indice, (acao, status) in enumerate(casos):
            with self.subTest(acao=acao):
                mail.outbox.clear()
                experiencia = self.criar_experiencia(
                    f"Edição decidida {indice}", Experiencia.StatusPublicacao.PUBLICADO
                )
                proposta = PropostaEdicaoExperiencia.objects.create(
                    experiencia=experiencia,
                    email_contato=self.autor.email,
                    dados_json={},
                )
                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        reverse("revisar_edicao_publicada", args=[proposta.pk]),
                        {
                            "acao": acao,
                            "comentario_revisor": "Decisão fundamentada.",
                        },
                    )
                proposta.refresh_from_db()

                self.assertEqual(response.status_code, 302)
                self.assertEqual(proposta.status, status)
                self.assertEqual(len(mail.outbox), 0)

    def test_falha_smtp_nao_desfaz_submissao_nem_retorna_erro_500(self):
        with patch(
            "praticas.emails.EmailMultiAlternatives.send",
            side_effect=SMTPException("serviço indisponível"),
        ):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    reverse("adicionar_boa_pratica"), self.dados_formulario()
                )

            experiencia_revisada = self.criar_experiencia(
                "Aprovação com SMTP indisponível",
                Experiencia.StatusPublicacao.ENVIADO,
            )
            self.client.force_login(self.revisor)
            with self.captureOnCommitCallbacks(execute=True):
                resposta_revisao = self.client.post(
                    reverse("revisar_experiencia", args=[experiencia_revisada.pk]),
                    {"acao": "aprovar", "comentario_revisor": "Aprovada."},
                )

        self.assertEqual(response.status_code, 302)
        experiencia = Experiencia.objects.get(titulo="Boa prática notificada")
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        experiencia_revisada.refresh_from_db()
        self.assertEqual(resposta_revisao.status_code, 302)
        self.assertEqual(
            experiencia_revisada.status_publicacao,
            Experiencia.StatusPublicacao.ENVIADO,
        )

    def test_submissao_e_urls_sao_equivalentes_em_pt_es_en(self):
        casos = (
            ("pt-br", "/adicionar-boa-pratica/", "Boa prática publicada", "/meus-envios/"),
            ("es", "/es/adicionar-boa-pratica/", "Buena práctica publicada", "/es/meus-envios/"),
            ("en", "/en/adicionar-boa-pratica/", "Good practice published", "/en/meus-envios/"),
        )
        for indice, (idioma, caminho, assunto, caminho_envios) in enumerate(casos):
            with self.subTest(idioma=idioma):
                mail.outbox.clear()
                usuario = get_user_model().objects.create_user(
                    username=f"autor-{idioma}",
                    email=f"autor-{indice}@example.org",
                    password=self.senha,
                )
                self.client.force_login(usuario)
                dados = self.dados_formulario(titulo=f"Prática idioma {indice}")
                dados["email_contato"] = usuario.email
                with translation.override(idioma):
                    with self.captureOnCommitCallbacks(execute=True):
                        response = self.client.post(caminho, dados, secure=True)

                self.assertEqual(response.status_code, 302)
                mensagem = self.mensagem_para(usuario.email)
                self.assertEqual(mensagem.subject, assunto)
                self.assertIn(f"https://testserver{caminho_envios}", mensagem.body)

    def test_rejeicao_e_solicitacao_edicao_sao_trilingues(self):
        casos = (
            (
                "pt-br",
                "Sua boa prática foi rejeitada",
                "/meus-envios/",
            ),
            (
                "es",
                "Su buena práctica fue rechazada",
                "/es/meus-envios/",
            ),
            (
                "en",
                "Your good practice was rejected",
                "/en/meus-envios/",
            ),
        )
        for indice, (
            idioma,
            assunto_rejeicao,
            caminho_envios,
        ) in enumerate(casos):
            with self.subTest(idioma=idioma):
                mail.outbox.clear()
                experiencia = self.criar_experiencia(
                    f"Rejeição idioma {indice}",
                    Experiencia.StatusPublicacao.EM_REVISAO,
                )
                self.client.force_login(self.revisor)
                with translation.override(idioma):
                    url_revisao = reverse(
                        "revisar_experiencia", args=[experiencia.pk]
                    )
                    with self.captureOnCommitCallbacks(execute=True):
                        response = self.client.post(
                            url_revisao,
                            {
                                "acao": "rejeitar",
                                "comentario_revisor": "Decisão registrada.",
                            },
                            secure=True,
                        )
                self.assertEqual(response.status_code, 302)
                experiencia.refresh_from_db()
                self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.EM_REVISAO)
                self.assertEqual(len(mail.outbox), 0)

                mail.outbox.clear()
                experiencia_edicao = self.criar_experiencia(
                    f"Edição idioma {indice}", Experiencia.StatusPublicacao.PUBLICADO
                )
                self.client.force_login(self.autor)
                with translation.override(idioma):
                    response = self.client.post(
                        reverse("solicitar_edicao_publicada", args=[experiencia_edicao.pk]),
                        {},
                        secure=True,
                    )
                    destino = reverse("editar_boa_pratica", args=[experiencia_edicao.pk])
                self.assertRedirects(response, destino)
                self.assertFalse(PropostaEdicaoExperiencia.objects.filter(experiencia=experiencia_edicao).exists())
                self.assertEqual(len(mail.outbox), 0)
