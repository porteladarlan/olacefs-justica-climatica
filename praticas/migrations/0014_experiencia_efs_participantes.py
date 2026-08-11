from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("praticas", "0013_fase2d1_fundacao_guia"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencia",
            name="efs_participantes",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Selecione somente as EFS participantes adicionais; "
                    "a EFS líder permanece no campo EFS."
                ),
                related_name="experiencias_como_participante",
                to="praticas.efs",
                verbose_name="EFS adicionais participantes",
            ),
        ),
    ]
