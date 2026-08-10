# Fase 2D.3 — preview interna do Guia

## Escopo

A primeira interface navegável do Guia permite consultar a versão publicada vigente
por eixos, subeixos, setores, subáreas, perguntas e referências. A preview é somente
leitura, usa a hierarquia já persistida e não altera importação, publicação ou models.

## Rotas

- `/guia/preview/`
- `/guia/preview/eixos/`
- `/guia/preview/eixos/<eixo_codigo>/`
- `/guia/preview/eixos/<eixo_codigo>/subeixos/<subeixo_codigo>/`
- `/guia/preview/setores/`
- `/guia/preview/setores/<setor_codigo>/`
- `/guia/preview/setores/<setor_codigo>/subareas/<subarea_codigo>/`

Os detalhes usam códigos institucionais e validam versão vigente e pertencimento ao
ancestral informado na URL.

## Acesso e versão

Todas as rotas usam temporariamente o gate existente de usuário autenticado, ativo e
staff/revisor. A preview não foi incluída na navegação pública. Somente a versão com
situação publicada e `vigente=True` é selecionada; rascunhos e versões publicadas não
vigentes não são fallback. Na ausência de versão disponível, as listagens apresentam
um estado indisponível neutro.

## Idioma e dados

Rótulos estruturais acompanham PT, ES e EN da interface. Nomes, perguntas e citações
institucionais exibem exclusivamente os campos espanhóis armazenados, identificados
com `lang="es"`, sem tradução, cópia ou correção editorial. Testes usam somente dados
sintéticos e nenhuma fonte institucional foi adicionada.

## Limitações e decisões pendentes

A entrega não define a experiência pública definitiva nem implementa respostas,
progresso, busca, seleção, relatórios, exportação ou associações curatoriais. Continuam
pendentes, sem decisão implícita, GUIA-01, GUIA-05, GUIA-06 e GUIA-08 a GUIA-13.
