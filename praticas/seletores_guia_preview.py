"""Consultas somente-leitura para a preview interna do Guia."""

from django.db.models import Count, Prefetch, Q

from .models import (
    EixoGuia,
    PerguntaGuia,
    SetorGuia,
    SubareaGuia,
    SubareaReferenciaGuia,
    SubeixoGuia,
    VersaoGuia,
)


def obter_versao_publicada_vigente():
    """Retorna exclusivamente a versao institucional apta para a preview."""
    return (
        VersaoGuia.objects.filter(
            situacao=VersaoGuia.Situacao.PUBLICADA,
            vigente=True,
        )
        .only("id", "codigo", "idioma_canonico", "publicado_em")
        .first()
    )


def listar_eixos(versao):
    return (
        EixoGuia.objects.filter(versao=versao)
        .annotate(
            total_subeixos=Count(
                "subeixos",
                filter=Q(subeixos__versao=versao),
                distinct=True,
            ),
            total_perguntas=(
                Count(
                    "perguntas_diretas",
                    filter=Q(perguntas_diretas__versao=versao),
                    distinct=True,
                )
                + Count(
                    "subeixos__perguntas",
                    filter=Q(
                        subeixos__versao=versao,
                        subeixos__perguntas__versao=versao,
                    ),
                    distinct=True,
                )
            ),
        )
        .order_by("ordem", "codigo")
    )


def listar_setores(versao):
    return (
        SetorGuia.objects.filter(versao=versao)
        .annotate(
            total_subareas=Count(
                "subareas",
                filter=Q(subareas__versao=versao),
                distinct=True,
            )
        )
        .order_by("ordem", "codigo")
    )


def queryset_eixo_detalhado(versao):
    perguntas = (
        PerguntaGuia.objects.filter(versao=versao)
        .only("id", "eixo_id", "codigo", "texto_es", "tipo_auditoria", "ordem")
        .order_by("tipo_auditoria", "ordem", "codigo")
    )
    subeixos = (
        SubeixoGuia.objects.filter(versao=versao)
        .only("id", "versao_id", "eixo_id", "codigo", "nome_es", "ordem")
        .order_by("ordem", "codigo")
    )
    return EixoGuia.objects.filter(versao=versao).prefetch_related(
        Prefetch("subeixos", queryset=subeixos, to_attr="subeixos_preview"),
        Prefetch(
            "perguntas_diretas",
            queryset=perguntas,
            to_attr="perguntas_preview",
        ),
    )


def queryset_subeixo_detalhado(versao, eixo_codigo):
    perguntas = (
        PerguntaGuia.objects.filter(versao=versao)
        .only(
            "id", "subeixo_id", "codigo", "texto_es", "tipo_auditoria", "ordem"
        )
        .order_by("tipo_auditoria", "ordem", "codigo")
    )
    return (
        SubeixoGuia.objects.filter(
            versao=versao,
            eixo__versao=versao,
            eixo__codigo=eixo_codigo,
        )
        .select_related("eixo")
        .prefetch_related(
            Prefetch("perguntas", queryset=perguntas, to_attr="perguntas_preview")
        )
    )


def queryset_setor_detalhado(versao):
    subareas = (
        SubareaGuia.objects.filter(versao=versao)
        .only("id", "versao_id", "setor_id", "codigo", "nome_es", "ordem")
        .order_by("ordem", "codigo")
    )
    return SetorGuia.objects.filter(versao=versao).prefetch_related(
        Prefetch("subareas", queryset=subareas, to_attr="subareas_preview")
    )


def queryset_subarea_detalhada(versao, setor_codigo):
    perguntas = (
        PerguntaGuia.objects.filter(versao=versao)
        .only(
            "id", "subarea_id", "codigo", "texto_es", "tipo_auditoria", "ordem"
        )
        .order_by("tipo_auditoria", "ordem", "codigo")
    )
    ocorrencias = (
        SubareaReferenciaGuia.objects.filter(
            subarea__versao=versao,
            referencia__versao=versao,
        )
        .select_related("referencia")
        .only(
            "id",
            "subarea_id",
            "referencia_id",
            "ordem",
            "referencia__codigo",
            "referencia__citacao_es",
        )
        .order_by("ordem", "pk")
    )
    return (
        SubareaGuia.objects.filter(
            versao=versao,
            setor__versao=versao,
            setor__codigo=setor_codigo,
        )
        .select_related("setor")
        .prefetch_related(
            Prefetch("perguntas", queryset=perguntas, to_attr="perguntas_preview"),
            Prefetch(
                "ocorrencias_referencias",
                queryset=ocorrencias,
                to_attr="ocorrencias_referencias_preview",
            ),
        )
    )


def separar_perguntas_por_tipo(perguntas):
    grupos = {
        PerguntaGuia.TipoAuditoria.CUMPLIMIENTO: [],
        PerguntaGuia.TipoAuditoria.GESTION: [],
    }
    for pergunta in perguntas:
        grupos[pergunta.tipo_auditoria].append(pergunta)
    return (
        grupos[PerguntaGuia.TipoAuditoria.CUMPLIMIENTO],
        grupos[PerguntaGuia.TipoAuditoria.GESTION],
    )
