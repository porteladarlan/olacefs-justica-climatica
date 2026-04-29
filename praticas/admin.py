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
    PropostaEdicaoExperiencia,
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


@admin.register(PropostaEdicaoExperiencia)
class PropostaEdicaoExperienciaAdmin(admin.ModelAdmin):
    list_display = ("experiencia", "email_contato", "status", "criado_em", "atualizado_em")
    list_filter = ("status", "criado_em")
    search_fields = ("experiencia__titulo", "email_contato", "comentario_autor", "comentario_revisor")
    readonly_fields = ("dados_json", "criado_em", "atualizado_em")
    autocomplete_fields = ("experiencia",)


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
