import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase
from django.utils.translation import override

from .forms import ExperienciaSubmissaoForm
from .models import EFS, Experiencia, NormaInternacional, Pais, Setor, TemaTransversal, TipoExperiencia
from .services.traducao import _timeout, _traduzir_lote, traduzir_campos_experiencia
from .views import idioma_original_interface, tentar_traduzir_experiencia


class TraducaoExperienciaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pais = Pais.objects.create(nome="Brasil", nome_es="Brasil", nome_en="Brazil")
        efs = EFS.objects.create(nome="EFS", nome_es="EFS", nome_en="SAI", sigla="EFS", pais=pais)
        tipo = TipoExperiencia.objects.create(nome="Auditoria", nome_es="Auditoría", nome_en="Audit", codigo="auditoria")
        setor = Setor.objects.create(nome="Água", nome_es="Agua", nome_en="Water", codigo="agua")
        cls.tema = TemaTransversal.objects.create(nome="Direitos humanos")
        cls.norma = NormaInternacional.objects.create(nome="Acordo de Paris")
        cls.usuario = get_user_model().objects.create_user(
            username="traducao-fluxo",
            email="traducao-fluxo@example.org",
            password="SenhaForte123!",
        )
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

    def test_provider_com_resposta_invalida_falha_abertamente(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"{\"unexpected\": true}"

        with patch.dict(os.environ, {"PJC_TRANSLATION_ENDPOINT": "https://translation.invalid"}, clear=False):
            with patch("praticas.services.traducao.urlopen", return_value=Response()):
                self.assertEqual(
                    traduzir_campos_experiencia(self.experiencia, ("titulo",), "pt"),
                    {},
                )

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

    def dados_submissao(self, titulo, descricao):
        dados = {
            "tipo_compartilhamento": "boa_pratica",
            "acao_envio": "enviar",
            "efs": str(self.experiencia.efs_id),
            "pais": str(self.experiencia.pais_id),
            "titulo": titulo,
            "tipo_experiencia": str(self.experiencia.tipo_experiencia_id),
            "tipo_auditoria": Experiencia.TipoAuditoria.DESEMPENHO,
            "setor": str(self.experiencia.setor_id),
            "temas_transversais": [str(self.tema.pk)],
            "normas_internacionais": [str(self.norma.pk)],
            "email_contato": self.usuario.email,
            "pessoa_responsavel": "Pessoa responsável",
            "descricao": descricao,
            "enfoque_justica_climatica": "Enfoque original",
            "ano_execucao": "2026",
        }
        for campo in ExperienciaSubmissaoForm.CAMPOS_TEXTUAIS_TRADUZIVEIS:
            if campo in ExperienciaSubmissaoForm.Meta.fields and campo != "perguntas_chave":
                dados[campo] = f"{campo}-original"
        dados["titulo"] = titulo
        dados["descricao"] = descricao
        return dados

    def test_submissoes_localizadas_gravam_o_original_na_familia_correta(self):
        self.client.force_login(self.usuario)
        casos = [
            ("/adicionar-boa-pratica/", "Título PT", "Descrição PT", "pt", "titulo", "descricao"),
            ("/es/adicionar-boa-pratica/", "Título ES", "Descripción ES", "es", "titulo_es", "descricao_es"),
            ("/en/adicionar-boa-pratica/", "Título EN", "Description EN", "en", "titulo_en", "descricao_en"),
        ]
        with override("pt-br"):
            for caminho, titulo, descricao, idioma, campo_titulo, campo_descricao in casos:
                with self.subTest(idioma=idioma), patch("praticas.views.tentar_traduzir_experiencia"):
                    resposta = self.client.post(caminho, self.dados_submissao(titulo, descricao))

                self.assertEqual(resposta.status_code, 302)
                experiencia = Experiencia.objects.exclude(pk=self.experiencia.pk).latest("pk")
                self.assertEqual(experiencia.idioma_original, idioma)
                self.assertEqual(getattr(experiencia, campo_titulo), titulo)
                self.assertEqual(getattr(experiencia, campo_descricao), descricao)
                for campo in ExperienciaSubmissaoForm.CAMPOS_TEXTUAIS_TRADUZIVEIS:
                    if campo not in ExperienciaSubmissaoForm.Meta.fields or campo == "perguntas_chave":
                        continue
                    valor = titulo if campo == "titulo" else descricao if campo == "descricao" else f"{campo}-original"
                    campo_familia = campo if idioma == "pt" else f"{campo}_{idioma}"
                    self.assertEqual(getattr(experiencia, campo_familia), valor)
                    for outro_idioma in ("pt", "es", "en"):
                        if outro_idioma == idioma:
                            continue
                        outro_campo = campo if outro_idioma == "pt" else f"{campo}_{outro_idioma}"
                        self.assertNotEqual(getattr(experiencia, outro_campo), valor)
                for campo in ("titulo", "titulo_es", "titulo_en"):
                    if campo != campo_titulo:
                        self.assertNotEqual(getattr(experiencia, campo), titulo, f"{idioma}: {campo}")
                for campo in ("descricao", "descricao_es", "descricao_en"):
                    if campo != campo_descricao:
                        self.assertNotEqual(getattr(experiencia, campo), descricao)

    def test_falha_do_provedor_nao_bloqueia_publicacao_pelo_fluxo_http(self):
        self.client.force_login(self.usuario)
        with patch("praticas.views.traduzir_campos_experiencia", side_effect=TimeoutError):
            with self.captureOnCommitCallbacks(execute=True):
                resposta = self.client.post(
                    "/adicionar-boa-pratica/",
                    self.dados_submissao("Título publicado", "Descrição publicada"),
                )
        self.assertEqual(resposta.status_code, 302)
        experiencia = Experiencia.objects.latest("pk")
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        self.assertEqual(experiencia.titulo, "Título publicado")

    def test_normalizacao_de_idioma_nao_trata_codigo_desconhecido_como_pt(self):
        request = type("Request", (), {"LANGUAGE_CODE": "pt-BR"})()
        self.assertEqual(idioma_original_interface(request), "pt")
        for codigo, esperado in (("pt", "pt"), ("pt-br", "pt"), ("es-MX", "es"), ("en-US", "en")):
            request.LANGUAGE_CODE = codigo
            self.assertEqual(idioma_original_interface(request), esperado)
        request.LANGUAGE_CODE = "fr"
        self.assertIsNone(idioma_original_interface(request))

    def test_tradutor_preserva_original_e_traducoes_nao_vazias(self):
        experiencia = self.experiencia
        experiencia.idioma_original = "es"
        experiencia.titulo = "Título PT manual"
        experiencia.titulo_es = "Título ES original"
        experiencia.titulo_en = ""
        experiencia.save(update_fields=["idioma_original", "titulo", "titulo_es", "titulo_en"])
        with patch(
            "praticas.views.traduzir_campos_experiencia",
            return_value={
                "titulo": "PT automático",
                "titulo_es": "ES incorreto",
                "titulo_en": "EN automático",
            },
        ):
            self.assertTrue(tentar_traduzir_experiencia(experiencia, "es"))
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.titulo_es, "Título ES original")
        self.assertEqual(experiencia.titulo, "Título PT manual")
        self.assertEqual(experiencia.titulo_en, "EN automático")

    def test_lista_vazia_de_campos_nao_dispara_traducao(self):
        with patch("praticas.views.traduzir_campos_experiencia") as traduzir:
            self.assertTrue(tentar_traduzir_experiencia(self.experiencia, "pt", []))
        traduzir.assert_not_called()

    def test_provedor_nao_sobrescreve_traducao_gravada_durante_a_chamada(self):
        experiencia = Experiencia.objects.get(pk=self.experiencia.pk)

        def provider(campos, origem, destino):
            if destino == "es":
                Experiencia.objects.filter(pk=experiencia.pk).update(titulo_es="Tradução manual concorrente")
            return {"titulo": "Tradução automática"}

        with patch.dict(os.environ, {"PJC_TRANSLATION_ENDPOINT": "https://translation.invalid"}, clear=False):
            with patch("praticas.services.traducao._traduzir_lote", side_effect=provider):
                self.assertTrue(tentar_traduzir_experiencia(experiencia, "pt", ["titulo"]))
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.titulo_es, "Tradução manual concorrente")
        self.assertEqual(experiencia.titulo_en, "Tradução automática")

    def test_registro_historico_sem_idioma_nao_e_reinterpretado(self):
        experiencia = self.experiencia
        experiencia.autor = self.usuario
        experiencia.idioma_original = ""
        experiencia.titulo = "Título histórico PT"
        experiencia.titulo_es = "Título histórico ES"
        experiencia.titulo_en = "Título histórico EN"
        experiencia.save(update_fields=["autor", "idioma_original", "titulo", "titulo_es", "titulo_en"])
        self.client.force_login(self.usuario)
        dados = self.dados_submissao("Título histórico PT editado", "Descrição PT")
        with override("es"), patch("praticas.views.tentar_traduzir_experiencia") as traduzir:
            with patch("praticas.views.traduzir_campos_experiencia") as provedor:
                with self.captureOnCommitCallbacks(execute=True):
                    resposta = self.client.post(f"/editar-boa-pratica/{experiencia.pk}/", dados)
        self.assertEqual(resposta.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.idioma_original, "")
        self.assertEqual(experiencia.titulo, "Título histórico PT editado")
        self.assertEqual(experiencia.titulo_es, "Título histórico ES")
        self.assertEqual(experiencia.titulo_en, "Título histórico EN")
        traduzir.assert_not_called()
        provedor.assert_not_called()

    def test_get_e_post_com_idioma_invalido_sao_controlados(self):
        self.client.force_login(self.usuario)
        with patch("praticas.views.idioma_original_interface", return_value=None):
            self.assertEqual(self.client.get("/adicionar-boa-pratica/?tipo=boa_pratica").status_code, 400)
            antes = Experiencia.objects.count()
            self.assertEqual(
                self.client.post("/adicionar-boa-pratica/", self.dados_submissao("Inválido", "Inválido")).status_code,
                400,
            )
        self.assertEqual(Experiencia.objects.count(), antes)

    def test_get_formulario_localizado_avalia_querysets_na_ordem_do_idioma(self):
        paises = [
            Pais.objects.create(nome="Zeta PT", nome_es="Alfa ES", nome_en="Omega EN", sigla="ZP"),
            Pais.objects.create(nome="Alfa PT", nome_es="Zeta ES", nome_en="Beta EN", sigla="AP"),
        ]
        efs = [
            EFS.objects.create(nome="Zeta EFS PT", nome_es="Alfa EFS ES", nome_en="Omega EFS EN", sigla="ZP", pais=paises[0]),
            EFS.objects.create(nome="Alfa EFS PT", nome_es="Zeta EFS ES", nome_en="Beta EFS EN", sigla="AP", pais=paises[1]),
        ]
        self.client.force_login(self.usuario)
        casos = (
            ("/adicionar-boa-pratica/", "nome", paises, efs, ["Alfa PT", "Zeta PT"], ["Alfa EFS PT", "Zeta EFS PT"]),
            ("/es/adicionar-boa-pratica/", "nome_es", paises, efs, ["Alfa ES", "Zeta ES"], ["Alfa EFS ES", "Zeta EFS ES"]),
            ("/en/adicionar-boa-pratica/", "nome_en", paises, efs, ["Beta EN", "Omega EN"], ["Beta EFS EN", "Omega EFS EN"]),
        )
        with override("pt-br"):
            for caminho, campo_ordem, paises_esperados, efs_esperados, paises_ordem, efs_ordem in casos:
                with self.subTest(caminho=caminho):
                    resposta = self.client.get(f"{caminho}?tipo=boa_pratica")
                    self.assertEqual(resposta.status_code, 200)
                    formulario = resposta.context["form"]
                    paises_obtidos = list(
                        formulario.fields["pais"].queryset.filter(pk__in=[p.pk for p in paises_esperados])
                        .values_list(campo_ordem, flat=True)
                    )
                    efs_obtidas = list(
                        formulario.fields["efs"].queryset.filter(pk__in=[e.pk for e in efs_esperados])
                        .values_list(campo_ordem, flat=True)
                    )
                    participantes = list(
                        formulario.fields["paises_participantes"].queryset.filter(pk__in=[p.pk for p in paises_esperados])
                        .values_list(campo_ordem, flat=True)
                    )
                    self.assertEqual(paises_obtidos, paises_ordem)
                    self.assertEqual(efs_obtidas, efs_ordem)
                    self.assertEqual(participantes, paises_ordem)

    def preparar_experiencia_es(self, status):
        experiencia = self.experiencia
        experiencia.autor = self.usuario
        experiencia.idioma_original = "es"
        experiencia.titulo = "Título PT manual"
        experiencia.titulo_es = "Título ES original"
        experiencia.titulo_en = "English manual title"
        experiencia.descricao = "Descrição PT manual"
        experiencia.descricao_es = "Descripción ES original"
        experiencia.descricao_en = "English manual description"
        experiencia.status_publicacao = status
        experiencia.save(update_fields=[
            "autor", "idioma_original", "titulo", "titulo_es", "titulo_en",
            "descricao", "descricao_es", "descricao_en", "status_publicacao",
        ])
        return experiencia

    def test_autor_edita_publicada_preservando_idioma_e_traducoes_manuais(self):
        experiencia = self.preparar_experiencia_es(Experiencia.StatusPublicacao.PUBLICADO)
        self.client.force_login(self.usuario)
        dados = self.dados_submissao("Título ES editado", "Descripción ES editada")
        with patch("praticas.views.tentar_traduzir_experiencia") as traduzir:
            with self.captureOnCommitCallbacks(execute=True):
                resposta = self.client.post(f"/editar-boa-pratica/{experiencia.pk}/", dados)
        self.assertEqual(resposta.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        self.assertEqual(experiencia.idioma_original, "es")
        self.assertEqual(experiencia.titulo_es, "Título ES editado")
        self.assertEqual(experiencia.descricao_es, "Descripción ES editada")
        self.assertEqual(experiencia.titulo, "Título PT manual")
        self.assertEqual(experiencia.titulo_en, "English manual title")
        traduzir.assert_called_once()

    def test_autor_edita_arquivada_sem_republicar_ou_traduzir(self):
        experiencia = self.preparar_experiencia_es(Experiencia.StatusPublicacao.ARQUIVADO)
        self.client.force_login(self.usuario)
        with patch("praticas.views.tentar_traduzir_experiencia") as traduzir:
            with patch("praticas.views.traduzir_campos_experiencia") as provedor:
                with self.captureOnCommitCallbacks(execute=True):
                    resposta = self.client.post(
                        f"/es/editar-boa-pratica/{experiencia.pk}/",
                        self.dados_submissao("Título ES arquivado", "Descripción ES archivada"),
                    )
        self.assertEqual(resposta.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ARQUIVADO)
        self.assertEqual(experiencia.idioma_original, "es")
        traduzir.assert_not_called()
        provedor.assert_not_called()

    def test_staff_edita_traducao_sem_disparar_tradutor(self):
        experiencia = self.preparar_experiencia_es(Experiencia.StatusPublicacao.PUBLICADO)
        staff = get_user_model().objects.create_user(
            username="traducao-staff",
            email="traducao-staff@example.org",
            password="SenhaForte123!",
            is_staff=True,
        )
        dados = self.dados_submissao("Título ES original", "Descripción ES original")
        dados.update({"traducao_pt__titulo": "Título PT revisado", "traducao_en__titulo": "English reviewed title"})
        self.client.force_login(staff)
        with patch("praticas.views.tentar_traduzir_experiencia") as traduzir:
            with patch("praticas.views.traduzir_campos_experiencia") as provedor:
                with self.captureOnCommitCallbacks(execute=True):
                    resposta = self.client.post(f"/editar-boa-pratica/{experiencia.pk}/", dados)
        self.assertEqual(resposta.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.idioma_original, "es")
        self.assertEqual(experiencia.titulo, "Título PT revisado")
        self.assertEqual(experiencia.titulo_en, "English reviewed title")
        traduzir.assert_not_called()
        provedor.assert_not_called()
