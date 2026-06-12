from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EFS, Experiencia, Pais, Setor, TemaTransversal, TipoExperiencia, NormaInternacional


class FluxoSubmissaoRevisaoAutorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.autor = cls.User.objects.create_user(
            username="autor16j",
            email="autor16j@example.org",
            password="SenhaForte123!",
        )
        cls.outro = cls.User.objects.create_user(
            username="outro16j",
            email="outro16j@example.org",
            password="SenhaForte123!",
        )
        cls.revisor = cls.User.objects.create_user(
            username="revisor16j",
            email="revisor16j@example.org",
            password="SenhaForte123!",
            is_staff=True,
        )
        cls.pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BR16J")
        cls.efs = EFS.objects.create(
            nome="Tribunal de Contas da União do Brasil",
            nome_es="Tribunal de Cuentas de la Unión de Brasil",
            nome_en="Federal Court of Accounts of Brazil",
            sigla="TCU16J",
            pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        cls.setor = Setor.objects.create(nome="Outro", nome_es="Otro", nome_en="Other")
        cls.tema = TemaTransversal.objects.create(nome="Idosos", nome_es="Personas mayores", nome_en="Older persons")
        cls.norma = NormaInternacional.objects.create(nome="Agenda 2030 — ODS 13", nome_es="Agenda 2030 — ODS 13", nome_en="2030 Agenda — SDG 13")

    def dados_validos(self, titulo="Boa prática 16J", email="autor16j@example.org"):
        return {
            "efs": self.efs.pk,
            "pais": self.pais.pk,
            "titulo": titulo,
            "tipo_experiencia": self.tipo.pk,
            "setor": self.setor.pk,
            "temas_transversais": [self.tema.pk],
            "normas_internacionais": [self.norma.pk],
            "contato_referencia": "Contato autor",
            "email_contato": email,
            "pessoa_responsavel": "Autor Teste",
            "descricao": "Descrição suficiente para teste.",
            "enfoque_justica_climatica": "Equidade e vulnerabilidades.",
            "objetivo": "Objetivo do teste.",
            "perguntas_chave": "Pergunta chave.",
            "criterios_utilizados": "Critérios de teste.",
            "metodologia": "Metodologia de teste.",
            "ferramentas_utilizadas": "Matriz de teste.",
            "resultados": "Resultados de teste.",
            "recomendacoes": "Recomendações de teste.",
            "replicabilidade": "Alta.",
            "informacoes_adicionais": "Observação adicional.",
            "ano_execucao": 2026,
            "contribui_para_guia": "on",
        }

    def test_rascunho_fica_vinculado_ao_autor_e_aparece_em_meus_envios(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos(titulo="Rascunho visível ao autor", email="email.diferente@example.org")
        dados["acao_envio"] = "rascunho"
        resposta = self.client.post(reverse("adicionar_boa_pratica"), dados)
        self.assertEqual(resposta.status_code, 302)

        experiencia = Experiencia.objects.get(titulo="Rascunho visível ao autor")
        self.assertEqual(experiencia.autor, self.autor)
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.RASCUNHO)

        resposta = self.client.get(reverse("meus_envios"))
        self.assertContains(resposta, "Rascunho visível ao autor")

    def test_rascunho_nao_aparece_para_revisor_no_painel(self):
        Experiencia.objects.create(
            autor=self.autor,
            titulo="Rascunho privado 16J",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            contato_referencia="Contato",
            email_contato="autor16j@example.org",
            descricao="Rascunho privado.",
            enfoque_justica_climatica="Equidade.",
            status_publicacao=Experiencia.StatusPublicacao.RASCUNHO,
        )
        Experiencia.objects.create(
            autor=self.autor,
            titulo="Enviado para revisão 16J",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            contato_referencia="Contato",
            email_contato="autor16j@example.org",
            descricao="Enviado para revisão.",
            enfoque_justica_climatica="Equidade.",
            status_publicacao=Experiencia.StatusPublicacao.ENVIADO,
        )
        self.client.force_login(self.revisor)
        resposta = self.client.get(reverse("painel_revisao"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Enviado para revisão 16J")
        self.assertNotContains(resposta, "Rascunho privado 16J")
        self.assertNotContains(resposta, "Rascunho")

    def test_outro_usuario_nao_acessa_edicao_do_envio_do_autor(self):
        experiencia = Experiencia.objects.create(
            autor=self.autor,
            titulo="Envio protegido 16J",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            contato_referencia="Contato",
            email_contato="autor16j@example.org",
            descricao="Envio protegido.",
            enfoque_justica_climatica="Equidade.",
            status_publicacao=Experiencia.StatusPublicacao.RASCUNHO,
        )
        self.client.force_login(self.outro)
        resposta = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse("meus_envios"))

    def test_autor_edita_sem_parametro_email_quando_possui_vinculo_autor(self):
        experiencia = Experiencia.objects.create(
            autor=self.autor,
            titulo="Envio editável 16J",
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            contato_referencia="Contato",
            email_contato="email.diferente@example.org",
            descricao="Envio editável.",
            enfoque_justica_climatica="Equidade.",
            status_publicacao=Experiencia.StatusPublicacao.RASCUNHO,
        )
        self.client.force_login(self.autor)
        resposta = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Envio editável 16J")
