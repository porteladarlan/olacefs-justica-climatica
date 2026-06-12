from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
VIEWS = BASE / "praticas" / "views.py"
TESTS_15E = BASE / "praticas" / "tests_fase15e.py"

CONSTANTES = '''# Configurações padrão para anexos.
# Mantém compatibilidade com validações de upload em testes e ambiente local.
ANEXO_LIMITE_POR_EXPERIENCIA = 5
ANEXO_TAMANHO_MAX_MB = 10
ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB * 1024 * 1024
ANEXO_EXTENSOES_PERMITIDAS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv",
    ".png", ".jpg", ".jpeg", ".geojson", ".zip",
}
ANEXO_CONTENT_TYPES_PERMITIDOS = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "image/png",
    "image/jpeg",
    "application/geo+json",
    "application/json",
    "application/zip",
    "application/x-zip-compressed",
}

'''

def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

def corrigir_constantes_anexo():
    texto = read(VIEWS)

    # Remove qualquer bloco antigo/mal posicionado das constantes para evitar duplicidade/confusão.
    texto = re.sub(
        r'# Configurações padrão para anexos\.\n'
        r'# Mantém compatibilidade com validações de upload em testes e ambiente local\.\n'
        r'ANEXO_LIMITE_POR_EXPERIENCIA = 5\n'
        r'ANEXO_TAMANHO_MAX_MB = 10\n'
        r'ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB \* 1024 \* 1024\n'
        r'ANEXO_EXTENSOES_PERMITIDAS = \{.*?\}\n'
        r'ANEXO_CONTENT_TYPES_PERMITIDOS = \{.*?\}\n\n',
        '',
        texto,
        flags=re.S,
    )

    linhas = texto.splitlines()
    pos = 0
    for idx, linha in enumerate(linhas):
        if linha.startswith("from ") or linha.startswith("import "):
            pos = idx + 1

    linhas.insert(pos, CONSTANTES.rstrip())
    texto = "\n".join(linhas) + "\n"
    write(VIEWS, texto)
    print("OK: constantes de anexos recolocadas no escopo global de views.py.")

def corrigir_teste_email():
    if not TESTS_15E.exists():
        print("INFO: tests_fase15e.py não encontrado.")
        return

    texto = read(TESTS_15E)

    texto = texto.replace(
        '        self.assertIn("SAI reference contact", conteudo)',
        '        self.assertIn("E-mail", conteudo)\n        self.assertNotIn("SAI reference contact", conteudo)',
    )
    texto = texto.replace(
        '        self.assertIn("Contacto de referencia de la EFS", conteudo)',
        '        self.assertIn("Correo electrónico", conteudo)\n        self.assertNotIn("Contacto de referencia de la EFS", conteudo)',
    )

    write(TESTS_15E, texto)
    print("OK: teste da página de envio ajustado para o novo requisito: apenas E-mail.")

def main():
    corrigir_constantes_anexo()
    corrigir_teste_email()

    print("")
    print("Agora rode:")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia")
    print("  python manage.py test praticas.tests_fase15e")
    print("  python manage.py test")

if __name__ == "__main__":
    main()
