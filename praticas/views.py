from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import (
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    Pais,
    Setor,
    TipoExperiencia,
)


def pagina_inicial(request):
    experiencias_publicadas = Experiencia.objects.filter(
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    )

    contexto = {
        "total_experiencias": experiencias_publicadas.count(),
        "total_efs": EFS.objects.count(),
        "total_paises": Pais.objects.count(),
        "ultimas_experiencias": experiencias_publicadas[:3],
    }
    return render(request, "praticas/pagina_inicial.html", contexto)


def catalogo_experiencias(request):
    experiencias = Experiencia.objects.filter(
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).select_related(
        "efs",
        "pais",
        "tipo_experiencia",
        "setor",
    ).prefetch_related(
        "dimensoes_consideradas",
        "grupos_vulneraveis",
    ).distinct()

    pais_id = request.GET.get("pais")
    efs_id = request.GET.get("efs")
    tipo_id = request.GET.get("tipo")
    setor_id = request.GET.get("setor")
    dimensao_id = request.GET.get("dimensao")
    grupo_id = request.GET.get("grupo")
    ano = request.GET.get("ano")
    termo = request.GET.get("q")

    if pais_id:
        experiencias = experiencias.filter(pais_id=pais_id)
    if efs_id:
        experiencias = experiencias.filter(efs_id=efs_id)
    if tipo_id:
        experiencias = experiencias.filter(tipo_experiencia_id=tipo_id)
    if setor_id:
        experiencias = experiencias.filter(setor_id=setor_id)
    if dimensao_id:
        experiencias = experiencias.filter(dimensoes_consideradas__id=dimensao_id)
    if grupo_id:
        experiencias = experiencias.filter(grupos_vulneraveis__id=grupo_id)
    if ano:
        experiencias = experiencias.filter(ano_execucao=ano)
    if termo:
        experiencias = experiencias.filter(
            Q(titulo__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(problema_climatico__icontains=termo)
            | Q(resultados__icontains=termo)
            | Q(motivo_boa_pratica__icontains=termo)
        )

    contexto = {
        "experiencias": experiencias,
        "paises": Pais.objects.all(),
        "efs_lista": EFS.objects.select_related("pais").all(),
        "tipos": TipoExperiencia.objects.all(),
        "setores": Setor.objects.all(),
        "dimensoes": DimensaoJusticaClimatica.objects.all(),
        "grupos": GrupoVulneravel.objects.all(),
        "anos": Experiencia.objects.values_list("ano_execucao", flat=True).distinct().order_by("-ano_execucao"),
    }
    return render(request, "praticas/catalogo_experiencias.html", contexto)


def detalhe_experiencia(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related(
            "efs",
            "pais",
            "tipo_experiencia",
            "setor",
        ).prefetch_related(
            "dimensoes_consideradas",
            "grupos_vulneraveis",
            "anexos",
        ),
        pk=pk,
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
    )
    return render(request, "praticas/detalhe_experiencia.html", {"experiencia": experiencia})


def banco_tecnico(request):
    recursos = BancoTecnico.objects.select_related("setor").prefetch_related("dimensoes")
    return render(request, "praticas/banco_tecnico.html", {"recursos": recursos})


def sobre_plataforma(request):
    return render(request, "praticas/sobre_plataforma.html")
