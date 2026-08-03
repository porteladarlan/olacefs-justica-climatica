import hashlib
import json
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from praticas.models import (
    Ferramenta,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    Setor,
)


class Command(BaseCommand):
    help = "Importa, reconcilia ou reverte as 15 ferramentas oficiais da Fase 2C."

    SHA256_FONTE_OFICIAL = "1a6c4444a5755a9ae3983e2af53b8764a90401774d2accb7d382a8f57dda29ef"
    VERSAO_FONTE = "fase2c-ferramentas-v1"
    QUANTIDADE_ESPERADA = 15
    CODIGOS_CANONICOS = {
        "Climate Scanner": "fase2c-climate-scanner",
        "Auditoría Cooperativa Global de Adaptación al Cambio Climático": (
            "fase2c-auditoria-cooperativa-adaptacion"
        ),
        "Guía sobre Auditoría Ambiental": "fase2c-guia-auditoria-ambiental",
        "Referencial para Evaluación de la Gobernanza en Políticas Públicas": (
            "fase2c-referencial-gobernanza-politicas-publicas"
        ),
        "Auditoría Coordinada sobre Recursos Hídricos": "fase2c-auditoria-recursos-hidricos",
        "Guía Práctica de Auditoría para la Transición Energética": (
            "fase2c-guia-transicion-energetica"
        ),
        (
            "Auditoría Coordinada sobre Preparación para la Implementación de los ODS "
            "con foco en la Meta 2.4 - Producción sostenible de alimentos"
        ): "fase2c-auditoria-ods-meta-2-4",
        "Auditoría Coordinada en Áreas Protegidas": "fase2c-auditoria-areas-protegidas",
        "Auditing Biodiversity: Guidance for Supreme Audit Institutions": (
            "fase2c-auditing-biodiversity"
        ),
        "GUID 5330 – Orientaciones sobre la Auditoría de la Gestión de Desastres": (
            "fase2c-guid-5330-gestion-desastres"
        ),
        (
            "Fiscalización Superior en México y la Región Latinoamericana para la "
            "Prevención de Desastres"
        ): "fase2c-fiscalizacion-prevencion-desastres",
        "EI Auditors' Toolkit – Extractive Industries Auditor Toolkit": (
            "fase2c-ei-auditors-toolkit"
        ),
        "Auditoría Coordinada de Pasivos Ambientales Mineros": (
            "fase2c-auditoria-pasivos-mineros"
        ),
        (
            "Géner.A / IMPGAI – Instrumento de Medición de la Perspectiva de Género "
            "en el Ámbito Institucional"
        ): "fase2c-gener-a-impgai",
        (
            "IMPGPP – Instrumento de Medición de la Perspectiva de Género en "
            "Políticas Públicas"
        ): "fase2c-impgpp-politicas-publicas",
    }
    TITULOS_ORDEM_ORIGINAL = tuple(CODIGOS_CANONICOS)
    SETORES_CANONICOS = {
        "Agua y saneamiento",
        "Alimentación y agricultura",
        "Bosques, biodiversidad y ecosistemas",
        "Energía",
        "Gestión de riesgo y desastres",
        "Industria extractiva y minería",
        "Transversal",
        "Transversal – Género",
    }
    CAMPOS_OBRIGATORIOS = (
        "sector",
        "nombre",
        "responsable",
        "ano",
        "desc",
        "link",
    )
    CAMPOS_CONTROLADOS = (
        "titulo_es",
        "descricao_es",
        "responsavel",
        "periodo",
        "setor_id",
        "url",
        "ordem",
    )
    ESTADO_POS_PREFIXO = "estado_pos_sha256:"

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            help="Caminho do HTML oficial que contém window.PJC_DATA.",
        )
        parser.add_argument(
            "--executado-por",
            required=True,
            help="Username de uma pessoa usuária staff ativa responsável pela operação.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valida e planeja a importação sem escrever no banco.",
        )
        parser.add_argument(
            "--publicar",
            action="store_true",
            help=(
                "Publica registros novos ou promove registros existentes aderentes "
                "ou reconciliados."
            ),
        )
        parser.add_argument(
            "--atualizar",
            action="store_true",
            help="Reconcilia explicitamente os campos controlados pela fonte.",
        )
        parser.add_argument(
            "--reverter-lote",
            metavar="IDENTIFICADOR",
            help=(
                "Reverte, com validações de segurança, um lote concluído ou com "
                "divergências da Fase 2C."
            ),
        )

    def handle(self, *args, **options):
        self._validar_opcoes(options)
        executor = self._obter_executor(options["executado_por"])
        identificador_reversao = options.get("reverter_lote")
        if identificador_reversao:
            self._reverter_lote(identificador_reversao, executor)
            return

        caminho = Path(options["arquivo"]).expanduser().resolve()
        conteudo, sha256 = self._ler_fonte(caminho)
        ferramentas = self._extrair_ferramentas(conteudo)
        self._validar_ferramentas(ferramentas)
        publicar = bool(options.get("publicar"))
        atualizar = bool(options.get("atualizar"))

        if options.get("dry_run"):
            plano = self._planejar_importacao(ferramentas, publicar, atualizar)
            self.stdout.write(
                self.style.SUCCESS(
                    "DRY-RUN APROVADO: "
                    f"{len(ferramentas)} ferramentas, "
                    f"{len(self.SETORES_CANONICOS)} setores, SHA-256 {sha256}. "
                    f"Criadas como rascunho: {plano['criadas_como_rascunho']}; "
                    f"publicadas: {plano['publicadas']}; "
                    f"atualizadas: {plano['atualizadas']}; "
                    f"ignoradas: {plano['ignoradas']}; "
                    f"divergências: {plano['divergencias']}. "
                    f"Executor validado: {executor.get_username()}."
                )
            )
            return

        self._executar_importacao(caminho, sha256, ferramentas, executor, publicar, atualizar)

    def _validar_opcoes(self, options):
        reversao = bool(options.get("reverter_lote"))
        arquivo = options.get("arquivo")
        if reversao:
            if arquivo or options.get("dry_run") or options.get("publicar") or options.get("atualizar"):
                raise CommandError(
                    "A reversão não pode ser combinada com arquivo, dry-run, publicação ou atualização."
                )
            return
        if not arquivo:
            raise CommandError("A importação normal exige o argumento --arquivo.")

    def _executar_importacao(
        self,
        caminho,
        sha256,
        ferramentas,
        executor,
        publicar,
        atualizar,
    ):
        sha256_banco_antes = self._hash_banco_sqlite_atual()
        relatorio = {
            "db_sha256_antes": sha256_banco_antes,
            "fonte_validada": True,
            "publicacao_solicitada": publicar,
            "atualizacao_solicitada": atualizar,
            "ferramentas": [],
        }
        lote = LoteImportacaoConteudo(
            fonte=f"prototipo-oficial/{caminho.name}",
            sha256=sha256,
            versao_fonte=self.VERSAO_FONTE,
            executado_por=executor,
            status=LoteImportacaoConteudo.Status.EM_EXECUCAO,
            contagens_esperadas={
                "ferramentas": self.QUANTIDADE_ESPERADA,
                "setores_canonicos": len(self.SETORES_CANONICOS),
            },
            contagens_realizadas={"ferramentas_lidas": len(ferramentas)},
            relatorio_divergencias=relatorio,
        )
        lote.full_clean()
        lote.save()

        contagens = self._contagens_iniciais(ferramentas)
        try:
            with transaction.atomic():
                self._importar_conteudos(
                    lote,
                    ferramentas,
                    contagens,
                    relatorio,
                    publicar,
                    atualizar,
                )
        except Exception as exc:
            # O lote existe fora do atomic interno para que o rollback integral
            # dos conteúdos não elimine a evidência sanitizada da tentativa.
            contagens["rollback_aplicado"] = True
            lote.refresh_from_db()
            lote.status = LoteImportacaoConteudo.Status.FALHOU
            lote.finalizado_em = timezone.now()
            lote.contagens_realizadas = contagens
            lote.relatorio_divergencias = relatorio
            lote.mensagem_sanitizada = (
                "A transação de conteúdo da Fase 2C falhou e foi revertida integralmente."
            )
            lote.full_clean()
            lote.save(
                update_fields=(
                    "status",
                    "finalizado_em",
                    "contagens_realizadas",
                    "relatorio_divergencias",
                    "mensagem_sanitizada",
                )
            )
            raise CommandError(
                "A importação falhou; a transação foi revertida e o lote "
                f"{lote.identificador} registrou a ocorrência."
            ) from exc

        lote.status = (
            LoteImportacaoConteudo.Status.COM_DIVERGENCIAS
            if contagens["divergencias_pendentes"]
            else LoteImportacaoConteudo.Status.CONCLUIDO
        )
        lote.finalizado_em = timezone.now()
        lote.contagens_realizadas = contagens
        lote.relatorio_divergencias = relatorio
        lote.mensagem_sanitizada = (
            "A carga terminou com divergências não reconciliadas."
            if contagens["divergencias_pendentes"]
            else ""
        )
        lote.full_clean()
        lote.save(
            update_fields=(
                "status",
                "finalizado_em",
                "contagens_realizadas",
                "relatorio_divergencias",
                "mensagem_sanitizada",
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Carga finalizada: lote {lote.identificador}, "
                f"{contagens['ferramentas_processadas']} ferramentas processadas, "
                f"{contagens['divergencias_pendentes']} divergências pendentes."
            )
        )

    def _contagens_iniciais(self, ferramentas):
        return {
            "ferramentas_lidas": len(ferramentas),
            "ferramentas_processadas": 0,
            "ferramentas_criadas": 0,
            "ferramentas_criadas_como_rascunho": 0,
            "ferramentas_atualizadas": 0,
            "ferramentas_publicadas": 0,
            "ferramentas_ignoradas": 0,
            "ferramentas_divergentes": 0,
            "divergencias_pendentes": 0,
            "setores_processados": 0,
            "setores_criados": 0,
            "setores_reutilizados": 0,
        }

    def _ler_fonte(self, caminho):
        if not caminho.is_file():
            raise CommandError("O arquivo-fonte informado não existe ou não é um arquivo.")
        conteudo_bytes = caminho.read_bytes()
        sha256 = hashlib.sha256(conteudo_bytes).hexdigest()
        if sha256 != self.SHA256_FONTE_OFICIAL:
            raise CommandError(
                "O SHA-256 do arquivo não corresponde ao HTML oficial aprovado para a Fase 2C."
            )
        try:
            conteudo = conteudo_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CommandError("O HTML oficial deve estar codificado em UTF-8.") from exc
        return conteudo, sha256

    def _extrair_ferramentas(self, conteudo):
        marcador = "window.PJC_DATA = "
        if conteudo.count(marcador) != 1:
            raise CommandError("A fonte deve conter uma única declaração window.PJC_DATA.")
        trecho = conteudo.split(marcador, 1)[1]
        try:
            dados, _fim = json.JSONDecoder().raw_decode(trecho)
        except json.JSONDecodeError as exc:
            raise CommandError("Não foi possível interpretar o bloco JSON window.PJC_DATA.") from exc
        ferramentas = dados.get("herramientas")
        if not isinstance(ferramentas, list):
            raise CommandError("A fonte não contém a lista de herramientas esperada.")
        return ferramentas

    def _validar_ferramentas(self, ferramentas):
        codigos = tuple(self.CODIGOS_CANONICOS.values())
        if len(self.CODIGOS_CANONICOS) != self.QUANTIDADE_ESPERADA or len(set(codigos)) != len(
            codigos
        ):
            raise CommandError("A tabela interna de códigos canônicos da Fase 2C é inválida.")
        if len(ferramentas) != self.QUANTIDADE_ESPERADA:
            raise CommandError(
                f"A fonte deve conter exatamente {self.QUANTIDADE_ESPERADA} ferramentas."
            )

        titulos = set()
        setores = set()
        validador_url = URLValidator(schemes=["http", "https"])
        for ordem, ferramenta in enumerate(ferramentas, start=1):
            if not isinstance(ferramenta, dict):
                raise CommandError(f"A ferramenta {ordem} não é um objeto válido.")
            for campo in self.CAMPOS_OBRIGATORIOS:
                valor = ferramenta.get(campo)
                if not isinstance(valor, str) or not valor.strip():
                    raise CommandError(
                        f"A ferramenta {ordem} não possui o campo obrigatório {campo}."
                    )
            titulo = ferramenta["nombre"]
            if titulo in titulos:
                raise CommandError("A fonte contém títulos de ferramenta duplicados.")
            if titulo not in self.CODIGOS_CANONICOS:
                raise CommandError("A fonte contém um título de ferramenta desconhecido.")
            titulos.add(titulo)
            setores.add(ferramenta["sector"])
            try:
                validador_url(ferramenta["link"])
            except ValidationError as exc:
                raise CommandError(f"A ferramenta {ordem} possui URL inválida.") from exc

        if titulos != set(self.CODIGOS_CANONICOS):
            raise CommandError("A fonte não contém os 15 títulos canônicos aprovados.")
        if setores != self.SETORES_CANONICOS:
            raise CommandError("Os setores da fonte divergem dos oito setores canônicos aprovados.")

    def _obter_executor(self, username):
        usuario_model = get_user_model()
        try:
            return usuario_model.objects.get(
                username=username,
                is_active=True,
                is_staff=True,
            )
        except usuario_model.DoesNotExist as exc:
            raise CommandError(
                "O executor deve ser uma pessoa usuária staff ativa existente."
            ) from exc

    def _hash_banco_sqlite_atual(self):
        if connection.vendor != "sqlite":
            return "nao_aplicavel"
        nome_banco = str(connection.settings_dict["NAME"])
        if not nome_banco or nome_banco.startswith("file:"):
            return "nao_aplicavel"
        connection.close()
        caminho_banco = Path(nome_banco)
        if not caminho_banco.is_file():
            raise CommandError("Não foi possível localizar o SQLite antes da carga.")
        digest = hashlib.sha256()
        with caminho_banco.open("rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
        return digest.hexdigest()

    def _planejar_importacao(self, ferramentas, publicar, atualizar):
        plano = {
            "criadas_como_rascunho": 0,
            "publicadas": 0,
            "atualizadas": 0,
            "ignoradas": 0,
            "divergencias": 0,
        }
        setores_existentes = {
            nome: self._localizar_setor(nome) for nome in self.SETORES_CANONICOS
        }
        for ordem, dados in enumerate(ferramentas, start=1):
            ferramenta, legado = self._resolver_ferramenta(dados)
            if ferramenta is None:
                if publicar:
                    plano["publicadas"] += 1
                else:
                    plano["criadas_como_rascunho"] += 1
                continue
            setor = setores_existentes[dados["sector"]]
            campos = self._campos_divergentes(ferramenta, dados, ordem, setor, legado)
            if campos:
                plano["divergencias"] += 1
                if atualizar:
                    plano["atualizadas"] += 1
                else:
                    plano["ignoradas"] += 1
            pode_publicar_existente = not campos or atualizar
            if (
                publicar
                and pode_publicar_existente
                and ferramenta.situacao != Ferramenta.Situacao.PUBLICADA
            ):
                plano["publicadas"] += 1
            elif not campos:
                plano["ignoradas"] += 1
        return plano

    def _importar_conteudos(
        self,
        lote,
        ferramentas,
        contagens,
        relatorio,
        publicar,
        atualizar,
    ):
        setores_por_nome = {}
        for nome_setor in dict.fromkeys(item["sector"] for item in ferramentas):
            setor, criado = self._obter_ou_criar_setor(nome_setor)
            setores_por_nome[nome_setor] = setor
            contagens["setores_processados"] += 1
            if criado:
                contagens["setores_criados"] += 1
            else:
                contagens["setores_reutilizados"] += 1
            self._registrar_item_setor(lote, setor, nome_setor, criado)

        snapshots_ordem = self._preparar_alteracoes_de_ordem(
            ferramentas,
            setores_por_nome,
            atualizar,
        )
        for ordem, dados in enumerate(ferramentas, start=1):
            self._importar_ferramenta(
                lote,
                ordem,
                dados,
                setores_por_nome[dados["sector"]],
                contagens,
                relatorio,
                publicar,
                atualizar,
                snapshots_ordem,
            )

    def _localizar_setor(self, nome_es):
        candidatos = list(
            Setor.objects.filter(
                Q(nome_es__iexact=nome_es) | Q(nome__iexact=nome_es)
            ).order_by("pk")
        )
        if len(candidatos) > 1:
            raise CommandError(
                "Há mais de um setor compatível com uma classificação canônica da fonte."
            )
        return candidatos[0] if candidatos else None

    def _obter_ou_criar_setor(self, nome_es):
        setor = self._localizar_setor(nome_es)
        if setor:
            return setor, False
        setor = Setor(nome=nome_es, nome_es=nome_es, nome_en="")
        setor.full_clean()
        setor.save()
        return setor, True

    def _registrar_item_setor(self, lote, setor, nome_es, criado):
        hash_estado = self._hash_estado_setor(setor) if criado else ""
        item = ItemLoteImportacaoConteudo(
            lote=lote,
            entidade=ItemLoteImportacaoConteudo.Entidade.SETOR,
            codigo_origem=f"fase2c-setor-{slugify(nome_es)}",
            objeto_pk=str(setor.pk),
            operacao=(
                ItemLoteImportacaoConteudo.Operacao.CRIADO
                if criado
                else ItemLoteImportacaoConteudo.Operacao.IGNORADO
            ),
            snapshot_anterior={},
            status_rollback=(
                ItemLoteImportacaoConteudo.StatusRollback.PENDENTE
                if criado
                else ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL
            ),
            mensagem=(
                f"Setor canônico criado pela carga. {self.ESTADO_POS_PREFIXO}{hash_estado}"
                if criado
                else "Setor existente reutilizado sem alteração."
            ),
        )
        item.full_clean()
        item.save()

    def _preparar_alteracoes_de_ordem(self, ferramentas, setores_por_nome, atualizar):
        snapshots = {}
        if not atualizar:
            return snapshots
        candidatos = []
        for ordem, dados in enumerate(ferramentas, start=1):
            ferramenta, legado = self._resolver_ferramenta(dados)
            if ferramenta is None:
                continue
            campos = self._campos_divergentes(
                ferramenta,
                dados,
                ordem,
                setores_por_nome[dados["sector"]],
                legado,
            )
            if "ordem" in campos:
                candidatos.append(ferramenta)
                snapshots[ferramenta.pk] = self._snapshot_ferramenta(ferramenta)
        if not candidatos:
            return snapshots

        ocupadas = set(
            Ferramenta.objects.exclude(pk__in=[item.pk for item in candidatos]).values_list(
                "ordem", flat=True
            )
        )
        temporarias = [valor for valor in range(65535, 65000, -1) if valor not in ocupadas]
        if len(temporarias) < len(candidatos):
            raise CommandError("Não foi possível reservar ordens temporárias para a reconciliação.")
        for ferramenta, ordem_temporaria in zip(candidatos, temporarias):
            ferramenta.ordem = ordem_temporaria
            ferramenta.save(update_fields=("ordem", "atualizado_em"))
        return snapshots

    def _resolver_ferramenta(self, dados):
        titulo = dados["nombre"]
        codigo = self.CODIGOS_CANONICOS[titulo]
        posicao_original = self.TITULOS_ORDEM_ORIGINAL.index(titulo) + 1
        codigo_legado = f"fase2c-ferramenta-{posicao_original:02d}"
        canonica = Ferramenta.objects.filter(codigo=codigo).first()
        legada = Ferramenta.objects.filter(codigo=codigo_legado).first()
        if canonica and legada and canonica.pk != legada.pk:
            raise CommandError("Existe conflito entre os códigos canônico e legado de uma ferramenta.")
        if canonica:
            return canonica, False
        if legada:
            if legada.titulo_es != titulo:
                raise CommandError("Um código legado está associado a um título incompatível.")
            return legada, True
        return None, False

    def _campos_divergentes(self, ferramenta, dados, ordem, setor, legado):
        campos = []
        valores = {
            "titulo_es": dados["nombre"],
            "descricao_es": dados["desc"],
            "responsavel": dados["responsable"],
            "periodo": dados["ano"],
            "url": dados["link"],
            "ordem": ordem,
        }
        for campo, valor in valores.items():
            if getattr(ferramenta, campo) != valor:
                campos.append(campo)
        if setor is None or ferramenta.setor_id != setor.pk:
            campos.append("setor")
        if legado:
            campos.append("codigo")
        return campos

    def _importar_ferramenta(
        self,
        lote,
        ordem,
        dados,
        setor,
        contagens,
        relatorio,
        publicar,
        atualizar,
        snapshots_ordem,
    ):
        codigo = self.CODIGOS_CANONICOS[dados["nombre"]]
        valores_fonte = {
            "titulo_es": dados["nombre"],
            "descricao_es": dados["desc"],
            "responsavel": dados["responsable"],
            "periodo": dados["ano"],
            "setor_id": setor.pk,
            "url": dados["link"],
            "ordem": ordem,
        }
        ferramenta, legado = self._resolver_ferramenta(dados)
        snapshot = {}
        if ferramenta is None:
            situacao = (
                Ferramenta.Situacao.PUBLICADA if publicar else Ferramenta.Situacao.RASCUNHO
            )
            ferramenta = Ferramenta(
                codigo=codigo,
                titulo="",
                titulo_en="",
                descricao="",
                descricao_en="",
                situacao=situacao,
                lote_origem=lote,
                **valores_fonte,
            )
            ferramenta.full_clean()
            ferramenta.save()
            operacao = ItemLoteImportacaoConteudo.Operacao.CRIADO
            status_rollback = ItemLoteImportacaoConteudo.StatusRollback.PENDENTE
            contagens["ferramentas_criadas"] += 1
            if situacao == Ferramenta.Situacao.PUBLICADA:
                contagens["ferramentas_publicadas"] += 1
            else:
                contagens["ferramentas_criadas_como_rascunho"] += 1
            mensagem_base = "Registro criado a partir da fonte oficial."
        else:
            snapshot_original = snapshots_ordem.get(ferramenta.pk)
            if snapshot_original:
                snapshot = snapshot_original
                legado = snapshot["codigo"].startswith("fase2c-ferramenta-")
            campos_divergentes = self._campos_divergentes(
                ferramenta,
                dados,
                ordem,
                setor,
                legado,
            )
            if campos_divergentes:
                contagens["ferramentas_divergentes"] += 1
            reconciliar = bool(campos_divergentes and atualizar)
            pode_publicar_existente = not campos_divergentes or atualizar
            publicar_existente = (
                publicar
                and pode_publicar_existente
                and ferramenta.situacao != Ferramenta.Situacao.PUBLICADA
            )
            if campos_divergentes and not atualizar:
                contagens["divergencias_pendentes"] += 1
                relatorio["ferramentas"].append(
                    {"codigo": codigo, "campos": sorted(campos_divergentes), "reconciliada": False}
                )
            elif campos_divergentes:
                relatorio["ferramentas"].append(
                    {"codigo": codigo, "campos": sorted(campos_divergentes), "reconciliada": True}
                )

            if reconciliar or publicar_existente:
                if not snapshot:
                    snapshot = self._snapshot_ferramenta(ferramenta)
                if reconciliar:
                    for campo, valor in valores_fonte.items():
                        setattr(ferramenta, campo, valor)
                    ferramenta.codigo = codigo
                    ferramenta.lote_origem = lote
                if publicar_existente:
                    ferramenta.situacao = Ferramenta.Situacao.PUBLICADA
                    contagens["ferramentas_publicadas"] += 1
                ferramenta.full_clean()
                ferramenta.save()
                operacao = ItemLoteImportacaoConteudo.Operacao.ATUALIZADO
                status_rollback = ItemLoteImportacaoConteudo.StatusRollback.PENDENTE
                contagens["ferramentas_atualizadas"] += 1
                mensagem_base = (
                    "Registro reconciliado e/ou publicado por opção explícita do comando."
                )
            else:
                operacao = ItemLoteImportacaoConteudo.Operacao.IGNORADO
                status_rollback = ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL
                contagens["ferramentas_ignoradas"] += 1
                mensagem_base = (
                    "Registro preservado; divergências exigem --atualizar."
                    if campos_divergentes
                    else "Registro existente preservado sem alteração."
                )

        mensagem = mensagem_base
        if operacao != ItemLoteImportacaoConteudo.Operacao.IGNORADO:
            mensagem += f" {self.ESTADO_POS_PREFIXO}{self._hash_estado_ferramenta(ferramenta)}"
        item = ItemLoteImportacaoConteudo(
            lote=lote,
            entidade=ItemLoteImportacaoConteudo.Entidade.FERRAMENTA,
            codigo_origem=codigo,
            objeto_pk=str(ferramenta.pk),
            operacao=operacao,
            snapshot_anterior=snapshot,
            status_rollback=status_rollback,
            mensagem=mensagem,
        )
        item.full_clean()
        item.save()
        contagens["ferramentas_processadas"] += 1

    def _snapshot_ferramenta(self, ferramenta):
        return {
            "codigo": ferramenta.codigo,
            "titulo_es": ferramenta.titulo_es,
            "descricao_es": ferramenta.descricao_es,
            "responsavel": ferramenta.responsavel,
            "periodo": ferramenta.periodo,
            "setor_id": ferramenta.setor_id,
            "url": ferramenta.url,
            "situacao": ferramenta.situacao,
            "ordem": ferramenta.ordem,
            "lote_origem_id": ferramenta.lote_origem_id,
        }

    def _hash_estado_ferramenta(self, ferramenta):
        estado = {
            "codigo": ferramenta.codigo,
            "titulo": ferramenta.titulo,
            "titulo_es": ferramenta.titulo_es,
            "titulo_en": ferramenta.titulo_en,
            "descricao": ferramenta.descricao,
            "descricao_es": ferramenta.descricao_es,
            "descricao_en": ferramenta.descricao_en,
            "responsavel": ferramenta.responsavel,
            "periodo": ferramenta.periodo,
            "setor_id": ferramenta.setor_id,
            "url": ferramenta.url,
            "situacao": ferramenta.situacao,
            "ordem": ferramenta.ordem,
            "lote_origem_id": ferramenta.lote_origem_id,
        }
        return self._hash_json(estado)

    def _hash_estado_setor(self, setor):
        return self._hash_json(
            {"nome": setor.nome, "nome_es": setor.nome_es, "nome_en": setor.nome_en}
        )

    def _hash_json(self, valor):
        serializado = json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()

    def _reverter_lote(self, identificador, executor):
        try:
            lote_base = LoteImportacaoConteudo.objects.get(identificador=identificador)
        except (LoteImportacaoConteudo.DoesNotExist, ValidationError, ValueError) as exc:
            raise CommandError("O lote informado para reversão não existe.") from exc
        if lote_base.versao_fonte != self.VERSAO_FONTE:
            raise CommandError("Somente lotes da Fase 2C podem ser revertidos por este comando.")
        if lote_base.status in {
            LoteImportacaoConteudo.Status.REVERTIDO,
            LoteImportacaoConteudo.Status.REVERSAO_PARCIAL,
        }:
            raise CommandError("O lote informado já possui uma reversão registrada.")
        estados_reversiveis = {
            LoteImportacaoConteudo.Status.CONCLUIDO,
            LoteImportacaoConteudo.Status.COM_DIVERGENCIAS,
        }
        if lote_base.status not in estados_reversiveis:
            raise CommandError(
                "Somente um lote concluído ou com divergências da Fase 2C pode ser revertido."
            )

        with transaction.atomic():
            lote = LoteImportacaoConteudo.objects.select_for_update().get(pk=lote_base.pk)
            itens = list(lote.itens.select_for_update().order_by("-pk"))
            contagens_reversao = {
                "itens_processados": 0,
                "itens_revertidos": 0,
                "itens_nao_aplicaveis": 0,
                "itens_bloqueados": 0,
            }
            for item in itens:
                status = self._reverter_item(item, lote)
                contagens_reversao["itens_processados"] += 1
                if status == ItemLoteImportacaoConteudo.StatusRollback.REVERTIDO:
                    contagens_reversao["itens_revertidos"] += 1
                elif status == ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO:
                    contagens_reversao["itens_bloqueados"] += 1
                else:
                    contagens_reversao["itens_nao_aplicaveis"] += 1

            parcial = bool(contagens_reversao["itens_bloqueados"])
            contagens = dict(lote.contagens_realizadas)
            contagens["reversao"] = contagens_reversao
            lote.status = (
                LoteImportacaoConteudo.Status.REVERSAO_PARCIAL
                if parcial
                else LoteImportacaoConteudo.Status.REVERTIDO
            )
            lote.revertido_em = timezone.now()
            lote.revertido_por = executor
            lote.justificativa_reversao = "Reversão solicitada pelo comando da Fase 2C."
            lote.contagens_realizadas = contagens
            lote.mensagem_sanitizada = (
                "A reversão foi concluída parcialmente; existem itens bloqueados para revisão."
                if parcial
                else ""
            )
            lote.full_clean()
            lote.save(
                update_fields=(
                    "status",
                    "revertido_em",
                    "revertido_por",
                    "justificativa_reversao",
                    "contagens_realizadas",
                    "mensagem_sanitizada",
                )
            )

        mensagem = (
            "Reversão parcial registrada"
            if parcial
            else "Reversão concluída"
        )
        self.stdout.write(self.style.SUCCESS(f"{mensagem}: lote {lote.identificador}."))

    def _reverter_item(self, item, lote):
        if item.operacao == ItemLoteImportacaoConteudo.Operacao.IGNORADO:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL,
                "Item ignorado na carga; nenhuma reversão necessária.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL
        if item.entidade == ItemLoteImportacaoConteudo.Entidade.FERRAMENTA:
            return self._reverter_ferramenta(item, lote)
        if item.entidade == ItemLoteImportacaoConteudo.Entidade.SETOR:
            return self._reverter_setor(item)
        self._marcar_rollback(
            item,
            ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
            "Entidade não suportada pela reversão da Fase 2C.",
        )
        return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO

    def _reverter_ferramenta(self, item, lote):
        ferramenta = Ferramenta.objects.filter(pk=item.objeto_pk).first()
        if ferramenta is None:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "A ferramenta não está disponível para reversão segura.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        if not self._estado_pos_importacao_confere(item, ferramenta):
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "A ferramenta possui alteração posterior incompatível.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO

        if item.operacao == ItemLoteImportacaoConteudo.Operacao.CRIADO:
            if ferramenta.lote_origem_id != lote.pk:
                self._marcar_rollback(
                    item,
                    ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                    "A ferramenta criada não pertence mais ao lote informado.",
                )
                return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
            try:
                with transaction.atomic():
                    ferramenta.delete()
            except Exception:
                self._marcar_rollback(
                    item,
                    ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                    "A ferramenta criada possui dependências incompatíveis com a reversão.",
                )
                return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        elif item.operacao == ItemLoteImportacaoConteudo.Operacao.ATUALIZADO:
            if not self._restaurar_snapshot_ferramenta(ferramenta, item.snapshot_anterior):
                self._marcar_rollback(
                    item,
                    ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                    "O snapshot anterior da ferramenta não permite restauração segura.",
                )
                return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        else:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "A operação da ferramenta não é reversível por este comando.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO

        self._marcar_rollback(
            item,
            ItemLoteImportacaoConteudo.StatusRollback.REVERTIDO,
            "Item revertido com segurança.",
        )
        return ItemLoteImportacaoConteudo.StatusRollback.REVERTIDO

    def _restaurar_snapshot_ferramenta(self, ferramenta, snapshot):
        obrigatorios = set(self.CAMPOS_CONTROLADOS) | {"lote_origem_id"}
        if not isinstance(snapshot, dict) or not obrigatorios.issubset(snapshot):
            return False
        campos = (
            "codigo",
            "titulo_es",
            "descricao_es",
            "responsavel",
            "periodo",
            "setor_id",
            "url",
            "situacao",
            "ordem",
            "lote_origem_id",
        )
        try:
            with transaction.atomic():
                for campo in campos:
                    if campo in snapshot:
                        setattr(ferramenta, campo, snapshot[campo])
                ferramenta.full_clean()
                ferramenta.save()
        except Exception:
            return False
        return True

    def _reverter_setor(self, item):
        if item.operacao != ItemLoteImportacaoConteudo.Operacao.CRIADO:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL,
                "Setor preexistente ou reutilizado preservado.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL
        setor = Setor.objects.filter(pk=item.objeto_pk).first()
        if setor is None:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "O setor criado não está disponível para reversão segura.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        hash_esperado = self._extrair_hash_estado(item.mensagem)
        if hash_esperado and self._hash_estado_setor(setor) != hash_esperado:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "O setor possui alteração posterior incompatível.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        if self._setor_em_uso(setor):
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "O setor criado está em uso e foi preservado.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        try:
            with transaction.atomic():
                setor.delete()
        except Exception:
            self._marcar_rollback(
                item,
                ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO,
                "O setor possui dependências incompatíveis com a reversão.",
            )
            return ItemLoteImportacaoConteudo.StatusRollback.BLOQUEADO
        self._marcar_rollback(
            item,
            ItemLoteImportacaoConteudo.StatusRollback.REVERTIDO,
            "Setor criado pelo lote removido com segurança.",
        )
        return ItemLoteImportacaoConteudo.StatusRollback.REVERTIDO

    def _setor_em_uso(self, setor):
        for relacao in setor._meta.related_objects:
            acessor = relacao.get_accessor_name()
            if not acessor:
                continue
            relacionado = getattr(setor, acessor)
            if relacao.one_to_one:
                try:
                    if relacionado:
                        return True
                except relacao.related_model.DoesNotExist:
                    continue
            elif relacionado.exists():
                return True
        return False

    def _estado_pos_importacao_confere(self, item, ferramenta):
        hash_esperado = self._extrair_hash_estado(item.mensagem)
        if hash_esperado:
            return self._hash_estado_ferramenta(ferramenta) == hash_esperado
        return ferramenta.atualizado_em <= item.criado_em

    def _extrair_hash_estado(self, mensagem):
        correspondencia = re.search(
            rf"{re.escape(self.ESTADO_POS_PREFIXO)}([0-9a-f]{{64}})",
            mensagem or "",
        )
        return correspondencia.group(1) if correspondencia else ""

    def _marcar_rollback(self, item, status, mensagem):
        item.status_rollback = status
        item.mensagem = mensagem
        item.full_clean()
        item.save(update_fields=("status_rollback", "mensagem", "atualizado_em"))
