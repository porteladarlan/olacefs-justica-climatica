from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class PipelineDeployTests(SimpleTestCase):
    comandos_proibidos = (
        "carregar_dados_ficticios",
        "aplicar_retroalimentacao_formulario",
        "criar_admin_render",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.raiz_projeto = Path(settings.BASE_DIR)
        cls.build = (cls.raiz_projeto / "build.sh").read_text(encoding="utf-8")

    def test_build_executa_somente_operacoes_tecnicas(self):
        linhas_ativas = [
            linha.strip()
            for linha in self.build.splitlines()
            if linha.strip() and not linha.startswith("#!")
        ]

        self.assertEqual(
            linhas_ativas,
            [
                "set -o errexit",
                "pip install -r requirements.txt",
                "python manage.py collectstatic --no-input",
                "python manage.py migrate",
            ],
        )

    def test_build_nao_executa_operacoes_negociais(self):
        for comando in self.comandos_proibidos:
            with self.subTest(comando=comando):
                self.assertNotIn(comando, self.build)

    def test_comandos_permanecem_disponiveis_para_execucao_manual(self):
        diretorio_comandos = (
            self.raiz_projeto / "praticas" / "management" / "commands"
        )

        for comando in self.comandos_proibidos:
            with self.subTest(comando=comando):
                self.assertTrue((diretorio_comandos / f"{comando}.py").is_file())
