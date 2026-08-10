from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone, translation

from .models import (
    EixoGuia,
    LoteImportacaoConteudo,
    PerguntaGuia,
    ReferenciaGuia,
    SetorGuia,
    SubareaGuia,
    SubareaReferenciaGuia,
    SubeixoGuia,
    VersaoGuia,
)
from .seletores_guia_preview import (
    listar_eixos,
    listar_setores,
    queryset_eixo_detalhado,
    queryset_setor_detalhado,
    queryset_subarea_detalhada,
    queryset_subeixo_detalhado,
)


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class GuiaPreviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario_model = get_user_model()
        cls.staff = usuario_model.objects.create_user(
            "staff-preview", password="senha-teste", is_staff=True
        )
        cls.comum = usuario_model.objects.create_user(
            "comum-preview", password="senha-teste"
        )
        cls.lote = LoteImportacaoConteudo.objects.create(
            fonte="fonte sintetica de teste",
            sha256="a" * 64,
            versao_fonte="preview-teste",
            executado_por=cls.staff,
        )

        cls.antiga = cls._criar_versao("guia-antiga")
        cls._criar_arvore_minima(
            cls.antiga,
            sufixo="antiga",
            nome_eixo="Eje de una versión anterior",
        )
        cls._publicar(cls.antiga, vigente=False)

        cls.rascunho = cls._criar_versao("guia-rascunho")
        cls._criar_arvore_minima(
            cls.rascunho,
            sufixo="rascunho",
            nome_eixo="Eje que no puede exponerse",
        )

        cls.vigente = cls._criar_versao("guia-vigente")
        cls._criar_arvore_vigente()
        cls._publicar(cls.vigente, vigente=True)

    @classmethod
    def _criar_versao(cls, codigo):
        return VersaoGuia.objects.create(
            codigo=codigo,
            fonte=f"sintetica/{codigo}.json",
            sha256_fonte="b" * 64,
        )

    @classmethod
    def _publicar(cls, versao, *, vigente):
        versao.situacao = VersaoGuia.Situacao.PUBLICADA
        versao.vigente = vigente
        versao.publicado_em = timezone.now()
        versao.lote_origem = cls.lote
        versao.save()

    @classmethod
    def _criar_arvore_minima(cls, versao, *, sufixo, nome_eixo):
        eixo = EixoGuia.objects.create(
            versao=versao,
            codigo=f"eixo-{sufixo}",
            nome_es=nome_eixo,
            ordem=1,
        )
        setor = SetorGuia.objects.create(
            versao=versao,
            codigo=f"setor-{sufixo}",
            nome_es=f"Sector {sufixo}",
            ordem=1,
        )
        SubareaGuia.objects.create(
            versao=versao,
            setor=setor,
            codigo=f"subarea-{sufixo}",
            nome_es=f"Subárea {sufixo}",
            ordem=1,
        )
        PerguntaGuia.objects.create(
            versao=versao,
            eixo=eixo,
            codigo=f"pregunta-{sufixo}",
            texto_es=f"¿Pregunta {sufixo}?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=1,
        )

    @classmethod
    def _criar_arvore_vigente(cls):
        cls.eixo_dois = EixoGuia.objects.create(
            versao=cls.vigente,
            codigo="eixo-dois",
            nome_es="Eje segundo",
            ordem=2,
        )
        cls.eixo_um = EixoGuia.objects.create(
            versao=cls.vigente,
            codigo="eixo-um",
            nome_es="Eje primero vigente",
            ordem=1,
        )
        cls.subeixo_dois = SubeixoGuia.objects.create(
            versao=cls.vigente,
            eixo=cls.eixo_um,
            codigo="subeixo-dois",
            nome_es="Subeje segundo",
            ordem=2,
        )
        cls.subeixo_um = SubeixoGuia.objects.create(
            versao=cls.vigente,
            eixo=cls.eixo_um,
            codigo="subeixo-um",
            nome_es="Subeje primero",
            ordem=1,
        )
        cls._criar_pergunta(
            codigo="eixo-gestion",
            texto="¿Gestión directa del eje?",
            tipo=PerguntaGuia.TipoAuditoria.GESTION,
            ordem=1,
            eixo=cls.eixo_um,
        )
        cls._criar_pergunta(
            codigo="sub-cumplimiento-2",
            texto="¿Cumplimiento segundo del subeje?",
            tipo=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=2,
            subeixo=cls.subeixo_um,
        )
        cls._criar_pergunta(
            codigo="sub-cumplimiento-1",
            texto="¿Cumplimiento primero del subeje?",
            tipo=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=1,
            subeixo=cls.subeixo_um,
        )
        cls._criar_pergunta(
            codigo="sub-gestion-1",
            texto="¿Gestión primera del subeje?",
            tipo=PerguntaGuia.TipoAuditoria.GESTION,
            ordem=1,
            subeixo=cls.subeixo_um,
        )

        cls.setor_dois = SetorGuia.objects.create(
            versao=cls.vigente,
            codigo="setor-dois",
            nome_es="Sector segundo",
            ordem=2,
        )
        cls.setor_um = SetorGuia.objects.create(
            versao=cls.vigente,
            codigo="setor-um",
            nome_es="Sector primero",
            ordem=1,
        )
        cls.subarea_dois = SubareaGuia.objects.create(
            versao=cls.vigente,
            setor=cls.setor_um,
            codigo="subarea-dois",
            nome_es="Subárea segunda",
            ordem=2,
        )
        cls.subarea_um = SubareaGuia.objects.create(
            versao=cls.vigente,
            setor=cls.setor_um,
            codigo="subarea-um",
            nome_es="Subárea primera",
            ordem=1,
        )
        cls._criar_pergunta(
            codigo="area-cumplimiento-2",
            texto="¿Cumplimiento segundo de la subárea?",
            tipo=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=2,
            subarea=cls.subarea_um,
        )
        cls._criar_pergunta(
            codigo="area-cumplimiento-1",
            texto="¿Cumplimiento primero de la subárea?",
            tipo=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=1,
            subarea=cls.subarea_um,
        )
        cls._criar_pergunta(
            codigo="area-gestion-1",
            texto="¿Gestión primera de la subárea?",
            tipo=PerguntaGuia.TipoAuditoria.GESTION,
            ordem=1,
            subarea=cls.subarea_um,
        )
        referencia_dois = ReferenciaGuia.objects.create(
            versao=cls.vigente,
            codigo="referencia-dois",
            citacao_es="Segunda cita institucional sintética.",
        )
        referencia_um = ReferenciaGuia.objects.create(
            versao=cls.vigente,
            codigo="referencia-um",
            citacao_es="Primera cita institucional sintética.",
        )
        SubareaReferenciaGuia.objects.create(
            subarea=cls.subarea_um, referencia=referencia_dois, ordem=2
        )
        SubareaReferenciaGuia.objects.create(
            subarea=cls.subarea_um, referencia=referencia_um, ordem=1
        )

    @classmethod
    def _criar_pergunta(cls, *, codigo, texto, tipo, ordem, **escopo):
        return PerguntaGuia.objects.create(
            versao=cls.vigente,
            codigo=codigo,
            texto_es=texto,
            tipo_auditoria=tipo,
            ordem=ordem,
            **escopo,
        )

    def setUp(self):
        self.client.force_login(self.staff)

    def _rotas_guia(self, prefixo):
        return (
            reverse(f"{prefixo}_inicio"),
            reverse(f"{prefixo}_eixos"),
            reverse(
                f"{prefixo}_eixo", kwargs={"eixo_codigo": self.eixo_um.codigo}
            ),
            reverse(
                f"{prefixo}_subeixo",
                kwargs={
                    "eixo_codigo": self.eixo_um.codigo,
                    "subeixo_codigo": self.subeixo_um.codigo,
                },
            ),
            reverse(f"{prefixo}_setores"),
            reverse(
                f"{prefixo}_setor", kwargs={"setor_codigo": self.setor_um.codigo}
            ),
            reverse(
                f"{prefixo}_subarea",
                kwargs={
                    "setor_codigo": self.setor_um.codigo,
                    "subarea_codigo": self.subarea_um.codigo,
                },
            ),
        )

    def test_acesso_exige_staff(self):
        rotas = self._rotas_guia("guia_preview")

        self.client.logout()
        for rota in rotas:
            with self.subTest(perfil="anonimo", rota=rota):
                resposta_anonima = self.client.get(rota)
                self.assertEqual(resposta_anonima.status_code, 302)
                self.assertTrue(
                    resposta_anonima.url.startswith(reverse("login_usuario"))
                )

        self.client.force_login(self.comum)
        for rota in rotas:
            with self.subTest(perfil="comum", rota=rota):
                resposta_comum = self.client.get(rota)
                self.assertEqual(resposta_comum.status_code, 302)
                self.assertTrue(
                    resposta_comum.url.startswith(reverse("login_usuario"))
                )

        self.client.force_login(self.staff)
        for rota in rotas:
            with self.subTest(perfil="staff", rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 200)

    def test_views_rejeitam_metodos_de_escrita(self):
        rotas = self._rotas_guia("guia_preview")

        for metodo in ("post", "put", "patch", "delete"):
            for rota in rotas:
                with self.subTest(metodo=metodo.upper(), rota=rota):
                    resposta = getattr(self.client, metodo)(rota)
                    self.assertEqual(resposta.status_code, 405)

    def test_guia_publico_permite_acesso_anonimo_e_usuario_comum(self):
        self.client.logout()
        for rota in self._rotas_guia("guia"):
            with self.subTest(perfil="anonimo", rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 200)

        self.client.force_login(self.comum)
        for rota in self._rotas_guia("guia"):
            with self.subTest(perfil="comum", rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 200)

    def test_guia_publico_permite_get_head_e_rejeita_metodos_de_escrita(self):
        self.client.logout()
        for rota in self._rotas_guia("guia"):
            for metodo in ("get", "head"):
                with self.subTest(metodo=metodo.upper(), rota=rota):
                    self.assertEqual(getattr(self.client, metodo)(rota).status_code, 200)
            for metodo in ("post", "put", "patch", "delete"):
                with self.subTest(metodo=metodo.upper(), rota=rota):
                    self.assertEqual(getattr(self.client, metodo)(rota).status_code, 405)

    def test_guia_publico_mantem_interface_trilingue_e_conteudo_em_espanhol(self):
        self.client.logout()
        for idioma, titulo, rotulo_preview in (
            ("pt-br", "Guia de Justiça Climática", "Prévia interna"),
            ("es", "Guía de Justicia Climática", "Vista previa interna"),
            ("en", "Climate Justice Guide", "Internal preview"),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                resposta_inicio = self.client.get(reverse("guia_inicio"))
                resposta_subarea = self.client.get(
                    reverse(
                        "guia_subarea",
                        kwargs={
                            "setor_codigo": self.setor_um.codigo,
                            "subarea_codigo": self.subarea_um.codigo,
                        },
                    )
                )

                self.assertContains(resposta_inicio, titulo)
                self.assertContains(resposta_inicio, "Eje primero vigente")
                self.assertContains(resposta_inicio, '<h3 lang="es">', html=False)
                self.assertNotContains(resposta_inicio, rotulo_preview)
                self.assertContains(
                    resposta_subarea,
                    '<p lang="es">¿Cumplimiento primero de la subárea?</p>',
                    html=False,
                )
                self.assertContains(
                    resposta_subarea,
                    '<p lang="es">Primera cita institucional sintética.</p>',
                    html=False,
                )

    def test_guia_publico_expoe_somente_publicada_vigente(self):
        self.client.logout()
        resposta = self.client.get(reverse("guia_inicio"))

        self.assertEqual(resposta.context["versao"], self.vigente)
        self.assertContains(resposta, "Eje primero vigente")
        self.assertNotContains(resposta, "Eje de una versión anterior")
        self.assertNotContains(resposta, "Eje que no puede exponerse")

        for rota in (
            reverse("guia_eixo", kwargs={"eixo_codigo": "inexistente"}),
            reverse("guia_eixo", kwargs={"eixo_codigo": "eixo-antiga"}),
            reverse("guia_eixo", kwargs={"eixo_codigo": "eixo-rascunho"}),
            reverse("guia_setor", kwargs={"setor_codigo": "setor-antiga"}),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_navegacao_publica_permanece_publica_e_preview_permanece_interna(self):
        self.client.logout()
        resposta_publica = self.client.get(reverse("guia_inicio"))
        self.assertContains(resposta_publica, reverse("guia_eixos"))
        self.assertContains(
            resposta_publica,
            reverse("guia_eixo", kwargs={"eixo_codigo": self.eixo_um.codigo}),
        )
        self.assertContains(resposta_publica, reverse("guia_setores"))
        self.assertContains(
            resposta_publica,
            reverse("guia_setor", kwargs={"setor_codigo": self.setor_um.codigo}),
        )
        self.assertNotContains(resposta_publica, reverse("guia_preview_inicio"))

        self.client.force_login(self.staff)
        resposta_preview = self.client.get(reverse("guia_preview_inicio"))
        self.assertContains(resposta_preview, reverse("guia_preview_eixos"))
        self.assertContains(resposta_preview, "Pr&eacute;via interna", html=False)

    def test_rotulos_seguem_idioma_da_interface_e_conteudo_permanece_es(self):
        for idioma, titulo in (
            ("pt-br", "Guia de Justiça Climática"),
            ("es", "Guía de Justicia Climática"),
            ("en", "Climate Justice Guide"),
        ):
            with self.subTest(idioma=idioma), translation.override(idioma):
                resposta = self.client.get(reverse("guia_preview_inicio"))
                self.assertContains(resposta, titulo)
                self.assertContains(resposta, "Eje primero vigente")
                self.assertContains(resposta, '<h3 lang="es">', html=False)

    def test_inicio_seleciona_somente_publicada_vigente(self):
        resposta = self.client.get(reverse("guia_preview_inicio"))

        self.assertEqual(resposta.context["versao"], self.vigente)
        self.assertContains(resposta, "Eje primero vigente")
        self.assertNotContains(resposta, "Eje de una versión anterior")
        self.assertNotContains(resposta, "Eje que no puede exponerse")

    def test_sem_versao_vigente_renderiza_estado_vazio(self):
        self.vigente.vigente = False
        self.vigente.save()

        resposta = self.client.get(reverse("guia_preview_inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(resposta.context["versao"])
        self.assertEqual(resposta.context["eixos"], ())
        self.assertEqual(resposta.context["setores"], ())

    def test_listagem_de_eixos_preserva_ordem_e_contadores_derivados(self):
        resposta = self.client.get(reverse("guia_preview_eixos"))
        eixos = list(resposta.context["eixos"])

        self.assertEqual([e.codigo for e in eixos], ["eixo-um", "eixo-dois"])
        self.assertEqual(eixos[0].total_subeixos, 2)
        self.assertEqual(eixos[0].total_perguntas, 4)

    def test_detalhe_de_eixo_mostra_subeixos_e_perguntas_diretas(self):
        resposta = self.client.get(
            reverse("guia_preview_eixo", kwargs={"eixo_codigo": "eixo-um"})
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            [item.codigo for item in resposta.context["subeixos"]],
            ["subeixo-um", "subeixo-dois"],
        )
        self.assertEqual(resposta.context["perguntas_cumplimiento"], [])
        self.assertEqual(
            [item.codigo for item in resposta.context["perguntas_gestion"]],
            ["eixo-gestion"],
        )

    def test_detalhe_de_subeixo_separa_tipos_e_preserva_ordem(self):
        resposta = self.client.get(
            reverse(
                "guia_preview_subeixo",
                kwargs={"eixo_codigo": "eixo-um", "subeixo_codigo": "subeixo-um"},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["eixo"], self.eixo_um)
        self.assertEqual(
            [item.codigo for item in resposta.context["perguntas_cumplimiento"]],
            ["sub-cumplimiento-1", "sub-cumplimiento-2"],
        )
        self.assertEqual(
            [item.codigo for item in resposta.context["perguntas_gestion"]],
            ["sub-gestion-1"],
        )

    def test_listagem_e_detalhe_de_setor_preservam_ordem(self):
        resposta_lista = self.client.get(reverse("guia_preview_setores"))
        setores = list(resposta_lista.context["setores"])
        self.assertEqual([setor.codigo for setor in setores], ["setor-um", "setor-dois"])
        self.assertEqual(setores[0].total_subareas, 2)

        resposta_detalhe = self.client.get(
            reverse("guia_preview_setor", kwargs={"setor_codigo": "setor-um"})
        )
        self.assertEqual(resposta_detalhe.status_code, 200)
        self.assertEqual(
            [item.codigo for item in resposta_detalhe.context["subareas"]],
            ["subarea-um", "subarea-dois"],
        )

    def test_detalhe_de_subarea_exibe_perguntas_e_referencias_em_ordem(self):
        resposta = self.client.get(
            reverse(
                "guia_preview_subarea",
                kwargs={"setor_codigo": "setor-um", "subarea_codigo": "subarea-um"},
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            [item.codigo for item in resposta.context["perguntas_cumplimiento"]],
            ["area-cumplimiento-1", "area-cumplimiento-2"],
        )
        self.assertEqual(
            [item.codigo for item in resposta.context["perguntas_gestion"]],
            ["area-gestion-1"],
        )
        self.assertEqual(
            [item.referencia.codigo for item in resposta.context["ocorrencias_referencias"]],
            ["referencia-um", "referencia-dois"],
        )

    def test_conteudo_es_e_preservado_sem_escritas_ou_traducoes(self):
        contagens_antes = {
            "versoes": VersaoGuia.objects.count(),
            "perguntas": PerguntaGuia.objects.count(),
            "referencias": ReferenciaGuia.objects.count(),
        }

        resposta = self.client.get(
            reverse(
                "guia_preview_subarea",
                kwargs={"setor_codigo": "setor-um", "subarea_codigo": "subarea-um"},
            )
        )

        self.assertContains(resposta, "¿Cumplimiento primero de la subárea?")
        self.assertContains(resposta, "Primera cita institucional sintética.")
        self.assertFalse(hasattr(resposta.context["subarea"], "nome_pt"))
        self.assertEqual(
            contagens_antes,
            {
                "versoes": VersaoGuia.objects.count(),
                "perguntas": PerguntaGuia.objects.count(),
                "referencias": ReferenciaGuia.objects.count(),
            },
        )

    def test_codigos_inexistentes_e_de_outra_versao_retornam_404(self):
        for rota in (
            reverse("guia_preview_eixo", kwargs={"eixo_codigo": "inexistente"}),
            reverse("guia_preview_eixo", kwargs={"eixo_codigo": "eixo-antiga"}),
            reverse("guia_preview_eixo", kwargs={"eixo_codigo": "eixo-rascunho"}),
            reverse("guia_preview_setor", kwargs={"setor_codigo": "setor-antiga"}),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_relacionamentos_do_guia_sao_isolados_por_versao(self):
        eixo_rascunho = EixoGuia.objects.get(
            versao=self.rascunho, codigo="eixo-rascunho"
        )
        setor_rascunho = SetorGuia.objects.get(
            versao=self.rascunho, codigo="setor-rascunho"
        )
        subarea_rascunho = SubareaGuia.objects.get(
            versao=self.rascunho, codigo="subarea-rascunho"
        )
        subeixo_rascunho = SubeixoGuia.objects.create(
            versao=self.rascunho,
            eixo=eixo_rascunho,
            codigo="subeixo-isolamento",
            nome_es="Subeje de otra versión",
            ordem=99,
        )
        pergunta_subeixo = PerguntaGuia.objects.create(
            versao=self.rascunho,
            subeixo=subeixo_rascunho,
            codigo="pergunta-subeixo-isolamento",
            texto_es="¿Pregunta de otra versión?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=99,
        )
        pergunta_subarea = PerguntaGuia.objects.create(
            versao=self.rascunho,
            subarea=subarea_rascunho,
            codigo="pergunta-subarea-isolamento",
            texto_es="¿Pregunta de subárea de otra versión?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=99,
        )
        referencia_rascunho = ReferenciaGuia.objects.create(
            versao=self.rascunho,
            codigo="referencia-isolamento",
            citacao_es="Referencia de otra versión.",
        )
        ocorrencia_rascunho = SubareaReferenciaGuia.objects.create(
            subarea=subarea_rascunho,
            referencia=referencia_rascunho,
            ordem=99,
        )

        PerguntaGuia.objects.filter(codigo="pregunta-rascunho").update(
            eixo=self.eixo_um
        )
        SubeixoGuia.objects.filter(pk=subeixo_rascunho.pk).update(eixo=self.eixo_um)
        PerguntaGuia.objects.filter(pk=pergunta_subeixo.pk).update(
            subeixo=self.subeixo_um
        )
        SubareaGuia.objects.filter(pk=subarea_rascunho.pk).update(
            setor=self.setor_um, ordem=99
        )
        PerguntaGuia.objects.filter(pk=pergunta_subarea.pk).update(
            subarea=self.subarea_um
        )
        SubareaReferenciaGuia.objects.filter(pk=ocorrencia_rascunho.pk).update(
            subarea=self.subarea_um
        )

        eixos = list(listar_eixos(self.vigente))
        setores = list(listar_setores(self.vigente))
        eixo = queryset_eixo_detalhado(self.vigente).get(pk=self.eixo_um.pk)
        subeixo = queryset_subeixo_detalhado(self.vigente, self.eixo_um.codigo).get(
            pk=self.subeixo_um.pk
        )
        setor = queryset_setor_detalhado(self.vigente).get(pk=self.setor_um.pk)
        subarea = queryset_subarea_detalhada(
            self.vigente, self.setor_um.codigo
        ).get(pk=self.subarea_um.pk)

        self.assertEqual(eixos[0].total_subeixos, 2)
        self.assertEqual(eixos[0].total_perguntas, 4)
        self.assertEqual(setores[0].total_subareas, 2)
        self.assertNotIn(
            "subeixo-isolamento", [item.codigo for item in eixo.subeixos_preview]
        )
        self.assertNotIn(
            "pregunta-rascunho", [item.codigo for item in eixo.perguntas_preview]
        )
        self.assertNotIn(
            "pergunta-subeixo-isolamento",
            [item.codigo for item in subeixo.perguntas_preview],
        )
        self.assertNotIn(
            "subarea-rascunho", [item.codigo for item in setor.subareas_preview]
        )
        self.assertNotIn(
            "pergunta-subarea-isolamento",
            [item.codigo for item in subarea.perguntas_preview],
        )
        self.assertNotIn(
            "referencia-isolamento",
            [
                item.referencia.codigo
                for item in subarea.ocorrencias_referencias_preview
            ],
        )

        resposta_eixo = self.client.get(
            reverse("guia_eixo", kwargs={"eixo_codigo": self.eixo_um.codigo})
        )
        resposta_subeixo = self.client.get(
            reverse(
                "guia_subeixo",
                kwargs={
                    "eixo_codigo": self.eixo_um.codigo,
                    "subeixo_codigo": self.subeixo_um.codigo,
                },
            )
        )
        resposta_setor = self.client.get(
            reverse("guia_setor", kwargs={"setor_codigo": self.setor_um.codigo})
        )
        resposta_subarea = self.client.get(
            reverse(
                "guia_subarea",
                kwargs={
                    "setor_codigo": self.setor_um.codigo,
                    "subarea_codigo": self.subarea_um.codigo,
                },
            )
        )
        for resposta in (
            resposta_eixo,
            resposta_subeixo,
            resposta_setor,
            resposta_subarea,
        ):
            self.assertNotContains(resposta, "isolamento")

    def test_hierarquia_incorreta_nao_permite_acesso_cruzado(self):
        for rota in (
            reverse(
                "guia_preview_subeixo",
                kwargs={
                    "eixo_codigo": "eixo-dois",
                    "subeixo_codigo": "subeixo-um",
                },
            ),
            reverse(
                "guia_preview_subarea",
                kwargs={
                    "setor_codigo": "setor-dois",
                    "subarea_codigo": "subarea-um",
                },
            ),
            reverse(
                "guia_preview_subarea",
                kwargs={
                    "setor_codigo": "setor-um",
                    "subarea_codigo": "subarea-antiga",
                },
            ),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_guia_publico_rejeita_hierarquia_cruzada(self):
        self.client.logout()
        for rota in (
            reverse(
                "guia_subeixo",
                kwargs={
                    "eixo_codigo": "eixo-dois",
                    "subeixo_codigo": "subeixo-um",
                },
            ),
            reverse(
                "guia_subarea",
                kwargs={
                    "setor_codigo": "setor-dois",
                    "subarea_codigo": "subarea-um",
                },
            ),
            reverse(
                "guia_subarea",
                kwargs={
                    "setor_codigo": "setor-um",
                    "subarea_codigo": "subarea-antiga",
                },
            ),
        ):
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_seletores_mantem_numero_de_queries_limitado_por_pagina(self):
        with self.assertNumQueries(1):
            list(listar_eixos(self.vigente))
        with self.assertNumQueries(1):
            list(listar_setores(self.vigente))
        with self.assertNumQueries(3):
            queryset_eixo_detalhado(self.vigente).get(codigo="eixo-um")
        with self.assertNumQueries(2):
            queryset_subeixo_detalhado(self.vigente, "eixo-um").get(
                codigo="subeixo-um"
            )
        with self.assertNumQueries(2):
            queryset_setor_detalhado(self.vigente).get(codigo="setor-um")
        with self.assertNumQueries(3):
            queryset_subarea_detalhada(self.vigente, "setor-um").get(
                codigo="subarea-um"
            )
