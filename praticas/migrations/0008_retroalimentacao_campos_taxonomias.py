from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("praticas", "0007_propostaedicaoexperiencia"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencia",
            name="informacoes_adicionais",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="informacoes_adicionais_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="experiencia",
            name="informacoes_adicionais_es",
            field=models.TextField(blank=True),
        ),
    ]
