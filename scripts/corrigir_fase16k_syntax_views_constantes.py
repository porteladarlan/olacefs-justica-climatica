from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
VIEWS = BASE / "praticas" / "views.py"
TESTS_15E = BASE / "praticas" / "tests_fase15e.py"

CONSTANTES = '\n\n# Configurações padrão para anexos.\n# Mantém compatibilidade com validações de upload em testes e ambiente local.\nANEXO_LIMITE_POR_EXPERIENCIA = 5\nANEXO_TAMANHO_MAX_MB = 10\nANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB * 1024 * 1024\nANEXO_EXTENSOES_PERMITIDAS = {\n    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv",\n    ".png", ".jpg", ".jpeg", ".geojson", ".zip",\n}\nANEXO_CONTENT_TYPES_PERMITIDOS = {\n    "application/pdf",\n    "application/msword",\n    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",\n    "application/vnd.ms-excel",\n    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",\n    "text/csv",\n    "image/png",\n    "image/jpeg",\n    "application/geo+json",\n    "application/json",\n    "application/zip",\n    "application/x-zip-compressed",\n}\n\n'

def ler(path):
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")

def salvar(path, texto):
    path.write_text(texto, encoding="utf-8")

def remover_blocos_constantes(texto):
    # Remove blocos anteriores, inclusive se tiverem sido inseridos dentro de imports.
    padrao = (
        r'\n?# Configurações padrão para anexos\.\n'
        r'# Mantém compatibilidade com validações de upload em testes e ambiente local\.\n'
        r'ANEXO_LIMITE_POR_EXPERIENCIA = 5\n'
        r'ANEXO_TAMANHO_MAX_MB = 10\n'
        r'ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB \* 1024 \* 1024\n'
        r'ANEXO_EXTENSOES_PERMITIDAS = \{.*?\}\n'
        r'ANEXO_CONTENT_TYPES_PERMITIDOS = \{.*?\}\n'
    )
    return re.sub(padrao, "\n", texto, flags=re.S)

def encontrar_fim_imports(texto):
    linhas = texto.splitlines()
    fim = 0
    dentro_import_multilinha = False
    saldo_parenteses = 0

    for idx, linha in enumerate(linhas):
        stripped = linha.strip()

        if not stripped or stripped.startswith("#"):
            fim = idx + 1
            continue

        if dentro_import_multilinha:
            saldo_parenteses += linha.count("(") - linha.count(")")
            fim = idx + 1
            if saldo_parenteses <= 0:
                dentro_import_multilinha = False
            continue

        if linha.startswith("import ") or linha.startswith("from "):
            saldo_parenteses = linha.count("(") - linha.count(")")
            dentro_import_multilinha = saldo_parenteses > 0
            fim = idx + 1
            continue

        break

    return fim

def corrigir_views():
    texto = ler(VIEWS)
    texto = remover_blocos_constantes(texto)

    linhas = texto.splitlines()
    fim_imports = encontrar_fim_imports(texto)

    novo = "\n".join(linhas[:fim_imports]).rstrip() + CONSTANTES + "\n".join(linhas[fim_imports:]).lstrip() + "\n"
    salvar(VIEWS, novo)
    print("OK: views.py corrigido. Constantes de anexo foram movidas para fora dos imports e para o escopo global.")

def corrigir_tests_15e():
    if not TESTS_15E.exists():
        print("INFO: tests_fase15e.py não encontrado.")
        return

    texto = ler(TESTS_15E)
    texto = texto.replace(
        '        self.assertIn("SAI reference contact", conteudo)',
        '        self.assertIn("E-mail", conteudo)\n        self.assertNotIn("SAI reference contact", conteudo)',
    )
    texto = texto.replace(
        '        self.assertIn("Contacto de referencia de la EFS", conteudo)',
        '        self.assertIn("Correo electrónico", conteudo)\n        self.assertNotIn("Contacto de referencia de la EFS", conteudo)',
    )
    salvar(TESTS_15E, texto)
    print("OK: tests_fase15e.py ajustado para novo requisito de E-mail.")

def main():
    corrigir_views()
    corrigir_tests_15e()

    print("")
    print("Valide primeiro a sintaxe:")
    print("  python manage.py check")
    print("")
    print("Depois rode:")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia")
    print("  python manage.py test praticas.tests_fase15e")
    print("  python manage.py test")

if __name__ == "__main__":
    main()
