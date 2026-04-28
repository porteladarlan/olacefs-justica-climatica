from pathlib import Path
import sqlite3


REPLACEMENTS = {
    # termos vistos na tela
    "adaptações": "adaptações",
    "Adaptações": "Adaptações",
    "Dimensões": "Dimensões",
    "dimensões": "dimensões",
    "intercâmbio": "intercâmbio",
    "Intercâmbio": "Intercâmbio",
    "←": "←",
    "→": "→",

    # português comum
    "Justiça": "Justiça",
    "justiça": "justiça",
    "Climática": "Climática",
    "climática": "climática",
    "Práticas": "Práticas",
    "práticas": "práticas",
    "Catálogo": "Catálogo",
    "catálogo": "catálogo",
    "Países": "Países",
    "países": "países",
    "Últimas": "Últimas",
    "últimas": "últimas",
    "experiências": "experiências",
    "Experiências": "Experiências",
    "experiência": "experiência",
    "Experiência": "Experiência",
    "técnico": "técnico",
    "Técnico": "Técnico",
    "técnica": "técnica",
    "Técnica": "Técnica",
    "pública": "pública",
    "Pública": "Pública",
    "demonstração": "demonstração",
    "Demonstração": "Demonstração",
    "resiliência": "resiliência",
    "Resiliência": "Resiliência",
    "hídrica": "hídrica",
    "Hídrica": "Hídrica",
    "áreas": "áreas",
    "Áreas": "Áreas",
    "Colômbia": "Colômbia",
    "México": "México",
    "Peru": "Peru",
    "República": "República",
    "União": "União",
    "adaptação": "adaptação",
    "mitigação": "mitigação",
    "gestão": "gestão",
    "avaliação": "avaliação",
    "população": "população",
    "situação": "situação",
    "informação": "informação",
    "informações": "informações",
    "relação": "relação",
    "execução": "execução",
    "concluída": "concluída",
    "Concluída": "Concluída",
    "descrição": "descrição",
    "Descrição": "Descrição",
    "página": "página",
    "Página": "Página",
    "opções": "opções",
    "ações": "ações",
    "Ações": "Ações",

    # símbolos e restos comuns
    "•": "•",
    "–": "–",
    "—": "—",
    "": "",

    # caracteres isolados comuns
    "ç": "ç",
    "ã": "ã",
    "õ": "õ",
    "á": "á",
    "é": "é",
    "ê": "ê",
    "í": "í",
    "ó": "ó",
    "ô": "ô",
    "ú": "ú",
    "Ç": "Ç",
    "Ã": "Ã",
}


def fix_text(value):
    if not isinstance(value, str):
        return value

    fixed = value
    for wrong, right in REPLACEMENTS.items():
        fixed = fixed.replace(wrong, right)
    return fixed


def fix_files():
    extensions = {".py", ".html", ".txt", ".md"}
    ignore_dirs = {"venv", ".git", "__pycache__", ".idea", ".vscode"}

    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignore_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in extensions:
            continue

        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        fixed = fix_text(original)

        if fixed != original:
            path.write_text(fixed, encoding="utf-8")
            print(f"Arquivo corrigido: {path}")


def fix_database():
    db_path = Path("db.sqlite3")
    if not db_path.exists():
        print("db.sqlite3 não encontrado. Pulando banco.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        if table.startswith("sqlite_"):
            continue

        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = cursor.fetchall()

        pk_column = None
        text_columns = []

        for col in columns:
            _cid, name, col_type, _notnull, _default_value, pk = col
            if pk:
                pk_column = name

            col_type = (col_type or "").upper()
            if "CHAR" in col_type or "TEXT" in col_type or "VARCHAR" in col_type:
                text_columns.append(name)

        if not pk_column or not text_columns:
            continue

        select_cols = ", ".join([f'"{pk_column}"'] + [f'"{col}"' for col in text_columns])
        cursor.execute(f'SELECT {select_cols} FROM "{table}"')

        for row in cursor.fetchall():
            pk_value = row[0]
            updates = {}

            for idx, col in enumerate(text_columns, start=1):
                original = row[idx]
                fixed = fix_text(original)

                if fixed != original:
                    updates[col] = fixed

            if updates:
                set_clause = ", ".join([f'"{col}" = ?' for col in updates])
                values = list(updates.values()) + [pk_value]
                cursor.execute(
                    f'UPDATE "{table}" SET {set_clause} WHERE "{pk_column}" = ?',
                    values,
                )
                print(f"Banco corrigido: {table} / id={pk_value}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    fix_files()
    fix_database()
    print("Correção final concluída.")