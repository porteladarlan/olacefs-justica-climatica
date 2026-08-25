from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override as translation_override

from .forms import RevisaoExperienciaForm
from .models import (
    EFS,
    Experiencia,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class AjustesPlataforma1206Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pais = Pais.objects.create(nome="Brasil", sigla="BR")
        cls.efs = EFS.objects.create(nome="Tribunal de Contas", sigla="TC", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria")
        cls.setor = Setor.objects.create(nome="Infraestrutura")
        cls.tema = TemaTransversal.objects.create(nome="Direitos humanos")
        cls.norma = NormaInternacional.objects.create(nome="Acordo de Paris")
        User = get_user_model()
        cls.autor = User.objects.create_user("autor16k", "autor16k@example.org", "senha12345")
        cls.revisor = User.objects.create_user("revisor16k", "revisor16k@example.org", "senha12345", is_staff=True)

    def criar_experiencia(self, titulo="Boa prática 16K", status=Experiencia.StatusPublicacao.ENVIADO, autor=None):
        return Experiencia.objects.create(
            titulo=titulo,
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            email_contato="autor16k@example.org",
            autor=autor,
            descricao="Descrição da prática.",
            enfoque_justica_climatica="Enfoque de justiça climática.",
            status_publicacao=status,
        )

    def test_rascunho_fica_visivel_para_autor_em_meus_envios(self):
        self.criar_experiencia("Rascunho visível", Experiencia.StatusPublicacao.RASCUNHO, self.autor)
        self.client.force_login(self.autor)
        response = self.client.get(reverse("meus_envios"))
        self.assertContains(response, "Rascunho visível")

    def test_rascunho_nao_aparece_no_painel_revisao(self):
        self.criar_experiencia("Rascunho privado", Experiencia.StatusPublicacao.RASCUNHO, self.autor)
        self.criar_experiencia("Enviada ao revisor", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.get(reverse("painel_revisao"))
        self.assertNotContains(response, "Rascunho privado")
        self.assertContains(response, "Enviada ao revisor")

    def test_acoes_de_revisao_respeitam_status_da_experiencia(self):
        publicado = self.criar_experiencia("Publicada", Experiencia.StatusPublicacao.PUBLICADO)
        arquivado = self.criar_experiencia("Arquivada", Experiencia.StatusPublicacao.ARQUIVADO)
        historicos = [
            self.criar_experiencia(f"Histórico {status}", status)
            for status in (
                Experiencia.StatusPublicacao.ENVIADO,
                Experiencia.StatusPublicacao.EM_REVISAO,
                Experiencia.StatusPublicacao.APROVADO,
                Experiencia.StatusPublicacao.REJEITADO,
            )
        ]

        publicado_acoes = dict(RevisaoExperienciaForm(instance=publicado).fields["acao"].choices)
        self.assertEqual(set(publicado_acoes), {"arquivar"})

        arquivado_acoes = dict(RevisaoExperienciaForm(instance=arquivado).fields["acao"].choices)
        self.assertEqual(set(arquivado_acoes), {"publicar"})
        self.assertEqual(arquivado_acoes["publicar"], "Restaurar / Publicar")

        acoes_legadas = {
            "em_revisao",
            "aprovar",
            "publicar",
            "arquivar",
            "devolver",
            "rejeitar",
        }
        for experiencia in historicos:
            with self.subTest(status=experiencia.status_publicacao):
                self.assertEqual(
                    {value for value, _label in RevisaoExperienciaForm(instance=experiencia).fields["acao"].choices},
                    acoes_legadas,
                )

    def test_nova_submissao_descreve_publicacao_imediata_nos_tres_idiomas(self):
        self.client.force_login(self.autor)
        textos = {
            "pt-br": ("Publicar boa", "Enviar para revisão", "Somente conteúdo aprovado"),
            "es": ("Publicar buena", "Enviar para revisión", "Solo el contenido aprobado"),
            "en": ("Publish good practice", "Submit for review", "Only approved content"),
        }
        for idioma, (publicar, antigo, aprovado) in textos.items():
            with self.subTest(idioma=idioma):
                with translation_override(idioma):
                    response = self.client.get(f'{reverse("adicionar_boa_pratica")}?tipo=boa_pratica')
                self.assertContains(response, publicar)
                self.assertNotContains(response, antigo)
                self.assertNotContains(response, aprovado)

    def test_edicao_publicada_arquivada_e_rascunho_exibem_acoes_corretas(self):
        self.client.force_login(self.autor)
        publicada = self.criar_experiencia("Publicada", Experiencia.StatusPublicacao.PUBLICADO, self.autor)
        arquivada = self.criar_experiencia("Arquivada", Experiencia.StatusPublicacao.ARQUIVADO, self.autor)
        rascunho = self.criar_experiencia("Rascunho", Experiencia.StatusPublicacao.RASCUNHO, self.autor)

        publicada_response = self.client.get(reverse("editar_boa_pratica", args=[publicada.pk]))
        self.assertContains(publicada_response, "Salvar altera")
        self.assertNotContains(publicada_response, "Save draft")
        self.assertNotContains(publicada_response, "Reenviar para revis")

        arquivada_response = self.client.get(reverse("editar_boa_pratica", args=[arquivada.pk]))
        self.assertContains(arquivada_response, "continu")
        self.assertContains(arquivada_response, "arquivada")
        self.assertContains(arquivada_response, "Salvar altera")
        self.assertNotContains(arquivada_response, "Publicar boa prática")

        rascunho_response = self.client.get(reverse("editar_boa_pratica", args=[rascunho.pk]))
        self.assertContains(rascunho_response, "Salvar rascunho")
        self.assertContains(rascunho_response, "Publicar boa")

    def test_revisor_consegue_acessar_edicao_da_boa_pratica(self):
        experiencia = self.criar_experiencia("Editável pelo revisor", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(response.status_code, 200)

    def test_aprovacao_publica_no_catalogo_aberto(self):
        experiencia = self.criar_experiencia("Aprovada e publicada", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {"acao": "aprovar", "comentario_revisor": "Aprovada."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        public_response = self.client.get(reverse("catalogo_experiencias"))
        self.assertContains(public_response, "Aprovada e publicada")

    def test_autor_edita_arquivada_sem_republica_la(self):
        experiencia = self.criar_experiencia(
            "Arquivada editável", Experiencia.StatusPublicacao.ARQUIVADO, self.autor
        )
        self.client.force_login(self.autor)
        response = self.client.post(
            reverse("editar_boa_pratica", args=[experiencia.pk]),
            {
                "efs": experiencia.efs_id,
                "pais": experiencia.pais_id,
                "titulo": "Arquivada editada",
                "tipo_experiencia": experiencia.tipo_experiencia_id,
                "setor": experiencia.setor_id,
                "temas_transversais": [str(self.tema.pk)],
                "normas_internacionais": [str(self.norma.pk)],
                "contato_referencia": "Contato",
                "email_contato": experiencia.email_contato,
                "pessoa_responsavel": "Autor",
                "descricao": "Descrição atualizada.",
                "enfoque_justica_climatica": experiencia.enfoque_justica_climatica,
                "objetivo": "Objetivo",
                "perguntas_chave": "Perguntas",
                "criterios_utilizados": "Critérios",
                "metodologia": "Metodologia",
                "ferramentas_utilizadas": "Fontes",
                "resultados": "Resultados",
                "recomendacoes": "Recomendações",
                "replicabilidade": "Replicabilidade",
                "ano_execucao": experiencia.ano_execucao,
                "acao_envio": "enviar",
            },
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ARQUIVADO)
        self.assertNotContains(self.client.get(reverse("catalogo_experiencias")), "Arquivada editada")

    def test_rota_legada_redireciona_sem_criar_proposta(self):
        experiencia = self.criar_experiencia("Legada", Experiencia.StatusPublicacao.PUBLICADO, self.autor)
        self.client.force_login(self.autor)
        antes = PropostaEdicaoExperiencia.objects.count()
        url = reverse("solicitar_edicao_publicada", args=[experiencia.pk])
        self.assertRedirects(
            self.client.get(url),
            reverse("editar_boa_pratica", args=[experiencia.pk]),
        )
        self.assertRedirects(
            self.client.post(url, {}),
            reverse("editar_boa_pratica", args=[experiencia.pk]),
        )
        self.assertEqual(PropostaEdicaoExperiencia.objects.count(), antes)

        outro = get_user_model().objects.create_user("outro-legado", password="senha12345")
        self.client.force_login(outro)
        self.assertRedirects(self.client.get(url), reverse("meus_envios"))

    def test_revisor_restaura_arquivada_com_publicar(self):
        experiencia = self.criar_experiencia(
            "Arquivada restaurável", Experiencia.StatusPublicacao.ARQUIVADO, self.autor
        )
        self.client.force_login(self.revisor)
        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {"acao": "publicar", "comentario_revisor": "Restaurada."},
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        self.assertContains(self.client.get(reverse("catalogo_experiencias")), "Arquivada restaurável")
