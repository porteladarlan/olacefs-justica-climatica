# Rastreabilidade

Identificadores: `RF`, `RNF`, `RN`, `ADR`, `SEC` e `TC`.

Cada mudança relaciona requisito, regra, decisão, arquivos, migration, testes, evidência, release e rollback.

Fonte: nota conceitual, protótipo, reunião, regra existente, correção, segurança ou infraestrutura.

## 2026-07-31 — Primeira evolução da página inicial

| ID | Requisito | Fonte | Código | Teste | Migration | Rollback |
|---|---|---|---|---|---|---|
| RNF-HOME-01 | Apresentar claramente o propósito da Plataforma | requisito da implementação e contexto aprovado | `templates/praticas/pagina_inicial.html` | `praticas.tests_home_primeira_evolucao` e regressão existente | não aplicável | reverter o bloco editorial da home |
| RNF-HOME-02 | Destacar Boas Práticas, Banco Técnico e Dimensões de Justiça Climática | requisito da implementação e protótipo atualizado | `templates/praticas/pagina_inicial.html`, `templates/praticas/base.html` | `praticas.tests_home_primeira_evolucao` | não aplicável | reverter cards, estilos e ativação da aba |
| RNF-HOME-03 | Preservar responsividade, acessibilidade e os três idiomas | requisitos de UI/i18n aprovados | `templates/praticas/pagina_inicial.html`, `templates/praticas/base.html` | `praticas.tests_home_primeira_evolucao` | não aplicável | reverter cards, estilos e script de foco |
