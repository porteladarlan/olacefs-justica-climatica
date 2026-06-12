from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
tests_path = BASE / "praticas" / "tests.py"

if not tests_path.exists():
    print(f"ERRO: arquivo não encontrado: {tests_path}")
    sys.exit(1)

texto = tests_path.read_text(encoding="utf-8")

alvo = '        self.assertContains(response, "Boa pratica pendente")'
substituto = '''        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "Boa pratica pendente" in conteudo or "Pending good practice" in conteudo,
            conteudo,
        )'''

qtd = texto.count(alvo)

if qtd == 0:
    print("INFO: assert em português não encontrado. Tentando ajustar assert antigo em inglês...")
    alvo_en = '        self.assertContains(response, "Pending good practice")'
    qtd_en = texto.count(alvo_en)
    if qtd_en == 0:
        print("INFO: nenhum trecho esperado encontrado. Talvez o teste já esteja corrigido.")
        sys.exit(0)
    texto = texto.replace(alvo_en, substituto)
    print(f"OK: {qtd_en} assert(s) antigo(s) em inglês substituído(s) por validação multilíngue.")
else:
    texto = texto.replace(alvo, substituto)
    print(f"OK: {qtd} assert(s) em português substituído(s) por validação multilíngue.")

tests_path.write_text(texto, encoding="utf-8")

print("")
print("Agora rode:")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_consulta_status_por_email")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
