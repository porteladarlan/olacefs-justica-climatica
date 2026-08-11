import os
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Audita a prontidão técnica do ambiente Django carregado."

    DOCS = [
        "docs/ambiente/checklist_ambiente_producao.md",
        "docs/ambiente/variaveis_ambiente_recomendadas.md",
        "docs/ambiente/guia_deploy_migracao_futura.md",
        "docs/ambiente/limitacoes_ambiente_gratuito.md",
    ]

    AMBIENTES_VALIDOS = {"development", "test", "staging", "production"}
    AMBIENTES_IMPLANTADOS = {"staging", "production"}
    PROXY_SSL_ESPERADO = ("HTTP_X_FORWARDED_PROTO", "https")

    PENDENCIAS_EXTERNAS = [
        "Definição da infraestrutura institucional.",
        "Provisionamento e operação do PostgreSQL institucional.",
        "Storage persistente para anexos.",
        "Backup e restauração testados.",
        "Domínio oficial e terminação TLS.",
        "Logs centralizados e monitoramento.",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro somente se encontrar falha crítica de código/configuração.",
        )

    def _registrar_verificacao(self, condicao, sucesso, falha, falhas_criticas):
        if condicao:
            self.stdout.write(self.style.SUCCESS(f"  OK  {sucesso}"))
            return

        falhas_criticas.append(falha)
        self.stdout.write(self.style.ERROR(f"  FALHA  {falha}"))

    def handle(self, *args, **options):
        falhas_criticas = []
        avisos_operacionais = []
        base_dir = Path(settings.BASE_DIR)
        ambiente = getattr(settings, "DJANGO_ENV", "development")
        ambiente_implantado = ambiente in self.AMBIENTES_IMPLANTADOS
        banco = settings.DATABASES.get("default", {})
        banco_engine = banco.get("ENGINE", "")

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Checagem de prontidão técnica do ambiente"
            )
        )
        self.stdout.write("")

        self.stdout.write(self.style.MIGRATE_LABEL("1. Documentação técnica"))
        for relativo in self.DOCS:
            caminho = base_dir / relativo
            self._registrar_verificacao(
                caminho.exists(),
                relativo,
                f"Documento obrigatório não encontrado: {relativo}",
                falhas_criticas,
            )

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Ambiente carregado"))
        self.stdout.write(f"  DJANGO_ENV = {ambiente}")
        self.stdout.write(f"  DEBUG = {settings.DEBUG}")
        self.stdout.write(
            f"  Banco default = {banco_engine or 'não identificado'}"
        )
        self._registrar_verificacao(
            ambiente in self.AMBIENTES_VALIDOS,
            "DJANGO_ENV reconhecido.",
            f"DJANGO_ENV inválido: {ambiente}",
            falhas_criticas,
        )

        if ambiente_implantado:
            self.stdout.write(
                self.style.SUCCESS(
                    "  MODO  staging/production: validações de implantação ativas."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "  MODO  ambiente local/teste: SQLite e defaults locais são permitidos."
                )
            )
            if banco_engine.endswith("sqlite3"):
                self.stdout.write(
                    self.style.SUCCESS("  OK  SQLite permitido neste ambiente.")
                )
            self.stdout.write(
                "  INFO  Variáveis e infraestrutura de produção não são exigidas."
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_LABEL("3. Configuração crítica de implantação")
        )
        if ambiente_implantado:
            origens_csrf = settings.CSRF_TRUSTED_ORIGINS
            proxy_ssl = getattr(settings, "SECURE_PROXY_SSL_HEADER", None)
            try:
                secret_key_configurada = bool(settings.SECRET_KEY)
            except ImproperlyConfigured:
                secret_key_configurada = False
            proxy_solicitado = os.environ.get(
                "TRUST_X_FORWARDED_PROTO", ""
            ).strip().lower() in {"true", "1", "yes"}

            verificacoes = [
                (
                    settings.DEBUG is False,
                    "DEBUG=False.",
                    "DEBUG deve permanecer False em staging/production.",
                ),
                (
                    secret_key_configurada,
                    "SECRET_KEY carregada (valor não exibido).",
                    "SECRET_KEY não configurada.",
                ),
                (
                    bool(settings.ALLOWED_HOSTS),
                    "ALLOWED_HOSTS explícito.",
                    "ALLOWED_HOSTS deve ser explícito em staging/production.",
                ),
                (
                    bool(origens_csrf)
                    and all(
                        origem.startswith("https://") for origem in origens_csrf
                    ),
                    "CSRF_TRUSTED_ORIGINS contém somente HTTPS.",
                    "CSRF_TRUSTED_ORIGINS deve conter origens HTTPS explícitas.",
                ),
                (
                    bool(banco_engine) and not banco_engine.endswith("sqlite3"),
                    "DATABASE_URL/banco carregado não usa SQLite.",
                    "DATABASE_URL deve configurar banco não SQLite.",
                ),
                (
                    settings.SESSION_COOKIE_SECURE is True,
                    "SESSION_COOKIE_SECURE=True.",
                    "SESSION_COOKIE_SECURE deve ser True.",
                ),
                (
                    settings.CSRF_COOKIE_SECURE is True,
                    "CSRF_COOKIE_SECURE=True.",
                    "CSRF_COOKIE_SECURE deve ser True.",
                ),
            ]
            for condicao, sucesso, falha in verificacoes:
                self._registrar_verificacao(
                    condicao, sucesso, falha, falhas_criticas
                )

            if proxy_ssl is None and not proxy_solicitado:
                self.stdout.write(
                    "  INFO  Proxy SSL desabilitado; habilitar somente com proxy confiável."
                )
            else:
                self._registrar_verificacao(
                    proxy_solicitado
                    and tuple(proxy_ssl or ()) == self.PROXY_SSL_ESPERADO,
                    "Proxy SSL habilitado explicitamente e com header esperado.",
                    "Proxy SSL deve existir somente quando "
                    "TRUST_X_FORWARDED_PROTO estiver explicitamente habilitada.",
                    falhas_criticas,
                )
        else:
            self.stdout.write(
                "  INFO  Validações de staging/production não se aplicam ao ambiente local/teste."
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_LABEL("4. HTTPS e HSTS dependentes da infraestrutura")
        )
        if ambiente_implantado:
            if settings.SECURE_SSL_REDIRECT:
                self.stdout.write(self.style.SUCCESS("  OK  SECURE_SSL_REDIRECT ativo."))
            else:
                aviso = (
                    "SECURE_SSL_REDIRECT ainda não habilitado; confirmar HTTPS e rollback."
                )
                avisos_operacionais.append(aviso)
                self.stdout.write(self.style.WARNING(f"  AVISO  {aviso}"))

            if settings.SECURE_HSTS_SECONDS > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  OK  HSTS ativo por {settings.SECURE_HSTS_SECONDS} segundos."
                    )
                )
            else:
                aviso = "HSTS ainda não habilitado; depende de HTTPS definitivo."
                avisos_operacionais.append(aviso)
                self.stdout.write(self.style.WARNING(f"  AVISO  {aviso}"))
        else:
            self.stdout.write(
                "  INFO  HTTPS/HSTS não são exigidos pelo gate local/teste."
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                "5. Pendências institucionais externas (não são falhas de código)"
            )
        )
        for pendencia in self.PENDENCIAS_EXTERNAS:
            self.stdout.write(f"  PENDENTE  {pendencia}")

        self.stdout.write("")
        if falhas_criticas:
            self.stdout.write(
                self.style.ERROR(
                    f"Checagem concluída com {len(falhas_criticas)} "
                    "falha(s) crítica(s)."
                )
            )
            for falha in falhas_criticas:
                self.stdout.write(self.style.ERROR(f"- {falha}"))
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS("Checagem concluída sem falhas críticas.")
            )

        if avisos_operacionais:
            self.stdout.write(
                self.style.WARNING(
                    f"{len(avisos_operacionais)} aviso(s) operacional(is) "
                    "não bloqueante(s); validar com a infraestrutura real."
                )
            )
