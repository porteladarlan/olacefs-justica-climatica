from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("praticas", "0008_retroalimentacao_campos_taxonomias"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiencia",
            name="autor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="boas_praticas_enviadas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
