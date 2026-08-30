# Limpeza recomendada de artefatos indevidos

Durante a revisão sênior do pacote, foram encontrados artefatos que não deveriam estar versionados dentro de `templates/praticas/`.

## Estado após a Fase 0A

Os artefatos duplicados, deslocados ou operacionais identificados nessa
revisão foram removidos do repositório na Fase 0A. A cópia canônica dos
templates funcionais e dos scripts de operação permanece preservada nos
diretórios principais do projeto.

Depois rode:

```powershell
git status
python manage.py test
```

## Motivo

Esses itens eram documentação operacional, script ou cópia duplicada de código. Eles não eram templates HTML funcionais canônicos e poderiam gerar confusão de manutenção, revisão e deploy.
