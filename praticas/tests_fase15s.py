from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class EntregaFinalValidacaoTests(TestCase):
    def test_documentos_de_entrega_final_existem(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/release/entrega_final_validacao.md",
            "docs/release/comandos_validacao_final.md",
            "docs/fase15s_entrega_final_validacao.md",
        ]

        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)

    def test_comando_validar_entrega_final_executa(self):
        call_command("validar_entrega_final", verbosity=0)
