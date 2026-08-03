from datetime import date, timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.recorder import MigrationRecorder
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    AtribuicaoPapelVinculo,
    EFS,
    EpisodioVinculoUsuarioEFS,
    EventoVinculoUsuarioEFS,
    Experiencia,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    Pais,
    PapelInstitucional,
    Setor,
    TipoExperiencia,
    VinculoUsuarioEFS,
)


class Fase2A1MigrationSchemaTests(TestCase):
    def test_migrations_e_constraints_estao_aplicadas(self):
        aplicadas = set(MigrationRecorder(connection).applied_migrations())
        self.assertIn(("praticas", "0010_fase2a1_lote_importacao"), aplicadas)
        self.assertIn(("praticas", "0011_fase2a1_vinculo_efs"), aplicadas)

        constraints_esperadas = {
            LoteImportacaoConteudo._meta.db_table: {
                "lote_sha256_hex_64",
                "lote_final_ge_inicio",
                "lote_status_final_com_data",
                "lote_falha_detalhada",
                "lote_reversao_detalhada",
            },
            ItemLoteImportacaoConteudo._meta.db_table: {"item_lote_origem_unico"},
            VinculoUsuarioEFS._meta.db_table: {"vinculo_usuario_efs_unico"},
            EpisodioVinculoUsuarioEFS._meta.db_table: {
                "episodio_corrente_unico",
                "episodio_fim_ge_inicio",
                "episodio_ativo_decidido",
                "episodio_suspenso_com_inicio",
                "episodio_decisao_detalhada",
                "episodio_encerrado_com_fim",
            },
            AtribuicaoPapelVinculo._meta.db_table: {
                "atribuicao_ativa_unica",
                "atribuicao_revogacao_completa",
            },
            EventoVinculoUsuarioEFS._meta.db_table: {
                "evento_papel_exige_papel",
                "evento_item_exige_lote",
            },
        }

        with connection.cursor() as cursor:
            for tabela, nomes in constraints_esperadas.items():
                with self.subTest(tabela=tabela):
                    existentes = set(connection.introspection.get_constraints(cursor, tabela))
                    self.assertTrue(nomes.issubset(existentes), nomes - existentes)

    def test_migrations_nao_carregam_papeis_vinculos_ou_lotes(self):
        for model in (
            PapelInstitucional,
            VinculoUsuarioEFS,
            EpisodioVinculoUsuarioEFS,
            AtribuicaoPapelVinculo,
            EventoVinculoUsuarioEFS,
            LoteImportacaoConteudo,
            ItemLoteImportacaoConteudo,
        ):
            with self.subTest(model=model.__name__):
                self.assertEqual(model.objects.count(), 0)


class Fase2A1VinculoEFSTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.usuario = User.objects.create_user(
            username="usuario_fase2a1",
            email="contato@efs.example.org",
            password="SenhaForte123!",
        )
        cls.outro_usuario = User.objects.create_user(
            username="outro_fase2a1",
            email="contato@efs.example.org",
            password="SenhaForte123!",
        )
        cls.aprovador = User.objects.create_user(
            username="aprovador_fase2a1",
            password="SenhaForte123!",
        )
        cls.staff = User.objects.create_user(
            username="staff_fase2a1",
            password="SenhaForte123!",
            is_staff=True,
        )
        cls.pais = Pais.objects.create(nome="Pais Fase 2A.1", sigla="F21")
        cls.efs = EFS.objects.create(nome="EFS Fase 2A.1", sigla="EFS21", pais=cls.pais)
        cls.outra_efs = EFS.objects.create(nome="Outra EFS Fase 2A.1", sigla="OE21", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Tipo Fase 2A.1")
        cls.setor = Setor.objects.create(nome="Setor Fase 2A.1")

    def criar_vinculo(self, usuario=None, efs=None):
        return VinculoUsuarioEFS.objects.create(
            usuario=usuario or self.usuario,
            efs=efs or self.efs,
        )

    def criar_episodio_ativo(self, vinculo=None):
        return EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=vinculo or self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
            origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            data_inicio=date.today(),
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
        )

    def criar_papel(self, codigo="papel_teste"):
        return PapelInstitucional.objects.create(
            codigo=codigo,
            nome="Papel de teste",
            nome_es="Rol de prueba",
            nome_en="Test role",
            ativo=True,
        )

    def criar_lote(self, sufixo="a"):
        return LoteImportacaoConteudo.objects.create(
            fonte=f"fonte-{sufixo}.json",
            sha256=sufixo[0] * 64,
            versao_fonte=f"versao-{sufixo}",
            executado_por=self.aprovador,
        )

    def criar_experiencia(self, autor, titulo, efs=None, email="contato@efs.example.org"):
        return Experiencia.objects.create(
            autor=autor,
            titulo=titulo,
            efs=efs or self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            ano_execucao=2026,
            setor=self.setor,
            email_contato=email,
            descricao="Descricao para teste da fundacao usuario-EFS.",
            status_publicacao=Experiencia.StatusPublicacao.RASCUNHO,
        )

    def test_vinculo_canonico_permite_relacoes_muitos_para_muitos(self):
        primeiro = self.criar_vinculo()
        mesmo_usuario_outra_efs = self.criar_vinculo(efs=self.outra_efs)
        outro_usuario_mesma_efs = self.criar_vinculo(usuario=self.outro_usuario)

        self.assertEqual(primeiro.usuario, self.usuario)
        self.assertEqual(primeiro.efs, self.efs)
        self.assertEqual(self.usuario.vinculos_efs.count(), 2)
        self.assertEqual(self.efs.vinculos_usuarios.count(), 2)
        self.assertNotEqual(primeiro.pk, mesmo_usuario_outra_efs.pk)
        self.assertNotEqual(primeiro.pk, outro_usuario_mesma_efs.pk)

    def test_vinculo_usuario_efs_e_unico_e_protegido(self):
        self.criar_vinculo()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.criar_vinculo()
        with self.assertRaises(ProtectedError):
            self.usuario.delete()
        with self.assertRaises(ProtectedError):
            self.efs.delete()

    def test_multiplos_episodios_historicos_sao_preservados(self):
        vinculo = self.criar_vinculo()
        encerrado = EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=vinculo,
            status=EpisodioVinculoUsuarioEFS.Status.ENCERRADO,
            origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today() - timedelta(days=1),
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
            justificativa_decisao="Ciclo encerrado para teste.",
        )
        rejeitado = EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=vinculo,
            status=EpisodioVinculoUsuarioEFS.Status.REJEITADO,
            origem=EpisodioVinculoUsuarioEFS.Origem.SOLICITACAO,
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
            justificativa_decisao="Solicitacao rejeitada para teste.",
        )

        self.assertEqual(list(vinculo.episodios.order_by("pk")), [encerrado, rejeitado])

    def test_nao_permite_dois_episodios_correntes(self):
        vinculo = self.criar_vinculo()
        EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=vinculo,
            status=EpisodioVinculoUsuarioEFS.Status.PENDENTE,
            origem=EpisodioVinculoUsuarioEFS.Origem.SOLICITACAO,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            EpisodioVinculoUsuarioEFS.objects.create(
                vinculo=vinculo,
                status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                data_inicio=date.today(),
                decidido_em=timezone.now(),
                decidido_por=self.aprovador,
            )

    def test_constraints_de_data_e_decisao_dos_episodios(self):
        vinculo = self.criar_vinculo()
        invalidos = (
            EpisodioVinculoUsuarioEFS(
                vinculo=vinculo,
                status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            ),
            EpisodioVinculoUsuarioEFS(
                vinculo=vinculo,
                status=EpisodioVinculoUsuarioEFS.Status.SUSPENSO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                decidido_em=timezone.now(),
                decidido_por=self.aprovador,
            ),
            EpisodioVinculoUsuarioEFS(
                vinculo=vinculo,
                status=EpisodioVinculoUsuarioEFS.Status.ENCERRADO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                data_inicio=date.today(),
                decidido_em=timezone.now(),
                decidido_por=self.aprovador,
                justificativa_decisao="Encerramento sem data final.",
            ),
            EpisodioVinculoUsuarioEFS(
                vinculo=vinculo,
                status=EpisodioVinculoUsuarioEFS.Status.ENCERRADO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                data_inicio=date.today(),
                data_fim=date.today() - timedelta(days=1),
                decidido_em=timezone.now(),
                decidido_por=self.aprovador,
                justificativa_decisao="Datas invalidas.",
            ),
        )

        for episodio in invalidos:
            with self.subTest(status=episodio.status, fim=episodio.data_fim):
                with self.assertRaises(ValidationError):
                    episodio.full_clean()

    def test_episodio_suspenso_sem_inicio_falha_em_full_clean(self):
        episodio = EpisodioVinculoUsuarioEFS(
            vinculo=self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.SUSPENSO,
            origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
            justificativa_decisao="Suspensao sem inicio para teste.",
        )

        with self.assertRaisesMessage(ValidationError, "episodio_suspenso_com_inicio"):
            episodio.full_clean()

    def test_banco_rejeita_episodio_suspenso_sem_inicio(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            EpisodioVinculoUsuarioEFS.objects.create(
                vinculo=self.criar_vinculo(),
                status=EpisodioVinculoUsuarioEFS.Status.SUSPENSO,
                origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                decidido_em=timezone.now(),
                decidido_por=self.aprovador,
                justificativa_decisao="Suspensao sem inicio para teste de banco.",
            )

    def test_episodio_suspenso_com_inicio_e_decisao_e_valido(self):
        episodio = EpisodioVinculoUsuarioEFS(
            vinculo=self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.SUSPENSO,
            origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            data_inicio=date.today(),
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
            justificativa_decisao="Suspensao valida para teste.",
        )

        episodio.full_clean()
        episodio.save()

        self.assertIsNotNone(episodio.pk)
        self.assertEqual(episodio.status, EpisodioVinculoUsuarioEFS.Status.SUSPENSO)

    def test_usuario_nao_pode_decidir_o_proprio_episodio(self):
        episodio = EpisodioVinculoUsuarioEFS(
            vinculo=self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
            origem=EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
            data_inicio=date.today(),
            decidido_em=timezone.now(),
            decidido_por=self.usuario,
        )

        with self.assertRaisesMessage(ValidationError, "proprio episodio"):
            episodio.full_clean()

    def test_atribuicao_temporal_permite_novo_ciclo_apos_revogacao(self):
        episodio = self.criar_episodio_ativo()
        papel = self.criar_papel()
        AtribuicaoPapelVinculo.objects.create(
            episodio=episodio,
            papel=papel,
            atribuido_por=self.aprovador,
            revogado_em=timezone.now(),
            revogado_por=self.aprovador,
            justificativa_revogacao="Revogacao registrada.",
        )
        atual = AtribuicaoPapelVinculo.objects.create(
            episodio=episodio,
            papel=papel,
            atribuido_por=self.aprovador,
        )

        self.assertIsNone(atual.revogado_em)
        self.assertEqual(episodio.atribuicoes.count(), 2)

    def test_nao_permite_duas_atribuicoes_ativas_do_mesmo_papel(self):
        episodio = self.criar_episodio_ativo()
        papel = self.criar_papel()
        AtribuicaoPapelVinculo.objects.create(
            episodio=episodio,
            papel=papel,
            atribuido_por=self.aprovador,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            AtribuicaoPapelVinculo.objects.create(
                episodio=episodio,
                papel=papel,
                atribuido_por=self.aprovador,
            )

    def test_revogacao_exige_data_responsavel_e_justificativa(self):
        atribuicao = AtribuicaoPapelVinculo(
            episodio=self.criar_episodio_ativo(),
            papel=self.criar_papel(),
            atribuido_por=self.aprovador,
            revogado_em=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            atribuicao.full_clean()

    def test_atribuicao_administrativa_exige_responsavel(self):
        atribuicao = AtribuicaoPapelVinculo(
            episodio=self.criar_episodio_ativo(),
            papel=self.criar_papel(),
        )

        with self.assertRaisesMessage(ValidationError, "responsavel pela atribuicao"):
            atribuicao.full_clean()

    def test_atribuicao_de_solicitacao_exige_responsavel(self):
        episodio = EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
            origem=EpisodioVinculoUsuarioEFS.Origem.SOLICITACAO,
            data_inicio=date.today(),
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
        )
        atribuicao = AtribuicaoPapelVinculo(
            episodio=episodio,
            papel=self.criar_papel(),
        )

        with self.assertRaisesMessage(ValidationError, "responsavel pela atribuicao"):
            atribuicao.full_clean()

    def test_atribuicao_de_migracao_aceita_responsavel_nulo(self):
        episodio = EpisodioVinculoUsuarioEFS.objects.create(
            vinculo=self.criar_vinculo(),
            status=EpisodioVinculoUsuarioEFS.Status.ATIVO,
            origem=EpisodioVinculoUsuarioEFS.Origem.MIGRACAO,
            data_inicio=date.today(),
            decidido_em=timezone.now(),
            decidido_por=self.aprovador,
        )
        atribuicao = AtribuicaoPapelVinculo(
            episodio=episodio,
            papel=self.criar_papel(),
        )

        atribuicao.full_clean()
        atribuicao.save()

        self.assertIsNone(atribuicao.atribuido_por)

    def test_atribuicao_administrativa_aceita_responsavel_distinto(self):
        atribuicao = AtribuicaoPapelVinculo(
            episodio=self.criar_episodio_ativo(),
            papel=self.criar_papel(),
            atribuido_por=self.aprovador,
        )

        atribuicao.full_clean()
        atribuicao.save()

        self.assertEqual(atribuicao.atribuido_por, self.aprovador)

    def test_nao_permite_autoatribuicao_ou_autorrevogacao(self):
        episodio = self.criar_episodio_ativo()
        papel = self.criar_papel()
        autoatribuicao = AtribuicaoPapelVinculo(
            episodio=episodio,
            papel=papel,
            atribuido_por=self.usuario,
        )
        with self.assertRaisesMessage(ValidationError, "atribuir papel a si mesmo"):
            autoatribuicao.full_clean()

        atribuicao = AtribuicaoPapelVinculo.objects.create(
            episodio=episodio,
            papel=papel,
            atribuido_por=self.aprovador,
        )
        atribuicao.revogado_em = timezone.now()
        atribuicao.revogado_por = self.usuario
        atribuicao.justificativa_revogacao = "Tentativa de autorrevogacao."
        with self.assertRaisesMessage(ValidationError, "revogar o proprio papel"):
            atribuicao.full_clean()

    def test_evento_de_papel_exige_papel(self):
        evento = EventoVinculoUsuarioEFS(
            episodio=self.criar_episodio_ativo(),
            acao=EventoVinculoUsuarioEFS.Acao.PAPEL_ADICIONADO,
            responsavel=self.aprovador,
        )

        with self.assertRaises(ValidationError):
            evento.save()

    def test_evento_valida_coerencia_com_episodio_e_atribuicao(self):
        primeiro = self.criar_episodio_ativo()
        segundo = self.criar_episodio_ativo(self.criar_vinculo(efs=self.outra_efs))
        papel = self.criar_papel()
        atribuicao = AtribuicaoPapelVinculo.objects.create(
            episodio=segundo,
            papel=papel,
            atribuido_por=self.aprovador,
        )
        evento = EventoVinculoUsuarioEFS(
            episodio=primeiro,
            papel=papel,
            atribuicao_papel=atribuicao,
            acao=EventoVinculoUsuarioEFS.Acao.PAPEL_ADICIONADO,
            responsavel=self.aprovador,
        )

        with self.assertRaisesMessage(ValidationError, "pertencer ao episodio"):
            evento.save()

    def test_evento_valida_coerencia_entre_item_e_lote(self):
        episodio = self.criar_episodio_ativo()
        primeiro_lote = self.criar_lote("a")
        segundo_lote = self.criar_lote("b")
        item = ItemLoteImportacaoConteudo.objects.create(
            lote=primeiro_lote,
            entidade=ItemLoteImportacaoConteudo.Entidade.EPISODIO_VINCULO_USUARIO_EFS,
            codigo_origem="episodio-1",
            operacao=ItemLoteImportacaoConteudo.Operacao.CRIADO,
        )
        evento = EventoVinculoUsuarioEFS(
            episodio=episodio,
            lote_origem=segundo_lote,
            item_lote_origem=item,
            acao=EventoVinculoUsuarioEFS.Acao.ATIVADO,
            responsavel=self.aprovador,
        )

        with self.assertRaisesMessage(ValidationError, "pertencer ao lote"):
            evento.save()

    def test_item_e_unico_no_lote_e_possui_allowlist_aprovada(self):
        lote = self.criar_lote()
        dados = {
            "lote": lote,
            "entidade": ItemLoteImportacaoConteudo.Entidade.VINCULO_USUARIO_EFS,
            "codigo_origem": "vinculo-1",
            "operacao": ItemLoteImportacaoConteudo.Operacao.CRIADO,
        }
        ItemLoteImportacaoConteudo.objects.create(**dados)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ItemLoteImportacaoConteudo.objects.create(**dados)

        self.assertEqual(
            {valor for valor, _rotulo in ItemLoteImportacaoConteudo.Entidade.choices},
            {
                "marco",
                "ferramenta",
                "setor",
                "versao_guia",
                "eixo",
                "subeixo",
                "subarea",
                "pergunta",
                "referencia",
                "experiencia_pergunta_guia",
                "vinculo_usuario_efs",
                "episodio_vinculo_usuario_efs",
                "atribuicao_papel_vinculo",
            },
        )

    def test_snapshot_rejeita_chave_sensivel(self):
        item = ItemLoteImportacaoConteudo(
            lote=self.criar_lote(),
            entidade=ItemLoteImportacaoConteudo.Entidade.VINCULO_USUARIO_EFS,
            codigo_origem="vinculo-com-token",
            operacao=ItemLoteImportacaoConteudo.Operacao.ATUALIZADO,
            snapshot_anterior={"token_acesso": "nao-deve-ser-armazenado"},
        )

        with self.assertRaisesMessage(ValidationError, "dado sensivel"):
            item.full_clean()

    def test_lote_valida_hash_status_falha_e_reversao(self):
        lote = self.criar_lote()
        lote.sha256 = "hash-invalido"
        with self.assertRaises(ValidationError):
            lote.full_clean()

        lote.sha256 = "a" * 64
        lote.status = LoteImportacaoConteudo.Status.FALHOU
        lote.finalizado_em = timezone.now()
        lote.mensagem_sanitizada = "Falha controlada."
        lote.contagens_realizadas = {}
        with self.assertRaises(ValidationError):
            lote.full_clean()

        lote.status = LoteImportacaoConteudo.Status.REVERTIDO
        lote.contagens_realizadas = {"vinculo_usuario_efs": {"falhos": 1}}
        with self.assertRaises(ValidationError):
            lote.full_clean()

    def test_eventos_sao_imutaveis_no_model_e_no_admin(self):
        evento = EventoVinculoUsuarioEFS.objects.create(
            episodio=self.criar_episodio_ativo(),
            acao=EventoVinculoUsuarioEFS.Acao.ATIVADO,
            responsavel=self.aprovador,
        )
        evento.justificativa = "Tentativa de alteracao."
        with self.assertRaisesMessage(ValidationError, "imutaveis"):
            evento.save()
        with self.assertRaisesMessage(ValidationError, "nao podem ser excluidos"):
            evento.delete()

        request = RequestFactory().get("/admin/")
        request.user = self.staff
        model_admin = admin.site._registry[EventoVinculoUsuarioEFS]
        self.assertIsNone(model_admin.actions)
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, evento))
        self.assertFalse(model_admin.has_delete_permission(request, evento))

    def test_vinculo_ativo_e_papel_nao_concedem_autorizacao(self):
        experiencia_alheia = self.criar_experiencia(
            autor=self.outro_usuario,
            titulo="Experiencia alheia com mesmo e-mail e dominio",
        )
        episodio = self.criar_episodio_ativo(self.criar_vinculo())
        AtribuicaoPapelVinculo.objects.create(
            episodio=episodio,
            papel=self.criar_papel(),
            atribuido_por=self.aprovador,
        )
        self.client.force_login(self.usuario)

        response = self.client.get(reverse("editar_boa_pratica", args=[experiencia_alheia.pk]))

        self.assertRedirects(response, reverse("meus_envios"))
        self.assertFalse(self.usuario.has_perm("praticas.change_experiencia", experiencia_alheia))
        self.assertEqual(self.usuario.user_permissions.count(), 0)
        self.assertEqual(self.usuario.groups.count(), 0)

    def test_registro_legado_sem_autor_continua_restrito_a_staff(self):
        legado = self.criar_experiencia(autor=None, titulo="Registro legado sem autor")
        url = reverse("editar_boa_pratica", args=[legado.pk])

        self.client.force_login(self.usuario)
        self.assertRedirects(self.client.get(url), reverse("meus_envios"))

        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(url).status_code, 200)
