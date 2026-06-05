from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Valida a presença dos documentos de release da versão de validação."

    DOCUMENTOS = [
        "docs/release/versao_validacao_retroalimentacao.md",
        "docs/release/checklist_final_validacao.md",
        "docs/release/roteiro_apresentacao_plataforma.md",
        "docs/release/pendencias_e_proximos_passos.md",
        "docs/fase15r_consolidacao_versao_validacao.md",
    ]

    COMANDOS_RECOMENDADOS = [
        "python manage.py test",
        "python manage.py auditar_traducoes_trilingues",
        "python manage.py auditar_autenticacao_perfis",
        "python manage.py validar_fluxo_ponta_a_ponta",
        "python manage.py checar_prontidao_ambiente",
        "python manage.py exibir_roteiro_teste_externo",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se algum documento de release não for encontrado.",
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        faltantes = []

        self.stdout.write(self.style.MIGRATE_HEADING("Validação da release de versão de validação"))
        self.stdout.write("")

        self.stdout.write(self.style.MIGRATE_LABEL("1. Documentos de release"))
        for relativo in self.DOCUMENTOS:
            caminho = base_dir / relativo
            if caminho.exists():
                self.stdout.write(self.style.SUCCESS(f"  OK  {relativo}"))
            else:
                faltantes.append(relativo)
                self.stdout.write(self.style.WARNING(f"  FALTA  {relativo}"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Comandos recomendados antes de demonstração"))
        for comando in self.COMANDOS_RECOMENDADOS:
            self.stdout.write(f"  - {comando}")

        self.stdout.write("")
        if faltantes:
            self.stdout.write(self.style.WARNING(f"Release com {len(faltantes)} documento(s) faltante(s)."))
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Release de validação documentada com sucesso."))
