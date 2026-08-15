from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .forms import ExperienciaSubmissaoForm
from .models import EFS, Experiencia, Pais, Setor, TemaTransversal


class Fase16FRetroalimentacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("aplicar_retroalimentacao_formulario", verbosity=0)

    def test_taxonomias_da_retroalimentacao_estao_disponiveis(self):
        self.assertTrue(Pais.objects.filter(sigla="BLZ", nome_es="Bélice").exists())
        self.assertTrue(Pais.objects.filter(sigla="OUTRO", nome_es="Otro").exists())

        # A partir da Fase 16H, a lista é trilíngue:
        # nome = português, nome_es = espanhol, nome_en = inglês.
        self.assertTrue(
            EFS.objects.filter(
                sigla="ASF",
                nome__icontains="Federação do México",
                nome_es__icontains="Federación de México",
                nome_en__icontains="Federation of Mexico",
            ).exists()
        )
        self.assertTrue(
            EFS.objects.filter(
                sigla="TCE-PA",
                nome__icontains="Estado do Pará",
                nome_es__icontains="Estado de Pará",
                nome_en__icontains="State of Pará",
            ).exists()
        )
        self.assertTrue(Setor.objects.filter(nome="Outro", nome_es="Otro", nome_en="Other").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Crianças", nome_es__icontains="Niños").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Idosos", nome_en="Older persons").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Outro").exists())

    def test_formulario_tem_explica_criterios_e_informacoes_adicionais(self):
        form = ExperienciaSubmissaoForm()
        self.assertIn("informacoes_adicionais", form.fields)
        self.assertIn("Critérios não são apenas normas", form.fields["criterios_utilizados"].help_text)
        self.assertIn("abordagem geral", form.fields["metodologia"].help_text)
        self.assertIn(
            "fontes de informação ou evidências",
            form.fields["ferramentas_utilizadas"].help_text,
        )
        self.assertEqual(form.fields["informacoes_adicionais"].label, "Informações adicionais")

    def test_modelo_exibe_informacoes_adicionais(self):
        experiencia = Experiencia(informacoes_adicionais="Observação complementar")
        self.assertEqual(experiencia.informacoes_adicionais_exibicao, "Observação complementar")

    def test_tela_envio_renderiza_campo_final(self):
        user = User.objects.create_user(username="autor", password="Teste@123", email="autor@efs.org")
        self.client.force_login(user)
        resposta = self.client.get("/adicionar-boa-pratica/")
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Informações adicionais")
        self.assertContains(resposta, 'name="informacoes_adicionais"')
