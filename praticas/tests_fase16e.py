import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings


class CriarUsuariosTesteCommandTests(TestCase):
    @override_settings(DEBUG=False)
    def test_bloqueia_em_ambiente_nao_debug_sem_variavel_de_permissao(self):
        os.environ.pop("PERMITIR_CRIACAO_USUARIOS_TESTE", None)

        with self.assertRaises(CommandError):
            call_command("criar_usuarios_teste", confirmar=True, stdout=StringIO())

    @override_settings(DEBUG=False)
    def test_cria_usuarios_de_teste_quando_variavel_autoriza(self):
        ambiente = {
            "PERMITIR_CRIACAO_USUARIOS_TESTE": "true",
            "SENHA_USUARIOS_TESTE": "SenhaTemporaria@2026",
            "USUARIO_TESTE_ADMIN_EMAIL": "admin.teste@example.org",
            "USUARIO_TESTE_REVISOR_EMAIL": "revisor.teste@example.org",
            "USUARIO_TESTE_COMUM_EMAIL": "usuario.teste@example.org",
        }

        with patch.dict(os.environ, ambiente, clear=False):
            saida = StringIO()
            call_command(
                "criar_usuarios_teste",
                confirmar=True,
                resetar_senha=True,
                stdout=saida,
            )

        admin = User.objects.get(username="admin_teste")
        revisor = User.objects.get(username="revisor_teste")
        usuario = User.objects.get(username="usuario_teste")

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.email, "admin.teste@example.org")
        self.assertTrue(admin.check_password("SenhaTemporaria@2026"))

        self.assertTrue(revisor.is_staff)
        self.assertFalse(revisor.is_superuser)
        self.assertEqual(revisor.email, "revisor.teste@example.org")
        self.assertTrue(revisor.check_password("SenhaTemporaria@2026"))

        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertEqual(usuario.email, "usuario.teste@example.org")
        self.assertTrue(usuario.check_password("SenhaTemporaria@2026"))

    @override_settings(DEBUG=True)
    def test_em_debug_pode_executar_sem_variavel_de_render(self):
        os.environ.pop("PERMITIR_CRIACAO_USUARIOS_TESTE", None)

        saida = StringIO()
        call_command("criar_usuarios_teste", confirmar=True, stdout=saida)

        self.assertTrue(User.objects.filter(username="admin_teste").exists())
        self.assertTrue(User.objects.filter(username="revisor_teste").exists())
        self.assertTrue(User.objects.filter(username="usuario_teste").exists())
