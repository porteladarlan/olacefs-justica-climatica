from django.contrib import admin

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


admin.site.site_header = "Plataforma Regional OLACEFS"
admin.site.site_title = "Administracao da Plataforma"
admin.site.index_title = "Gestao de boas praticas em justica climatica"


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en", "sigla")
    search_fields = ("nome", "nome_es", "nome_en", "sigla")
    ordering = ("nome",)


@admin.register(EFS)
class EFSAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en", "sigla", "pais")
    list_filter = ("pais",)
    search_fields = ("nome", "nome_es", "nome_en", "sigla", "pais__nome")
    ordering = ("pais__nome", "nome")


@admin.register(TipoExperiencia)
class TipoExperienciaAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(TemaTransversal)
class TemaTransversalAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(NormaInternacional)
class NormaInternacionalAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en", "url_referencia")
    search_fields = ("nome", "nome_es", "nome_en", "resumo", "resumo_es", "resumo_en")
    ordering = ("nome",)


@admin.register(DimensaoJusticaClimatica)
class DimensaoJusticaClimaticaAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(GrupoVulneravel)
class GrupoVulneravelAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0
    fields = ("titulo", "titulo_es", "titulo_en", "arquivo", "url_externa")


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
        "ano_execucao",
        "status_publicacao",
        "contribui_para_guia",
        "destacado",
        "relevante",
    )
    list_filter = (
        "status_publicacao",
        "status_iniciativa",
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
        "temas_transversais",
        "normas_internacionais",
        "dimensoes_consideradas",
        "grupos_vulneraveis",
        "ano_execucao",
        "contribui_para_guia",
        "destacado",
        "relevante",
    )
    search_fields = (
        "titulo",
        "titulo_es",
        "titulo_en",
        "descricao",
        "descricao_es",
        "descricao_en",
        "contato_referencia",
        "email_contato",
        "pessoa_responsavel",
        "pais__nome",
        "efs__nome",
        "setor__nome",
    )
    autocomplete_fields = ("pais", "efs", "tipo_experiencia", "setor")
    filter_horizontal = (
        "temas_transversais",
        "normas_internacionais",
        "dimensoes_consideradas",
        "grupos_vulneraveis",
    )
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [AnexoInline]
    date_hierarchy = "criado_em"
    list_per_page = 20

    fieldsets = (
        ("Identificacao obrigatoria", {"fields": ("titulo", "titulo_es", "titulo_en", "efs", "pais", "tipo_experiencia", "ano_execucao", "status_iniciativa", "setor", "temas_transversais", "normas_internacionais")}),
        ("Contato e revisao", {"fields": ("contato_referencia", "email_contato", "pessoa_responsavel", "status_publicacao", "comentario_revisor", "contribui_para_guia", "destacado", "relevante")}),
        ("Contexto PT", {"fields": ("descricao", "problema_climatico", "relacao_adaptacao_mitigacao_gestao_desastres", "riscos_climaticos", "enfoque_justica_climatica", "impactos_diferenciados")}),
        ("Contexto ES", {"fields": ("descricao_es", "problema_climatico_es", "relacao_adaptacao_mitigacao_gestao_desastres_es", "riscos_climaticos_es", "enfoque_justica_climatica_es", "impactos_diferenciados_es")}),
        ("Contexto EN", {"fields": ("descricao_en", "problema_climatico_en", "relacao_adaptacao_mitigacao_gestao_desastres_en", "riscos_climaticos_en", "enfoque_justica_climatica_en", "impactos_diferenciados_en")}),
        ("Classificacao complementar", {"fields": ("dimensoes_consideradas", "grupos_vulneraveis")}),
        ("Perguntas, criterios e ferramentas PT", {"fields": ("objetivo", "perguntas_chave", "criterios_utilizados", "metodologia", "ferramentas_utilizadas", "fontes_informacao")}),
        ("Perguntas, criterios e ferramentas ES", {"fields": ("objetivo_es", "perguntas_chave_es", "criterios_utilizados_es", "metodologia_es", "ferramentas_utilizadas_es", "fontes_informacao_es")}),
        ("Perguntas, criterios e ferramentas EN", {"fields": ("objetivo_en", "perguntas_chave_en", "criterios_utilizados_en", "metodologia_en", "ferramentas_utilizadas_en", "fontes_informacao_en")}),
        ("Resultados PT", {"fields": ("resultados", "recomendacoes", "mudancas_ou_impactos", "motivo_boa_pratica")}),
        ("Resultados ES", {"fields": ("resultados_es", "recomendacoes_es", "mudancas_ou_impactos_es", "motivo_boa_pratica_es")}),
        ("Resultados EN", {"fields": ("resultados_en", "recomendacoes_en", "mudancas_ou_impactos_en", "motivo_boa_pratica_en")}),
        ("Replicabilidade PT", {"fields": ("elementos_replicaveis", "dificuldades", "licoes_aprendidas", "o_que_fariam_diferente", "replicabilidade", "necessidades_para_replicacao", "ferramentas_metodologias_uteis", "temas_sugeridos_para_guia", "apoio_requerido_pelas_efs")}),
        ("Replicabilidade ES", {"fields": ("elementos_replicaveis_es", "dificuldades_es", "licoes_aprendidas_es", "o_que_fariam_diferente_es", "replicabilidade_es", "necessidades_para_replicacao_es", "ferramentas_metodologias_uteis_es", "temas_sugeridos_para_guia_es", "apoio_requerido_pelas_efs_es")}),
        ("Replicabilidade EN", {"fields": ("elementos_replicaveis_en", "dificuldades_en", "licoes_aprendidas_en", "o_que_fariam_diferente_en", "replicabilidade_en", "necessidades_para_replicacao_en", "ferramentas_metodologias_uteis_en", "temas_sugeridos_para_guia_en", "apoio_requerido_pelas_efs_en")}),
        ("Controle", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "titulo_es", "titulo_en", "experiencia", "url_externa")
    list_filter = ("experiencia__pais", "experiencia__setor")
    search_fields = ("titulo", "titulo_es", "titulo_en", "experiencia__titulo", "url_externa")


@admin.register(BancoTecnico)
class BancoTecnicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "titulo_es", "titulo_en", "tipo_recurso", "tipo_recurso_es", "tipo_recurso_en", "setor", "url")
    list_filter = ("tipo_recurso", "setor", "dimensoes")
    search_fields = ("titulo", "titulo_es", "titulo_en", "descricao", "descricao_es", "descricao_en", "tipo_recurso", "tipo_recurso_es", "tipo_recurso_en", "setor__nome")
    autocomplete_fields = ("setor",)
    filter_horizontal = ("dimensoes",)
    list_per_page = 20
