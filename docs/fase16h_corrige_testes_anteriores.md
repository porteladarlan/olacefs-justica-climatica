# Fase 16H — Correção dos testes anteriores para taxonomias trilíngues

## Objetivo

Atualizar os testes das Fases 16F e 16G para a nova regra da Fase 16H:

- `nome`: rótulo em português;
- `nome_es`: rótulo em espanhol;
- `nome_en`: rótulo em inglês.

## Correção

Os testes anteriores ainda verificavam nomes oficiais em espanhol dentro do campo `nome`. Após a trilíngualização das taxonomias, isso ficou incorreto.

Foram ajustados:

- `praticas/tests_fase16f.py`
- `praticas/tests_fase16g.py`

## Validação recomendada

```bash
python manage.py test praticas.tests_fase16f
python manage.py test praticas.tests_fase16g
python manage.py test praticas.tests_fase16h
python manage.py test
```
