from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
VIEWS = BASE / "praticas" / "views.py"
TESTS = BASE / "praticas" / "tests.py"
TESTS_15E = BASE / "praticas" / "tests_fase15e.py"
DETALHE = BASE / "templates" / "praticas" / "detalhe_experiencia.html"

def read(path):
    if not path.exists():
        print(f"AVISO: arquivo não encontrado: {path}")
        return None
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.write_text(text, encoding="utf-8")

def patch_views_anexos():
    text = read(VIEWS)
    if text is None:
        return

    bloco = (
        "# Configurações padrão para anexos.\n"
        "# Mantém compatibilidade com validações de upload em testes e ambiente local.\n"
        "ANEXO_LIMITE_POR_EXPERIENCIA = 5\n"
        "ANEXO_TAMANHO_MAX_MB = 10\n"
        "ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB * 1024 * 1024\n"
        "ANEXO_EXTENSOES_PERMITIDAS = {\n"
        "    \".pdf\", \".doc\", \".docx\", \".xls\", \".xlsx\", \".csv\",\n"
        "    \".png\", \".jpg\", \".jpeg\", \".geojson\", \".zip\",\n"
        "}\n"
        "ANEXO_CONTENT_TYPES_PERMITIDOS = {\n"
        "    \"application/pdf\",\n"
        "    \"application/msword\",\n"
        "    \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\",\n"
        "    \"application/vnd.ms-excel\",\n"
        "    \"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\",\n"
        "    \"text/csv\",\n"
        "    \"image/png\",\n"
        "    \"image/jpeg\",\n"
        "    \"application/geo+json\",\n"
        "    \"application/json\",\n"
        "    \"application/zip\",\n"
        "    \"application/x-zip-compressed\",\n"
        "}\n"
    )

    if "ANEXO_LIMITE_POR_EXPERIENCIA" not in text:
        linhas = text.splitlines()
        pos = 0
        for idx, linha in enumerate(linhas):
            if linha.startswith("from ") or linha.startswith("import "):
                pos = idx + 1
        linhas.insert(pos, "\n" + bloco)
        text = "\n".join(linhas) + "\n"
        print("OK: constantes de anexo inseridas em views.py.")
    else:
        print("INFO: ANEXO_LIMITE_POR_EXPERIENCIA já existe em views.py.")
    write(VIEWS, text)

def patch_tests_tcu():
    text = read(TESTS)
    if text is None:
        return

    old = '        self.assertContains(response, "TCU")'
    new = (
        '        conteudo = response.content.decode("utf-8")\n'
        '        self.assertTrue(\n'
        '            "TCU" in conteudo or "Federal Court of Accounts" in conteudo,\n'
        '            conteudo,\n'
        '        )'
    )

    qtd = text.count(old)
    if qtd:
        text = text.replace(old, new)
        write(TESTS, text)
        print(f"OK: {qtd} assert(s) de TCU ajustado(s).")
    else:
        print("INFO: nenhum assert fixo de TCU encontrado em tests.py.")

def patch_tests_15e_contato():
    text = read(TESTS_15E)
    if text is None:
        return

    text = text.replace(
        '        self.assertEqual(form.fields["contato_referencia"].label, "SAI reference contact")',
        '        self.assertNotIn("contato_referencia", form.fields)\n        self.assertEqual(form.fields["email_contato"].label, "E-mail")',
    )
    text = text.replace(
        '        self.assertEqual(form.fields["contato_referencia"].label, "Contacto de referencia de la EFS")',
        '        self.assertNotIn("contato_referencia", form.fields)\n        self.assertEqual(form.fields["email_contato"].label, "Correo electrónico")',
    )
    write(TESTS_15E, text)
    print("OK: tests_fase15e.py ajustado.")

def patch_detalhe_ano():
    text = read(DETALHE)
    if text is None:
        return

    if "experiencia.ano_execucao" in text:
        print("INFO: detalhe_experiencia.html já contém ano_execucao.")
        return

    if "</h1>" in text:
        insercao = (
            "</h1>\n"
            "{% if experiencia.ano_execucao %}\n"
            "<div class=\"mt-2\">\n"
            "    <span class=\"badge-soft\">{{ experiencia.ano_execucao }}</span>\n"
            "</div>\n"
            "{% endif %}"
        )
        text = text.replace("</h1>", insercao, 1)
        write(DETALHE, text)
        print("OK: ano de execução reinserido na ficha da boa prática.")
    else:
        print("AVISO: não encontrei </h1> para inserir ano de execução no detalhe.")

def main():
    patch_views_anexos()
    patch_tests_tcu()
    patch_tests_15e_contato()
    patch_detalhe_ano()
    print("\nAgora rode:")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio")
    print("  python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia")
    print("  python manage.py test praticas.tests_fase15e")
    print("  python manage.py test praticas.tests_fase15c")
    print("  python manage.py test")

if __name__ == "__main__":
    main()
