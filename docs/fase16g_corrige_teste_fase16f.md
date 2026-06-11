# Fase 16G — Correção de teste da Fase 16F após padronização da lista oficial de EFS

## Contexto

Após a correção da lista oficial de EFS, a sigla da Auditoría Superior de la Federación de México foi padronizada como `ASF`.

O teste anterior da Fase 16F ainda esperava `ASF-MEX`, o que gerava falha mesmo com a taxonomia correta aplicada.

## Ajuste realizado

- Atualizado `praticas/tests_fase16f.py` para validar `sigla="ASF"`.
- Mantida a validação do nome institucional `Auditoría Superior de la Federación de México`.

## Comandos de validação

```powershell
python manage.py test praticas.tests_fase16f
python manage.py test praticas.tests_fase16g
python manage.py test
```

## Resultado esperado

Todos os testes devem passar.
