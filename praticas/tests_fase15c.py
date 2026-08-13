from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import (
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class FichaBoaPraticaRetroalimentacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA")
        efs = EFS.objects.create(nome="Tribunal de Contas", nome_es="Tribunal de Cuentas", nome_en="Court of Accounts", sigla="TC", pais=pais)
        tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoria", nome_en="Audit")
        setor = Setor.objects.create(nome="Agua", nome_es="Agua", nome_en="Water")
        tema = TemaTransversal.objects.create(nome="Genero", nome_es="Genero", nome_en="Gender")
        norma = NormaInternacional.objects.create(nome="Acordo de Paris", nome_es="Acuerdo de Paris", nome_en="Paris Agreement")
        dimensao = DimensaoJusticaClimatica.objects.create(nome="Participacao", nome_es="Participacion", nome_en="Participation")
        grupo = GrupoVulneravel.objects.create(nome="Povos indigenas", nome_es="Pueblos indigenas", nome_en="Indigenous peoples")

        cls.experiencia = Experiencia.objects.create(
            titulo="Auditoria climatica exemplo",
            titulo_es="Auditoria climatica ejemplo",
            titulo_en="Climate audit example",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            contato_referencia="Contato",
            email_contato="contato@example.org",
            pessoa_responsavel="Pessoa responsavel",
            descricao="Breve descricao da experiencia.",
            descricao_es="Breve descripcion de la experiencia.",
            descricao_en="Brief description of the experience.",
            problema_climatico="Secas e inseguranca hidrica.",
            problema_climatico_es="Sequias e inseguridad hidrica.",
            problema_climatico_en="Droughts and water insecurity.",
            riscos_climaticos="Risco de desabastecimento.",
            riscos_climaticos_es="Riesgo de desabastecimiento.",
            riscos_climaticos_en="Risk of supply disruption.",
            enfoque_justica_climatica="Sim, com foco em comunidades vulneraveis.",
            enfoque_justica_climatica_es="Si, con foco en comunidades vulnerables.",
            enfoque_justica_climatica_en="Yes, focused on vulnerable communities.",
            perguntas_chave="Pergunta de auditoria.",
            criterios_utilizados="Criterio utilizado.",
            metodologia="Metodologia aplicada.",
            ferramentas_utilizadas="Instrumento metodologico.",
            resultados="Resultado apresentado.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.experiencia.temas_transversais.add(tema)
        cls.experiencia.normas_internacionais.add(norma)
        cls.experiencia.dimensoes_consideradas.add(dimensao)
        cls.experiencia.grupos_vulneraveis.add(grupo)

    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate()

    def test_ficha_usa_breve_descricao_e_campos_de_justica_climatica(self):
        experiencia = Experiencia.objects.get(titulo="Auditoria climatica exemplo")
        response = self.client.get(reverse("detalhe_experiencia", args=[experiencia.pk]))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        # Validação estrutural: evita falhas por idioma ativo, entidades HTML
        # ou escolha de campos traduzidos no template.
        self.assertIn("detail-layout-card", conteudo)
        self.assertIn("headingJustica", conteudo)
        self.assertIn("collapseJustica", conteudo)
        self.assertIn("headingAuditoria", conteudo)
        self.assertIn("collapseAuditoria", conteudo)

        # Validação de que a ficha exibe os dados principais da experiência.
        self.assertIn("Auditoria climatica", conteudo)
        self.assertIn("TC", conteudo)
        self.assertIn("Brasil", conteudo)
        self.assertIn("2026", conteudo)
        self.assertIn("contato@example.org", conteudo)

        # Validação dos novos blocos da retroalimentação sem fixar idioma.
        self.assertTrue(
            "Breve descri" in conteudo
            or "Brief description" in conteudo
        )
        self.assertTrue(
            "V&iacute;nculo com justi" in conteudo
            or "V&iacute;nculo con justicia" in conteudo
            or "Climate justice link" in conteudo
        )
        self.assertTrue(
            "metodologias" in conteudo
            or "metodolog&iacute;as" in conteudo
            or "methodologies" in conteudo
        )

        # A retroalimentação pediu remover a referência visual à Guia.
        self.assertNotIn("Insumo para", conteudo)

    def test_ficha_publica_exibe_contato_no_final_da_coluna_lateral(self):
        response = self.client.get(
            reverse("detalhe_experiencia", args=[self.experiencia.pk])
        )
        conteudo = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Pessoa responsável", conteudo)
        self.assertNotIn("Persona responsable", conteudo)
        self.assertNotIn("Responsible person", conteudo)
        self.assertIn('id="experience-contact"', conteudo)
        self.assertIn("Contato", conteudo)
        self.assertIn("contato@example.org", conteudo)
        self.assertIn('href="mailto:contato@example.org"', conteudo)
        self.assertNotIn("Pessoa responsavel", conteudo)
        self.assertLess(
            conteudo.index("experience-vulnerable-groups"),
            conteudo.index("experience-contact"),
        )
        self.assertLess(
            conteudo.index("experience-contact"),
            conteudo.index(
                '<form method="post"',
                conteudo.index("experience-contact"),
            ),
        )

    def test_ficha_publica_usa_pessoa_responsavel_como_fallback_legado(self):
        self.experiencia.contato_referencia = ""
        self.experiencia.email_contato = ""
        self.experiencia.pessoa_responsavel = "Responsável legado"
        self.experiencia.save(
            update_fields=[
                "contato_referencia",
                "email_contato",
                "pessoa_responsavel",
            ]
        )

        response = self.client.get(
            reverse("detalhe_experiencia", args=[self.experiencia.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="experience-contact"')
        self.assertContains(response, "Responsável legado")
        self.assertNotContains(response, "mailto:")

    def test_ficha_publica_oculta_contato_quando_todos_os_dados_estao_vazios(self):
        self.experiencia.contato_referencia = ""
        self.experiencia.email_contato = ""
        self.experiencia.pessoa_responsavel = ""
        self.experiencia.save(
            update_fields=[
                "contato_referencia",
                "email_contato",
                "pessoa_responsavel",
            ]
        )

        response = self.client.get(
            reverse("detalhe_experiencia", args=[self.experiencia.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="experience-contact"')
        self.assertNotContains(response, "mailto:")

    def test_ficha_publica_nao_cria_mailto_para_email_invalido(self):
        self.experiencia.contato_referencia = "Contato sem e-mail válido"
        self.experiencia.email_contato = "email-invalido"
        self.experiencia.save(
            update_fields=["contato_referencia", "email_contato"]
        )

        response = self.client.get(
            reverse("detalhe_experiencia", args=[self.experiencia.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "email-invalido")
        self.assertNotContains(response, 'href="mailto:email-invalido"')

    def test_ficha_publica_traduz_rotulo_de_contato(self):
        casos = (
            (f"/experiencias/{self.experiencia.pk}/", "Contato"),
            (f"/es/experiencias/{self.experiencia.pk}/", "Contacto"),
            (f"/en/experiencias/{self.experiencia.pk}/", "Contact"),
        )

        for caminho, rotulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                contato = response.content.decode("utf-8").split(
                    'id="experience-contact"', 1
                )[1].split("</section>", 1)[0]
                self.assertIn(rotulo, contato)
