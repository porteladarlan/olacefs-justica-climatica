from django.contrib import admin

from .models import (
    Anexo,
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    Pais,
    Setor,
    TipoExperiencia,
)


admin.site.site_header = "Plataforma Regional OLACEFS"
admin.site.site_title = "Administração da Plataforma"
admin.site.index_title = "Gestão de boas práticas em justiça climática"


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla")
    search_fields = ("nome", "sigla")
    ordering = ("nome",)


@admin.register(EFS)
class EFSAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "pais")
    list_filter = ("pais",)
    search_fields = ("nome", "sigla", "pais__nome")
    ordering = ("pais__nome", "nome")


@admin.register(TipoExperiencia)
class TipoExperienciaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(DimensaoJusticaClimatica)
class DimensaoJusticaClimaticaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(GrupoVulneravel)
class GrupoVulneravelAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    ordering = ("nome",)


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0
    fields = ("titulo", "arquivo", "url_externa")


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
        "ano_execucao",
        "status_iniciativa",
        "status_publicacao",
    )
    list_filter = (
        "status_publicacao",
        "status_iniciativa",
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
        "ano_execucao",
        "dimensoes_consideradas",
        "grupos_vulneraveis",
    )
    search_fields = (
        "titulo",
        "descricao",
        "problema_climatico",
        "objetivo",
        "resultados",
        "recomendacoes",
        "pais__nome",
        "efs__nome",
        "setor__nome",
    )
    autocomplete_fields = (
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
    )
    filter_horizontal = (
        "dimensoes_consideradas",
        "grupos_vulneraveis",
    )
    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )
    inlines = [AnexoInline]
    date_hierarchy = "criado_em"
    list_per_page = 20

    fieldsets = (
        (
            "Identificação da experiência",
            {
                "fields": (
                    "titulo",
                    "efs",
                    "pais",
                    "tipo_experiencia",
                    "ano_execucao",
                    "status_iniciativa",
                    "setor",
                    "status_publicacao",
                )
            },
        ),
        (
            "Contexto climático e justiça climática",
            {
                "fields": (
                    "descricao",
                    "problema_climatico",
                    "relacao_adaptacao_mitigacao_gestao_desastres",
                    "riscos_climaticos",
                    "enfoque_justica_climatica",
                    "dimensoes_consideradas",
                    "grupos_vulneraveis",
                    "impactos_diferenciados",
                )
            },
        ),
        (
            "Planejamento e metodologia",
            {
                "fields": (
                    "objetivo",
                    "perguntas_chave",
                    "criterios_utilizados",
                    "metodologia",
                    "fontes_informacao",
                )
            },
        ),
        (
            "Resultados e recomendações",
            {
                "fields": (
                    "resultados",
                    "recomendacoes",
                    "mudancas_ou_impactos",
                    "motivo_boa_pratica",
                )
            },
        ),
        (
            "Replicabilidade e aprendizagem",
            {
                "fields": (
                    "elementos_replicaveis",
                    "dificuldades",
                    "licoes_aprendidas",
                    "o_que_fariam_diferente",
                    "replicabilidade",
                    "necessidades_para_replicacao",
                    "ferramentas_metodologias_uteis",
                    "temas_sugeridos_para_guia",
                    "apoio_requerido_pelas_efs",
                )
            },
        ),
        (
            "Controle do registro",
            {
                "fields": (
                    "criado_em",
                    "atualizado_em",
                )
            },
        ),
    )


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "experiencia", "url_externa")
    list_filter = ("experiencia__pais", "experiencia__setor")
    search_fields = ("titulo", "experiencia__titulo", "url_externa")


@admin.register(BancoTecnico)
class BancoTecnicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo_recurso", "setor", "url")
    list_filter = ("tipo_recurso", "setor", "dimensoes")
    search_fields = ("titulo", "descricao", "tipo_recurso", "setor__nome")
    autocomplete_fields = ("setor",)
    filter_horizontal = ("dimensoes",)
    list_per_page = 20

    fieldsets = (
        (
            "Identificação do recurso",
            {
                "fields": (
                    "titulo",
                    "tipo_recurso",
                    "setor",
                    "url",
                )
            },
        ),
        (
            "Descrição e classificação",
            {
                "fields": (
                    "descricao",
                    "dimensoes",
                )
            },
        ),
    )