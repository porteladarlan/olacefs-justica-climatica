import os
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria usuários temporários de teste para validação controlada da plataforma."

    USUARIOS_PADRAO = [
        {
            "username": "admin_teste",
            "email_env": "USUARIO_TESTE_ADMIN_EMAIL",
            "email_default": "admin.teste@olacefs.local",
            "is_staff": True,
            "is_superuser": True,
            "descricao": "Administrador de teste",
        },
        {
            "username": "revisor_teste",
            "email_env": "USUARIO_TESTE_REVISOR_EMAIL",
            "email_default": "revisor.teste@olacefs.local",
            "is_staff": True,
            "is_superuser": False,
            "descricao": "Revisor de teste",
        },
        {
            "username": "usuario_teste",
            "email_env": "USUARIO_TESTE_COMUM_EMAIL",
            "email_default": "usuario.teste@olacefs.local",
            "is_staff": False,
            "is_superuser": False,
            "descricao": "Usuário comum de teste",
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma explicitamente a criação/atualização dos usuários de teste.",
        )
        parser.add_argument(
            "--resetar-senha",
            action="store_true",
            help="Redefine a senha também para usuários já existentes.",
        )

    def handle(self, *args, **options):
        confirmar = options.get("confirmar")
        resetar_senha = options.get("resetar_senha")

        if not confirmar:
            raise CommandError(
                "Use --confirmar para evitar execução acidental deste comando."
            )

        permitido = os.environ.get("PERMITIR_CRIACAO_USUARIOS_TESTE", "").lower()
        if not settings.DEBUG and permitido not in {"1", "true", "sim", "yes"}:
            raise CommandError(
                "Criação de usuários de teste bloqueada. "
                "Defina PERMITIR_CRIACAO_USUARIOS_TESTE=true no ambiente para executar em Render/produção."
            )

        senha = os.environ.get("SENHA_USUARIOS_TESTE")
        senha_gerada = False
        if not senha:
            senha = secrets.token_urlsafe(18)
            senha_gerada = True

        self.stdout.write("Criação controlada de usuários de teste")
        self.stdout.write("Modo: validação/apresentação controlada")
        self.stdout.write("")

        for perfil in self.USUARIOS_PADRAO:
            email = os.environ.get(perfil["email_env"], perfil["email_default"])
            usuario, criado = User.objects.get_or_create(
                username=perfil["username"],
                defaults={
                    "email": email,
                    "is_staff": perfil["is_staff"],
                    "is_superuser": perfil["is_superuser"],
                    "is_active": True,
                },
            )

            usuario.email = email
            usuario.is_staff = perfil["is_staff"]
            usuario.is_superuser = perfil["is_superuser"]
            usuario.is_active = True

            if criado or resetar_senha:
                usuario.set_password(senha)
                acao_senha = "senha definida"
            else:
                acao_senha = "senha preservada"

            usuario.save()

            status = "criado" if criado else "atualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"OK  {perfil['username']} ({perfil['descricao']}) -> {status}; {acao_senha}"
                )
            )

        self.stdout.write("")
        self.stdout.write("Acessos criados/atualizados:")
        self.stdout.write("  admin_teste   -> Django Admin e painéis internos")
        self.stdout.write("  revisor_teste -> painéis de revisão da plataforma")
        self.stdout.write("  usuario_teste -> envio de boas práticas e meus envios")
        self.stdout.write("")

        if senha_gerada:
            self.stdout.write(
                self.style.WARNING(
                    "SENHA GERADA AUTOMATICAMENTE. Copie agora dos logs do Render:"
                )
            )
        else:
            self.stdout.write("Senha definida pela variável SENHA_USUARIOS_TESTE.")

        self.stdout.write(self.style.WARNING(f"Senha temporária: {senha}"))
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "Após criar os usuários, remova o comando temporário do Start Command "
                "e desative PERMITIR_CRIACAO_USUARIOS_TESTE."
            )
        )
