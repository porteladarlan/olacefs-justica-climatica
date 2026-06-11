from django.core.management import call_command
from django.test import TestCase

from praticas.models import EFS, Pais, Setor, TemaTransversal


class RetroalimentacaoEFSOficialTests(TestCase):
    def test_comando_aplica_lista_ampliada_e_renomeia_efs_demo(self):
        brasil = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA")
        EFS.objects.create(
            sigla="TCU",
            nome="Tribunal de Contas da União",
            nome_es="Tribunal de Cuentas de la Unión",
            nome_en="Federal Court of Accounts",
            pais=brasil,
        )

        call_command("aplicar_retroalimentacao_formulario")

        self.assertTrue(EFS.objects.filter(nome="Tribunal de Cuentas de la Unión de Brasil").exists())
        self.assertFalse(EFS.objects.filter(nome="Tribunal de Contas da União").exists())
        self.assertTrue(EFS.objects.filter(nome="Auditoria General de Bélice").exists())
        self.assertTrue(EFS.objects.filter(nome="Tribunal de Cuentas del Estado de Pará").exists())
        self.assertTrue(EFS.objects.filter(nome="Otro").exists())

    def test_comando_mantem_setor_e_temas_solicitados(self):
        call_command("aplicar_retroalimentacao_formulario")

        self.assertTrue(Setor.objects.filter(nome="Outro", nome_es="Otro", nome_en="Other").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Crianças").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Idosos").exists())
        self.assertTrue(TemaTransversal.objects.filter(nome="Outro").exists())
