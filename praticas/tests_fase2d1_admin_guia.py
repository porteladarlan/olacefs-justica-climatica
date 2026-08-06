from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from .admin import (
    EixoGuiaAdmin,
    SubareaReferenciaGuiaAdmin,
    VersaoGuiaAdmin,
)
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


class AdminFundacaoGuiaTestCase(TestCase):
    HASH = "d" * 64

    def setUp(self):
        self.factory = RequestFactory()
        self.usuario = get_user_model().objects.create_superuser(
            username="admin_guia",
            email="admin@example.test",
            password="senha-segura-de-teste",
        )
        self.request = self.factory.get("/admin/")
        self.request.user = self.usuario
        self.lote = LoteImportacaoConteudo.objects.create(
            fonte="fonte institucional controlada",
            sha256=self.HASH,
            versao_fonte="fase2d1-admin",
            executado_por=self.usuario,
        )
        self.rascunho = VersaoGuia.objects.create(
            codigo="admin-rascunho",
            fonte="fonte/admin-rascunho.json",
            sha256_fonte=self.HASH,
        )

    def publicar(self, versao):
        versao.situacao = VersaoGuia.Situacao.PUBLICADA
        versao.publicado_em = timezone.now()
        versao.lote_origem = self.lote
        versao.save()
        versao.refresh_from_db()
        return versao

    def test_oito_models_do_guia_estao_registrados(self):
        modelos = {
            VersaoGuia,
            EixoGuia,
            SubeixoGuia,
            SetorGuia,
            SubareaGuia,
            PerguntaGuia,
            ReferenciaGuia,
            SubareaReferenciaGuia,
        }

        self.assertTrue(modelos.issubset(admin.site._registry.keys()))

    def test_versao_publicada_permite_editar_somente_vigencia(self):
        publicada = VersaoGuia.objects.create(
            codigo="admin-publicada",
            fonte="fonte/admin-publicada.json",
            sha256_fonte=self.HASH,
            situacao=VersaoGuia.Situacao.PUBLICADA,
            publicado_em=timezone.now(),
            lote_origem=self.lote,
        )
        model_admin = VersaoGuiaAdmin(VersaoGuia, admin.site)
        readonly = set(
            model_admin.get_readonly_fields(self.request, publicada)
        )

        self.assertNotIn("vigente", readonly)
        self.assertIn("codigo", readonly)
        self.assertIn("fonte", readonly)
        self.assertIn("sha256_fonte", readonly)
        self.assertIn("situacao", readonly)
        self.assertIn("publicado_em", readonly)
        self.assertIn("lote_origem", readonly)

    def test_versao_publicada_nao_pode_ser_excluida_pelo_admin(self):
        publicada = VersaoGuia.objects.create(
            codigo="admin-nao-excluir",
            fonte="fonte/admin-nao-excluir.json",
            sha256_fonte=self.HASH,
            situacao=VersaoGuia.Situacao.PUBLICADA,
            publicado_em=timezone.now(),
            lote_origem=self.lote,
        )
        model_admin = VersaoGuiaAdmin(VersaoGuia, admin.site)

        self.assertFalse(
            model_admin.has_delete_permission(self.request, publicada)
        )
        self.assertTrue(
            model_admin.has_delete_permission(self.request, self.rascunho)
        )

    def test_conteudo_publicado_fica_totalmente_somente_leitura(self):
        eixo = EixoGuia.objects.create(
            versao=self.rascunho,
            codigo="admin-eixo",
            nome_es="Eje de administración",
            ordem=1,
        )
        self.publicar(self.rascunho)
        model_admin = EixoGuiaAdmin(EixoGuia, admin.site)
        readonly = set(model_admin.get_readonly_fields(self.request, eixo))
        campos = {campo.name for campo in EixoGuia._meta.fields}

        self.assertTrue(campos.issubset(readonly))
        self.assertFalse(
            model_admin.has_delete_permission(self.request, eixo)
        )

    def test_conteudo_de_rascunho_permanece_editavel(self):
        eixo = EixoGuia.objects.create(
            versao=self.rascunho,
            codigo="admin-eixo-editavel",
            nome_es="Eje editable",
            ordem=1,
        )
        model_admin = EixoGuiaAdmin(EixoGuia, admin.site)
        readonly = set(model_admin.get_readonly_fields(self.request, eixo))

        self.assertNotIn("codigo", readonly)
        self.assertNotIn("nome_es", readonly)
        self.assertNotIn("ordem", readonly)
        self.assertTrue(
            model_admin.has_delete_permission(self.request, eixo)
        )

    def test_ocorrencia_de_referencia_exibe_a_versao_da_subarea(self):
        setor = SetorGuia.objects.create(
            versao=self.rascunho,
            codigo="admin-setor",
            nome_es="Sector de administración",
            ordem=1,
        )
        subarea = SubareaGuia.objects.create(
            versao=self.rascunho,
            setor=setor,
            codigo="admin-subarea",
            nome_es="Subárea de administración",
            ordem=1,
        )
        referencia = ReferenciaGuia.objects.create(
            versao=self.rascunho,
            codigo="admin-referencia",
            citacao_es="Referencia de administración.",
        )
        ocorrencia = SubareaReferenciaGuia.objects.create(
            subarea=subarea,
            referencia=referencia,
            ordem=1,
        )
        model_admin = SubareaReferenciaGuiaAdmin(
            SubareaReferenciaGuia,
            admin.site,
        )

        self.assertEqual(model_admin.versao(ocorrencia), self.rascunho)
