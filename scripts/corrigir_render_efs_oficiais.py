from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]

BUILD_SH = BASE / "build.sh"
DOCS_RENDER = [
    BASE / "docs" / "render" / "comandos_pos_deploy.md",
    BASE / "docs" / "render" / "checklist_render_teste_externo.md",
    BASE / "DEPLOY_RENDER.md",
]

COMANDO_RETRO = "python manage.py aplicar_retroalimentacao_formulario"
COMANDO_DEMO = "python manage.py carregar_dados_ficticios"

START_RECOMENDADO = (
    "python manage.py migrate && "
    "python manage.py aplicar_retroalimentacao_formulario && "
    "python manage.py criar_usuarios_teste --confirmar --resetar-senha && "
    "gunicorn config.wsgi:application"
)

def ler(path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")

def salvar(path, texto):
    path.write_text(texto, encoding="utf-8")

def corrigir_build_sh():
    texto = ler(BUILD_SH)
    if texto is None:
        print("INFO: build.sh não encontrado. Pulando.")
        return

    if COMANDO_RETRO in texto:
        print("OK: build.sh já executa aplicar_retroalimentacao_formulario.")
        return

    linhas = texto.splitlines()
    novas = []
    inseriu = False

    for linha in linhas:
        novas.append(linha)
        if linha.strip().startswith(COMANDO_DEMO):
            novas.append(COMANDO_RETRO)
            inseriu = True

    if not inseriu:
        # Fallback: insere depois de migrate.
        novas = []
        for linha in linhas:
            novas.append(linha)
            if linha.strip() == "python manage.py migrate":
                novas.append(COMANDO_RETRO)
                inseriu = True

    if not inseriu:
        novas.append(COMANDO_RETRO)

    salvar(BUILD_SH, "\n".join(novas) + "\n")
    print("OK: build.sh atualizado para carregar a lista oficial/ampliada de EFS.")

def atualizar_docs_render():
    for path in DOCS_RENDER:
        texto = ler(path)
        if texto is None:
            continue

        original = texto

        texto = texto.replace(
            "python manage.py carregar_dados_ficticios --limpar-demo",
            "python manage.py carregar_dados_ficticios\npython manage.py aplicar_retroalimentacao_formulario",
        )

        if COMANDO_DEMO in texto and COMANDO_RETRO not in texto:
            texto = texto.replace(COMANDO_DEMO, COMANDO_DEMO + "\n" + COMANDO_RETRO)

        if "Start Command:" in texto and "aplicar_retroalimentacao_formulario" not in texto:
            texto = re.sub(
                r"Start Command:\s*.*",
                f"Start Command: {START_RECOMENDADO}",
                texto,
            )

        if texto != original:
            salvar(path, texto)
            print(f"OK: documentação atualizada: {path.relative_to(BASE)}")

def criar_doc_operacional():
    doc = BASE / "docs" / "render" / "start_command_preservando_efs_e_envios.md"
    texto = f"""# Render — Start Command preservando EFS oficiais e envios

## Problema

Quando o comando `carregar_dados_ficticios --limpar-demo` é usado em deploy/start, dados cadastrados manualmente podem ser removidos.

Quando o comando `aplicar_retroalimentacao_formulario` não é executado, a lista oficial/ampliada de EFS pode não aparecer no formulário, ficando apenas a lista demonstrativa reduzida.

## Start Command recomendado

Use no Render:

```bash
{START_RECOMENDADO}
```

## O que cada parte faz

```bash
python manage.py migrate
```

Aplica as migrations.

```bash
python manage.py aplicar_retroalimentacao_formulario
```

Garante a lista oficial/ampliada de países, EFS e taxonomias no formulário.

```bash
python manage.py criar_usuarios_teste --confirmar --resetar-senha
```

Garante os usuários de teste, sem recriar boas práticas.

```bash
gunicorn config.wsgi:application
```

Inicia a aplicação.

## Evitar no Start Command

Não use no Start Command:

```bash
python manage.py carregar_dados_ficticios --limpar-demo
```

Esse comando deve ser usado apenas quando a intenção for resetar a base demonstrativa.

## Build Script

O `build.sh` pode executar:

```bash
python manage.py carregar_dados_ficticios
python manage.py aplicar_retroalimentacao_formulario
```

sem `--limpar-demo`, para garantir dados básicos e lista oficial de EFS.
"""
    salvar(doc, texto)
    print(f"OK: documento criado: {doc.relative_to(BASE)}")

def main():
    corrigir_build_sh()
    atualizar_docs_render()
    criar_doc_operacional()

    print("")
    print("No Render, ajuste o Start Command para:")
    print(START_RECOMENDADO)
    print("")
    print("Depois rode localmente:")
    print("  python manage.py check")
    print("  python manage.py test")
    print("")
    print("Commit:")
    print("  git add build.sh docs/render/ DEPLOY_RENDER.md scripts/corrigir_render_efs_oficiais.py")
    print('  git commit -m "Garante EFS oficiais no deploy do Render"')
    print("  git push")

if __name__ == "__main__":
    main()
