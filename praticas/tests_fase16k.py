from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EFS, Experiencia, Pais, Setor, TipoExperiencia


class AjustesPlataforma1206Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pais = Pais.objects.create(nome="Brasil", sigla="BR")
        cls.efs = EFS.objects.create(nome="Tribunal de Contas", sigla="TC", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria")
        cls.setor = Setor.objects.create(nome="Infraestrutura")
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
