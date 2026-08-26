from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("praticas", "0019_alter_experiencia_status_publicacao")]

    operations = [
        migrations.AddField(
            model_name="experiencia",
            name="idioma_original",
            field=models.CharField(
                choices=[("pt", "Português"), ("es", "Español"), ("en", "English")],
                blank=True,
                default="",
                editable=False,
                max_length=2,
            ),
        ),
    ]
