from django.core.management import call_command
from django.test import TestCase


class ValidacaoPontaAPontaTests(TestCase):
    def test_comando_validacao_ponta_a_ponta_executa_sem_erro(self):
        call_command("validar_fluxo_ponta_a_ponta", verbosity=0)
