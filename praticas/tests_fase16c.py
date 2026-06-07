from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class RevisaoSeniorSegurancaTests(TestCase):
    def test_readme_atualizado_sem_mvp_local(self):
        readme = Path(settings.BASE_DIR) / "README.md"
        self.assertTrue(readme.exists())
        conteudo = readme.read_text(encoding="utf-8")
        self.assertIn("versão de validação", conteudo.lower())
        self.assertNotIn("MVP local", conteudo)
        self.assertIn("Segurança", conteudo)

    def test_configuracoes_basicas_de_seguranca(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(settings.SECURE_REFERRER_POLICY, "strict-origin-when-cross-origin")
        self.assertGreaterEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 10 * 1024 * 1024)

    def test_alternar_favorito_nao_aceita_get(self):
        # A rota exige um ID existente para testar 405 antes de consulta de objeto.
        response = self.client.get(reverse("alternar_favorito", args=[999]))
        self.assertEqual(response.status_code, 405)

    def test_documentos_de_revisao_senior_existem(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [
            "docs/release/auditoria_senior_codigo_seguranca.md",
            "docs/ambiente/checklist_hardening_producao.md",
            "docs/release/limpeza_artefatos_recomendados.md",
        ]
        for relativo in arquivos:
            self.assertTrue((base_dir / relativo).exists(), relativo)
