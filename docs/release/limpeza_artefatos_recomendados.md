# Limpeza recomendada de artefatos indevidos

Durante a revisão sênior do pacote, foram encontrados artefatos que não deveriam estar versionados dentro de `templates/praticas/`.

## Remover se existirem no repositório real

No PowerShell, a partir da raiz do projeto:

```powershell
Remove-Item templates/praticas/ADMIN_RENDER.md -Force -ErrorAction SilentlyContinue
Remove-Item templates/praticas/build.sh -Force -ErrorAction SilentlyContinue
Remove-Item templates/praticas/praticas -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item olacefs-justica-climatica-main -Recurse -Force -ErrorAction SilentlyContinue
```

Depois rode:

```powershell
git status
python manage.py test
```

## Motivo

Esses arquivos são documentação operacional, script ou cópia duplicada de código. Eles não são templates HTML e podem gerar confusão de manutenção, revisão e deploy.
