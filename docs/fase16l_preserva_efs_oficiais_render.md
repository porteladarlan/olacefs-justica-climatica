# Fase 16L — Preservar EFS oficiais no Render

Este pacote corrige o fluxo de deploy/start para evitar dois problemas:

1. Perda dos dados cadastrados manualmente quando se usa `--limpar-demo`.
2. Perda da lista oficial/ampliada de EFS quando `aplicar_retroalimentacao_formulario` não é executado.

## Aplicar

Na raiz do projeto:

```powershell
python scripts/corrigir_render_efs_oficiais.py
```

## Start Command recomendado no Render

```bash
python manage.py migrate && python manage.py aplicar_retroalimentacao_formulario && python manage.py criar_usuarios_teste --confirmar --resetar-senha && gunicorn config.wsgi:application
```

## Validar

```powershell
python manage.py check
python manage.py test
```

## Commit

```powershell
git add build.sh
git add docs/render/
git add DEPLOY_RENDER.md
git add scripts/corrigir_render_efs_oficiais.py

git commit -m "Garante EFS oficiais no deploy do Render"
git push
```
