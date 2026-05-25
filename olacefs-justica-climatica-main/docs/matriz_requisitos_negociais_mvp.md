# Matriz de Requisitos Negociais do MVP — Status Consolidado

Esta matriz consolida a aderência do MVP ao questionário funcional respondido pela equipe negocial.

| Requisito negocial | Implementação no MVP | Status |
|---|---|---|
| Plataforma como hub vivo de boas práticas | Página inicial conceitual, catálogo, filtros, fichas, favoritos, comparação, normas e banco técnico | Implementado |
| Reunir experiências, facilitar consulta, apoiar auditorias e alimentar a Guia | Experiências estruturadas com perguntas, critérios, ferramentas, normas e campo de contribuição para a Guia | Implementado |
| Página introdutória com conceito de justiça climática | Página inicial com “O que é justiça climática?”, propósito da plataforma e público-alvo | Implementado |
| Exibir COMTEMA, CGID, OLACEFS e GIZ na entrada | Bloco institucional com placeholders para logos oficiais | Implementado no MVP |
| Visualização pública | Catálogo, fichas, normas, banco técnico, favoritos e comparação acessíveis publicamente | Implementado |
| Submissão mediante cadastro | Envio de boa prática exige login/cadastro | Implementado |
| Perfis: visitante, usuário, revisor e administrador | Visitante público, usuário autenticado, staff/revisor e Admin Django | Implementado no MVP |
| Conteúdo aprovado público e pendente interno | Catálogo lista apenas conteúdos publicados; pendentes ficam em revisão/status | Implementado |
| Ficha estruturada | EFS, país, tipo, setor, resumo, justiça climática, perguntas, critérios, ferramentas, normas, resultados e replicabilidade | Implementado |
| Campos obrigatórios | EFS, país, título, tipo, setor, temas, normas, contato, e-mail, resumo, vínculo com justiça climática e ano | Implementado |
| Campos desejáveis | Pessoa responsável, objetivo, metodologia, ferramentas, resultados, recomendações, replicabilidade, anexos e links | Implementado |
| Modelo padrão para comparação | Formulário estruturado e comparador lado a lado | Implementado |
| Conteúdo proibido | Orientação explícita no formulário e fluxo de revisão humana | Implementado no MVP |
| Múltiplos temas, normas e grupos vulneráveis | Relações many-to-many e exibição na ficha | Implementado |
| Busca por filtros | País, EFS, tipo, setor, tema, norma, dimensão, grupo e ano | Implementado |
| Busca por palavra-chave | Campo de busca textual no catálogo | Implementado |
| Resultado em cards/lista/tabela | Cards no catálogo e tabelas na comparação | Implementado |
| Destaque para recentes e relevantes | Ordenação cronológica e marcações `destacado`/`relevante` | Implementado |
| Comparação entre experiências | Página `/comparar/` e seleção integrada ao catálogo | Implementado |
| Favoritar experiências relevantes | Favoritos por sessão do navegador | Implementado no MVP |
| Envio dentro da plataforma | Formulário `/adicionar-boa-pratica/` | Implementado |
| Formulário detalhado | Campos alinhados ao questionário funcional | Implementado |
| Salvar e continuar depois | Rascunho e edição antes da publicação | Implementado |
| Editar antes da publicação | Autor pode editar e reenviar conteúdo pendente/devolvido | Implementado |
| Confirmação de envio | Página de confirmação e mensagens do sistema | Implementado |
| Revisão antes de publicação | Status enviado, em revisão, aprovado, publicado e rejeitado | Implementado |
| Voltar para ajuste | Revisor pode devolver com comentário | Implementado |
| Reenvio pelo autor | Autor edita e reenvia sem novo cadastro | Implementado |
| Edição após publicação com aprovação | Proposta de edição publicada com painel específico | Implementado |
| Comparativo da edição publicada | Tabela “valor atual x valor proposto” | Implementado |
| Perguntas, critérios e ferramentas dentro da experiência | Campos específicos na ficha | Implementado |
| Sem área separada obrigatória para perguntas | Conteúdo principal fica dentro da ficha; banco técnico é apoio complementar | Implementado |
| Relação Guia/plataforma | Texto “A Guia orienta; a plataforma demonstra” e campo de contribuição para Guia | Implementado |
| Anexos opcionais | Até três anexos por experiência | Implementado |
| PDF, Word e Excel | Validação de extensão | Implementado |
| Links externos | Campo de URL externa em anexos | Implementado |
| Download público dos anexos | Anexos vinculados à ficha pública | Implementado |
| Títulos autoexplicativos para anexos | Orientação textual no formulário | Implementado |
| Portal de conhecimento vivo | Estrutura visual, catálogo, normas, banco técnico, comparação e submissão contínua | Implementado |
| Navegação enxuta e intuitiva | Header com grupos “Meu espaço” e “Gestão” | Implementado |
| PT/ES/EN | Estrutura trilíngue nas principais telas e dados demonstrativos | Implementado no MVP |
| Acessibilidade básica | Skip link, foco visual, aria-labels, aria-live e redução de movimento | Implementado |
| Dados demonstrativos executivos | 6 EFS/países, experiências institucionais, normas, temas e banco técnico | Implementado |
| Homologação | Checklist, roteiro de testes e documentação de demonstração | Implementado |

## Observações para produção

- A validação de vínculo real com EFS ainda é declaratória no MVP. Em produção, recomenda-se validação por domínio institucional, aprovação manual ou integração com cadastro oficial.
- A moderação de conteúdo proibido é feita por orientação e revisão humana. Em produção, pode-se incluir termo formal de responsabilidade e trilha de auditoria mais robusta.
- Os placeholders de logos devem ser substituídos pelos arquivos oficiais de OLACEFS, COMTEMA, CGID e GIZ.
