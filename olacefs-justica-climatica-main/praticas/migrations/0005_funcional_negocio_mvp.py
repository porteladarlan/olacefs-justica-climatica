from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("praticas", "0004_alter_anexo_options_alter_efs_unique_together_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NormaInternacional",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=180, unique=True)),
                ("nome_es", models.CharField(blank=True, max_length=180)),
                ("nome_en", models.CharField(blank=True, max_length=180)),
                ("resumo", models.TextField(blank=True)),
                ("resumo_es", models.TextField(blank=True)),
                ("resumo_en", models.TextField(blank=True)),
                ("url_referencia", models.URLField(blank=True)),
            ],
            options={
                "verbose_name": "Norma internacional",
                "verbose_name_plural": "Normas internacionais",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="TemaTransversal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=160, unique=True)),
                ("nome_es", models.CharField(blank=True, max_length=160)),
                ("nome_en", models.CharField(blank=True, max_length=160)),
            ],
            options={
                "verbose_name": "Tema transversal",
                "verbose_name_plural": "Temas transversais",
                "ordering": ["nome"],
            },
        ),
        migrations.AddField(
            model_name="experiencia",
            name="comentario_revisor",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="contato_referencia",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="contribui_para_guia",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="destacado",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="email_contato",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="ferramentas_utilizadas",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="ferramentas_utilizadas_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="ferramentas_utilizadas_es",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="normas_internacionais",
            field=models.ManyToManyField(blank=True, related_name="experiencias", to="praticas.normainternacional"),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="pessoa_responsavel",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="relevante",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="temas_transversais",
            field=models.ManyToManyField(blank=True, related_name="experiencias", to="praticas.tematransversal"),
        ),
        migrations.AlterField(
            model_name="experiencia",
            name="status_publicacao",
            field=models.CharField(
                choices=[
                    ("rascunho", "Rascunho"),
                    ("enviado", "Enviado"),
                    ("em_revisao", "Em revisao"),
                    ("aprovado", "Aprovado"),
                    ("publicado", "Publicado"),
                    ("rejeitado", "Rejeitado"),
                ],
                default="publicado",
                max_length=30,
            ),
        ),
    ]
