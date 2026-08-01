from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client, override_settings


class Command(BaseCommand):
    help = "Audita fluxos de autenticação, perfis e permissões da plataforma."

    URLS_PUBLICAS = [
        "/",
        "/catalogo/",
        "/banco-tecnico/",
        "/normas-internacionais/",
        "/sobre/",
        "/entrar/",
        "/favoritos/",
    ]

    CANDIDATOS_CADASTRO = [
        "/registrar/",
        "/cadastro/",
        "/cadastrar/",
        "/criar-conta/",
    ]

    URLS_RESTRITAS_AUTOR = [
        "/adicionar-boa-pratica/",
        "/meus-envios/",
        "/status-envio/",
    ]

    URLS_RESTRITAS_REVISAO = [
        "/painel-revisao/",
        "/painel-revisao-edicoes/",
    ]

    IDIOMAS = ["", "/en", "/es"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se encontrar comportamento suspeito.",
        )

    @override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
    def handle(self, *args, **options):
        User = get_user_model()
        senha = "SenhaTemporariaTeste123!"

        usuario_comum, _ = User.objects.get_or_create(
            username="auditoria_usuario_comum",
            defaults={
                "email": "usuario.comum@example.org",
                "is_staff": False,
                "is_superuser": False,
            },
        )
        usuario_comum.set_password(senha)
        usuario_comum.is_staff = False
        usuario_comum.is_superuser = False
        usuario_comum.save()

        usuario_staff, _ = User.objects.get_or_create(
            username="auditoria_usuario_staff",
            defaults={
                "email": "usuario.staff@example.org",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        usuario_staff.set_password(senha)
        usuario_staff.is_staff = True
        usuario_staff.is_superuser = False
        usuario_staff.save()

        alertas = []

        self.stdout.write(self.style.MIGRATE_HEADING("Auditoria de autenticação, perfis e permissões"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("1. Acesso anônimo a páginas públicas"))
        alertas.extend(self.auditar_publicas_anonimas())

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Verificação de rota de cadastro"))
        alertas.extend(self.auditar_cadastro())

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("3. Acesso anônimo a páginas restritas"))
        alertas.extend(self.auditar_restritas_anonimas())

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("4. Acesso de usuário comum"))
        alertas.extend(self.auditar_usuario_comum(usuario_comum, senha))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("5. Acesso de usuário staff/revisor"))
        alertas.extend(self.auditar_usuario_staff(usuario_staff, senha))

        self.stdout.write("")
        if alertas:
            self.stdout.write(self.style.WARNING(f"Auditoria concluída com {len(alertas)} alerta(s)."))
            for alerta in alertas:
                self.stdout.write(self.style.WARNING(f"- {alerta}"))
            self.stdout.write("")
            self.stdout.write("Nem todo alerta é erro. Use este relatório para decidir ajustes de UX, permissões ou mensagens.")
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Auditoria concluída sem alertas."))

    def caminho(self, prefixo, url):
        if prefixo:
            return f"{prefixo}{url}"
        return url

    def get(self, client, caminho):
        return client.get(caminho, HTTP_HOST="testserver")

    def auditar_publicas_anonimas(self):
        client = Client()
        alertas = []

        for prefixo in self.IDIOMAS:
            for url in self.URLS_PUBLICAS:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"  ANON {caminho} -> 200"))
                else:
                    msg = f"Página pública não retornou 200 para anônimo: {caminho} -> {response.status_code}"
                    alertas.append(msg)
                    self.stdout.write(self.style.WARNING(f"  ANON {caminho} -> {response.status_code}"))
        return alertas

    def auditar_cadastro(self):
        client = Client()
        alertas = []

        for prefixo in self.IDIOMAS:
            encontrados = []
            for url in self.CANDIDATOS_CADASTRO:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code == 200:
                    encontrados.append(caminho)
                    self.stdout.write(self.style.SUCCESS(f"  CADASTRO {caminho} -> 200"))
                elif response.status_code in [301, 302]:
                    encontrados.append(caminho)
                    self.stdout.write(self.style.SUCCESS(f"  CADASTRO {caminho} -> {response.status_code}"))
                else:
                    self.stdout.write(f"  CADASTRO {caminho} -> {response.status_code}")

            if not encontrados:
                alertas.append(f"Nenhuma rota pública de cadastro encontrada para prefixo '{prefixo or '/'}'.")

        return alertas

    def auditar_restritas_anonimas(self):
        client = Client()
        alertas = []

        urls = self.URLS_RESTRITAS_AUTOR + self.URLS_RESTRITAS_REVISAO
        for prefixo in self.IDIOMAS:
            for url in urls:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code in [302, 403]:
                    self.stdout.write(self.style.SUCCESS(f"  ANON {caminho} -> {response.status_code}"))
                elif response.status_code == 200:
                    msg = f"Página restrita retornou 200 para anônimo: {caminho}"
                    alertas.append(msg)
                    self.stdout.write(self.style.WARNING(f"  ANON {caminho} -> 200"))
                else:
                    self.stdout.write(f"  ANON {caminho} -> {response.status_code}")
        return alertas

    def auditar_usuario_comum(self, usuario, senha):
        client = Client()
        client.login(username=usuario.username, password=senha)
        alertas = []

        for prefixo in self.IDIOMAS:
            for url in self.URLS_RESTRITAS_AUTOR:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code in [200, 302]:
                    self.stdout.write(self.style.SUCCESS(f"  USER {caminho} -> {response.status_code}"))
                else:
                    msg = f"Usuário comum teve resposta inesperada em área de autor: {caminho} -> {response.status_code}"
                    alertas.append(msg)
                    self.stdout.write(self.style.WARNING(f"  USER {caminho} -> {response.status_code}"))

            for url in self.URLS_RESTRITAS_REVISAO:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code in [302, 403]:
                    self.stdout.write(self.style.SUCCESS(f"  USER {caminho} -> {response.status_code}"))
                elif response.status_code == 200:
                    msg = f"Usuário comum acessou área de revisão com 200: {caminho}"
                    alertas.append(msg)
                    self.stdout.write(self.style.WARNING(f"  USER {caminho} -> 200"))
                else:
                    self.stdout.write(f"  USER {caminho} -> {response.status_code}")

        return alertas

    def auditar_usuario_staff(self, usuario, senha):
        client = Client()
        client.login(username=usuario.username, password=senha)
        alertas = []

        for prefixo in self.IDIOMAS:
            for url in self.URLS_RESTRITAS_REVISAO:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"  STAFF {caminho} -> 200"))
                else:
                    msg = f"Usuário staff não acessou área de revisão com 200: {caminho} -> {response.status_code}"
                    alertas.append(msg)
                    self.stdout.write(self.style.WARNING(f"  STAFF {caminho} -> {response.status_code}"))

        return alertas
