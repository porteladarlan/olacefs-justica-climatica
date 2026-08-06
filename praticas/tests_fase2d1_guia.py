from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import (
    EixoGuia,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    PerguntaGuia,
    ReferenciaGuia,
    Setor,
    SetorGuia,
    SubareaGuia,
    SubareaReferenciaGuia,
    SubeixoGuia,
    VersaoGuia,
)


class FundacaoGuiaTestCase(TestCase):
    HASH_A = "a" * 64
    HASH_B = "b" * 64
    HASH_C = "c" * 64

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="revisor_guia",
            password="senha-segura-de-teste",
        )
        self.lote = LoteImportacaoConteudo.objects.create(
            fonte="fonte institucional controlada",
            sha256=self.HASH_A,
            versao_fonte="fase2d1-teste",
            executado_por=self.usuario,
        )
        self.versao = self.criar_versao("guia-v1")
        self.eixo = EixoGuia.objects.create(
            versao=self.versao,
            codigo="governanza",
            nome_es="Gobernanza",
            ordem=1,
        )
        self.subeixo = SubeixoGuia.objects.create(
            versao=self.versao,
            eixo=self.eixo,
            codigo="marco-normativo",
            nome_es="Marco normativo y regulatorio",
            ordem=1,
        )
        self.setor = SetorGuia.objects.create(
            versao=self.versao,
            codigo="agua-energia",
            nome_es="AGUA Y ENERGÍA",
            ordem=1,
        )
        self.subarea = SubareaGuia.objects.create(
            versao=self.versao,
            setor=self.setor,
            codigo="acceso-agua",
            nome_es="Acceso al Agua Potable y Saneamiento",
            ordem=1,
        )

    def criar_versao(self, codigo, **campos):
        dados = {
            "codigo": codigo,
            "fonte": f"fonte/{codigo}.json",
            "sha256_fonte": self.HASH_A,
        }
        dados.update(campos)
        return VersaoGuia.objects.create(**dados)

    def criar_versao_publicada(self, codigo, vigente=False, hash_fonte=None):
        return self.criar_versao(
            codigo,
            sha256_fonte=hash_fonte or self.HASH_B,
            situacao=VersaoGuia.Situacao.PUBLICADA,
            vigente=vigente,
            publicado_em=timezone.now(),
            lote_origem=self.lote,
        )

    def test_ledger_diferencia_setor_compartilhado_e_entidades_do_guia(self):
        escolhas = dict(ItemLoteImportacaoConteudo.Entidade.choices)

        self.assertEqual(escolhas["setor"], "Setor")
        self.assertEqual(escolhas["setor_guia"], "Setor do guia")
        self.assertEqual(escolhas["versao_guia"], "Versao do guia")
        self.assertEqual(
            escolhas["subarea_referencia_guia"],
            "Ocorrencia de referencia em subarea",
        )

    def test_setor_guia_e_independente_do_setor_compartilhado(self):
        campos_relacionais = {
            campo.name: campo.related_model
            for campo in SetorGuia._meta.get_fields()
            if getattr(campo, "is_relation", False)
            and getattr(campo, "related_model", None) is not None
        }

        self.assertEqual(campos_relacionais["versao"], VersaoGuia)
        self.assertNotIn(Setor, campos_relacionais.values())
        self.assertNotIn("setor", campos_relacionais)

    def test_rascunho_valido_permanece_nao_vigente_e_sem_publicacao(self):
        self.assertEqual(self.versao.situacao, VersaoGuia.Situacao.RASCUNHO)
        self.assertFalse(self.versao.vigente)
        self.assertIsNone(self.versao.publicado_em)
        self.assertEqual(self.versao.idioma_canonico, "es")

    def test_rascunho_nao_pode_ser_vigente_nem_ter_data_de_publicacao(self):
        with self.assertRaises(ValidationError):
            self.criar_versao("rascunho-vigente", vigente=True)

        with self.assertRaises(ValidationError):
            self.criar_versao(
                "rascunho-com-data",
                publicado_em=timezone.now(),
            )

    def test_publicacao_exige_data_e_lote_de_origem(self):
        with self.assertRaises(ValidationError):
            self.criar_versao(
                "publicada-sem-lote",
                situacao=VersaoGuia.Situacao.PUBLICADA,
                publicado_em=timezone.now(),
            )

        with self.assertRaises(ValidationError):
            self.criar_versao(
                "publicada-sem-data",
                situacao=VersaoGuia.Situacao.PUBLICADA,
                lote_origem=self.lote,
            )

    def test_versao_publicada_e_imutavel_mas_pode_alterar_vigencia(self):
        versao = self.criar_versao_publicada("publicada-imutavel")

        versao.fonte = "outra-fonte.json"
        with self.assertRaises(ValidationError):
            versao.save()

        versao.refresh_from_db()
        versao.vigente = True
        versao.save()
        versao.refresh_from_db()

        self.assertTrue(versao.vigente)
        self.assertEqual(versao.fonte, "fonte/publicada-imutavel.json")

    def test_apenas_uma_versao_pode_ficar_vigente(self):
        self.criar_versao_publicada("vigente-1", vigente=True)

        with self.assertRaises(ValidationError):
            self.criar_versao_publicada("vigente-2", vigente=True)

        segunda = VersaoGuia(
            codigo="vigente-bypass",
            fonte="fonte/vigente-bypass.json",
            sha256_fonte=self.HASH_C,
            situacao=VersaoGuia.Situacao.PUBLICADA,
            vigente=True,
            publicado_em=timezone.now(),
            lote_origem=self.lote,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                VersaoGuia.objects.bulk_create([segunda])

    def test_versao_publicada_nao_pode_ser_excluida(self):
        versao = self.criar_versao_publicada("publicada-nao-excluir")

        with self.assertRaises(ValidationError):
            versao.delete()

        self.assertTrue(VersaoGuia.objects.filter(pk=versao.pk).exists())

    def test_conteudo_de_versao_publicada_nao_pode_ser_criado_alterado_ou_excluido(self):
        publicada = self.criar_versao_publicada("publicada-com-conteudo")

        with self.assertRaises(ValidationError):
            EixoGuia.objects.create(
                versao=publicada,
                codigo="novo-eixo",
                nome_es="Nuevo eje",
                ordem=1,
            )

        versao_editavel = self.criar_versao("publicar-depois")
        eixo = EixoGuia.objects.create(
            versao=versao_editavel,
            codigo="eixo-existente",
            nome_es="Eje existente",
            ordem=1,
        )
        versao_editavel.situacao = VersaoGuia.Situacao.PUBLICADA
        versao_editavel.publicado_em = timezone.now()
        versao_editavel.lote_origem = self.lote
        versao_editavel.save()

        eixo.nome_es = "Alteración no permitida"
        with self.assertRaises(ValidationError):
            eixo.save()

        eixo.refresh_from_db()
        with self.assertRaises(ValidationError):
            eixo.delete()

    def test_codigos_sao_unicos_por_versao_e_reutilizaveis_em_outra_versao(self):
        with self.assertRaises(ValidationError):
            EixoGuia.objects.create(
                versao=self.versao,
                codigo=self.eixo.codigo,
                nome_es="Duplicado",
                ordem=2,
            )

        outra_versao = self.criar_versao("guia-v2")
        outro_eixo = EixoGuia.objects.create(
            versao=outra_versao,
            codigo=self.eixo.codigo,
            nome_es=self.eixo.nome_es,
            ordem=1,
        )

        self.assertNotEqual(outro_eixo.pk, self.eixo.pk)

    def test_hierarquia_rejeita_relacoes_entre_versoes(self):
        outra_versao = self.criar_versao("guia-hierarquia-v2")

        with self.assertRaises(ValidationError):
            SubeixoGuia.objects.create(
                versao=outra_versao,
                eixo=self.eixo,
                codigo="subeixo-invalido",
                nome_es="Subeje inválido",
                ordem=1,
            )

        with self.assertRaises(ValidationError):
            SubareaGuia.objects.create(
                versao=outra_versao,
                setor=self.setor,
                codigo="subarea-invalida",
                nome_es="Subárea inválida",
                ordem=1,
            )

    def test_pergunta_exige_exatamente_um_escopo_e_mesma_versao(self):
        pergunta = PerguntaGuia.objects.create(
            versao=self.versao,
            codigo="pergunta-valida",
            texto_es="¿Pregunta válida?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=1,
            subeixo=self.subeixo,
        )
        self.assertEqual(pergunta.subeixo, self.subeixo)

        with self.assertRaises(ValidationError):
            PerguntaGuia.objects.create(
                versao=self.versao,
                codigo="pergunta-sem-escopo",
                texto_es="¿Sin alcance?",
                tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
                ordem=2,
            )

        with self.assertRaises(ValidationError):
            PerguntaGuia.objects.create(
                versao=self.versao,
                codigo="pergunta-dois-escopos",
                texto_es="¿Dos alcances?",
                tipo_auditoria=PerguntaGuia.TipoAuditoria.GESTION,
                ordem=1,
                eixo=self.eixo,
                subeixo=self.subeixo,
            )

        outra_versao = self.criar_versao("guia-pergunta-v2")
        with self.assertRaises(ValidationError):
            PerguntaGuia.objects.create(
                versao=outra_versao,
                codigo="pergunta-versao-invalida",
                texto_es="¿Versión inválida?",
                tipo_auditoria=PerguntaGuia.TipoAuditoria.GESTION,
                ordem=1,
                subarea=self.subarea,
            )

    def test_constraint_de_banco_impede_pergunta_sem_escopo(self):
        pergunta = PerguntaGuia(
            versao=self.versao,
            codigo="pergunta-bypass-sem-escopo",
            texto_es="¿Sin alcance por bulk create?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=99,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PerguntaGuia.objects.bulk_create([pergunta])

    def test_ordem_da_pergunta_e_unica_por_escopo_e_tipo(self):
        PerguntaGuia.objects.create(
            versao=self.versao,
            codigo="cumplimiento-1",
            texto_es="¿Cumplimiento uno?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
            ordem=1,
            subarea=self.subarea,
        )

        with self.assertRaises(ValidationError):
            PerguntaGuia.objects.create(
                versao=self.versao,
                codigo="cumplimiento-duplicada",
                texto_es="¿Cumplimiento duplicada?",
                tipo_auditoria=PerguntaGuia.TipoAuditoria.CUMPLIMIENTO,
                ordem=1,
                subarea=self.subarea,
            )

        gestao = PerguntaGuia.objects.create(
            versao=self.versao,
            codigo="gestion-1",
            texto_es="¿Gestión uno?",
            tipo_auditoria=PerguntaGuia.TipoAuditoria.GESTION,
            ordem=1,
            subarea=self.subarea,
        )

        self.assertEqual(gestao.ordem, 1)

    def test_referencias_preservam_ocorrencias_ordenadas_na_subarea(self):
        referencia = ReferenciaGuia.objects.create(
            versao=self.versao,
            codigo="referencia-1",
            citacao_es="Referencia normativa de prueba.",
        )
        primeira = SubareaReferenciaGuia.objects.create(
            subarea=self.subarea,
            referencia=referencia,
            ordem=1,
        )
        segunda = SubareaReferenciaGuia.objects.create(
            subarea=self.subarea,
            referencia=referencia,
            ordem=2,
        )

        self.assertEqual(
            list(
                self.subarea.ocorrencias_referencias.values_list(
                    "ordem",
                    flat=True,
                )
            ),
            [1, 2],
        )
        self.assertEqual(primeira.referencia, segunda.referencia)

        outra_referencia = ReferenciaGuia.objects.create(
            versao=self.versao,
            codigo="referencia-2",
            citacao_es="Segunda referencia normativa de prueba.",
        )
        with self.assertRaises(ValidationError):
            SubareaReferenciaGuia.objects.create(
                subarea=self.subarea,
                referencia=outra_referencia,
                ordem=2,
            )

        outra_versao = self.criar_versao("guia-referencia-v2")
        referencia_outra_versao = ReferenciaGuia.objects.create(
            versao=outra_versao,
            codigo="referencia-outra-versao",
            citacao_es="Referencia de otra versión.",
        )
        with self.assertRaises(ValidationError):
            SubareaReferenciaGuia.objects.create(
                subarea=self.subarea,
                referencia=referencia_outra_versao,
                ordem=3,
            )
