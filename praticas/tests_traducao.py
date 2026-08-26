import os
from unittest.mock import patch

from django.test import TestCase
from django.http import QueryDict
from django.utils.translation import override

from .forms import ExperienciaSubmissaoForm
from .models import EFS, Experiencia, Pais, Setor, TipoExperiencia
from .services.traducao import _timeout, _traduzir_lote, traduzir_campos_experiencia


class TraducaoExperienciaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil")
        efs = EFS.objects.create(nome="EFS", nome_es="EFS", nome_en="SAI", sigla="EFS", pais=pais)
        tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit", codigo="auditoria")
        setor = Setor.objects.create(nome="Água", nome_es="Agua", nome_en="Water", codigo="agua")
        cls.experiencia = Experiencia.objects.create(
            titulo="Título original",
            descricao="Descrição original",
            enfoque_justica_climatica="Enfoque original",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            setor=setor,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            idioma_original="pt",
        )

    def test_provider_sem_endpoint_nao_finge_traducoes(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PJC_TRANSLATION_ENDPOINT", None)
            with patch("praticas.services.traducao.urlopen") as abrir:
                resultado = traduzir_campos_experiencia(self.experiencia, ("titulo",), "pt")
        abrir.assert_not_called()
        self.assertEqual(resultado, {})
        self.assertEqual(self.experiencia.titulo, "Título original")

    def test_provider_fake_faz_no_maximo_duas_chamadas_em_lote(self):
        chamadas = []

        def fake(campos, origem, destino):
            chamadas.append((campos, origem, destino))
            return {campo: f"{destino}:{texto}" for campo, texto in campos.items()}

        with patch.dict(os.environ, {"PJC_TRANSLATION_ENDPOINT": "https://translation.invalid"}, clear=False):
            with patch("praticas.services.traducao._traduzir_lote", side_effect=fake):
                resultado = traduzir_campos_experiencia(self.experiencia, ("titulo",), "pt")
        self.assertEqual(resultado["titulo_es"], "es:Título original")
        self.assertEqual(resultado["titulo_en"], "en:Título original")
        self.assertEqual(len(chamadas), 2)
        self.assertEqual({item[2] for item in chamadas}, {"es", "en"})

    def test_resposta_parcial_nao_apaga_traducao_anterior(self):
        with patch.dict(os.environ, {"PJC_TRANSLATION_ENDPOINT": "https://translation.invalid"}, clear=False):
            with patch("praticas.services.traducao._traduzir_lote", return_value={"titulo": "Título traduzido"}):
                resultado = traduzir_campos_experiencia(self.experiencia, ("titulo", "descricao"), "pt")
        self.assertEqual(resultado, {"titulo_es": "Título traduzido", "titulo_en": "Título traduzido"})

    def test_endpoint_timeout_e_token_sao_lidos_do_ambiente(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"translations": {"titulo": "Translated"}}'

        with patch.dict(os.environ, {
            "PJC_TRANSLATION_ENDPOINT": "https://translation.invalid/api",
            "PJC_TRANSLATION_TIMEOUT": "3.5",
            "PJC_TRANSLATION_TOKEN": "secret-not-logged",
        }, clear=False):
            with patch("praticas.services.traducao.urlopen", return_value=Response()) as abrir:
                resultado = _traduzir_lote({"titulo": "Título"}, "pt", "es")
        request, timeout = abrir.call_args.args[0], abrir.call_args.kwargs["timeout"]
        self.assertEqual(request.full_url, "https://translation.invalid/api")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-not-logged")
        self.assertEqual(timeout, 3.5)
        self.assertEqual(resultado["titulo"], "Translated")

    def test_timeout_invalido_volta_para_oito_segundos(self):
        with patch.dict(os.environ, {"PJC_TRANSLATION_TIMEOUT": "not-a-number"}, clear=False):
            self.assertEqual(_timeout(), 8.0)

    def test_migration_deixa_historico_sem_idioma_assumido(self):
        campo = Experiencia._meta.get_field("idioma_original")
        self.assertEqual(campo.default, "")
        self.assertTrue(campo.blank)

    def test_fallback_de_exibicao_nao_grava_no_banco(self):
        self.experiencia.titulo_es = ""
        self.experiencia.save(update_fields=["titulo_es"])
        with override("es"):
            self.assertEqual(self.experiencia.titulo_exibicao, "Título original")
        self.experiencia.refresh_from_db()
        self.assertEqual(self.experiencia.titulo_es, "")

    def test_formulario_staff_expoe_correcoes_pt_es_en_e_preserva_idioma_original(self):
        self.experiencia.titulo_es = "Título em espanhol"
        self.experiencia.titulo_en = "Title in English"
        self.experiencia.save(update_fields=["titulo_es", "titulo_en"])
        with override("es"):
            form = ExperienciaSubmissaoForm(instance=self.experiencia, permitir_traducoes=True)
        nomes = {campo.name for campo in form.translation_fields}
        self.assertIn("traducao_pt__titulo", nomes)
        self.assertIn("traducao_es__titulo", nomes)
        self.assertIn("traducao_en__titulo", nomes)
        self.assertNotIn("titulo_es", form.fields)
        self.assertNotIn("titulo_en", form.fields)
        self.assertEqual(form.initial["traducao_es__titulo"], "Título em espanhol")
        self.assertEqual(form.fields["titulo"].required, True)
        self.assertEqual(self.experiencia.idioma_original, "pt")

    def test_form_bound_compara_o_idioma_original_es_e_en(self):
        self.experiencia.idioma_original = "es"
        self.experiencia.titulo_es = "Título ES"
        self.experiencia.save(update_fields=["idioma_original", "titulo_es"])
        with override("pt"):
            sem_alteracao = ExperienciaSubmissaoForm(QueryDict("titulo=T%C3%ADtulo+ES"), instance=self.experiencia)
            alterado = ExperienciaSubmissaoForm(QueryDict("titulo=T%C3%ADtulo+ES+alterado"), instance=self.experiencia)
        self.assertNotIn("titulo", sem_alteracao.changed_data)
        self.assertIn("titulo", alterado.changed_data)

        self.experiencia.idioma_original = "en"
        self.experiencia.titulo_en = "English title"
        self.experiencia.save(update_fields=["idioma_original", "titulo_en"])
        with override("es"):
            sem_alteracao = ExperienciaSubmissaoForm(QueryDict("titulo=English+title"), instance=self.experiencia)
        self.assertNotIn("titulo", sem_alteracao.changed_data)
