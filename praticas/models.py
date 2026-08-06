import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import get_language


def idioma_atual():
    return (get_language() or "pt-br").lower()


def texto_por_idioma(texto_pt, texto_es="", texto_en=""):
    idioma = idioma_atual()
    if idioma.startswith("en") and texto_en:
        return texto_en
    if idioma.startswith("es") and texto_es:
        return texto_es
    return texto_pt


def texto_por_idioma_com_fallback_es(texto_es, texto_pt="", texto_en=""):
    idioma = idioma_atual()
    if idioma.startswith("en") and texto_en:
        return texto_en
    if idioma.startswith("pt") and texto_pt:
        return texto_pt
    return texto_es


class Pais(models.Model):
    nome = models.CharField(max_length=100)
    nome_es = models.CharField(max_length=100, blank=True)
    nome_en = models.CharField(max_length=100, blank=True)
    sigla = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Pais"
        verbose_name_plural = "Paises"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class EFS(models.Model):
    nome = models.CharField(max_length=200)
    nome_es = models.CharField(max_length=200, blank=True)
    nome_en = models.CharField(max_length=200, blank=True)
    sigla = models.CharField(max_length=30, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="efs")

    class Meta:
        verbose_name = "EFS"
        verbose_name_plural = "EFS"
        ordering = ["pais__nome", "nome"]

    def __str__(self):
        if self.sigla:
            return f"{self.nome_exibicao} ({self.sigla})"
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class TipoExperiencia(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    nome_es = models.CharField(max_length=120, blank=True)
    nome_en = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "Tipo de experiencia"
        verbose_name_plural = "Tipos de experiencia"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class Setor(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    nome_es = models.CharField(max_length=120, blank=True)
    nome_en = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class TemaTransversal(models.Model):
    nome = models.CharField(max_length=160, unique=True)
    nome_es = models.CharField(max_length=160, blank=True)
    nome_en = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Tema transversal"
        verbose_name_plural = "Temas transversais"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class NormaInternacional(models.Model):
    nome = models.CharField(max_length=180, unique=True)
    nome_es = models.CharField(max_length=180, blank=True)
    nome_en = models.CharField(max_length=180, blank=True)
    resumo = models.TextField(blank=True)
    resumo_es = models.TextField(blank=True)
    resumo_en = models.TextField(blank=True)
    url_referencia = models.URLField(blank=True)

    class Meta:
        verbose_name = "Norma internacional"
        verbose_name_plural = "Normas internacionais"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)

    @property
    def resumo_exibicao(self):
        return texto_por_idioma(self.resumo, self.resumo_es, self.resumo_en)


class DimensaoJusticaClimatica(models.Model):
    nome = models.CharField(max_length=160, unique=True)
    nome_es = models.CharField(max_length=160, blank=True)
    nome_en = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Dimensao de justica climatica"
        verbose_name_plural = "Dimensoes de justica climatica"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class GrupoVulneravel(models.Model):
    nome = models.CharField(max_length=160, unique=True)
    nome_es = models.CharField(max_length=160, blank=True)
    nome_en = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Grupo vulneravel"
        verbose_name_plural = "Grupos vulneraveis"
        ordering = ["nome"]

    def __str__(self):
        return self.nome_exibicao

    @property
    def nome_exibicao(self):
        return texto_por_idioma(self.nome, self.nome_es, self.nome_en)


class Experiencia(models.Model):
    class StatusIniciativa(models.TextChoices):
        PLANEJADA = "planejada", "Planejada"
        EXECUCAO = "execucao", "Em execucao"
        CONCLUIDA = "concluida", "Concluida"

    class StatusPublicacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        ENVIADO = "enviado", "Enviado"
        EM_REVISAO = "em_revisao", "Em revisao"
        APROVADO = "aprovado", "Aprovado"
        PUBLICADO = "publicado", "Publicado"
        REJEITADO = "rejeitado", "Rejeitado"

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boas_praticas_enviadas",
    )

    titulo = models.CharField(max_length=220)
    titulo_es = models.CharField(max_length=220, blank=True)
    titulo_en = models.CharField(max_length=220, blank=True)

    efs = models.ForeignKey(EFS, on_delete=models.PROTECT, related_name="experiencias")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="experiencias")
    tipo_experiencia = models.ForeignKey(TipoExperiencia, on_delete=models.PROTECT, related_name="experiencias")
    ano_execucao = models.PositiveIntegerField()
    status_iniciativa = models.CharField(max_length=30, choices=StatusIniciativa.choices, default=StatusIniciativa.CONCLUIDA)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name="experiencias")

    temas_transversais = models.ManyToManyField(TemaTransversal, blank=True, related_name="experiencias")
    normas_internacionais = models.ManyToManyField(NormaInternacional, blank=True, related_name="experiencias")

    contato_referencia = models.CharField(max_length=180, blank=True)
    email_contato = models.EmailField(blank=True)
    pessoa_responsavel = models.CharField(max_length=180, blank=True)

    descricao = models.TextField()
    descricao_es = models.TextField(blank=True)
    descricao_en = models.TextField(blank=True)

    problema_climatico = models.TextField(blank=True)
    problema_climatico_es = models.TextField(blank=True)
    problema_climatico_en = models.TextField(blank=True)

    relacao_adaptacao_mitigacao_gestao_desastres = models.TextField(blank=True)
    relacao_adaptacao_mitigacao_gestao_desastres_es = models.TextField(blank=True)
    relacao_adaptacao_mitigacao_gestao_desastres_en = models.TextField(blank=True)

    riscos_climaticos = models.TextField(blank=True)
    riscos_climaticos_es = models.TextField(blank=True)
    riscos_climaticos_en = models.TextField(blank=True)

    enfoque_justica_climatica = models.TextField(blank=True)
    enfoque_justica_climatica_es = models.TextField(blank=True)
    enfoque_justica_climatica_en = models.TextField(blank=True)

    dimensoes_consideradas = models.ManyToManyField(DimensaoJusticaClimatica, blank=True, related_name="experiencias")
    grupos_vulneraveis = models.ManyToManyField(GrupoVulneravel, blank=True, related_name="experiencias")

    impactos_diferenciados = models.TextField(blank=True)
    impactos_diferenciados_es = models.TextField(blank=True)
    impactos_diferenciados_en = models.TextField(blank=True)

    objetivo = models.TextField(blank=True)
    objetivo_es = models.TextField(blank=True)
    objetivo_en = models.TextField(blank=True)

    perguntas_chave = models.TextField(blank=True)
    perguntas_chave_es = models.TextField(blank=True)
    perguntas_chave_en = models.TextField(blank=True)

    criterios_utilizados = models.TextField(blank=True)
    criterios_utilizados_es = models.TextField(blank=True)
    criterios_utilizados_en = models.TextField(blank=True)

    metodologia = models.TextField(blank=True)
    metodologia_es = models.TextField(blank=True)
    metodologia_en = models.TextField(blank=True)

    ferramentas_utilizadas = models.TextField(blank=True)
    ferramentas_utilizadas_es = models.TextField(blank=True)
    ferramentas_utilizadas_en = models.TextField(blank=True)

    fontes_informacao = models.TextField(blank=True)
    fontes_informacao_es = models.TextField(blank=True)
    fontes_informacao_en = models.TextField(blank=True)

    resultados = models.TextField(blank=True)
    resultados_es = models.TextField(blank=True)
    resultados_en = models.TextField(blank=True)

    recomendacoes = models.TextField(blank=True)
    recomendacoes_es = models.TextField(blank=True)
    recomendacoes_en = models.TextField(blank=True)

    mudancas_ou_impactos = models.TextField(blank=True)
    mudancas_ou_impactos_es = models.TextField(blank=True)
    mudancas_ou_impactos_en = models.TextField(blank=True)

    motivo_boa_pratica = models.TextField(blank=True)
    motivo_boa_pratica_es = models.TextField(blank=True)
    motivo_boa_pratica_en = models.TextField(blank=True)

    elementos_replicaveis = models.TextField(blank=True)
    elementos_replicaveis_es = models.TextField(blank=True)
    elementos_replicaveis_en = models.TextField(blank=True)

    dificuldades = models.TextField(blank=True)
    dificuldades_es = models.TextField(blank=True)
    dificuldades_en = models.TextField(blank=True)

    licoes_aprendidas = models.TextField(blank=True)
    licoes_aprendidas_es = models.TextField(blank=True)
    licoes_aprendidas_en = models.TextField(blank=True)

    o_que_fariam_diferente = models.TextField(blank=True)
    o_que_fariam_diferente_es = models.TextField(blank=True)
    o_que_fariam_diferente_en = models.TextField(blank=True)

    replicabilidade = models.TextField(blank=True)
    replicabilidade_es = models.TextField(blank=True)
    replicabilidade_en = models.TextField(blank=True)

    informacoes_adicionais = models.TextField(blank=True)
    informacoes_adicionais_es = models.TextField(blank=True)
    informacoes_adicionais_en = models.TextField(blank=True)

    necessidades_para_replicacao = models.TextField(blank=True)
    necessidades_para_replicacao_es = models.TextField(blank=True)
    necessidades_para_replicacao_en = models.TextField(blank=True)

    ferramentas_metodologias_uteis = models.TextField(blank=True)
    ferramentas_metodologias_uteis_es = models.TextField(blank=True)
    ferramentas_metodologias_uteis_en = models.TextField(blank=True)

    temas_sugeridos_para_guia = models.TextField(blank=True)
    temas_sugeridos_para_guia_es = models.TextField(blank=True)
    temas_sugeridos_para_guia_en = models.TextField(blank=True)

    apoio_requerido_pelas_efs = models.TextField(blank=True)
    apoio_requerido_pelas_efs_es = models.TextField(blank=True)
    apoio_requerido_pelas_efs_en = models.TextField(blank=True)

    contribui_para_guia = models.BooleanField(default=False)
    destacado = models.BooleanField(default=False)
    relevante = models.BooleanField(default=False)

    status_publicacao = models.CharField(max_length=30, choices=StatusPublicacao.choices, default=StatusPublicacao.PUBLICADO)
    comentario_revisor = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Experiencia"
        verbose_name_plural = "Experiencias"
        ordering = ["-ano_execucao", "-criado_em", "titulo"]

    def __str__(self):
        return self.titulo_exibicao

    @property
    def titulo_exibicao(self):
        return texto_por_idioma(self.titulo, self.titulo_es, self.titulo_en)

    @property
    def descricao_exibicao(self):
        return texto_por_idioma(self.descricao, self.descricao_es, self.descricao_en)

    @property
    def problema_climatico_exibicao(self):
        return texto_por_idioma(self.problema_climatico, self.problema_climatico_es, self.problema_climatico_en)

    @property
    def relacao_adaptacao_mitigacao_gestao_desastres_exibicao(self):
        return texto_por_idioma(
            self.relacao_adaptacao_mitigacao_gestao_desastres,
            self.relacao_adaptacao_mitigacao_gestao_desastres_es,
            self.relacao_adaptacao_mitigacao_gestao_desastres_en,
        )

    @property
    def riscos_climaticos_exibicao(self):
        return texto_por_idioma(self.riscos_climaticos, self.riscos_climaticos_es, self.riscos_climaticos_en)

    @property
    def impactos_diferenciados_exibicao(self):
        return texto_por_idioma(self.impactos_diferenciados, self.impactos_diferenciados_es, self.impactos_diferenciados_en)

    @property
    def objetivo_exibicao(self):
        return texto_por_idioma(self.objetivo, self.objetivo_es, self.objetivo_en)

    @property
    def resultados_exibicao(self):
        return texto_por_idioma(self.resultados, self.resultados_es, self.resultados_en)

    @property
    def recomendacoes_exibicao(self):
        return texto_por_idioma(self.recomendacoes, self.recomendacoes_es, self.recomendacoes_en)

    @property
    def replicabilidade_exibicao(self):
        return texto_por_idioma(self.replicabilidade, self.replicabilidade_es, self.replicabilidade_en)

    @property
    def enfoque_justica_climatica_exibicao(self):
        return texto_por_idioma(self.enfoque_justica_climatica, self.enfoque_justica_climatica_es, self.enfoque_justica_climatica_en)

    @property
    def mudancas_ou_impactos_exibicao(self):
        return texto_por_idioma(self.mudancas_ou_impactos, self.mudancas_ou_impactos_es, self.mudancas_ou_impactos_en)

    @property
    def metodologia_exibicao(self):
        return texto_por_idioma(self.metodologia, self.metodologia_es, self.metodologia_en)

    @property
    def ferramentas_utilizadas_exibicao(self):
        return texto_por_idioma(self.ferramentas_utilizadas, self.ferramentas_utilizadas_es, self.ferramentas_utilizadas_en)

    @property
    def criterios_utilizados_exibicao(self):
        return texto_por_idioma(self.criterios_utilizados, self.criterios_utilizados_es, self.criterios_utilizados_en)

    @property
    def perguntas_chave_exibicao(self):
        return texto_por_idioma(self.perguntas_chave, self.perguntas_chave_es, self.perguntas_chave_en)

    @property
    def fontes_informacao_exibicao(self):
        return texto_por_idioma(self.fontes_informacao, self.fontes_informacao_es, self.fontes_informacao_en)

    @property
    def licoes_aprendidas_exibicao(self):
        return texto_por_idioma(self.licoes_aprendidas, self.licoes_aprendidas_es, self.licoes_aprendidas_en)

    @property
    def elementos_replicaveis_exibicao(self):
        return texto_por_idioma(self.elementos_replicaveis, self.elementos_replicaveis_es, self.elementos_replicaveis_en)

    @property
    def motivo_boa_pratica_exibicao(self):
        return texto_por_idioma(self.motivo_boa_pratica, self.motivo_boa_pratica_es, self.motivo_boa_pratica_en)

    @property
    def dificuldades_exibicao(self):
        return texto_por_idioma(self.dificuldades, self.dificuldades_es, self.dificuldades_en)

    @property
    def necessidades_para_replicacao_exibicao(self):
        return texto_por_idioma(
            self.necessidades_para_replicacao,
            self.necessidades_para_replicacao_es,
            self.necessidades_para_replicacao_en,
        )

    @property
    def ferramentas_metodologias_uteis_exibicao(self):
        return texto_por_idioma(
            self.ferramentas_metodologias_uteis,
            self.ferramentas_metodologias_uteis_es,
            self.ferramentas_metodologias_uteis_en,
        )

    @property
    def informacoes_adicionais_exibicao(self):
        return texto_por_idioma(
            self.informacoes_adicionais,
            self.informacoes_adicionais_es,
            self.informacoes_adicionais_en,
        )


class Anexo(models.Model):
    experiencia = models.ForeignKey(Experiencia, on_delete=models.CASCADE, related_name="anexos")
    titulo = models.CharField(max_length=200)
    titulo_es = models.CharField(max_length=200, blank=True)
    titulo_en = models.CharField(max_length=200, blank=True)
    arquivo = models.FileField(upload_to="anexos/", blank=True, null=True)
    url_externa = models.URLField(blank=True)

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo_exibicao

    @property
    def titulo_exibicao(self):
        return texto_por_idioma(self.titulo, self.titulo_es, self.titulo_en)


class PropostaEdicaoExperiencia(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_REVISAO = "em_revisao", "Em revisao"
        APROVADA = "aprovada", "Aprovada"
        REJEITADA = "rejeitada", "Rejeitada"

    experiencia = models.ForeignKey(
        Experiencia,
        on_delete=models.CASCADE,
        related_name="propostas_edicao",
    )
    email_contato = models.EmailField()
    comentario_autor = models.TextField(blank=True)
    comentario_revisor = models.TextField(blank=True)
    dados_json = models.JSONField(default=dict)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proposta de edicao"
        verbose_name_plural = "Propostas de edicao"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Proposta de edicao - {self.experiencia.titulo_exibicao} ({self.get_status_display()})"


class BancoTecnico(models.Model):

    titulo = models.CharField(max_length=220)
    titulo_es = models.CharField(max_length=220, blank=True)
    titulo_en = models.CharField(max_length=220, blank=True)
    descricao = models.TextField(blank=True)
    descricao_es = models.TextField(blank=True)
    descricao_en = models.TextField(blank=True)
    tipo_recurso = models.CharField(max_length=100)
    tipo_recurso_es = models.CharField(max_length=100, blank=True)
    tipo_recurso_en = models.CharField(max_length=100, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, related_name="recursos_tecnicos")
    dimensoes = models.ManyToManyField(DimensaoJusticaClimatica, blank=True, related_name="recursos_tecnicos")
    url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Banco tecnico"
        verbose_name_plural = "Banco tecnico"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo_exibicao

    @property
    def titulo_exibicao(self):
        return texto_por_idioma(self.titulo, self.titulo_es, self.titulo_en)

    @property
    def descricao_exibicao(self):
        return texto_por_idioma(self.descricao, self.descricao_es, self.descricao_en)

    @property
    def tipo_recurso_exibicao(self):
        return texto_por_idioma(self.tipo_recurso, self.tipo_recurso_es, self.tipo_recurso_en)


class Ferramenta(models.Model):
    class Situacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        PUBLICADA = "publicada", "Publicada"
        ARQUIVADA = "arquivada", "Arquivada"

    codigo = models.SlugField(max_length=160, unique=True)
    titulo = models.CharField(max_length=220, blank=True)
    titulo_es = models.CharField(max_length=220)
    titulo_en = models.CharField(max_length=220, blank=True)
    descricao = models.TextField(blank=True)
    descricao_es = models.TextField()
    descricao_en = models.TextField(blank=True)
    responsavel = models.CharField(max_length=255)
    periodo = models.CharField(max_length=30)
    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="ferramentas",
    )
    url = models.URLField(max_length=500)
    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.RASCUNHO,
    )
    ordem = models.PositiveSmallIntegerField()
    lote_origem = models.ForeignKey(
        "LoteImportacaoConteudo",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ferramentas_importadas",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ferramenta"
        verbose_name_plural = "Ferramentas"
        ordering = ["ordem", "titulo_es"]
        constraints = [
            models.UniqueConstraint(
                fields=["ordem"],
                name="ferramenta_ordem_unica",
            ),
        ]
        indexes = [
            models.Index(
                fields=["situacao", "ordem"],
                name="ferramenta_status_ordem",
            ),
            models.Index(
                fields=["setor", "situacao"],
                name="ferramenta_setor_status",
            ),
        ]

    def __str__(self):
        return self.titulo_exibicao

    @property
    def titulo_exibicao(self):
        return texto_por_idioma_com_fallback_es(
            self.titulo_es,
            self.titulo,
            self.titulo_en,
        )

    @property
    def descricao_exibicao(self):
        return texto_por_idioma_com_fallback_es(
            self.descricao_es,
            self.descricao,
            self.descricao_en,
        )


class LoteImportacaoConteudo(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_EXECUCAO = "em_execucao", "Em execucao"
        CONCLUIDO = "concluido", "Concluido"
        COM_DIVERGENCIAS = "com_divergencias", "Com divergencias"
        FALHOU = "falhou", "Falhou"
        REVERTIDO = "revertido", "Revertido"
        REVERSAO_PARCIAL = "reversao_parcial", "Reversao parcial"

    identificador = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    fonte = models.CharField(max_length=500)
    sha256 = models.CharField(
        max_length=64,
        validators=[
            RegexValidator(
                regex=r"^[0-9a-fA-F]{64}$",
                message="Informe um hash SHA-256 hexadecimal com 64 caracteres.",
            )
        ],
    )
    versao_fonte = models.CharField(max_length=100)
    executado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lotes_importacao_executados",
    )
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDENTE)
    contagens_esperadas = models.JSONField(default=dict)
    contagens_realizadas = models.JSONField(default=dict)
    relatorio_divergencias = models.JSONField(default=dict)
    mensagem_sanitizada = models.TextField(blank=True)
    revertido_em = models.DateTimeField(null=True, blank=True)
    revertido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lotes_importacao_revertidos",
    )
    justificativa_reversao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lote de importacao de conteudo"
        verbose_name_plural = "Lotes de importacao de conteudo"
        ordering = ["-iniciado_em"]
        indexes = [
            models.Index(fields=["status", "-iniciado_em"]),
            models.Index(fields=["sha256", "versao_fonte"]),
            models.Index(fields=["executado_por", "-iniciado_em"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(sha256__regex=r"^[0-9a-fA-F]{64}$"),
                name="lote_sha256_hex_64",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(finalizado_em__isnull=True)
                    | models.Q(finalizado_em__gte=models.F("iniciado_em"))
                ),
                name="lote_final_ge_inicio",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(
                        status__in=(
                            "concluido",
                            "com_divergencias",
                            "falhou",
                            "revertido",
                            "reversao_parcial",
                        )
                    )
                    | models.Q(finalizado_em__isnull=False)
                ),
                name="lote_status_final_com_data",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="falhou")
                    | (
                        ~models.Q(mensagem_sanitizada="")
                        & ~models.Q(contagens_realizadas={})
                    )
                ),
                name="lote_falha_detalhada",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status__in=("revertido", "reversao_parcial"))
                    | (
                        models.Q(revertido_em__isnull=False)
                        & models.Q(revertido_por__isnull=False)
                        & ~models.Q(justificativa_reversao="")
                    )
                ),
                name="lote_reversao_detalhada",
            ),
        ]

    def __str__(self):
        return f"{self.identificador} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        erros = {}
        status_finais = {
            self.Status.CONCLUIDO,
            self.Status.COM_DIVERGENCIAS,
            self.Status.FALHOU,
            self.Status.REVERTIDO,
            self.Status.REVERSAO_PARCIAL,
        }
        if self.finalizado_em and self.iniciado_em and self.finalizado_em < self.iniciado_em:
            erros["finalizado_em"] = "A finalizacao nao pode anteceder o inicio."
        if self.status in status_finais and not self.finalizado_em:
            erros["finalizado_em"] = "Um lote em estado final deve informar a finalizacao."
        if self.status == self.Status.FALHOU:
            if not self.mensagem_sanitizada.strip():
                erros["mensagem_sanitizada"] = "Uma falha deve possuir mensagem sanitizada."
            if not self.contagens_realizadas:
                erros["contagens_realizadas"] = "Uma falha deve registrar as contagens realizadas."
        if self.status in {self.Status.REVERTIDO, self.Status.REVERSAO_PARCIAL}:
            if not self.revertido_em:
                erros["revertido_em"] = "Uma reversao deve informar sua data."
            if not self.revertido_por_id:
                erros["revertido_por"] = "Uma reversao deve informar o responsavel."
            if not self.justificativa_reversao.strip():
                erros["justificativa_reversao"] = "Uma reversao deve possuir justificativa."
        if erros:
            raise ValidationError(erros)


class ItemLoteImportacaoConteudo(models.Model):
    class Entidade(models.TextChoices):
        MARCO = "marco", "Marco"
        FERRAMENTA = "ferramenta", "Ferramenta"
        SETOR = "setor", "Setor"
        SETOR_GUIA = "setor_guia", "Setor do guia"
        VERSAO_GUIA = "versao_guia", "Versao do guia"
        EIXO = "eixo", "Eixo"
        SUBEIXO = "subeixo", "Subeixo"
        SUBAREA = "subarea", "Subarea"
        PERGUNTA = "pergunta", "Pergunta"
        REFERENCIA = "referencia", "Referencia"
        SUBAREA_REFERENCIA_GUIA = "subarea_referencia_guia", "Ocorrencia de referencia em subarea"
        EXPERIENCIA_PERGUNTA_GUIA = "experiencia_pergunta_guia", "Experiencia e pergunta do guia"
        VINCULO_USUARIO_EFS = "vinculo_usuario_efs", "Vinculo usuario-EFS"
        EPISODIO_VINCULO_USUARIO_EFS = "episodio_vinculo_usuario_efs", "Episodio de vinculo usuario-EFS"
        ATRIBUICAO_PAPEL_VINCULO = "atribuicao_papel_vinculo", "Atribuicao de papel no vinculo"

    class Operacao(models.TextChoices):
        CRIADO = "criado", "Criado"
        ATUALIZADO = "atualizado", "Atualizado"
        IGNORADO = "ignorado", "Ignorado"
        FALHOU = "falhou", "Falhou"

    class StatusRollback(models.TextChoices):
        NAO_APLICAVEL = "nao_aplicavel", "Nao aplicavel"
        PENDENTE = "pendente", "Pendente"
        REVERTIDO = "revertido", "Revertido"
        BLOQUEADO = "bloqueado", "Bloqueado"

    lote = models.ForeignKey(
        LoteImportacaoConteudo,
        on_delete=models.PROTECT,
        related_name="itens",
    )
    entidade = models.CharField(max_length=50, choices=Entidade.choices)
    codigo_origem = models.CharField(max_length=160)
    objeto_pk = models.CharField(max_length=64, blank=True)
    operacao = models.CharField(max_length=20, choices=Operacao.choices)
    snapshot_anterior = models.JSONField(default=dict, blank=True)
    status_rollback = models.CharField(
        max_length=20,
        choices=StatusRollback.choices,
        default=StatusRollback.NAO_APLICAVEL,
    )
    mensagem = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de lote de importacao de conteudo"
        verbose_name_plural = "Itens de lote de importacao de conteudo"
        ordering = ["lote", "entidade", "codigo_origem"]
        constraints = [
            models.UniqueConstraint(
                fields=["lote", "entidade", "codigo_origem"],
                name="item_lote_origem_unico",
            )
        ]
        indexes = [
            models.Index(fields=["lote", "operacao"]),
            models.Index(fields=["entidade", "objeto_pk"]),
        ]

    def __str__(self):
        return f"{self.lote.identificador} - {self.entidade}:{self.codigo_origem}"

    def clean(self):
        super().clean()
        if not isinstance(self.snapshot_anterior, dict):
            raise ValidationError({"snapshot_anterior": "O snapshot deve ser um objeto JSON."})

        chaves_proibidas = {
            "arquivo",
            "authorization",
            "conteudo_binario",
            "cookie",
            "email",
            "ip",
            "password",
            "secret",
            "segredo",
            "senha",
            "sessao",
            "session",
            "token",
        }

        def validar(valor):
            if isinstance(valor, (bytes, bytearray, memoryview)):
                raise ValidationError({"snapshot_anterior": "O snapshot nao pode armazenar conteudo binario."})
            if isinstance(valor, dict):
                for chave, item in valor.items():
                    chave_normalizada = str(chave).casefold().replace("-", "_")
                    partes = set(chave_normalizada.split("_"))
                    if chave_normalizada in chaves_proibidas or partes & chaves_proibidas:
                        raise ValidationError(
                            {"snapshot_anterior": "O snapshot contem uma chave de dado sensivel nao permitida."}
                        )
                    validar(item)
            elif isinstance(valor, (list, tuple)):
                for item in valor:
                    validar(item)

        validar(self.snapshot_anterior)


class PapelInstitucional(models.Model):
    codigo = models.SlugField(max_length=50, unique=True)
    nome = models.CharField(max_length=100)
    nome_es = models.CharField(max_length=100)
    nome_en = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    descricao_es = models.TextField(blank=True)
    descricao_en = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Papel institucional"
        verbose_name_plural = "Papeis institucionais"
        ordering = ["ordem", "codigo"]
        indexes = [models.Index(fields=["ativo", "ordem"])]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def clean(self):
        super().clean()
        erros = {}
        if self.ativo:
            campos_traduzidos = {
                "nome": self.nome,
                "nome_es": self.nome_es,
                "nome_en": self.nome_en,
            }
            for campo, valor in campos_traduzidos.items():
                if not valor.strip():
                    erros[campo] = "Um papel ativo deve possuir nome nos tres idiomas."
        if self.pk and self.atribuicoes.exists():
            codigo_original = type(self).objects.filter(pk=self.pk).values_list("codigo", flat=True).first()
            if codigo_original and codigo_original != self.codigo:
                erros["codigo"] = "O codigo nao pode mudar depois que o papel for utilizado."
        if erros:
            raise ValidationError(erros)


class VinculoUsuarioEFS(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vinculos_efs",
    )
    efs = models.ForeignKey(EFS, on_delete=models.PROTECT, related_name="vinculos_usuarios")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vinculo usuario-EFS"
        verbose_name_plural = "Vinculos usuario-EFS"
        ordering = ["efs__nome", "usuario__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "efs"],
                name="vinculo_usuario_efs_unico",
            )
        ]

    def __str__(self):
        return f"{self.usuario.get_username()} - {self.efs}"


class EpisodioVinculoUsuarioEFS(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        ATIVO = "ativo", "Ativo"
        SUSPENSO = "suspenso", "Suspenso"
        ENCERRADO = "encerrado", "Encerrado"
        REJEITADO = "rejeitado", "Rejeitado"

    class Origem(models.TextChoices):
        SOLICITACAO = "solicitacao", "Solicitacao"
        ADMINISTRACAO = "administracao", "Administracao"
        MIGRACAO = "migracao", "Migracao"

    vinculo = models.ForeignKey(
        VinculoUsuarioEFS,
        on_delete=models.PROTECT,
        related_name="episodios",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    origem = models.CharField(max_length=20, choices=Origem.choices)
    solicitado_em = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    decidido_em = models.DateTimeField(null=True, blank=True)
    decidido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="episodios_vinculo_decididos",
    )
    justificativa_decisao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Episodio de vinculo usuario-EFS"
        verbose_name_plural = "Episodios de vinculo usuario-EFS"
        ordering = ["-solicitado_em", "-pk"]
        indexes = [
            models.Index(fields=["vinculo", "status"]),
            models.Index(fields=["status", "data_fim"]),
            models.Index(fields=["decidido_por", "-decidido_em"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["vinculo"],
                condition=models.Q(status__in=("pendente", "ativo", "suspenso")),
                name="episodio_corrente_unico",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(data_fim__isnull=True)
                    | (
                        models.Q(data_inicio__isnull=False)
                        & models.Q(data_fim__gte=models.F("data_inicio"))
                    )
                ),
                name="episodio_fim_ge_inicio",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="ativo")
                    | (
                        models.Q(data_inicio__isnull=False)
                        & models.Q(decidido_em__isnull=False)
                        & models.Q(decidido_por__isnull=False)
                    )
                ),
                name="episodio_ativo_decidido",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="suspenso")
                    | models.Q(data_inicio__isnull=False)
                ),
                name="episodio_suspenso_com_inicio",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status__in=("rejeitado", "suspenso", "encerrado"))
                    | (
                        models.Q(decidido_em__isnull=False)
                        & models.Q(decidido_por__isnull=False)
                        & ~models.Q(justificativa_decisao="")
                    )
                ),
                name="episodio_decisao_detalhada",
            ),
            models.CheckConstraint(
                condition=(~models.Q(status="encerrado") | models.Q(data_fim__isnull=False)),
                name="episodio_encerrado_com_fim",
            ),
        ]

    def __str__(self):
        return f"{self.vinculo} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.decidido_por_id and self.vinculo_id:
            usuario_id = (
                VinculoUsuarioEFS.objects.filter(pk=self.vinculo_id)
                .values_list("usuario_id", flat=True)
                .first()
            )
            if self.decidido_por_id == usuario_id:
                raise ValidationError({"decidido_por": "O usuario do vinculo nao pode decidir o proprio episodio."})


class AtribuicaoPapelVinculo(models.Model):
    episodio = models.ForeignKey(
        EpisodioVinculoUsuarioEFS,
        on_delete=models.PROTECT,
        related_name="atribuicoes",
    )
    papel = models.ForeignKey(
        PapelInstitucional,
        on_delete=models.PROTECT,
        related_name="atribuicoes",
    )
    atribuido_em = models.DateTimeField(auto_now_add=True)
    atribuido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="papeis_institucionais_atribuidos",
    )
    revogado_em = models.DateTimeField(null=True, blank=True)
    revogado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="papeis_institucionais_revogados",
    )
    justificativa_revogacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Atribuicao de papel no vinculo"
        verbose_name_plural = "Atribuicoes de papel no vinculo"
        ordering = ["episodio", "papel", "-atribuido_em"]
        indexes = [
            models.Index(fields=["episodio", "revogado_em"]),
            models.Index(fields=["papel", "revogado_em"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["episodio", "papel"],
                condition=models.Q(revogado_em__isnull=True),
                name="atribuicao_ativa_unica",
            ),
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(revogado_em__isnull=True)
                        & models.Q(revogado_por__isnull=True)
                        & models.Q(justificativa_revogacao="")
                    )
                    | (
                        models.Q(revogado_em__isnull=False)
                        & models.Q(revogado_por__isnull=False)
                        & ~models.Q(justificativa_revogacao="")
                    )
                ),
                name="atribuicao_revogacao_completa",
            ),
        ]

    def __str__(self):
        return f"{self.episodio} - {self.papel.codigo}"

    def clean(self):
        super().clean()
        erros = {}
        if (
            not self.pk
            and self.papel_id
            and PapelInstitucional.objects.filter(pk=self.papel_id, ativo=False).exists()
        ):
            erros["papel"] = "Somente um papel ativo pode ser atribuido."
        if self.episodio_id:
            episodio = (
                EpisodioVinculoUsuarioEFS.objects.filter(pk=self.episodio_id)
                .values("origem", "vinculo__usuario_id")
                .first()
            )
            if episodio:
                origens_com_responsavel = {
                    EpisodioVinculoUsuarioEFS.Origem.SOLICITACAO,
                    EpisodioVinculoUsuarioEFS.Origem.ADMINISTRACAO,
                }
                if episodio["origem"] in origens_com_responsavel and not self.atribuido_por_id:
                    erros["atribuido_por"] = "A origem do episodio exige o responsavel pela atribuicao."
                usuario_id = episodio["vinculo__usuario_id"]
                if self.atribuido_por_id == usuario_id:
                    erros["atribuido_por"] = "O usuario do vinculo nao pode atribuir papel a si mesmo."
                if self.revogado_por_id == usuario_id:
                    erros["revogado_por"] = "O usuario do vinculo nao pode revogar o proprio papel."
        dados_revogacao = (
            bool(self.revogado_em),
            bool(self.revogado_por_id),
            bool(self.justificativa_revogacao.strip()),
        )
        if any(dados_revogacao) and not all(dados_revogacao):
            erros["revogado_em"] = "A revogacao exige data, responsavel e justificativa."
        if erros:
            raise ValidationError(erros)


class EventoVinculoUsuarioEFS(models.Model):
    class Acao(models.TextChoices):
        SOLICITADO = "solicitado", "Solicitado"
        ATIVADO = "ativado", "Ativado"
        REJEITADO = "rejeitado", "Rejeitado"
        SUSPENSO = "suspenso", "Suspenso"
        REATIVADO = "reativado", "Reativado"
        ENCERRADO = "encerrado", "Encerrado"
        PAPEL_ADICIONADO = "papel_adicionado", "Papel adicionado"
        PAPEL_REVOGADO = "papel_revogado", "Papel revogado"

    episodio = models.ForeignKey(
        EpisodioVinculoUsuarioEFS,
        on_delete=models.PROTECT,
        related_name="eventos",
    )
    papel = models.ForeignKey(
        PapelInstitucional,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_vinculo",
    )
    atribuicao_papel = models.ForeignKey(
        AtribuicaoPapelVinculo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos",
    )
    lote_origem = models.ForeignKey(
        LoteImportacaoConteudo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_vinculo",
    )
    item_lote_origem = models.ForeignKey(
        ItemLoteImportacaoConteudo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="eventos_vinculo",
    )
    acao = models.CharField(max_length=30, choices=Acao.choices)
    status_anterior = models.CharField(
        max_length=20,
        choices=EpisodioVinculoUsuarioEFS.Status.choices,
        blank=True,
    )
    status_novo = models.CharField(
        max_length=20,
        choices=EpisodioVinculoUsuarioEFS.Status.choices,
        blank=True,
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_vinculo_efs",
    )
    justificativa = models.TextField(blank=True)
    ocorrido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de vinculo usuario-EFS"
        verbose_name_plural = "Eventos de vinculo usuario-EFS"
        ordering = ["-ocorrido_em", "-pk"]
        indexes = [
            models.Index(fields=["episodio", "-ocorrido_em"]),
            models.Index(fields=["papel", "-ocorrido_em"]),
            models.Index(fields=["responsavel", "-ocorrido_em"]),
            models.Index(fields=["lote_origem", "ocorrido_em"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~models.Q(acao__in=("papel_adicionado", "papel_revogado"))
                    | models.Q(papel__isnull=False)
                ),
                name="evento_papel_exige_papel",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(item_lote_origem__isnull=True)
                    | models.Q(lote_origem__isnull=False)
                ),
                name="evento_item_exige_lote",
            ),
        ]

    def __str__(self):
        return f"{self.episodio} - {self.get_acao_display()}"

    def clean(self):
        super().clean()
        erros = {}
        if self.acao in {self.Acao.PAPEL_ADICIONADO, self.Acao.PAPEL_REVOGADO} and not self.papel_id:
            erros["papel"] = "Uma acao de papel deve identificar o papel."
        if self.atribuicao_papel_id:
            atribuicao = (
                AtribuicaoPapelVinculo.objects.filter(pk=self.atribuicao_papel_id)
                .values("episodio_id", "papel_id")
                .first()
            )
            if atribuicao and atribuicao["episodio_id"] != self.episodio_id:
                erros["atribuicao_papel"] = "A atribuicao deve pertencer ao episodio do evento."
            if atribuicao and self.papel_id and atribuicao["papel_id"] != self.papel_id:
                erros["papel"] = "O papel deve corresponder ao papel da atribuicao."
        if self.item_lote_origem_id:
            if not self.lote_origem_id:
                erros["lote_origem"] = "Um item de origem exige o lote correspondente."
            elif not ItemLoteImportacaoConteudo.objects.filter(
                pk=self.item_lote_origem_id,
                lote_id=self.lote_origem_id,
            ).exists():
                erros["item_lote_origem"] = "O item deve pertencer ao lote informado."
        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError("Eventos de vinculo sao imutaveis.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Eventos de vinculo nao podem ser excluidos pelo fluxo normal.")


class VersaoGuia(models.Model):
    class Situacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        PUBLICADA = "publicada", "Publicada"

    codigo = models.SlugField(max_length=100, unique=True)
    fonte = models.CharField(max_length=500)
    sha256_fonte = models.CharField(
        max_length=64,
        validators=[
            RegexValidator(
                regex=r"^[0-9a-fA-F]{64}$",
                message="Informe um hash SHA-256 hexadecimal com 64 caracteres.",
            )
        ],
    )
    idioma_canonico = models.CharField(max_length=5, default="es", editable=False)
    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.RASCUNHO,
    )
    vigente = models.BooleanField(default=False)
    publicado_em = models.DateTimeField(null=True, blank=True)
    lote_origem = models.ForeignKey(
        LoteImportacaoConteudo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="versoes_guia",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Versao do guia"
        verbose_name_plural = "Versoes do guia"
        ordering = ["-vigente", "-publicado_em", "-criado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["vigente"],
                condition=models.Q(vigente=True),
                name="guia_versao_vigente_unica",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        situacao="rascunho",
                        vigente=False,
                        publicado_em__isnull=True,
                    )
                    | models.Q(
                        situacao="publicada",
                        publicado_em__isnull=False,
                        lote_origem__isnull=False,
                    )
                ),
                name="guia_versao_estado_coerente",
            ),
            models.CheckConstraint(
                condition=models.Q(sha256_fonte__regex=r"^[0-9a-fA-F]{64}$"),
                name="guia_versao_sha256_valido",
            ),
        ]
        indexes = [
            models.Index(fields=["situacao", "vigente"], name="guia_versao_status_vig"),
            models.Index(fields=["sha256_fonte"], name="guia_versao_sha256"),
        ]

    def __str__(self):
        marcador = " vigente" if self.vigente else ""
        return f"{self.codigo} - {self.get_situacao_display()}{marcador}"

    def clean(self):
        super().clean()
        erros = {}
        if self.idioma_canonico != "es":
            erros["idioma_canonico"] = "O idioma canonico desta fundacao deve permanecer espanhol."
        if self.situacao == self.Situacao.RASCUNHO:
            if self.vigente:
                erros["vigente"] = "Uma versao em rascunho nao pode estar vigente."
            if self.publicado_em:
                erros["publicado_em"] = "Uma versao em rascunho nao pode ter data de publicacao."
        elif self.situacao == self.Situacao.PUBLICADA:
            if not self.publicado_em:
                erros["publicado_em"] = "Uma versao publicada deve informar a data de publicacao."
            if not self.lote_origem_id:
                erros["lote_origem"] = "Uma versao publicada deve registrar o lote de origem."
        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).first()
            if original and original.situacao == self.Situacao.PUBLICADA:
                campos_imutaveis = (
                    "codigo",
                    "fonte",
                    "sha256_fonte",
                    "idioma_canonico",
                    "situacao",
                    "publicado_em",
                    "lote_origem_id",
                )
                alterados = [
                    campo
                    for campo in campos_imutaveis
                    if getattr(original, campo) != getattr(self, campo)
                ]
                if alterados:
                    raise ValidationError(
                        "Uma versao publicada e imutavel; somente sua vigencia pode ser alterada."
                    )
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.situacao == self.Situacao.PUBLICADA:
            raise ValidationError("Uma versao publicada nao pode ser excluida.")
        return super().delete(*args, **kwargs)


class ConteudoGuiaProtegido(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def versao_guia(self):
        raise NotImplementedError

    def _validar_versao_editavel(self):
        versao = self.versao_guia
        if versao and versao.situacao == VersaoGuia.Situacao.PUBLICADA:
            raise ValidationError("O conteudo de uma versao publicada e imutavel.")

    def save(self, *args, **kwargs):
        self._validar_versao_editavel()
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._validar_versao_editavel()
        return super().delete(*args, **kwargs)


class EixoGuia(ConteudoGuiaProtegido):
    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="eixos",
    )
    codigo = models.SlugField(max_length=160)
    nome_es = models.CharField(max_length=220)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Eixo do guia"
        verbose_name_plural = "Eixos do guia"
        ordering = ["versao", "ordem", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_eixo_codigo_versao_unico",
            ),
            models.UniqueConstraint(
                fields=["versao", "ordem"],
                name="guia_eixo_ordem_versao_unica",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.nome_es}"


class SubeixoGuia(ConteudoGuiaProtegido):
    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="subeixos",
    )
    eixo = models.ForeignKey(
        EixoGuia,
        on_delete=models.PROTECT,
        related_name="subeixos",
    )
    codigo = models.SlugField(max_length=160)
    nome_es = models.CharField(max_length=220)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Subeixo do guia"
        verbose_name_plural = "Subeixos do guia"
        ordering = ["versao", "eixo__ordem", "ordem", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_subeixo_codigo_versao_unico",
            ),
            models.UniqueConstraint(
                fields=["eixo", "ordem"],
                name="guia_subeixo_ordem_eixo_unica",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.nome_es}"

    def clean(self):
        super().clean()
        if self.versao_id and self.eixo_id and self.eixo.versao_id != self.versao_id:
            raise ValidationError({"eixo": "O eixo deve pertencer a mesma versao do subeixo."})


class SetorGuia(ConteudoGuiaProtegido):
    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="setores",
    )
    codigo = models.SlugField(max_length=160)
    nome_es = models.CharField(max_length=220)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Setor do guia"
        verbose_name_plural = "Setores do guia"
        ordering = ["versao", "ordem", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_setor_codigo_versao_unico",
            ),
            models.UniqueConstraint(
                fields=["versao", "ordem"],
                name="guia_setor_ordem_versao_unica",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.nome_es}"


class SubareaGuia(ConteudoGuiaProtegido):
    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="subareas",
    )
    setor = models.ForeignKey(
        SetorGuia,
        on_delete=models.PROTECT,
        related_name="subareas",
    )
    codigo = models.SlugField(max_length=160)
    nome_es = models.CharField(max_length=220)
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Subarea do guia"
        verbose_name_plural = "Subareas do guia"
        ordering = ["versao", "setor__ordem", "ordem", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_subarea_codigo_versao_unico",
            ),
            models.UniqueConstraint(
                fields=["setor", "ordem"],
                name="guia_subarea_ordem_setor_unica",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.nome_es}"

    def clean(self):
        super().clean()
        if self.versao_id and self.setor_id and self.setor.versao_id != self.versao_id:
            raise ValidationError({"setor": "O setor deve pertencer a mesma versao da subarea."})


class PerguntaGuia(ConteudoGuiaProtegido):
    class TipoAuditoria(models.TextChoices):
        CUMPLIMIENTO = "cumplimiento", "Conformidade"
        GESTION = "gestion", "Gestao"

    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="perguntas",
    )
    codigo = models.SlugField(max_length=160)
    texto_es = models.TextField()
    tipo_auditoria = models.CharField(max_length=20, choices=TipoAuditoria.choices)
    ordem = models.PositiveSmallIntegerField()
    eixo = models.ForeignKey(
        EixoGuia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perguntas_diretas",
    )
    subeixo = models.ForeignKey(
        SubeixoGuia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perguntas",
    )
    subarea = models.ForeignKey(
        SubareaGuia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perguntas",
    )

    class Meta:
        verbose_name = "Pergunta do guia"
        verbose_name_plural = "Perguntas do guia"
        ordering = ["versao", "tipo_auditoria", "ordem", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_pergunta_codigo_versao_unico",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(eixo__isnull=False, subeixo__isnull=True, subarea__isnull=True)
                    | models.Q(eixo__isnull=True, subeixo__isnull=False, subarea__isnull=True)
                    | models.Q(eixo__isnull=True, subeixo__isnull=True, subarea__isnull=False)
                ),
                name="guia_pergunta_um_escopo",
            ),
            models.UniqueConstraint(
                fields=["eixo", "tipo_auditoria", "ordem"],
                condition=models.Q(eixo__isnull=False),
                name="guia_pergunta_ordem_eixo_unica",
            ),
            models.UniqueConstraint(
                fields=["subeixo", "tipo_auditoria", "ordem"],
                condition=models.Q(subeixo__isnull=False),
                name="guia_pergunta_ordem_subeixo_unica",
            ),
            models.UniqueConstraint(
                fields=["subarea", "tipo_auditoria", "ordem"],
                condition=models.Q(subarea__isnull=False),
                name="guia_pergunta_ordem_subarea_unica",
            ),
        ]
        indexes = [
            models.Index(
                fields=["versao", "tipo_auditoria"],
                name="guia_pergunta_versao_tipo",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.get_tipo_auditoria_display()}"

    def clean(self):
        super().clean()
        escopos = [self.eixo_id, self.subeixo_id, self.subarea_id]
        if sum(valor is not None for valor in escopos) != 1:
            raise ValidationError("A pergunta deve possuir exatamente um escopo hierarquico.")
        erros = {}
        if self.eixo_id and self.eixo.versao_id != self.versao_id:
            erros["eixo"] = "O eixo deve pertencer a mesma versao da pergunta."
        if self.subeixo_id and self.subeixo.versao_id != self.versao_id:
            erros["subeixo"] = "O subeixo deve pertencer a mesma versao da pergunta."
        if self.subarea_id and self.subarea.versao_id != self.versao_id:
            erros["subarea"] = "A subarea deve pertencer a mesma versao da pergunta."
        if erros:
            raise ValidationError(erros)


class ReferenciaGuia(ConteudoGuiaProtegido):
    versao = models.ForeignKey(
        VersaoGuia,
        on_delete=models.PROTECT,
        related_name="referencias",
    )
    codigo = models.SlugField(max_length=160)
    citacao_es = models.TextField()

    class Meta:
        verbose_name = "Referencia do guia"
        verbose_name_plural = "Referencias do guia"
        ordering = ["versao", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["versao", "codigo"],
                name="guia_referencia_codigo_versao_unico",
            ),
        ]

    @property
    def versao_guia(self):
        return self.versao

    def __str__(self):
        return f"{self.codigo} - {self.citacao_es[:80]}"


class SubareaReferenciaGuia(ConteudoGuiaProtegido):
    subarea = models.ForeignKey(
        SubareaGuia,
        on_delete=models.PROTECT,
        related_name="ocorrencias_referencias",
    )
    referencia = models.ForeignKey(
        ReferenciaGuia,
        on_delete=models.PROTECT,
        related_name="ocorrencias_subareas",
    )
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = "Ocorrencia de referencia do guia"
        verbose_name_plural = "Ocorrencias de referencias do guia"
        ordering = ["subarea", "ordem", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["subarea", "ordem"],
                name="guia_ref_ordem_subarea_unica",
            ),
        ]
        indexes = [
            models.Index(
                fields=["referencia", "subarea"],
                name="guia_ref_subarea_lookup",
            ),
        ]

    @property
    def versao_guia(self):
        if not self.subarea_id:
            return None
        return self.subarea.versao

    def __str__(self):
        return f"{self.subarea} - {self.ordem}: {self.referencia.codigo}"

    def clean(self):
        super().clean()
        if (
            self.subarea_id
            and self.referencia_id
            and self.subarea.versao_id != self.referencia.versao_id
        ):
            raise ValidationError(
                {"referencia": "A referencia deve pertencer a mesma versao da subarea."}
            )
