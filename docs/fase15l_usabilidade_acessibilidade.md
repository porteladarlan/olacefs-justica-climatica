# Fase 15L — Usabilidade e acessibilidade

Esta fase faz um refinamento transversal de usabilidade e acessibilidade sem alterar regras de negócio.

## Ajustes realizados

- Amplia área mínima de toque para botões, links de navegação, inputs e selects.
- Melhora leitura de labels, textos de ajuda e mensagens de erro.
- Melhora comportamento visual de cards e blocos com textos longos.
- Ajusta responsividade mobile para:
  - página inicial;
  - catálogo;
  - recursos técnicos;
  - formulários;
  - painéis internos.
- Melhora botões em telas pequenas para evitar cliques difíceis.
- Adiciona suporte visual para usuários com preferência de maior contraste.
- Mantém o `skip-link` e o foco no conteúdo principal.
- Adiciona testes específicos da Fase 15L.

## Validação

```powershell
python manage.py test praticas.tests_fase15l
python manage.py test
```

## Observação

Esta fase é de refinamento visual/acessível. Ela não altera models, migrations, views nem fluxo de revisão/envio.
