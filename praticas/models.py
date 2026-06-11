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
