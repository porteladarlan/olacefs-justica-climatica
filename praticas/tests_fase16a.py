from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class PreparacaoRenderTesteExternoTests(TestCase):
    def test_documentos_render_existentes(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/render/checklist_render_teste_externo.md",
            "docs/render/comandos_pos_deploy.md",
            "docs/render/usuarios_teste.md",
            "docs/teste_externo/mensagem_envio_link_teste.md",
            "docs/fase16a_preparacao_render_teste_externo.md",
        ]

        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)

    def test_comando_preparar_checklist_render_executa(self):
        call_command("preparar_checklist_render", verbosity=0)
