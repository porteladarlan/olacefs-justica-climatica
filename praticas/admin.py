from django.contrib import admin

from .forms import AnexoAdminForm, ExperienciaAdminForm, NormaInternacionalAdminForm, NormaInternacionalPaisAdminForm
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
    EixoGuia,
    PerguntaGuia,
    PerguntaAuditoria,
    ReferenciaGuia,
    SetorGuia,
    SubareaGuia,
    SubareaReferenciaGuia,
    SubeixoGuia,
    VersaoGuia,
    GrupoVulneravel,
    ItemLoteImportacaoConteudo,
    LoteImportacaoConteudo,
    NormaInternacional,
    NormaInternacionalPais,
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
    list_display = ("codigo", "nome", "nome_es", "nome_en")
    search_fields = ("codigo", "nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "nome_es", "nome_en")
    search_fields = ("codigo", "nome", "nome_es", "nome_en")
    ordering = ("nome",)


@admin.register(TemaTransversal)
class TemaTransversalAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_es", "nome_en")
    search_fields = ("nome", "nome_es", "nome_en")
    ordering = ("nome",)


class NormaInternacionalPaisInline(admin.TabularInline):
    model = NormaInternacionalPais
    form = NormaInternacionalPaisAdminForm
    extra = 0
    fields = ("pais", "status", "status_es", "status_en")


@admin.register(NormaInternacional)
class NormaInternacionalAdmin(admin.ModelAdmin):
    form = NormaInternacionalAdminForm
    list_display = ("nome", "ano", "natureza_juridica_exibicao", "url_referencia")
    list_filter = ("natureza_juridica", "natureza_juridica_es", "natureza_juridica_en")
    search_fields = ("nome", "nome_es", "nome_en", "resumo", "resumo_es", "resumo_en", "natureza_juridica", "natureza_juridica_es", "natureza_juridica_en")
    ordering = ("nome",)
    inlines = (NormaInternacionalPaisInline,)


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
    form = AnexoAdminForm
    extra = 0
    fields = ("titulo", "titulo_es", "titulo_en", "arquivo", "url_externa")


class PerguntaAuditoriaInline(admin.TabularInline):
    model = PerguntaAuditoria
    extra = 0
    fields = ("ordem", "texto")
    ordering = ("ordem",)


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    form = ExperienciaAdminForm
    list_display = (
        "titulo",
        "pais",
        "efs",
        "tipo_experiencia",
        "tipo_auditoria",
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
        "tipo_auditoria",
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
        "efs_participantes",
        "paises_participantes",
        "temas_transversais",
        "normas_internacionais",
        "dimensoes_consideradas",
        "grupos_vulneraveis",
    )
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [PerguntaAuditoriaInline, AnexoInline]
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
    form = AnexoAdminForm
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
        "titulo_exibicao",
        "idioma_submissao",
        "setor",
        "responsavel",
        "periodo",
        "ano",
        "pais_ou_instancia",
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
        "pais_ou_instancia",
        "autor__username",
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


class GuiaPublicacaoProtegidaAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 25

    def _versao_publicada(self, obj):
        if obj is None:
            return False
        versao = obj if isinstance(obj, VersaoGuia) else obj.versao_guia
        return (
            versao is not None
            and versao.situacao == VersaoGuia.Situacao.PUBLICADA
        )

    def get_readonly_fields(self, request, obj=None):
        campos = list(super().get_readonly_fields(request, obj))
        if self._versao_publicada(obj):
            campos.extend(campo.name for campo in self.model._meta.fields)
        return tuple(dict.fromkeys(campos))

    def has_delete_permission(self, request, obj=None):
        if self._versao_publicada(obj):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(VersaoGuia)
class VersaoGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = (
        "codigo",
        "situacao",
        "vigente",
        "idioma_canonico",
        "publicado_em",
        "lote_origem",
        "atualizado_em",
    )
    list_filter = ("situacao", "vigente", "idioma_canonico")
    search_fields = (
        "codigo",
        "fonte",
        "sha256_fonte",
        "lote_origem__identificador",
        "lote_origem__versao_fonte",
    )
    list_select_related = ("lote_origem",)
    readonly_fields = ("idioma_canonico", "criado_em", "atualizado_em")
    date_hierarchy = "criado_em"
    ordering = ("-vigente", "-publicado_em", "-criado_em")

    def get_readonly_fields(self, request, obj=None):
        campos = list(
            admin.ModelAdmin.get_readonly_fields(self, request, obj)
        )
        campos.extend(("idioma_canonico", "criado_em", "atualizado_em"))
        if obj and obj.situacao == VersaoGuia.Situacao.PUBLICADA:
            campos.extend(
                campo.name
                for campo in self.model._meta.fields
                if campo.name != "vigente"
            )
        return tuple(dict.fromkeys(campos))


@admin.register(EixoGuia)
class EixoGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = ("codigo", "nome_es", "versao", "ordem", "atualizado_em")
    list_filter = ("versao__situacao", "versao__vigente", "versao")
    search_fields = ("codigo", "nome_es", "versao__codigo")
    autocomplete_fields = ("versao",)
    list_select_related = ("versao",)
    ordering = ("versao", "ordem", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(SubeixoGuia)
class SubeixoGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = (
        "codigo",
        "nome_es",
        "eixo",
        "versao",
        "ordem",
        "atualizado_em",
    )
    list_filter = ("versao__situacao", "versao__vigente", "versao", "eixo")
    search_fields = (
        "codigo",
        "nome_es",
        "versao__codigo",
        "eixo__codigo",
        "eixo__nome_es",
    )
    autocomplete_fields = ("versao", "eixo")
    list_select_related = ("versao", "eixo")
    ordering = ("versao", "eixo__ordem", "ordem", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(SetorGuia)
class SetorGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = ("codigo", "nome_es", "versao", "ordem", "atualizado_em")
    list_filter = ("versao__situacao", "versao__vigente", "versao")
    search_fields = ("codigo", "nome_es", "versao__codigo")
    autocomplete_fields = ("versao",)
    list_select_related = ("versao",)
    ordering = ("versao", "ordem", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(SubareaGuia)
class SubareaGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = (
        "codigo",
        "nome_es",
        "setor",
        "versao",
        "ordem",
        "atualizado_em",
    )
    list_filter = ("versao__situacao", "versao__vigente", "versao", "setor")
    search_fields = (
        "codigo",
        "nome_es",
        "versao__codigo",
        "setor__codigo",
        "setor__nome_es",
    )
    autocomplete_fields = ("versao", "setor")
    list_select_related = ("versao", "setor")
    ordering = ("versao", "setor__ordem", "ordem", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(PerguntaGuia)
class PerguntaGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = (
        "codigo",
        "tipo_auditoria",
        "escopo",
        "versao",
        "ordem",
        "atualizado_em",
    )
    list_filter = (
        "tipo_auditoria",
        "versao__situacao",
        "versao__vigente",
        "versao",
    )
    search_fields = (
        "codigo",
        "texto_es",
        "versao__codigo",
        "eixo__codigo",
        "subeixo__codigo",
        "subarea__codigo",
    )
    autocomplete_fields = ("versao", "eixo", "subeixo", "subarea")
    list_select_related = ("versao", "eixo", "subeixo", "subarea")
    ordering = ("versao", "tipo_auditoria", "ordem", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")

    @admin.display(description="Escopo")
    def escopo(self, obj):
        return obj.eixo or obj.subeixo or obj.subarea


@admin.register(ReferenciaGuia)
class ReferenciaGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = ("codigo", "versao", "citacao_resumida", "atualizado_em")
    list_filter = ("versao__situacao", "versao__vigente", "versao")
    search_fields = ("codigo", "citacao_es", "versao__codigo")
    autocomplete_fields = ("versao",)
    list_select_related = ("versao",)
    ordering = ("versao", "codigo")
    readonly_fields = ("criado_em", "atualizado_em")

    @admin.display(description="Citacao")
    def citacao_resumida(self, obj):
        return obj.citacao_es[:100]


@admin.register(SubareaReferenciaGuia)
class SubareaReferenciaGuiaAdmin(GuiaPublicacaoProtegidaAdmin):
    list_display = ("subarea", "referencia", "ordem", "versao")
    list_filter = (
        "subarea__versao__situacao",
        "subarea__versao__vigente",
        "subarea__versao",
        "subarea__setor",
    )
    search_fields = (
        "subarea__codigo",
        "subarea__nome_es",
        "referencia__codigo",
        "referencia__citacao_es",
    )
    autocomplete_fields = ("subarea", "referencia")
    list_select_related = (
        "subarea",
        "subarea__versao",
        "subarea__setor",
        "referencia",
    )
    ordering = ("subarea", "ordem", "pk")
    readonly_fields = ("criado_em", "atualizado_em")

    @admin.display(
        ordering="subarea__versao__codigo",
        description="Versao",
    )
    def versao(self, obj):
        return obj.subarea.versao
