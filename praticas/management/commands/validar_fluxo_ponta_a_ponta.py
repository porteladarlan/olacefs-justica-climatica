from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client, override_settings


class Command(BaseCommand):
    help = "Audita o fluxo funcional ponta a ponta da plataforma."

    IDIOMAS = ["", "/en", "/es"]

    URLS_FLUXO = [
        ("home", "/"),
        ("catalogo", "/catalogo/"),
        ("cadastro", "/cadastro/"),
        ("login", "/entrar/"),
        ("enviar", "/adicionar-boa-pratica/"),
        ("meus_envios", "/meus-envios/"),
        ("painel_revisao", "/painel-revisao/"),
        ("painel_revisao_edicoes", "/painel-revisao-edicoes/"),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se encontrar comportamento incompatível com o fluxo ponta a ponta.",
        )

    @override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
    def handle(self, *args, **options):
        alertas = []

        self.stdout.write(self.style.MIGRATE_HEADING("Validação funcional ponta a ponta"))
        self.stdout.write("Fluxo esperado: público consulta -> usuário autentica -> envia -> revisor acessa -> publicação aparece no catálogo.")
        self.stdout.write("")

        alertas.extend(self.validar_fluxo_publico())
        alertas.extend(self.validar_fluxo_autor())
        alertas.extend(self.validar_fluxo_revisor())
        alertas.extend(self.validar_catalogo_publico())

        self.stdout.write("")
        if alertas:
            self.stdout.write(self.style.WARNING(f"Validação concluída com {len(alertas)} alerta(s)."))
            for alerta in alertas:
                self.stdout.write(self.style.WARNING(f"- {alerta}"))
            self.stdout.write("")
            self.stdout.write("Nem todo alerta é erro. Use o relatório para decidir correções de fluxo ou UX.")
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Validação ponta a ponta concluída sem alertas."))

    def caminho(self, prefixo, url):
        return f"{prefixo}{url}" if prefixo else url

    def get(self, client, caminho):
        return client.get(caminho, HTTP_HOST="testserver")

    def criar_usuario(self, username, email, staff=False):
        User = get_user_model()
        senha = "SenhaTemporariaTeste123!"
        usuario, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": staff,
                "is_superuser": False,
            },
        )
        usuario.set_password(senha)
        usuario.email = email
        usuario.is_staff = staff
        usuario.is_superuser = False
        usuario.save()
        return usuario, senha

    def validar_fluxo_publico(self):
        alertas = []
        client = Client()

        self.stdout.write(self.style.MIGRATE_LABEL("1. Consulta pública"))

        for prefixo in self.IDIOMAS:
            for nome, url in [
                ("home", "/"),
                ("catalogo", "/catalogo/"),
                ("recursos_tecnicos", "/banco-tecnico/"),
                ("normas", "/normas-internacionais/"),
                ("sobre", "/sobre/"),
            ]:
                caminho = self.caminho(prefixo, url)
                response = self.get(client, caminho)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"  PUBLIC {caminho} -> 200"))
                else:
                    alerta = f"Consulta pública falhou em {caminho}: {response.status_code}"
                    alertas.append(alerta)
                    self.stdout.write(self.style.WARNING(f"  PUBLIC {caminho} -> {response.status_code}"))

        return alertas

    def validar_fluxo_autor(self):
        alertas = []
        client_anon = Client()

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Fluxo de autor: anônimo -> login -> áreas de envio"))

        for prefixo in self.IDIOMAS:
            for url in ["/adicionar-boa-pratica/", "/meus-envios/"]:
                caminho = self.caminho(prefixo, url)
                response = self.get(client_anon, caminho)
                if response.status_code in [302, 403]:
                    self.stdout.write(self.style.SUCCESS(f"  ANON {caminho} -> {response.status_code}"))
                else:
                    alerta = f"Área de autor deveria exigir autenticação: {caminho} -> {response.status_code}"
                    alertas.append(alerta)
                    self.stdout.write(self.style.WARNING(f"  ANON {caminho} -> {response.status_code}"))

        usuario, senha = self.criar_usuario(
            "validacao_ponta_a_ponta_autor",
            "validacao.autor@example.org",
            staff=False,
        )
        client_user = Client()
        login_ok = client_user.login(username=usuario.username, password=senha)

        if not login_ok:
            alertas.append("Login do usuário autor de validação falhou.")
            self.stdout.write(self.style.ERROR("  USER login -> falhou"))
            return alertas

        self.stdout.write(self.style.SUCCESS("  USER login -> OK"))

        for prefixo in self.IDIOMAS:
            for url in ["/adicionar-boa-pratica/", "/meus-envios/"]:
                caminho = self.caminho(prefixo, url)
                response = self.get(client_user, caminho)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"  USER {caminho} -> 200"))
                else:
                    alerta = f"Usuário autenticado não acessou área de autor: {caminho} -> {response.status_code}"
                    alertas.append(alerta)
                    self.stdout.write(self.style.WARNING(f"  USER {caminho} -> {response.status_code}"))

        return alertas

    def validar_fluxo_revisor(self):
        alertas = []

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("3. Fluxo de revisão: usuário comum bloqueado e staff autorizado"))

        usuario_comum, senha_comum = self.criar_usuario(
            "validacao_ponta_a_ponta_comum",
            "validacao.comum@example.org",
            staff=False,
        )
        client_comum = Client()
        client_comum.login(username=usuario_comum.username, password=senha_comum)

        for prefixo in self.IDIOMAS:
            for url in ["/painel-revisao/", "/painel-revisao-edicoes/"]:
                caminho = self.caminho(prefixo, url)
                response = self.get(client_comum, caminho)
                if response.status_code in [302, 403]:
                    self.stdout.write(self.style.SUCCESS(f"  USER {caminho} -> {response.status_code}"))
                else:
                    alerta = f"Usuário comum acessou área de revisão indevidamente: {caminho} -> {response.status_code}"
                    alertas.append(alerta)
                    self.stdout.write(self.style.WARNING(f"  USER {caminho} -> {response.status_code}"))

        usuario_staff, senha_staff = self.criar_usuario(
            "validacao_ponta_a_ponta_staff",
            "validacao.staff@example.org",
            staff=True,
        )
        client_staff = Client()
        client_staff.login(username=usuario_staff.username, password=senha_staff)

        for prefixo in self.IDIOMAS:
            for url in ["/painel-revisao/", "/painel-revisao-edicoes/"]:
                caminho = self.caminho(prefixo, url)
                response = self.get(client_staff, caminho)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"  STAFF {caminho} -> 200"))
                else:
                    alerta = f"Staff/revisor não acessou área de revisão: {caminho} -> {response.status_code}"
                    alertas.append(alerta)
                    self.stdout.write(self.style.WARNING(f"  STAFF {caminho} -> {response.status_code}"))

        return alertas

    def validar_catalogo_publico(self):
        alertas = []
        client = Client()

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("4. Catálogo público e dados demonstrativos"))

        try:
            from praticas.models import Experiencia
        except Exception as exc:
            alertas.append(f"Não foi possível importar Experiencia para validar catálogo: {exc}")
            return alertas

        publicados = Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.PUBLICADO).count()
        if publicados:
            self.stdout.write(self.style.SUCCESS(f"  Experiências publicadas -> {publicados}"))
        else:
            self.stdout.write(self.style.WARNING("  Experiências publicadas -> 0"))
            self.stdout.write("  Dica: rode python manage.py carregar_dados_ficticios --limpar-demo para demonstração.")

        for prefixo in self.IDIOMAS:
            caminho = self.caminho(prefixo, "/catalogo/")
            response = self.get(client, caminho)
            conteudo = response.content.decode("utf-8", errors="ignore")
            if response.status_code == 200 and ("catalog-card" in conteudo or publicados == 0):
                self.stdout.write(self.style.SUCCESS(f"  CATALOG {caminho} -> OK"))
            else:
                alerta = f"Catálogo não exibiu estrutura esperada: {caminho} -> {response.status_code}"
                alertas.append(alerta)
                self.stdout.write(self.style.WARNING(f"  CATALOG {caminho} -> alerta"))

        return alertas
