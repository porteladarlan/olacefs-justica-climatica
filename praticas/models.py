from django.db import models


class Pais(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    sigla = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Pais"
        verbose_name_plural = "Paises"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class EFS(models.Model):
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=30, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="efs")

    class Meta:
        verbose_name = "EFS"
        verbose_name_plural = "EFS"
        ordering = ["pais__nome", "nome"]
        unique_together = ("nome", "pais")

    def __str__(self):
        if self.sigla:
            return f"{self.nome} ({self.sigla})"
        return self.nome


class TipoExperiencia(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Tipo de experiencia"
        verbose_name_plural = "Tipos de experiencia"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Setor(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class DimensaoJusticaClimatica(models.Model):
    nome = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Dimensao de justica climatica"
        verbose_name_plural = "Dimensoes de justica climatica"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class GrupoVulneravel(models.Model):
    nome = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Grupo vulneravel"
        verbose_name_plural = "Grupos vulneraveis"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Experiencia(models.Model):
    class StatusIniciativa(models.TextChoices):
        PLANEJAMENTO = "planejamento", "Planejamento"
        EXECUCAO = "execucao", "Execucao"
        CONCLUIDA = "concluida", "Concluida"

    class StatusPublicacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        PUBLICADO = "publicado", "Publicado"

    titulo = models.CharField(max_length=250)
    efs = models.ForeignKey(EFS, on_delete=models.PROTECT, related_name="experiencias")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="experiencias")
    tipo_experiencia = models.ForeignKey(TipoExperiencia, on_delete=models.PROTECT, related_name="experiencias")
    ano_execucao = models.PositiveIntegerField()
    status_iniciativa = models.CharField(
        max_length=20,
        choices=StatusIniciativa.choices,
        default=StatusIniciativa.PLANEJAMENTO,
    )
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name="experiencias")

    descricao = models.TextField(blank=True)
    problema_climatico = models.TextField(blank=True)
    relacao_adaptacao_mitigacao_gestao_desastres = models.TextField(blank=True)
    riscos_climaticos = models.TextField(blank=True)
    enfoque_justica_climatica = models.TextField(blank=True)

    dimensoes_consideradas = models.ManyToManyField(
        DimensaoJusticaClimatica,
        blank=True,
        related_name="experiencias",
    )
    grupos_vulneraveis = models.ManyToManyField(
        GrupoVulneravel,
        blank=True,
        related_name="experiencias",
    )

    impactos_diferenciados = models.TextField(blank=True)
    objetivo = models.TextField(blank=True)
    perguntas_chave = models.TextField(blank=True)
    criterios_utilizados = models.TextField(blank=True)
    metodologia = models.TextField(blank=True)
    fontes_informacao = models.TextField(blank=True)
    resultados = models.TextField(blank=True)
    recomendacoes = models.TextField(blank=True)
    mudancas_ou_impactos = models.TextField(blank=True)
    motivo_boa_pratica = models.TextField(blank=True)
    elementos_replicaveis = models.TextField(blank=True)
    dificuldades = models.TextField(blank=True)
    licoes_aprendidas = models.TextField(blank=True)
    o_que_fariam_diferente = models.TextField(blank=True)
    replicabilidade = models.TextField(blank=True)
    necessidades_para_replicacao = models.TextField(blank=True)
    ferramentas_metodologias_uteis = models.TextField(blank=True)
    temas_sugeridos_para_guia = models.TextField(blank=True)
    apoio_requerido_pelas_efs = models.TextField(blank=True)

    status_publicacao = models.CharField(
        max_length=20,
        choices=StatusPublicacao.choices,
        default=StatusPublicacao.RASCUNHO,
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Experiencia"
        verbose_name_plural = "Experiencias"
        ordering = ["-ano_execucao", "titulo"]

    def __str__(self):
        return self.titulo


class Anexo(models.Model):
    experiencia = models.ForeignKey(
        Experiencia,
        on_delete=models.CASCADE,
        related_name="anexos",
    )
    titulo = models.CharField(max_length=200)
    arquivo = models.FileField(upload_to="anexos_experiencias/", blank=True, null=True)
    url_externa = models.URLField(blank=True)

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        ordering = ["experiencia", "titulo"]

    def __str__(self):
        return self.titulo


class BancoTecnico(models.Model):
    titulo = models.CharField(max_length=250)
    descricao = models.TextField(blank=True)
    tipo_recurso = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    setor = models.ForeignKey(
        Setor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recursos_banco_tecnico",
    )
    dimensoes = models.ManyToManyField(
        DimensaoJusticaClimatica,
        blank=True,
        related_name="recursos_banco_tecnico",
    )

    class Meta:
        verbose_name = "Banco tecnico"
        verbose_name_plural = "Banco tecnico"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo
