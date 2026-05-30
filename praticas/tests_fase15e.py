from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .forms import ExperienciaSubmissaoForm
from .models import EFS, Pais, Setor, TipoExperiencia


class RevisaoTraducaoTrilingueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil", sigla="BRA")
        EFS.objects.create(nome="Tribunal de Contas", nome_es="Tribunal de Cuentas", nome_en="Court of Accounts", sigla="TC", pais=pais)
        TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit")
        Setor.objects.create(nome="Agua", nome_es="Agua", nome_en="Water")

    def test_formulario_exibe_labels_em_ingles(self):
        with translation.override("en"):
            form = ExperienciaSubmissaoForm()

        self.assertEqual(form.fields["pais"].label, "Country")
        self.assertEqual(form.fields["titulo"].label, "Name of the good practice / initiative")
        self.assertEqual(form.fields["tipo_experiencia"].label, "Type of good practice")
        self.assertEqual(form.fields["setor"].label, "Sector")
        self.assertEqual(form.fields["contato_referencia"].label, "SAI reference contact")
        self.assertEqual(form.fields["descricao"].label, "Brief description of the good practice")
        self.assertEqual(form.fields["enfoque_justica_climatica"].label, "Climate justice link")

    def test_formulario_exibe_labels_em_espanhol(self):
        with translation.override("es"):
            form = ExperienciaSubmissaoForm()

        self.assertEqual(form.fields["pais"].label, "País")
        self.assertEqual(form.fields["titulo"].label, "Nombre de la buena práctica / iniciativa")
        self.assertEqual(form.fields["tipo_experiencia"].label, "Tipo de buena práctica")
        self.assertEqual(form.fields["contato_referencia"].label, "Contacto de referencia de la EFS")
        self.assertEqual(form.fields["descricao"].label, "Breve descripción de la buena práctica")
        self.assertEqual(form.fields["enfoque_justica_climatica"].label, "Vínculo con justicia climática")

    def test_pagina_envio_em_ingles_nao_exibe_labels_portugueses_principais(self):
        usuario = get_user_model().objects.create_user(
            username="traducao_teste",
            email="traducao_teste@example.org",
            password="teste123",
        )
        self.client.force_login(usuario)

        response = self.client.get("/en/adicionar-boa-pratica/")

        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")

        self.assertIn("SAI", conteudo)
        self.assertIn("Country", conteudo)
        self.assertIn("Name of the good practice", conteudo)
        self.assertIn("Type of good practice", conteudo)
        self.assertIn("Sector", conteudo)
        self.assertIn("SAI reference contact", conteudo)
        self.assertIn("Reference institutional e-mail", conteudo)
        self.assertIn("Brief description of the good practice", conteudo)
        self.assertIn("Climate justice link", conteudo)
        self.assertIn("Year", conteudo)

        self.assertNotIn("Nome da boa prática", conteudo)
        self.assertNotIn("Tipo de boa prática", conteudo)
        self.assertNotIn("Resumo da boa prática", conteudo)
        self.assertNotIn("Vínculo com justiça climática", conteudo)
