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


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla")
    search_fields = ("nome", "sigla")


@admin.register(EFS)
class EFSAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "pais")
    list_filter = ("pais",)
    search_fields = ("nome", "sigla")


admin.site.register(TipoExperiencia)
admin.site.register(Setor)
admin.site.register(DimensaoJusticaClimatica)
admin.site.register(GrupoVulneravel)


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "efs", "pais", "tipo_experiencia", "setor", "ano_execucao", "status_publicacao")
    list_filter = (
        "pais",
        "efs",
        "tipo_experiencia",
        "setor",
        "status_iniciativa",
        "status_publicacao",
        "ano_execucao",
    )
    search_fields = ("titulo", "descricao", "problema_climatico", "resultados")
    filter_horizontal = ("dimensoes_consideradas", "grupos_vulneraveis")
    inlines = [AnexoInline]


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "experiencia", "url_externa")
    search_fields = ("titulo", "experiencia__titulo")


@admin.register(BancoTecnico)
class BancoTecnicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo_recurso", "setor", "url")
    list_filter = ("tipo_recurso", "setor", "dimensoes")
    search_fields = ("titulo", "descricao", "tipo_recurso")
    filter_horizontal = ("dimensoes",)
