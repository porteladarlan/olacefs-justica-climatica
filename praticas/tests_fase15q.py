from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class PreparacaoAmbienteProducaoTests(TestCase):
    def test_documentos_de_ambiente_existem(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/ambiente/checklist_ambiente_producao.md",
            "docs/ambiente/variaveis_ambiente_recomendadas.md",
            "docs/ambiente/guia_deploy_migracao_futura.md",
            "docs/ambiente/limitacoes_ambiente_gratuito.md",
            "docs/fase15q_preparacao_ambiente_producao.md",
        ]

        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)

    def test_comando_checar_prontidao_ambiente_executa(self):
        call_command("checar_prontidao_ambiente", verbosity=0)
