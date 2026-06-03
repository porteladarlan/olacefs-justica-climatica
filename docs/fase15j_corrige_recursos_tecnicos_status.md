# Correção Fase 15J — status da área de Recursos Técnicos

Esta correção mantém a nova redação da Fase 15J sobre curadoria técnica, mas também preserva a expressão esperada pelos testes legados da Fase 15D.

## Ajuste realizado

Em `templates/praticas/banco_tecnico.html`, o status da área passa a exibir:

- português: `Conteúdo em desenvolvimento · Conteúdo em curadoria técnica`;
- espanhol: `Contenido en desarrollo · Contenido en curaduría técnica`;
- inglês: `Content under development · Content under technical curation`.

## Motivo

A Fase 15J refinou a linguagem institucional para "curadoria técnica", mas a Fase 15D ainda valida explicitamente que a área de Recursos Técnicos se apresenta como conteúdo em desenvolvimento. A correção mantém as duas mensagens, sem alterar regra de negócio.
