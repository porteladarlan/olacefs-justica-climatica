from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]
models_path = BASE / "praticas" / "models.py"
migrations_dir = BASE / "praticas" / "migrations"

if not models_path.exists():
    print(f"ERRO: arquivo não encontrado: {models_path}")
    sys.exit(1)

texto = models_path.read_text(encoding="utf-8")

if "from django.conf import settings" not in texto:
    linhas = texto.splitlines()
    inserido = False
    for idx, linha in enumerate(linhas):
        if linha.startswith("from django.db import models"):
            linhas.insert(idx, "from django.conf import settings")
            inserido = True
            break
    if not inserido:
        linhas.insert(0, "from django.conf import settings")
    texto = "\n".join(linhas) + "\n"

inicio_exp = texto.find("class Experiencia(models.Model):")
if inicio_exp == -1:
    print("ERRO: classe Experiencia não encontrada em praticas/models.py")
    sys.exit(1)

inicio_banco = texto.find("class BancoTecnico(models.Model):")
if inicio_banco == -1:
    inicio_banco = len(texto)

bloco_exp = texto[inicio_exp:inicio_banco]
antes_exp = texto[:inicio_exp]
depois_exp = texto[inicio_banco:]

if re.search(r"\n    autor\s*=\s*models\.ForeignKey\(", bloco_exp):
    print("INFO: Experiencia.autor já existe no model.")
    novo_bloco_exp = bloco_exp
else:
    campo_autor = '''    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boas_praticas_enviadas",
    )
'''
    marcador = "    criado_em ="
    pos = bloco_exp.find(marcador)
    if pos != -1:
        novo_bloco_exp = bloco_exp[:pos] + campo_autor + bloco_exp[pos:]
    else:
        primeira_quebra = bloco_exp.find("\n") + 1
        novo_bloco_exp = bloco_exp[:primeira_quebra] + campo_autor + bloco_exp[primeira_quebra:]
    print("OK: campo Experiencia.autor inserido em praticas/models.py.")

texto_parcial = antes_exp + novo_bloco_exp + depois_exp

inicio_banco = texto_parcial.find("class BancoTecnico(models.Model):")
if inicio_banco != -1:
    proxima = texto_parcial.find("\nclass ", inicio_banco + 1)
    if proxima == -1:
        proxima = len(texto_parcial)
    antes = texto_parcial[:inicio_banco]
    bloco = texto_parcial[inicio_banco:proxima]
    depois = texto_parcial[proxima:]
    bloco_novo = re.sub(
        r'\n    autor = models\.ForeignKey\(\n'
        r'        settings\.AUTH_USER_MODEL,\n'
        r'        on_delete=models\.SET_NULL,\n'
        r'        null=True,\n'
        r'        blank=True,\n'
        r'        related_name="experiencias_enviadas",\n'
        r'    \)\n',
        "\n",
        bloco,
        count=1,
    )
    if bloco_novo != bloco:
        print("OK: campo BancoTecnico.autor indevido removido.")
    texto_parcial = antes + bloco_novo + depois

models_path.write_text(texto_parcial, encoding="utf-8")

migrations_dir.mkdir(exist_ok=True)
mig_existente = None
for p in migrations_dir.glob("*.py"):
    if p.name == "__init__.py":
        continue
    conteudo = p.read_text(encoding="utf-8", errors="ignore")
    if "boas_praticas_enviadas" in conteudo or "autor_experiencia" in p.name:
        mig_existente = p
        break

if mig_existente:
    print(f"INFO: migration de autor já existe: {mig_existente.name}")
else:
    nums = []
    for p in migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.py"):
        try:
            nums.append(int(p.name[:4]))
        except ValueError:
            pass
    proximo = (max(nums) + 1) if nums else 1
    anterior = max(nums) if nums else 0
    nome_anterior = None
    if anterior:
        for p in migrations_dir.glob(f"{anterior:04d}_*.py"):
            nome_anterior = p.stem
            break

    nome_mig = f"{proximo:04d}_autor_experiencia.py"
    dependency = f"        ('praticas', '{nome_anterior}'),\n" if nome_anterior else ""
    migration = f'''# Generated manually for Fase 16J

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
{dependency}        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='experiencia',
            name='autor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='boas_praticas_enviadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
'''
    mig_path = migrations_dir / nome_mig
    mig_path.write_text(migration, encoding="utf-8")
    print(f"OK: migration criada: {mig_path.name}")

print("")
print("Validação recomendada:")
print("  python manage.py makemigrations --check")
print("  python manage.py migrate")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
