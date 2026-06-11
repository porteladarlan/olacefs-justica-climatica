# Fase 16G — Correção da lista oficial de EFS no formulário

Esta correção garante que a retroalimentação recebida seja refletida no formulário de envio.

## Problema identificado

A lista antiga de EFS demonstrativas continuava aparecendo no formulário, por exemplo:

- Tribunal de Contas da União (TCU)
- Contraloría General de la República do Paraguai

Isso acontecia porque os dados demonstrativos antigos já existiam no banco e não eram renomeados/removidos pelo comando da Fase 16F.

## Ajustes aplicados

- O comando `aplicar_retroalimentacao_formulario` passa a atualizar a lista oficial ampliada de EFS.
- As denominações institucionais foram mantidas em espanhol/oficial, conforme a revisão recebida.
- Siglas antigas usadas nos dados demonstrativos são atualizadas para os nomes oficiais.
- Duplicidades criadas por versões intermediárias são mescladas quando possível.
- O comando `carregar_dados_ficticios` também foi ajustado para não recriar nomes antigos.
- Foram adicionados testes específicos da Fase 16G.

## Comandos de validação

```bash
python manage.py aplicar_retroalimentacao_formulario
python manage.py test praticas.tests_fase16g
python manage.py test
```
