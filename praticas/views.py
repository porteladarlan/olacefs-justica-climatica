from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExperienciaSubmissaoForm
from .models import (
    Anexo,
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


def experiencias_publicas():
    return Experiencia.objects.filter(
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    )


def pagina_inicial(request):
    experiencias = experiencias_publicas().select_related(
        "efs",
        "pais",
        "tipo_experiencia",
        "setor",
    ).prefetch_related(
        "temas_transversais",
        "normas_internacionais",
    )

    contexto = {
        "total_experiencias": experiencias.count(),
        "total_efs": EFS.objects.count(),
        "total_paises": Pais.objects.count(),
        "total_normas": NormaInternacional.objects.count(),
        "ultimas_experiencias": experiencias[:3],
        "experiencias_destacadas": experiencias.filter(Q(destacado=True) | Q(relevante=True))[:3],
    }
    return render(request, "praticas/pagina_inicial.html", contexto)


def catalogo_experiencias(request):
    experiencias = (
        experiencias_publicas()
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
        )
        .distinct()
    )

    pais_id = request.GET.get("pais")
    efs_id = request.GET.get("efs")
    tipo_id = request.GET.get("tipo")
    setor_id = request.GET.get("setor")
    tema_id = request.GET.get("tema")
    norma_id = request.GET.get("norma")
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

    if tema_id:
        experiencias = experiencias.filter(temas_transversais__id=tema_id)

    if norma_id:
        experiencias = experiencias.filter(normas_internacionais__id=norma_id)

    if dimensao_id:
        experiencias = experiencias.filter(dimensoes_consideradas__id=dimensao_id)

    if grupo_id:
        experiencias = experiencias.filter(grupos_vulneraveis__id=grupo_id)

    if ano:
        experiencias = experiencias.filter(ano_execucao=ano)

    if termo:
        experiencias = experiencias.filter(
            Q(titulo__icontains=termo)
            | Q(titulo_es__icontains=termo)
            | Q(titulo_en__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(descricao_es__icontains=termo)
            | Q(descricao_en__icontains=termo)
            | Q(problema_climatico__icontains=termo)
            | Q(problema_climatico_es__icontains=termo)
            | Q(problema_climatico_en__icontains=termo)
            | Q(objetivo__icontains=termo)
            | Q(objetivo_es__icontains=termo)
            | Q(objetivo_en__icontains=termo)
            | Q(resultados__icontains=termo)
            | Q(resultados_es__icontains=termo)
            | Q(resultados_en__icontains=termo)
            | Q(recomendacoes__icontains=termo)
            | Q(recomendacoes_es__icontains=termo)
            | Q(recomendacoes_en__icontains=termo)
            | Q(motivo_boa_pratica__icontains=termo)
            | Q(motivo_boa_pratica_es__icontains=termo)
            | Q(motivo_boa_pratica_en__icontains=termo)
            | Q(elementos_replicaveis__icontains=termo)
            | Q(elementos_replicaveis_es__icontains=termo)
            | Q(elementos_replicaveis_en__icontains=termo)
            | Q(perguntas_chave__icontains=termo)
            | Q(perguntas_chave_es__icontains=termo)
            | Q(perguntas_chave_en__icontains=termo)
            | Q(criterios_utilizados__icontains=termo)
            | Q(criterios_utilizados_es__icontains=termo)
            | Q(criterios_utilizados_en__icontains=termo)
            | Q(ferramentas_utilizadas__icontains=termo)
            | Q(ferramentas_utilizadas_es__icontains=termo)
            | Q(ferramentas_utilizadas_en__icontains=termo)
            | Q(setor__nome__icontains=termo)
            | Q(setor__nome_es__icontains=termo)
            | Q(setor__nome_en__icontains=termo)
            | Q(tipo_experiencia__nome__icontains=termo)
            | Q(tipo_experiencia__nome_es__icontains=termo)
            | Q(tipo_experiencia__nome_en__icontains=termo)
            | Q(temas_transversais__nome__icontains=termo)
            | Q(temas_transversais__nome_es__icontains=termo)
            | Q(temas_transversais__nome_en__icontains=termo)
            | Q(normas_internacionais__nome__icontains=termo)
            | Q(normas_internacionais__nome_es__icontains=termo)
            | Q(normas_internacionais__nome_en__icontains=termo)
            | Q(pais__nome__icontains=termo)
            | Q(pais__nome_es__icontains=termo)
            | Q(pais__nome_en__icontains=termo)
            | Q(efs__nome__icontains=termo)
            | Q(efs__nome_es__icontains=termo)
            | Q(efs__nome_en__icontains=termo)
            | Q(efs__sigla__icontains=termo)
        ).distinct()

    contexto = {
        "experiencias": experiencias,
        "paises": Pais.objects.all(),
        "efs_lista": EFS.objects.select_related("pais").all(),
        "tipos": TipoExperiencia.objects.all(),
        "setores": Setor.objects.all(),
        "temas": TemaTransversal.objects.all(),
        "normas": NormaInternacional.objects.all(),
        "dimensoes": DimensaoJusticaClimatica.objects.all(),
        "grupos": GrupoVulneravel.objects.all(),
        "anos": (
            Experiencia.objects.values_list("ano_execucao", flat=True)
            .distinct()
            .order_by("-ano_execucao")
        ),
    }
    return render(request, "praticas/catalogo_experiencias.html", contexto)


def detalhe_experiencia(request, pk):
    experiencia = get_object_or_404(
        experiencias_publicas()
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
            "anexos",
        ),
        pk=pk,
    )
    return render(
        request,
        "praticas/detalhe_experiencia.html",
        {"experiencia": experiencia},
    )


def normas_internacionais(request):
    normas = NormaInternacional.objects.all()
    return render(request, "praticas/normas_internacionais.html", {"normas": normas})


def adicionar_boa_pratica(request):
    if request.method == "POST":
        form = ExperienciaSubmissaoForm(request.POST, request.FILES)
        if form.is_valid():
            experiencia = form.save(commit=False)
            experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
            experiencia.status_iniciativa = Experiencia.StatusIniciativa.CONCLUIDA
            experiencia.save()
            form.save_m2m()

            for indice in range(1, 4):
                titulo = request.POST.get(f"anexo_titulo_{indice}", "").strip()
                arquivo = request.FILES.get(f"anexo_arquivo_{indice}")
                url = request.POST.get(f"anexo_url_{indice}", "").strip()

                if titulo or arquivo or url:
                    Anexo.objects.create(
                        experiencia=experiencia,
                        titulo=titulo or f"Anexo {indice}",
                        arquivo=arquivo,
                        url_externa=url,
                    )

            messages.success(
                request,
                "Boa prática enviada com sucesso. Ela ficará pendente até a revisão.",
            )
            return redirect("confirmacao_envio")
    else:
        form = ExperienciaSubmissaoForm()

    return render(request, "praticas/adicionar_boa_pratica.html", {"form": form})


def confirmacao_envio(request):
    return render(request, "praticas/confirmacao_envio.html")


def banco_tecnico(request):
    recursos = (
        BancoTecnico.objects.select_related("setor")
        .prefetch_related("dimensoes")
        .all()
    )
    return render(request, "praticas/banco_tecnico.html", {"recursos": recursos})


def sobre_plataforma(request):
    return render(request, "praticas/sobre_plataforma.html")
