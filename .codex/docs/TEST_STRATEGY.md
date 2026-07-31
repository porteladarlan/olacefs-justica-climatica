# Testes

## Prioridade

Regras, autorização, estados, dados, uploads, filtros, i18n e regressão.

## Níveis

- unidade: validações e serviços;
- integração: models, forms, views, queries, constraints, transações;
- fluxo: conta, rascunho, envio, revisão, publicação, catálogo, idioma;
- interface: ferramenta existente; Playwright/Selenium somente por decisão.

## Mínimo

```text
python manage.py check
python manage.py makemigrations --check --dry-run
[runner existente]
```

Testar conteúdo não publicado, usuário de outra EFS, upload inválido, três idiomas e estados da interface.
