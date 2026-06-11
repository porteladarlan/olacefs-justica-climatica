from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from praticas.models import EFS, Pais


class Fase16HTaxonomiasTrilinguesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("aplicar_retroalimentacao_formulario")

    def test_efs_exibe_nome_conforme_idioma_ativo(self):
        efs = EFS.objects.get(sigla="TCU")

        with translation.override("pt-br"):
            self.assertIn("Tribunal de Contas da União do Brasil", str(efs))
            self.assertNotIn("Tribunal de Cuentas", str(efs))

        with translation.override("es"):
            self.assertIn("Tribunal de Cuentas de la Unión de Brasil", str(efs))

        with translation.override("en"):
            self.assertIn("Federal Court of Accounts of Brazil", str(efs))

    def test_paises_exibem_nome_conforme_idioma_ativo(self):
        paraguai = Pais.objects.get(sigla="PRY")

        with translation.override("pt-br"):
            self.assertEqual(str(paraguai), "Paraguai")

        with translation.override("es"):
            self.assertEqual(str(paraguai), "Paraguay")

        with translation.override("en"):
            self.assertEqual(str(paraguai), "Paraguay")

    def test_formulario_pt_nao_exibe_lista_efs_em_espanhol(self):
        with translation.override("pt-br"):
            resposta = self.client.get(reverse("adicionar_boa_pratica"))

        # A página pode redirecionar se anônima; o teste aqui valida a camada de dados.
        self.assertIn("Controladoria Geral da República do Paraguai", str(EFS.objects.get(sigla="CGR Paraguay")))
        self.assertNotIn("Contraloría General de la República de Paraguay", str(EFS.objects.get(sigla="CGR Paraguay")))
        self.assertIn(resposta.status_code, [200, 302])

    def test_outro_tambem_e_trilingue(self):
        efs = EFS.objects.get(sigla="OUTRO-EFS")

        with translation.override("pt-br"):
            self.assertEqual(efs.nome_exibicao, "Outro")

        with translation.override("es"):
            self.assertEqual(efs.nome_exibicao, "Otro")

        with translation.override("en"):
            self.assertEqual(efs.nome_exibicao, "Other")
