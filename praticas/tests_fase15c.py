from django.test import TestCase
from django.urls import reverse

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

        experiencia = Experiencia.objects.create(
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
        experiencia.temas_transversais.add(tema)
        experiencia.normas_internacionais.add(norma)
        experiencia.dimensoes_consideradas.add(dimensao)
        experiencia.grupos_vulneraveis.add(grupo)

    def test_ficha_usa_breve_descricao_e_campos_de_justica_climatica(self):
        experiencia = Experiencia.objects.get(titulo="Auditoria climatica exemplo")
        response = self.client.get(reverse("detalhe_experiencia", args=[experiencia.pk]))

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        # O idioma padrão do teste pode variar entre pt-br, es e en.
        # Além disso, acentos podem aparecer como entidades HTML.
        # Por isso validamos alternativas equivalentes por idioma.
        self.assertTrue(
            "Breve descri" in conteudo
            or "Brief description" in conteudo
        )
        self.assertTrue(
            "problema clim" in conteudo
            or "climate problem" in conteudo
        )
        self.assertTrue(
            "Riscos clim" in conteudo
            or "Riesgos clim" in conteudo
            or "climate risks" in conteudo
        )
        self.assertTrue(
            "enfoque de justi" in conteudo
            or "justice approach" in conteudo
        )
        self.assertTrue(
            "Dimens" in conteudo
            or "Dimensions" in conteudo
        )
        self.assertTrue(
            "metodologias" in conteudo
            or "metodolog&iacute;as" in conteudo
            or "methodologies" in conteudo
        )
        self.assertNotIn("Insumo para", conteudo)
