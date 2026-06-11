# Fase 16H — Taxonomias trilíngues no formulário

## Objetivo

Corrigir as opções do formulário para que EFS e países sejam exibidos conforme o idioma ativo da plataforma: português, espanhol ou inglês.

## Ajustes realizados

- A lista oficial de EFS agora possui `nome`, `nome_es` e `nome_en` preenchidos.
- A lista de países foi revisada para português, espanhol e inglês.
- O comando `aplicar_retroalimentacao_formulario` passa a atualizar as três versões linguísticas das EFS.
- O comando `carregar_dados_ficticios` deixa de recriar EFS demonstrativas apenas em espanhol.
- Foram adicionados testes para garantir que as opções mudam conforme o idioma ativo.

## Observação

As siglas permanecem iguais para preservar vínculos existentes no banco e nas experiências já cadastradas.

## Comandos de validação

```bash
python manage.py aplicar_retroalimentacao_formulario
python manage.py test praticas.tests_fase16h
python manage.py test
```
