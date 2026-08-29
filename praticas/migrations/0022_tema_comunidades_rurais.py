from django.db import migrations


def criar_tema(apps, schema_editor):
    TemaTransversal = apps.get_model("praticas", "TemaTransversal")
    TemaTransversal.objects.update_or_create(
        nome="Comunidades rurais",
        defaults={"nome_es": "Comunidades rurales", "nome_en": "Rural communities"},
    )


class Migration(migrations.Migration):
    dependencies = [("praticas", "0021_normas_internacionais_trilingues")]
    operations = [migrations.RunPython(criar_tema, migrations.RunPython.noop)]
