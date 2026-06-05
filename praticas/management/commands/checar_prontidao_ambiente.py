import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Checa pontos básicos de prontidão técnica do ambiente."

    DOCS = [
        "docs/ambiente/checklist_ambiente_producao.md",
        "docs/ambiente/variaveis_ambiente_recomendadas.md",
        "docs/ambiente/guia_deploy_migracao_futura.md",
        "docs/ambiente/limitacoes_ambiente_gratuito.md",
    ]

    VARIAVEIS_RECOMENDADAS = [
        "SECRET_KEY",
        "DEBUG",
        "ALLOWED_HOSTS",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se encontrar alerta de prontidão.",
        )

    def handle(self, *args, **options):
        alertas = []
        base_dir = Path(settings.BASE_DIR)

        self.stdout.write(self.style.MIGRATE_HEADING("Checagem de prontidão técnica do ambiente"))
        self.stdout.write("")

        self.stdout.write(self.style.MIGRATE_LABEL("1. Documentação técnica"))
        for relativo in self.DOCS:
            caminho = base_dir / relativo
            if caminho.exists():
                self.stdout.write(self.style.SUCCESS(f"  OK  {relativo}"))
            else:
                alertas.append(f"Documento não encontrado: {relativo}")
                self.stdout.write(self.style.WARNING(f"  FALTA  {relativo}"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Configurações Django carregadas"))
        self.stdout.write(f"  DEBUG = {settings.DEBUG}")
        self.stdout.write(f"  ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"  Banco default = {settings.DATABASES.get('default', {}).get('ENGINE', 'não identificado')}")

        if settings.DEBUG:
            alertas.append("DEBUG está True. Para produção futura deve ser False.")

        if not settings.SECRET_KEY:
            alertas.append("SECRET_KEY não configurada.")

        if not settings.ALLOWED_HOSTS:
            alertas.append("ALLOWED_HOSTS vazio. Para produção futura deve ser restrito ao domínio oficial.")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("3. Variáveis de ambiente observadas"))
        for nome in self.VARIAVEIS_RECOMENDADAS:
            valor = os.environ.get(nome)
            if valor:
                self.stdout.write(self.style.SUCCESS(f"  OK  {nome}"))
            else:
                self.stdout.write(f"  INFO  {nome} não encontrada diretamente no ambiente. Pode estar definida em settings/default.")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("4. Lembretes para produção futura"))
        lembretes = [
            "Configurar banco persistente.",
            "Configurar storage persistente para anexos.",
            "Configurar backup e restore.",
            "Configurar domínio oficial e HTTPS.",
            "Validar permissões de staff/admin.",
            "Definir governança editorial e suporte.",
        ]
        for item in lembretes:
            self.stdout.write(f"  - {item}")

        self.stdout.write("")
        if alertas:
            self.stdout.write(self.style.WARNING(f"Checagem concluída com {len(alertas)} alerta(s)."))
            for alerta in alertas:
                self.stdout.write(self.style.WARNING(f"- {alerta}"))
            self.stdout.write("Os alertas podem ser aceitáveis em ambiente local/free, mas devem ser resolvidos antes de produção real.")
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Checagem concluída sem alertas críticos."))
