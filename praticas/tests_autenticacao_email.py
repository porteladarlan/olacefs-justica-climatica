from datetime import datetime, timedelta
from html import unescape
from smtplib import SMTPException
from unittest.mock import patch
from urllib.parse import urlencode, urlsplit

from django.contrib.auth import SESSION_KEY, get_user_model
from django.core import mail
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import ConfirmacaoEmailPendente
from .tokens import confirmacao_email_token


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="plataforma@example.org",
)
class AutenticacaoEmailTests(TestCase):
    senha_inicial = "SenhaForte123!"

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def dados_cadastro(self, **alteracoes):
        dados = {
            "first_name": "Ana",
            "last_name": "Silva",
            "username": "ana.silva",
            "email": "ANA.SILVA@EXAMPLE.ORG",
            "password1": self.senha_inicial,
            "password2": self.senha_inicial,
        }
        dados.update(alteracoes)
        return dados

    def cadastrar(self, **alteracoes):
        return self.client.post(
            reverse("registrar_usuario"),
            self.dados_cadastro(**alteracoes),
            secure=True,
        )

    def usuario_inativo(self, com_pendencia=True, **alteracoes):
        dados = self.dados_cadastro(**alteracoes)
        usuario = get_user_model().objects.create_user(
            username=dados["username"],
            email=dados["email"].lower(),
            password=dados["password1"],
            first_name=dados["first_name"],
            last_name=dados["last_name"],
            is_active=False,
        )
        if com_pendencia:
            ConfirmacaoEmailPendente.objects.create(usuario=usuario)
        return usuario

    def url_confirmacao(self, usuario):
        return reverse(
            "confirmar_email",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(usuario.pk)),
                "token": confirmacao_email_token.make_token(usuario),
            },
        )

    def test_cadastro_cria_conta_inativa_normaliza_email_e_nao_autentica(self):
        response = self.cadastrar()
        usuario = get_user_model().objects.get(username="ana.silva")

        self.assertRedirects(response, reverse("confirmacao_email_enviada"))
        self.assertFalse(usuario.is_active)
        self.assertEqual(usuario.email, "ana.silva@example.org")
        self.assertEqual(usuario.first_name, "Ana")
        self.assertEqual(usuario.last_name, "Silva")
        self.assertTrue(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario).exists()
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_cadastro_envia_confirmacao_com_url_https_sem_dominio_fixo(self):
        self.cadastrar()

        self.assertEqual(len(mail.outbox), 1)
        mensagem = mail.outbox[0]
        self.assertEqual(mensagem.to, ["ana.silva@example.org"])
        self.assertIn("Plataforma Regional de Justiça Climática", mensagem.body)
        self.assertIn("https://testserver/confirmar-email/", mensagem.body)
        self.assertIn("ignore esta mensagem", mensagem.body)

    def test_token_valido_ativa_sem_autenticar_e_nao_pode_ser_reutilizado(self):
        usuario = self.usuario_inativo()
        url = self.url_confirmacao(usuario)

        response = self.client.get(url)
        usuario.refresh_from_db()

        self.assertRedirects(response, reverse("login_usuario"))
        self.assertTrue(usuario.is_active)
        self.assertFalse(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario).exists()
        )
        self.assertNotIn(SESSION_KEY, self.client.session)
        reutilizacao = self.client.get(url)
        self.assertEqual(reutilizacao.status_code, 400)
        self.assertContains(reutilizacao, "Link inválido ou expirado", status_code=400)

    def test_token_invalido_nao_ativa_conta(self):
        usuario = self.usuario_inativo()
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))

        response = self.client.get(
            reverse("confirmar_email", kwargs={"uidb64": uid, "token": "invalido"})
        )
        usuario.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(usuario.is_active)

    def test_usuario_desativado_sem_pendencia_nao_recebe_email_nem_e_reativado(self):
        usuario = self.usuario_inativo(com_pendencia=False)
        url = self.url_confirmacao(usuario)

        reenvio = self.client.post(
            reverse("reenviar_confirmacao_email"),
            {"email": usuario.email},
            follow=True,
        )
        confirmacao = self.client.get(url)
        usuario.refresh_from_db()

        self.assertContains(reenvio, "Se houver uma conta pendente associada")
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(confirmacao.status_code, 400)
        self.assertFalse(usuario.is_active)
        self.assertFalse(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario).exists()
        )

    def test_token_sem_pendencia_e_rejeitado(self):
        usuario = self.usuario_inativo()
        url = self.url_confirmacao(usuario)
        ConfirmacaoEmailPendente.objects.get(usuario=usuario).delete()

        response = self.client.get(url)
        usuario.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(usuario.is_active)

    @override_settings(PASSWORD_RESET_TIMEOUT=60)
    def test_token_de_confirmacao_expira_conforme_password_reset_timeout(self):
        usuario = self.usuario_inativo()
        agora = datetime(2026, 8, 14, 12, 0, 0)
        with patch.object(confirmacao_email_token, "_now", return_value=agora):
            url = self.url_confirmacao(usuario)

        with patch.object(
            confirmacao_email_token,
            "_now",
            return_value=agora + timedelta(seconds=61),
        ):
            response = self.client.get(url)
        usuario.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(usuario.is_active)
        self.assertTrue(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario).exists()
        )

    def test_usuario_inativo_nao_entra_e_ativado_consegue_entrar(self):
        usuario = self.usuario_inativo()
        dados = {"username": usuario.username, "password": self.senha_inicial}

        bloqueado = self.client.post(reverse("login_usuario"), dados)
        self.assertEqual(bloqueado.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

        usuario.is_active = True
        usuario.save(update_fields=["is_active"])
        permitido = self.client.post(reverse("login_usuario"), dados)
        self.assertRedirects(permitido, reverse("meus_envios"))
        self.assertIn(SESSION_KEY, self.client.session)

    def test_email_duplicado_e_rejeitado_sem_diferenciar_maiusculas(self):
        get_user_model().objects.create_user(
            username="existente",
            email="ana.silva@example.org",
            password=self.senha_inicial,
        )

        response = self.cadastrar()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Já existe uma conta com este e-mail")
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_falha_smtp_preserva_conta_inativa_e_oferece_reenvio(self):
        with patch(
            "praticas.views.enviar_confirmacao_email",
            side_effect=SMTPException("indisponível"),
        ):
            response = self.cadastrar()

        usuario = get_user_model().objects.get(username="ana.silva")
        self.assertFalse(usuario.is_active)
        self.assertTrue(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario).exists()
        )
        self.assertRedirects(
            response,
            f"{reverse('confirmacao_email_enviada')}?envio=pendente",
        )
        pagina = self.client.get(response.url)
        self.assertContains(pagina, reverse("reenviar_confirmacao_email"))

    def test_reenvio_entrega_para_conta_inativa(self):
        usuario = self.usuario_inativo()

        response = self.client.post(
            reverse("reenviar_confirmacao_email"),
            {"email": usuario.email.upper()},
            secure=True,
            follow=True,
        )

        self.assertRedirects(response, f"{reverse('reenviar_confirmacao_email')}?enviado=1")
        self.assertContains(response, "Se houver uma conta pendente associada")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://testserver/confirmar-email/", mail.outbox[0].body)

    def test_reenvio_nao_revela_conta_inexistente_ou_ativa(self):
        usuario_ativo = get_user_model().objects.create_user(
            username="ativa",
            email="ativa@example.org",
            password=self.senha_inicial,
        )
        mensagem_generica = "Se houver uma conta pendente associada"

        inexistente = self.client.post(
            reverse("reenviar_confirmacao_email"),
            {"email": "ausente@example.org"},
            follow=True,
        )
        ativa = self.client.post(
            reverse("reenviar_confirmacao_email"),
            {"email": "ativa@example.org"},
            follow=True,
        )

        self.assertEqual(inexistente.status_code, ativa.status_code)
        self.assertContains(inexistente, mensagem_generica)
        self.assertContains(ativa, mensagem_generica)
        self.assertNotContains(inexistente, "ausente@example.org")
        self.assertNotContains(ativa, "ativa@example.org")
        self.assertEqual(len(mail.outbox), 0)
        usuario_ativo.refresh_from_db()
        self.assertTrue(usuario_ativo.is_active)
        self.assertFalse(
            ConfirmacaoEmailPendente.objects.filter(usuario=usuario_ativo).exists()
        )

    def test_next_interno_e_preservado_ate_o_login(self):
        destino = reverse("adicionar_boa_pratica")
        cadastro = self.client.get(
            f"{reverse('registrar_usuario')}?{urlencode({'next': destino})}"
        )
        self.assertContains(
            cadastro,
            f'<input type="hidden" name="next" value="{destino}">',
            html=True,
        )

        dados = self.dados_cadastro(next=destino)
        resposta_cadastro = self.client.post(
            reverse("registrar_usuario"), dados, secure=True
        )
        usuario = get_user_model().objects.get(username="ana.silva")
        pendencia = ConfirmacaoEmailPendente.objects.get(usuario=usuario)
        self.assertRedirects(resposta_cadastro, reverse("confirmacao_email_enviada"))
        self.assertEqual(pendencia.destino_apos_login, destino)

        resposta_confirmacao = self.client.get(self.url_confirmacao(usuario))
        login_com_destino = f"{reverse('login_usuario')}?{urlencode({'next': destino})}"
        self.assertRedirects(resposta_confirmacao, login_com_destino)

        resposta_login = self.client.post(
            reverse("login_usuario"),
            {
                "username": usuario.username,
                "password": self.senha_inicial,
                "next": destino,
            },
        )
        self.assertRedirects(resposta_login, destino, fetch_redirect_response=False)

    def test_next_externo_e_descartado_sem_open_redirect(self):
        destino_externo = "https://malicioso.example/roubar-sessao"
        dados = self.dados_cadastro(next=destino_externo)

        resposta_cadastro = self.client.post(reverse("registrar_usuario"), dados)
        usuario = get_user_model().objects.get(username="ana.silva")
        pendencia = ConfirmacaoEmailPendente.objects.get(usuario=usuario)

        self.assertRedirects(resposta_cadastro, reverse("confirmacao_email_enviada"))
        self.assertEqual(pendencia.destino_apos_login, "")
        resposta_confirmacao = self.client.get(self.url_confirmacao(usuario))
        self.assertRedirects(resposta_confirmacao, reverse("login_usuario"))
        self.assertNotIn("malicioso.example", resposta_confirmacao.url)

    def test_login_exibe_esqueci_senha_nos_tres_idiomas(self):
        casos = (
            ("/entrar/", "Esqueci minha senha"),
            ("/es/entrar/", "Olvidé mi contraseña"),
            ("/en/entrar/", "Forgot my password"),
        )
        for caminho, rotulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertIn(rotulo, unescape(response.content.decode("utf-8")))

    def test_rotas_de_conta_funcionam_em_pt_es_en(self):
        sufixos = (
            "senha/esqueci/",
            "senha/email-enviado/",
            "confirmar-email/reenviar/",
            "cadastro/confirmacao-enviada/",
        )
        for prefixo in ("/", "/es/", "/en/"):
            for sufixo in sufixos:
                caminho = f"{prefixo}{sufixo}"
                with self.subTest(caminho=caminho):
                    self.assertEqual(self.client.get(caminho).status_code, 200)

    def test_emails_de_confirmacao_sao_trilingues(self):
        casos = (
            ("/cadastro/", "Confirmar meu e-mail", "ignore esta mensagem"),
            ("/es/cadastro/", "Confirmar mi correo", "ignore este mensaje"),
            ("/en/cadastro/", "Confirm my e-mail", "ignore this message"),
        )
        for indice, (caminho, cta, aviso) in enumerate(casos):
            with self.subTest(caminho=caminho):
                dados = self.dados_cadastro(
                    username=f"usuario{indice}",
                    email=f"usuario{indice}@example.org",
                )
                response = self.client.post(caminho, dados, secure=True)
                self.assertEqual(response.status_code, 302)
                html = mail.outbox[-1].alternatives[0].content
                self.assertIn(cta, html)
                self.assertIn(aviso, html)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="plataforma@example.org",
)
class RecuperacaoSenhaTests(TestCase):
    senha_inicial = "SenhaForte123!"

    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="recuperacao",
            email="recuperacao@example.org",
            password=cls.senha_inicial,
        )

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def solicitar(self, email="recuperacao@example.org", caminho=None):
        return self.client.post(
            caminho or reverse("password_reset"),
            {"email": email},
            secure=True,
        )

    def caminho_recuperacao(self):
        url = next(
            linha for linha in mail.outbox[-1].body.splitlines() if linha.startswith("https://")
        )
        return urlsplit(url).path

    def test_recuperacao_envia_email_https_sem_revelar_existencia(self):
        existente = self.solicitar()
        self.assertRedirects(existente, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://testserver/senha/redefinir/", mail.outbox[0].body)
        self.assertNotIn(self.senha_inicial, mail.outbox[0].body)

        mail.outbox.clear()
        inexistente = self.solicitar("ausente@example.org")
        self.assertRedirects(inexistente, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_token_de_recuperacao_permite_definir_nova_senha(self):
        self.solicitar()
        primeira_etapa = self.client.get(self.caminho_recuperacao())
        self.assertEqual(primeira_etapa.status_code, 302)

        nova_senha = "NovaSenhaForte456!"
        response = self.client.post(
            primeira_etapa.url,
            {"new_password1": nova_senha, "new_password2": nova_senha},
        )
        self.usuario.refresh_from_db()

        self.assertRedirects(response, reverse("password_reset_complete"))
        self.assertTrue(self.usuario.check_password(nova_senha))

    def test_token_invalido_nao_permite_alterar_senha(self):
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": "token-invalido"},
            )
        )
        self.usuario.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inválido ou expirou")
        self.assertTrue(self.usuario.check_password(self.senha_inicial))

    def test_emails_de_recuperacao_sao_trilingues(self):
        casos = (
            ("/senha/esqueci/", "Redefinir minha senha", "ignore esta mensagem"),
            ("/es/senha/esqueci/", "Redefinir mi contraseña", "ignore este mensaje"),
            ("/en/senha/esqueci/", "Reset my password", "ignore this message"),
        )
        for caminho, cta, aviso in casos:
            with self.subTest(caminho=caminho):
                mail.outbox.clear()
                response = self.solicitar(caminho=caminho)
                self.assertEqual(response.status_code, 302)
                html = mail.outbox[0].alternatives[0].content
                self.assertIn(cta, html)
                self.assertIn(aviso, html)


class ConfirmacaoEmailPendenteMigrationTests(TransactionTestCase):
    migrate_from = ("praticas", "0015_lote2_marcos_normativos")
    migrate_to = ("praticas", "0016_confirmacao_email_pendente")

    def test_migration_preserva_estado_das_contas_existentes_sem_criar_pendencias(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        apps_anteriores = executor.loader.project_state([self.migrate_from]).apps
        UserAnterior = apps_anteriores.get_model("auth", "User")
        UserAnterior.objects.create(username="ativa-anterior", is_active=True)
        UserAnterior.objects.create(username="inativa-anterior", is_active=False)

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        apps_atuais = executor.loader.project_state([self.migrate_to]).apps
        UserAtual = apps_atuais.get_model("auth", "User")
        PendenciaAtual = apps_atuais.get_model(
            "praticas", "ConfirmacaoEmailPendente"
        )

        self.assertTrue(UserAtual.objects.get(username="ativa-anterior").is_active)
        self.assertFalse(UserAtual.objects.get(username="inativa-anterior").is_active)
        self.assertEqual(PendenciaAtual.objects.count(), 0)
