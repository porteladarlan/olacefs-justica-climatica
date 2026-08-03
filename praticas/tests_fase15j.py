from django.test import TestCase


class ConteudoInstitucionalNormasTests(TestCase):
    def test_banco_tecnico_em_ingles_informa_preparacao_institucional(self):
        response = self.client.get('/en/banco-tecnico/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Technical and normative resources', conteudo)
        self.assertIn('The Technical Bank is being prepared.', conteudo)
        self.assertIn('Documents and references will be published after institutional curation is complete.', conteudo)
        self.assertNotIn('publication or origin marker', conteudo)
        self.assertEqual(response.context['total_resultados'], 0)
        self.assertNotIn('MVP', conteudo)

    def test_banco_tecnico_em_espanhol_reforca_area_em_preparacao(self):
        response = self.client.get('/es/banco-tecnico/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Recursos t&eacute;cnicos y normativos', conteudo)
        self.assertIn('El Banco T&eacute;cnico est&aacute; en preparaci&oacute;n.', conteudo)
        self.assertIn('Los documentos y referencias se publicar&aacute;n despu&eacute;s de concluir la curadur&iacute;a institucional.', conteudo)
        self.assertNotIn('marcador de publicaci&oacute;n u origen', conteudo)
        self.assertEqual(response.context['total_resultados'], 0)
        self.assertNotIn('MVP', conteudo)

    def test_normas_internacionais_em_ingles_usa_biblioteca_e_contador_real(self):
        response = self.client.get('/en/normas-internacionais/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Normative library', conteudo)
        self.assertIn('Normative frameworks for climate justice audits', conteudo)
        self.assertIn('No normative framework found', conteudo)
        self.assertEqual(response.context['total_resultados'], 0)
        self.assertNotIn('34 results', conteudo)

    def test_sobre_reforca_relacao_guia_e_plataforma(self):
        response = self.client.get('/sobre/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('A Guia orienta; a plataforma demonstra', conteudo)
        self.assertIn('Conectar marcos', conteudo)
        self.assertNotIn('MVP', conteudo)
