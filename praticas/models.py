from django.db import models


class Pais(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nome


class EFS(models.Model):
    nome = models.CharField(max_length=150)
    sigla = models.CharField(max_length=20, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="efs")

    class Meta:
        ordering = ["nome"]
        verbose_name = "EFS"
        verbose_name_plural = "EFS"
        unique_together = ("nome", "pais")

    def __str__(self):
        return f"{self.nome} ({self.pais.sigla})"


class TipoExperiencia(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Tipo de experiência"
        verbose_name_plural = "Tipos de experiência"

    def __str__(self):
        return self.nome


class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class DimensaoJusticaClimatica(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Dimensão de justiça climática"
        verbose_name_plural = "Dimensões de justiça climática"

    def __str__(self):
        return self.nome


class GrupoVulneravel(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Grupo vulnerável"
        verbose_name_plural = "Grupos vulneráveis"

    def __str__(self):
        return self.nome


class Experiencia(models.Model):
    class StatusIniciativa(models.TextChoices):
        EM_PLANEJAMENTO = "planejamento", "Em planejamento"
        EM_EXECUCAO = "execucao", "Em execução"
        CONCLUIDA = "concluida", "Concluída"

    class StatusPublicacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        PUBLICADO = "publicado", "Publicado"

    titulo = models.CharField(max_length=250)
    efs = models.ForeignKey(EFS, on_delete=models.PROTECT, related_name="experiencias")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="experiencias")
    tipo_experiencia = models.ForeignKey(TipoExperiencia, on_delete=models.PROTECT, related_name="experiencias")
    ano_execucao = models.PositiveIntegerField()
    status_iniciativa = models.CharField(max_length=20, choices=StatusIniciativa.choices)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name="experiencias")
    descricao = models.TextField()
    problema_climatico = models.TextField()
    relacao_adaptacao_mitigacao_gestao_desastres = models.TextField()
    riscos_climaticos = models.TextField()
    enfoque_justica_climatica = models.TextField()
    dimensoes_consideradas = models.ManyToManyField(DimensaoJusticaClimatica, related_name="experiencias")
    grupos_vulneraveis = models.ManyToManyField(GrupoVulneravel, related_name="experiencias")
    impactos_diferenciados = models.TextField()
    objetivo = models.TextField()
    perguntas_chave = models.TextField()
    criterios_utilizados = models.TextField()
    metodologia = models.TextField()
    fontes_informacao = models.TextField()
    resultados = models.TextField()
    recomendacoes = models.TextField()
    mudancas_ou_impactos = models.TextField()
    motivo_boa_pratica = models.TextField()
    elementos_replicaveis = models.TextField()
    dificuldades = models.TextField()
    licoes_aprendidas = models.TextField()
    o_que_fariam_diferente = models.TextField()
    replicabilidade = models.TextField()
    necessidades_para_replicacao = models.TextField()
    ferramentas_metodologias_uteis = models.TextField()
    temas_sugeridos_para_guia = models.TextField()
    apoio_requerido_pelas_efs = models.TextField()
    status_publicacao = models.CharField(max_length=20, choices=StatusPublicacao.choices, default=StatusPublicacao.PUBLICADO)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ano_execucao", "titulo"]

    def __str__(self):
        return self.titulo


class Anexo(models.Model):
    experiencia = models.ForeignKey(Experiencia, on_delete=models.CASCADE, related_name="anexos")
    titulo = models.CharField(max_length=150)
    arquivo = models.FileField(upload_to="anexos/", blank=True, null=True)
    url_externa = models.URLField(blank=True)

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class BancoTecnico(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo_recurso = models.CharField(max_length=100)
    url = models.URLField()
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, related_name="recursos_banco")
    dimensoes = models.ManyToManyField(DimensaoJusticaClimatica, blank=True, related_name="recursos_banco")

    class Meta:
        ordering = ["titulo"]
        verbose_name = "Banco técnico"
        verbose_name_plural = "Banco técnico"

    def __str__(self):
        return self.titulo
