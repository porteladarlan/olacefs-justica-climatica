from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class ValidacaoPontaAPontaTests(TestCase):
    def test_comando_validacao_ponta_a_ponta_executa_sem_erro(self):
        saida = StringIO()
        call_command("validar_fluxo_ponta_a_ponta", falhar=True, stdout=saida, verbosity=0)
        self.assertIn("Gerenciamento de submissões", saida.getvalue())
        self.assertIn("Validação ponta a ponta concluída sem alertas.", saida.getvalue())

    def test_auditoria_de_perfis_aceita_redirecionamento_da_rota_legada(self):
        saida = StringIO()
        call_command("auditar_autenticacao_perfis", falhar=True, stdout=saida, verbosity=0)
        self.assertIn("Acesso de usuário staff ao gerenciamento", saida.getvalue())
        self.assertIn("Auditoria concluída sem alertas.", saida.getvalue())
