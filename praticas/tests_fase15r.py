from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class ConsolidacaoVersaoValidacaoTests(TestCase):
    def test_documentos_de_release_existem(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/release/versao_validacao_retroalimentacao.md",
            "docs/release/checklist_final_validacao.md",
            "docs/release/roteiro_apresentacao_plataforma.md",
            "docs/release/pendencias_e_proximos_passos.md",
            "docs/fase15r_consolidacao_versao_validacao.md",
        ]

        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)

    def test_comando_validar_release_validacao_executa(self):
        call_command("validar_release_validacao", verbosity=0)
