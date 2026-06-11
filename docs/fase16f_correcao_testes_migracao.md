# Fase 16F — correção de testes e migração

Correção complementar da Fase 16F para estabilizar a suíte de testes.

## Ajustes realizados

- Corrigida a asserção com aspas no arquivo `praticas/tests_fase16f.py`.
- Ajustada a migração `0008_retroalimentacao_campos_taxonomias.py` para adicionar apenas os novos campos, sem popular dados automaticamente durante a migração.
- Mantido o carregamento das taxonomias via comando explícito `aplicar_retroalimentacao_formulario`.
- Ajustado o template `banco_tecnico.html` para manter compatibilidade com testes anteriores que procuram a expressão `Conte&uacute;do em desenvolvimento`.

## Motivo técnico

A versão anterior populava países/EFS diretamente na migração. Isso criava `Brasil/BRA` no banco de testes antes de testes legados que também criavam `BRA`, causando `UNIQUE constraint failed: praticas_pais.sigla`.

A abordagem corrigida é mais segura: schema em migração; dados referenciais por comando idempotente.
