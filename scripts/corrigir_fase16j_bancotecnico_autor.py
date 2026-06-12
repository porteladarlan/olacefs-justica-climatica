from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]
models_path = BASE / "praticas" / "models.py"

if not models_path.exists():
    print(f"ERRO: arquivo não encontrado: {models_path}")
    sys.exit(1)

texto = models_path.read_text(encoding="utf-8")

inicio = texto.find("class BancoTecnico(models.Model):")
if inicio == -1:
    print("ERRO: classe BancoTecnico não encontrada em praticas/models.py")
    sys.exit(1)

proxima_classe = texto.find("\nclass ", inicio + 1)
if proxima_classe == -1:
    proxima_classe = len(texto)

antes = texto[:inicio]
bloco = texto[inicio:proxima_classe]
depois = texto[proxima_classe:]

padrao = re.compile(
    r'\n    autor = models\.ForeignKey\(\n'
    r'        settings\.AUTH_USER_MODEL,\n'
    r'        on_delete=models\.SET_NULL,\n'
    r'        null=True,\n'
    r'        blank=True,\n'
    r'        related_name="experiencias_enviadas",\n'
    r'    \)\n',
    re.MULTILINE,
)

novo_bloco, qtd = padrao.subn("\n", bloco, count=1)

if qtd == 0:
    print("INFO: nenhum campo BancoTecnico.autor indevido encontrado. Nada foi alterado.")
    sys.exit(0)

novo_texto = antes + novo_bloco + depois
models_path.write_text(novo_texto, encoding="utf-8")

print("OK: campo indevido BancoTecnico.autor removido de praticas/models.py")
print("Agora rode:")
print("  python manage.py makemigrations --check")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
