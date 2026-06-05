from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class PreparacaoTesteExternoTests(TestCase):
    def test_documentos_de_teste_externo_existem(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/teste_externo/roteiro_teste_externo.md",
            "docs/teste_externo/checklist_teste_externo.md",
            "docs/teste_externo/perguntas_feedback_teste_externo.md",
            "docs/teste_externo/preparacao_ambiente_teste_externo.md",
            "docs/fase15p_preparacao_teste_externo.md",
        ]

        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)

    def test_comando_exibir_roteiro_teste_externo_executa(self):
        call_command("exibir_roteiro_teste_externo", verbosity=0)
