from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Exibe os materiais disponíveis para conduzir teste externo da plataforma."

    ARQUIVOS = [
        "docs/teste_externo/roteiro_teste_externo.md",
        "docs/teste_externo/checklist_teste_externo.md",
        "docs/teste_externo/perguntas_feedback_teste_externo.md",
        "docs/teste_externo/preparacao_ambiente_teste_externo.md",
    ]

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)

        self.stdout.write(self.style.MIGRATE_HEADING("Materiais para teste externo da plataforma"))
        self.stdout.write("")

        for relativo in self.ARQUIVOS:
            caminho = base_dir / relativo
            if caminho.exists():
                self.stdout.write(self.style.SUCCESS(f"OK  {relativo}"))
            else:
                self.stdout.write(self.style.WARNING(f"NÃO ENCONTRADO  {relativo}"))

        self.stdout.write("")
        self.stdout.write("Sugestão de uso:")
        self.stdout.write("1. Envie o roteiro para as pessoas testadoras.")
        self.stdout.write("2. Use o checklist para validação interna.")
        self.stdout.write("3. Cole as perguntas de feedback em um formulário ou planilha.")
        self.stdout.write("4. Antes do teste, rode as auditorias e carregue dados demonstrativos.")
