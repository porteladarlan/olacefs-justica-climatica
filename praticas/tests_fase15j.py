from django.test import TestCase


class ConteudoInstitucionalNormasTests(TestCase):
    def test_banco_tecnico_em_ingles_reforca_curadoria_tecnica(self):
        response = self.client.get('/en/banco-tecnico/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Technical and normative resources', conteudo)
        self.assertIn('Content under technical curation', conteudo)
        self.assertIn('The area is ready, but the final collection is not closed', conteudo)
        self.assertIn('Relationship with the catalog', conteudo)
        self.assertNotIn('MVP', conteudo)

    def test_banco_tecnico_em_espanhol_reforca_area_em_preparacao(self):
        response = self.client.get('/es/banco-tecnico/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Recursos técnicos y normativos', conteudo)
        self.assertIn('Contenido en curaduría técnica', conteudo)
        self.assertIn('En preparación', conteudo)
        self.assertNotIn('MVP', conteudo)

    def test_normas_internacionais_em_ingles_nao_parece_repositorio_juridico(self):
        response = self.client.get('/en/normas-internacionais/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('Normative references as anchors for good practices', conteudo)
        self.assertIn('The platform is not a legal repository', conteudo)
        self.assertIn('No frameworks registered yet', conteudo)

    def test_sobre_reforca_relacao_guia_e_plataforma(self):
        response = self.client.get('/sobre/')
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode('utf-8')

        self.assertIn('A Guia orienta; a plataforma demonstra', conteudo)
        self.assertIn('Conectar marcos', conteudo)
        self.assertNotIn('MVP', conteudo)
