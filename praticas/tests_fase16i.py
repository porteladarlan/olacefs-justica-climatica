from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EFS, Experiencia, Pais, Setor, TipoExperiencia


class ExclusaoAdminBoaPraticaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.admin = cls.User.objects.create_user(
            username="admin_fase16i",
            email="admin16i@example.org",
            password="SenhaForte123!",
            is_staff=True,
        )
        cls.usuario = cls.User.objects.create_user(
            username="usuario_fase16i",
            email="usuario16i@example.org",
            password="SenhaForte123!",
            is_staff=False,
        )
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BR16I")
        cls.efs = EFS.objects.create(
            nome="Tribunal de Contas da União do Brasil",
            nome_es="Tribunal de Cuentas de la Unión de Brasil",
            nome_en="Federal Court of Accounts of Brazil",
            sigla="TCU16I",
            pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        cls.setor = Setor.objects.create(nome="Outro", nome_es="Otro", nome_en="Other")

    def criar_experiencia(self, status=None):
        kwargs = {
            "titulo": "Boa prática para exclusão",
            "titulo_es": "Buena práctica para eliminación",
            "titulo_en": "Good practice for deletion",
            "efs": self.efs,
            "pais": self.pais,
            "tipo_experiencia": self.tipo,
            "ano_execucao": 2026,
            "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
            "setor": self.setor,
            "contato_referencia": "Contato de teste",
            "email_contato": "autor16i@example.org",
            "descricao": "Registro criado para validar exclusão administrativa.",
            "descricao_es": "Registro creado para validar eliminación administrativa.",
            "descricao_en": "Record created to validate administrative deletion.",
            "enfoque_justica_climatica": "Teste.",
            "enfoque_justica_climatica_es": "Prueba.",
            "enfoque_justica_climatica_en": "Test.",
            "status_publicacao": status or Experiencia.StatusPublicacao.PUBLICADO,
        }
        if any(field.name == "informacoes_adicionais" for field in Experiencia._meta.fields):
            kwargs["informacoes_adicionais"] = ""
        return Experiencia.objects.create(**kwargs)

    def test_usuario_comum_nao_acessa_exclusao(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="usuario_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("excluir_boa_pratica", args=[experiencia.pk]))
        self.assertIn(resposta.status_code, [302, 403])
        self.assertTrue(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_staff_acessa_tela_de_confirmacao(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("excluir_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Boa prática para exclusão")
        self.assertContains(resposta, "confirmar_exclusao")

    def test_staff_exclui_boa_pratica_por_post_confirmado(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.post(
            reverse("excluir_boa_pratica", args=[experiencia.pk]),
            {"confirmar_exclusao": "sim"},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(Experiencia.objects.filter(pk=experiencia.pk).exists())

    def test_catalogo_exibe_acao_de_exclusao_para_staff(self):
        experiencia = self.criar_experiencia()
        self.client.login(username="admin_fase16i", password="SenhaForte123!")
        resposta = self.client.get(reverse("catalogo_experiencias"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, reverse("excluir_boa_pratica", args=[experiencia.pk]))
