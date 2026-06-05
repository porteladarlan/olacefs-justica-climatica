from django.core.management import call_command
from django.test import TestCase
from django.utils.translation import activate, deactivate

from .models import BancoTecnico, Experiencia, NormaInternacional, Pais


class DadosDemonstrativosTests(TestCase):
    def setUp(self):
        call_command("carregar_dados_ficticios", verbosity=0)

    def tearDown(self):
        deactivate()

    def test_comando_cria_oito_boas_praticas_publicadas(self):
        self.assertGreaterEqual(
            Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.PUBLICADO).count(),
            8,
        )
        self.assertTrue(
            Experiencia.objects.filter(
                titulo="Avaliação de planos locais de adaptação em zonas costeiras"
            ).exists()
        )
        self.assertTrue(
            Experiencia.objects.filter(
                titulo="Painel de priorização de auditorias climáticas em infraestrutura viária"
            ).exists()
        )

    def test_dados_demonstrativos_possuem_metadados_para_catalogo(self):
        experiencias = Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.PUBLICADO)
        for experiencia in experiencias:
            self.assertTrue(experiencia.efs_id)
            self.assertTrue(experiencia.pais_id)
            self.assertTrue(experiencia.tipo_experiencia_id)
            self.assertTrue(experiencia.setor_id)
            self.assertTrue(experiencia.descricao)
            self.assertTrue(experiencia.descricao_es)
            self.assertTrue(experiencia.descricao_en)
            self.assertTrue(experiencia.problema_climatico)
            self.assertTrue(experiencia.riscos_climaticos)
            self.assertTrue(experiencia.enfoque_justica_climatica)
            self.assertGreaterEqual(experiencia.temas_transversais.count(), 1)
            self.assertGreaterEqual(experiencia.normas_internacionais.count(), 1)
            self.assertGreaterEqual(experiencia.dimensoes_consideradas.count(), 1)

    def test_dados_demonstrativos_nao_reintroduzem_contribuicao_para_guia(self):
        self.assertFalse(
            Experiencia.objects.filter(contribui_para_guia=True).exists()
        )

    def test_taxonomias_e_recursos_tecnicos_ficam_suficientes_para_demonstracao(self):
        self.assertGreaterEqual(Pais.objects.count(), 8)
        self.assertGreaterEqual(NormaInternacional.objects.count(), 5)
        self.assertGreaterEqual(BancoTecnico.objects.count(), 4)

    def test_titulos_funcionam_em_ingles_e_espanhol(self):
        experiencia = Experiencia.objects.get(
            titulo="Auditoria da resiliência climática em obras de drenagem urbana"
        )

        activate("en")
        self.assertIn("Audit", experiencia.titulo_exibicao)

        activate("es")
        self.assertIn("Auditoría", experiencia.titulo_exibicao)
