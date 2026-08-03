from django.contrib import admin

from .models import (
    Anexo,
    AtribuicaoPapelVinculo,
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    EpisodioVinculoUsuarioEFS,
    EventoVinculoUsuarioEFS,
    Experiencia,
    Ferramenta,
    GrupoVulneravel,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    NormaInternacional,
    PapelInstitucional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
    VinculoUsuarioEFS,
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


@admin.register(Ferramenta)
class FerramentaAdmin(admin.ModelAdmin):
    list_display = (
        "ordem",
        "titulo_es",
        "setor",
        "responsavel",
        "periodo",
        "situacao",
    )
    list_filter = ("situacao", "setor")
    search_fields = (
        "codigo",
        "titulo",
        "titulo_es",
        "titulo_en",
        "descricao",
        "descricao_es",
        "descricao_en",
        "responsavel",
        "setor__nome",
        "setor__nome_es",
        "setor__nome_en",
    )
    autocomplete_fields = ("setor",)
    readonly_fields = ("lote_origem", "criado_em", "atualizado_em")
    ordering = ("ordem",)
    list_per_page = 20


class InspecaoSeguraAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LoteImportacaoConteudo)
class LoteImportacaoConteudoAdmin(InspecaoSeguraAdmin):
    list_display = (
        "id",
        "identificador",
        "status",
        "versao_fonte",
        "executado_por",
        "iniciado_em",
        "finalizado_em",
    )
    list_filter = ("status", "iniciado_em", "finalizado_em")
    search_fields = ("=identificador", "fonte", "versao_fonte", "executado_por__username")
    list_select_related = ("executado_por",)
    date_hierarchy = "iniciado_em"


@admin.register(ItemLoteImportacaoConteudo)
class ItemLoteImportacaoConteudoAdmin(InspecaoSeguraAdmin):
    list_display = (
        "id",
        "lote",
        "entidade",
        "codigo_origem",
        "operacao",
        "status_rollback",
        "criado_em",
    )
    list_filter = ("entidade", "operacao", "status_rollback", "criado_em")
    search_fields = ("lote__identificador", "codigo_origem", "objeto_pk")
    list_select_related = ("lote",)


@admin.register(PapelInstitucional)
class PapelInstitucionalAdmin(InspecaoSeguraAdmin):
    list_display = ("id", "codigo", "nome", "nome_es", "nome_en", "ativo", "ordem")
    list_filter = ("ativo",)
    search_fields = ("codigo", "nome", "nome_es", "nome_en")
    ordering = ("ordem", "codigo")


@admin.register(VinculoUsuarioEFS)
class VinculoUsuarioEFSAdmin(InspecaoSeguraAdmin):
    list_display = ("id", "usuario", "efs", "criado_em", "atualizado_em")
    list_filter = ("efs", "criado_em")
    search_fields = ("usuario__username", "efs__nome", "efs__sigla")
    list_select_related = ("usuario", "efs", "efs__pais")
    date_hierarchy = "criado_em"


@admin.register(EpisodioVinculoUsuarioEFS)
class EpisodioVinculoUsuarioEFSAdmin(InspecaoSeguraAdmin):
    list_display = (
        "id",
        "usuario",
        "efs",
        "status",
        "origem",
        "solicitado_em",
        "data_inicio",
        "data_fim",
        "decidido_por",
    )
    list_filter = ("status", "origem", "vinculo__efs", "solicitado_em")
    search_fields = ("vinculo__usuario__username", "vinculo__efs__nome", "vinculo__efs__sigla")
    list_select_related = ("vinculo__usuario", "vinculo__efs", "decidido_por")
    date_hierarchy = "solicitado_em"

    @admin.display(ordering="vinculo__usuario__username", description="Usuario")
    def usuario(self, obj):
        return obj.vinculo.usuario

    @admin.display(ordering="vinculo__efs__nome", description="EFS")
    def efs(self, obj):
        return obj.vinculo.efs


@admin.register(AtribuicaoPapelVinculo)
class AtribuicaoPapelVinculoAdmin(InspecaoSeguraAdmin):
    list_display = (
        "id",
        "usuario",
        "efs",
        "papel",
        "atribuido_em",
        "atribuido_por",
        "revogado_em",
        "revogado_por",
    )
    list_filter = ("papel", "episodio__vinculo__efs", "revogado_em", "atribuido_em")
    search_fields = (
        "episodio__vinculo__usuario__username",
        "episodio__vinculo__efs__nome",
        "papel__codigo",
    )
    list_select_related = (
        "episodio__vinculo__usuario",
        "episodio__vinculo__efs",
        "papel",
        "atribuido_por",
        "revogado_por",
    )

    @admin.display(ordering="episodio__vinculo__usuario__username", description="Usuario")
    def usuario(self, obj):
        return obj.episodio.vinculo.usuario

    @admin.display(ordering="episodio__vinculo__efs__nome", description="EFS")
    def efs(self, obj):
        return obj.episodio.vinculo.efs


@admin.register(EventoVinculoUsuarioEFS)
class EventoVinculoUsuarioEFSAdmin(InspecaoSeguraAdmin):
    list_display = (
        "id",
        "usuario",
        "efs",
        "acao",
        "papel",
        "status_anterior",
        "status_novo",
        "responsavel",
        "ocorrido_em",
    )
    list_filter = ("acao", "status_anterior", "status_novo", "episodio__vinculo__efs", "ocorrido_em")
    search_fields = (
        "episodio__vinculo__usuario__username",
        "episodio__vinculo__efs__nome",
        "papel__codigo",
        "responsavel__username",
    )
    list_select_related = (
        "episodio__vinculo__usuario",
        "episodio__vinculo__efs",
        "papel",
        "responsavel",
    )
    date_hierarchy = "ocorrido_em"

    @admin.display(ordering="episodio__vinculo__usuario__username", description="Usuario")
    def usuario(self, obj):
        return obj.episodio.vinculo.usuario

    @admin.display(ordering="episodio__vinculo__efs__nome", description="EFS")
    def efs(self, obj):
        return obj.episodio.vinculo.efs
