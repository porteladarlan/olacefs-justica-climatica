# Correção Fase 15F — teste de comparativo multidioma

Corrige o teste `test_revisao_edicao_publicada_exibe_comparativo_visual`.

Motivo:
- A tela de revisão de edição publicada agora respeita o idioma ativo.
- No teste atual, a página foi renderizada em inglês e apresentou `Current value` e `Proposed value`.
- O teste antigo procurava apenas `Valor atual` e `Valor proposto`.

A nova validação aceita:
- português: `Valor atual` / `Valor proposto`;
- espanhol: `Valor actual` / `Valor propuesto`;
- inglês: `Current value` / `Proposed value`.

Não altera regra de negócio nem template.
