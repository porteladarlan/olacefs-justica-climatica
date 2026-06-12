from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
tests_path = BASE / "praticas" / "tests.py"

if not tests_path.exists():
    print(f"ERRO: arquivo não encontrado: {tests_path}")
    sys.exit(1)

texto = tests_path.read_text(encoding="utf-8")

alvo = 'self.assertContains(response, "Pending good practice")'
substituto = 'self.assertContains(response, "Boa pratica pendente")'

if alvo not in texto:
    print("INFO: trecho antigo não encontrado. Verifique se o teste já foi ajustado.")
    sys.exit(0)

texto = texto.replace(alvo, substituto, 1)
tests_path.write_text(texto, encoding="utf-8")

print("OK: teste de Meus envios ajustado para o idioma padrão PT-BR.")
print("")
print("Agora rode:")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
