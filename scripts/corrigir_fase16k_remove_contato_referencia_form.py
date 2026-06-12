from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
FORMS = BASE / "praticas" / "forms.py"
TESTS_15E = BASE / "praticas" / "tests_fase15e.py"

BLOCO_INIT = (
    "    def __init__(self, *args, **kwargs):\n"
    "        super().__init__(*args, **kwargs)\n\n"
    "        # Fase 16K: manter apenas e-mail no formulario publico de envio.\n"
    "        # O campo legado contato_referencia pode continuar no modelo/banco,\n"
    "        # mas nao deve ser exibido nem validado no formulario publico.\n"
    "        self.fields.pop(\"contato_referencia\", None)\n\n"
    "        if \"email_contato\" in self.fields:\n"
    "            self.fields[\"email_contato\"].label = \"E-mail\"\n"
    "            self.fields[\"email_contato\"].help_text = (\n"
    "                \"Provide the institutional e-mail to track the submission \"\n"
    "                \"and receive review guidance.\"\n"
    "            )\n\n"
)

def ler(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    return path.read_text(encoding="utf-8")

def salvar(path: Path, texto: str) -> None:
    path.write_text(texto, encoding="utf-8")

def localizar_classe_form(texto: str):
    padroes = [
        r"^class\s+BoaPraticaForm\s*\(",
        r"^class\s+ExperienciaForm\s*\(",
        r"^class\s+.*Form\s*\(forms\.ModelForm\):",
    ]
    for padrao in padroes:
        m = re.search(padrao, texto, flags=re.M)
        if m:
            return m.start()
    raise RuntimeError("Nao foi possivel localizar a classe principal de formulario em praticas/forms.py.")

def encontrar_fim_classe(texto: str, inicio_classe: int) -> int:
    resto = texto[inicio_classe + 1:]
    m = re.search(r"^class\s+\w+", resto, flags=re.M)
    if m:
        return inicio_classe + 1 + m.start()
    return len(texto)

def encontrar_fim_bloco_def(texto: str, inicio_def: int) -> int:
    resto = texto[inicio_def + 1:]
    for padrao in [r"^    def\s+\w+", r"^    class\s+\w+", r"^class\s+\w+"]:
        m = re.search(padrao, resto, flags=re.M)
        if m:
            return inicio_def + 1 + m.start()
    return len(texto)

def remover_init_existente_da_classe(texto: str, inicio_classe: int):
    fim_classe = encontrar_fim_classe(texto, inicio_classe)
    trecho_classe = texto[inicio_classe:fim_classe]
    m_init = re.search(r"^    def __init__\(self, \*args, \*\*kwargs\):", trecho_classe, flags=re.M)
    if not m_init:
        return texto, False
    inicio_init = inicio_classe + m_init.start()
    fim_init = encontrar_fim_bloco_def(texto, inicio_init)
    texto = texto[:inicio_init] + texto[fim_init:].lstrip("\n")
    return texto, True

def inserir_init(texto: str, inicio_classe: int) -> str:
    fim_linha_classe = texto.find("\n", inicio_classe)
    if fim_linha_classe == -1:
        raise RuntimeError("Classe de formulario sem quebra de linha.")
    return texto[:fim_linha_classe + 1] + "\n" + BLOCO_INIT + texto[fim_linha_classe + 1:].lstrip("\n")

def corrigir_forms():
    texto = ler(FORMS)
    inicio_classe = localizar_classe_form(texto)
    texto, removeu_init = remover_init_existente_da_classe(texto, inicio_classe)
    inicio_classe = localizar_classe_form(texto)
    texto = inserir_init(texto, inicio_classe)
    salvar(FORMS, texto)
    if removeu_init:
        print("OK: __init__ antigo substituido por versao sem contato_referencia.")
    else:
        print("OK: __init__ inserido para remover contato_referencia.")

def corrigir_tests_15e():
    if not TESTS_15E.exists():
        print("INFO: tests_fase15e.py nao encontrado. Pulando.")
        return

    texto = ler(TESTS_15E)

    substituicoes = {
        'self.assertIn("SAI reference contact", conteudo)': 'self.assertNotIn("SAI reference contact", conteudo)',
        'self.assertIn("Contacto de referencia de la EFS", conteudo)': 'self.assertNotIn("Contacto de referencia de la EFS", conteudo)',
        'self.assertIn("Reference institutional e-mail", conteudo)': 'self.assertIn("E-mail", conteudo)',
        'self.assertIn("Correo institucional de referencia", conteudo)': 'self.assertIn("Correo electrónico", conteudo)',
        'self.assertEqual(form.fields["contato_referencia"].label, "SAI reference contact")': 'self.assertNotIn("contato_referencia", form.fields)',
        'self.assertEqual(form.fields["contato_referencia"].label, "Contacto de referencia de la EFS")': 'self.assertNotIn("contato_referencia", form.fields)',
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    salvar(TESTS_15E, texto)
    print("OK: tests_fase15e.py ajustado para manter apenas E-mail.")

def main():
    corrigir_forms()
    corrigir_tests_15e()
    print("")
    print("Agora rode:")
    print("  python manage.py check")
    print("  python manage.py test praticas.tests_fase15e")
    print("  python manage.py test")
    print("")
    print("Se passar:")
    print("  git add praticas/forms.py praticas/tests_fase15e.py scripts/corrigir_fase16k_remove_contato_referencia_form.py docs/fase16k_remove_contato_referencia_form.md")
    print('  git commit -m "Remove contato referencia do formulario publico"')
    print("  git push")

if __name__ == "__main__":
    main()
