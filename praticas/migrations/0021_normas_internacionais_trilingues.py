from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("praticas", "0020_experiencia_idioma_original")]

    operations = [
        migrations.AddField(model_name="normainternacional", name="natureza_juridica_es", field=models.CharField(max_length=80, blank=True)),
        migrations.AddField(model_name="normainternacional", name="natureza_juridica_en", field=models.CharField(max_length=80, blank=True)),
        migrations.AddField(model_name="normainternacional", name="setores_aplicaveis_es", field=models.TextField(blank=True)),
        migrations.AddField(model_name="normainternacional", name="setores_aplicaveis_en", field=models.TextField(blank=True)),
        migrations.AddField(model_name="normainternacional", name="cobertura_paises", field=models.TextField(blank=True)),
        migrations.AddField(model_name="normainternacional", name="cobertura_paises_en", field=models.TextField(blank=True)),
        migrations.AddField(model_name="normainternacionalpais", name="status_es", field=models.CharField(max_length=300, blank=True)),
        migrations.AddField(model_name="normainternacionalpais", name="status_en", field=models.CharField(max_length=300, blank=True)),
    ]
