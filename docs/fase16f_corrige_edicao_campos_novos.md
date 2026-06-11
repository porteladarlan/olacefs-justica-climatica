# Fase 16F - Correção de edição publicada com campos novos

## Problema corrigido

Após a inclusão do campo `informacoes_adicionais`, propostas de edição antigas ou testes que não enviam todos os campos do formulário podiam salvar `None` em campos `TextField` sem `null=True`, causando erro de banco:

`NOT NULL constraint failed: praticas_experiencia.informacoes_adicionais`

## Ajuste aplicado

A função `aplicar_proposta_edicao` agora:

- preserva campos ausentes no JSON da proposta;
- converte valores `None` para string vazia quando o campo do modelo não aceita `NULL`;
- mantém compatibilidade com propostas antigas criadas antes da retroalimentação.

## Validação recomendada

```bash
python manage.py test praticas.tests_fase16f
python manage.py test
```
