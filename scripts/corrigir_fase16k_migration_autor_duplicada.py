from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
MIGRATIONS = BASE / "praticas" / "migrations"
APLICAR_16K = BASE / "scripts" / "aplicar_fase16k_ajustes_12_06.py"

def migration_adiciona_autor_experiencia(texto: str) -> bool:
    if "AddField" not in texto:
        return False

    tem_model = (
        "model_name='experiencia'" in texto
        or 'model_name="experiencia"' in texto
        or "model_name = 'experiencia'" in texto
        or 'model_name = "experiencia"' in texto
    )
    tem_nome = (
        "name='autor'" in texto
        or 'name="autor"' in texto
        or "name = 'autor'" in texto
        or 'name = "autor"' in texto
    )
    return tem_model and tem_nome

def numero_migration(path: Path) -> int:
    try:
        return int(path.name[:4])
    except ValueError:
        return 9999

def corrigir_migrations_duplicadas():
    if not MIGRATIONS.exists():
        print(f"ERRO: pasta não encontrada: {MIGRATIONS}")
        sys.exit(1)

    arquivos_autor = []
    for path in MIGRATIONS.glob("[0-9][0-9][0-9][0-9]_*.py"):
        texto = path.read_text(encoding="utf-8", errors="ignore")
        if migration_adiciona_autor_experiencia(texto):
            arquivos_autor.append(path)

    arquivos_autor = sorted(arquivos_autor, key=numero_migration)

    if not arquivos_autor:
        print("ERRO: nenhuma migration adicionando Experiencia.autor foi encontrada.")
        print("Verifique se praticas/models.py possui o campo autor e rode makemigrations.")
        sys.exit(1)

    print("Migrations encontradas para Experiencia.autor:")
    for path in arquivos_autor:
        print(f"  - {path.name}")

    manter = arquivos_autor[0]
    duplicadas = arquivos_autor[1:]

    print(f"\nMantendo: {manter.name}")

    if not duplicadas:
        print("OK: não há migration duplicada para remover.")
        return

    backup_dir = MIGRATIONS / "_backup_migrations_autor_duplicadas"
    backup_dir.mkdir(exist_ok=True)

    for path in duplicadas:
        backup = backup_dir / path.name
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        path.unlink()
        print(f"REMOVIDA: {path.name}  | backup: {backup}")

def corrigir_script_16k():
    if not APLICAR_16K.exists():
        print("INFO: script da Fase 16K não encontrado. Ignorando correção do script.")
        return

    texto = APLICAR_16K.read_text(encoding="utf-8")

    antigo = (
        '        if "boas_praticas_enviadas" in content and "model_name=\\\'experiencia\\\'" in content:\\n'
        '            print(f"INFO: migration de autor já existe: {p.name}")\\n'
        '            return'
    )

    novo = (
        '        tem_model = (\\n'
        '            "model_name=\\\'experiencia\\\'" in content\\n'
        '            or \\'model_name="experiencia"\\' in content\\n'
        '            or "model_name = \\\'experiencia\\\'" in content\\n'
        '            or \\'model_name = "experiencia"\\' in content\\n'
        '        )\\n'
        '        tem_nome = (\\n'
        '            "name=\\\'autor\\\'" in content\\n'
        '            or \\'name="autor"\\' in content\\n'
        '            or "name = \\\'autor\\\'" in content\\n'
        '            or \\'name = "autor"\\' in content\\n'
        '        )\\n'
        '        if "AddField" in content and tem_model and tem_nome:\\n'
        '            print(f"INFO: migration de autor já existe: {p.name}")\\n'
        '            return'
    )

    if antigo in texto:
        texto = texto.replace(antigo, novo)
        APLICAR_16K.write_text(texto, encoding="utf-8")
        print("OK: script aplicar_fase16k ajustado para não recriar migration duplicada.")
    else:
        print("INFO: trecho exato do script 16K não encontrado; nenhuma alteração feita nele.")

def main():
    corrigir_migrations_duplicadas()
    corrigir_script_16k()

    print("\\nAgora rode:")
    print("  python manage.py makemigrations --check")
    print("  python manage.py migrate")
    print("  python manage.py test praticas.tests_fase16k")
    print("  python manage.py test")

if __name__ == "__main__":
    main()
