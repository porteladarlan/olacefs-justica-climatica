from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DimensaoJusticaClimatica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, unique=True)),
            ],
            options={
                'verbose_name': 'Dimensão de justiça climática',
                'verbose_name_plural': 'Dimensões de justiça climática',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='GrupoVulneravel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, unique=True)),
            ],
            options={
                'verbose_name': 'Grupo vulnerável',
                'verbose_name_plural': 'Grupos vulneráveis',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('sigla', models.CharField(max_length=3, unique=True)),
            ],
            options={
                'verbose_name': 'País',
                'verbose_name_plural': 'Países',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='TipoExperiencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Tipo de experiência',
                'verbose_name_plural': 'Tipos de experiência',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='BancoTecnico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descricao', models.TextField()),
                ('tipo_recurso', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('dimensoes', models.ManyToManyField(blank=True, related_name='recursos_banco', to='praticas.dimensaojusticaclimatica')),
                ('setor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recursos_banco', to='praticas.setor')),
            ],
            options={
                'verbose_name': 'Banco técnico',
                'verbose_name_plural': 'Banco técnico',
                'ordering': ['titulo'],
            },
        ),
        migrations.CreateModel(
            name='EFS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('sigla', models.CharField(blank=True, max_length=20)),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='efs', to='praticas.pais')),
            ],
            options={
                'verbose_name': 'EFS',
                'verbose_name_plural': 'EFS',
                'ordering': ['nome'],
                'unique_together': {('nome', 'pais')},
            },
        ),
        migrations.CreateModel(
            name='Experiencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=250)),
                ('ano_execucao', models.PositiveIntegerField()),
                ('status_iniciativa', models.CharField(choices=[('planejamento', 'Em planejamento'), ('execucao', 'Em execução'), ('concluida', 'Concluída')], max_length=20)),
                ('descricao', models.TextField()),
                ('problema_climatico', models.TextField()),
                ('relacao_adaptacao_mitigacao_gestao_desastres', models.TextField()),
                ('riscos_climaticos', models.TextField()),
                ('enfoque_justica_climatica', models.TextField()),
                ('impactos_diferenciados', models.TextField()),
                ('objetivo', models.TextField()),
                ('perguntas_chave', models.TextField()),
                ('criterios_utilizados', models.TextField()),
                ('metodologia', models.TextField()),
                ('fontes_informacao', models.TextField()),
                ('resultados', models.TextField()),
                ('recomendacoes', models.TextField()),
                ('mudancas_ou_impactos', models.TextField()),
                ('motivo_boa_pratica', models.TextField()),
                ('elementos_replicaveis', models.TextField()),
                ('dificuldades', models.TextField()),
                ('licoes_aprendidas', models.TextField()),
                ('o_que_fariam_diferente', models.TextField()),
                ('replicabilidade', models.TextField()),
                ('necessidades_para_replicacao', models.TextField()),
                ('ferramentas_metodologias_uteis', models.TextField()),
                ('temas_sugeridos_para_guia', models.TextField()),
                ('apoio_requerido_pelas_efs', models.TextField()),
                ('status_publicacao', models.CharField(choices=[('rascunho', 'Rascunho'), ('publicado', 'Publicado')], default='publicado', max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('dimensoes_consideradas', models.ManyToManyField(related_name='experiencias', to='praticas.dimensaojusticaclimatica')),
                ('efs', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='experiencias', to='praticas.efs')),
                ('grupos_vulneraveis', models.ManyToManyField(related_name='experiencias', to='praticas.grupovulneravel')),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='experiencias', to='praticas.pais')),
                ('setor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='experiencias', to='praticas.setor')),
                ('tipo_experiencia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='experiencias', to='praticas.tipoexperiencia')),
            ],
            options={
                'ordering': ['-ano_execucao', 'titulo'],
            },
        ),
        migrations.CreateModel(
            name='Anexo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150)),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='anexos/')),
                ('url_externa', models.URLField(blank=True)),
                ('experiencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anexos', to='praticas.experiencia')),
            ],
            options={
                'ordering': ['titulo'],
            },
        ),
    ]
