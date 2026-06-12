from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]

EXTENSOES = {
    ".py", ".html", ".txt", ".md", ".json", ".yml", ".yaml", ".css", ".js"
}

IGNORAR_PASTAS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "node_modules", "staticfiles", "media", "dist", "build"
}

PADROES_MOJIBAKE = [
    "Ã", "Â", "â€™", "â€œ", "â€", "â€“", "â€”", "ï»¿",
    "prÃ", "revisÃ", "informaÃ", "descriÃ", "aÃ§", "Ã©", "Ã¡", "Ã£", "Ã³", "Ãº", "Ã­", "Ãª", "Ã´", "Ã§"
]

SUBSTITUICOES_SEGURAS = {
    "Boa prática enviada com sucesso. Ela ficará pendente até a revisão.": "Boa prática enviada com sucesso. Ela ficará pendente até a revisão.",
    "Boa prática salva como rascunho.": "Boa prática salva como rascunho.",
    "Boa prática atualizada com sucesso.": "Boa prática atualizada com sucesso.",
    "Boa prática reenviada com sucesso. Ela ficará pendente até a revisão.": "Boa prática reenviada com sucesso. Ela ficará pendente até a revisão.",
    "Alterações salvas com sucesso.": "Alterações salvas com sucesso.",
    "Informações": "Informações",
    "Descrição": "Descrição",
    "descrição": "descrição",
    "Revisão": "Revisão",
    "revisão": "revisão",
    "Aprovação": "Aprovação",
    "aprovação": "aprovação",
    "Publicação": "Publicação",
    "publicação": "publicação",
    "Edição": "Edição",
    "edição": "edição",
    "Exclusão": "Exclusão",
    "exclusão": "exclusão",
    "Catálogo": "Catálogo",
    "catálogo": "catálogo",
    "Título": "Título",
    "título": "título",
    "País": "País",
    "país": "país",
    "Prática": "Prática",
    "prática": "prática",
    "Até": "Até",
    "até": "até",
    "Não": "Não",
    "não": "não",
    "Está": "Está",
    "está": "está",
    "Usuário": "Usuário",
    "usuário": "usuário",
    "Autenticação": "Autenticação",
    "autenticação": "autenticação",
}

def deve_ignorar(path: Path) -> bool:
    partes = set(path.parts)
    return bool(partes & IGNORAR_PASTAS)

def arquivos_alvo():
    for path in BASE.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXTENSOES and not deve_ignorar(path):
            yield path

def linhas_com_suspeita(texto: str):
    achados = []
    for numero, linha in enumerate(texto.splitlines(), start=1):
        if any(p in linha for p in PADROES_MOJIBAKE):
            achados.append((numero, linha.rstrip()))
    return achados

def auditar(corrigir=False):
    total_arquivos = 0
    total_linhas = 0
    alterados = []

    print("Auditoria de codificação/mojibake UTF-8")
    print("=" * 72)

    for path in arquivos_alvo():
        try:
            texto = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"\n[IGNORADO - não UTF-8] {path.relative_to(BASE)}")
            continue

        original = texto
        achados = linhas_com_suspeita(texto)

        if achados:
            total_arquivos += 1
            total_linhas += len(achados)
            print(f"\n[ARQUIVO] {path.relative_to(BASE)}")
            for numero, linha in achados[:30]:
                print(f"  L{numero}: {linha}")
            if len(achados) > 30:
                print(f"  ... +{len(achados) - 30} linha(s) suspeita(s)")

        if corrigir:
            for antigo, novo in SUBSTITUICOES_SEGURAS.items():
                texto = texto.replace(antigo, novo)

            if texto != original:
                path.write_text(texto, encoding="utf-8")
                alterados.append(path.relative_to(BASE))

    print("\n" + "=" * 72)
    print(f"Arquivos com suspeita: {total_arquivos}")
    print(f"Linhas suspeitas: {total_linhas}")

    if corrigir:
        print(f"Arquivos alterados automaticamente: {len(alterados)}")
        for item in alterados:
            print(f"  OK {item}")
        print("\nObservação: a correção automática usa apenas substituições seguras.")
        print("Revise os demais achados manualmente antes do commit.")

def main():
    corrigir = "--corrigir" in sys.argv
    auditar(corrigir=corrigir)

if __name__ == "__main__":
    main()
