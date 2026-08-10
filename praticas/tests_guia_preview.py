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

    def test_acesso_exige_staff(self):
        rotas = (
            reverse("guia_preview_inicio"),
            reverse("guia_preview_eixos"),
            reverse(
                "guia_preview_eixo", kwargs={"eixo_codigo": self.eixo_um.codigo}
            ),
            reverse(
                "guia_preview_subeixo",
                kwargs={
                    "eixo_codigo": self.eixo_um.codigo,
                    "subeixo_codigo": self.subeixo_um.codigo,
                },
            ),
            reverse("guia_preview_setores"),
            reverse(
                "guia_preview_setor", kwargs={"setor_codigo": self.setor_um.codigo}
            ),
            reverse(
                "guia_preview_subarea",
                kwargs={
                    "setor_codigo": self.setor_um.codigo,
                    "subarea_codigo": self.subarea_um.codigo,
                },
            ),
        )

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

    def test_hierarquia_incorreta_nao_permite_acesso_cruzado(self):
        rota_subeixo = reverse(
            "guia_preview_subeixo",
            kwargs={"eixo_codigo": "eixo-dois", "subeixo_codigo": "subeixo-um"},
        )
        rota_subarea = reverse(
            "guia_preview_subarea",
            kwargs={"setor_codigo": "setor-dois", "subarea_codigo": "subarea-um"},
        )

        self.assertEqual(self.client.get(rota_subeixo).status_code, 404)
        self.assertEqual(self.client.get(rota_subarea).status_code, 404)

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
