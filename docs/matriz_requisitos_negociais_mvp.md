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
| Perfis: visitante, usuário, staff e administrador | Visitante público, usuário autenticado, staff de gerenciamento e Admin Django | Implementado no MVP |
| Rascunho interno e publicação direta | Catálogo lista somente conteúdos publicados; usuário autenticado salva rascunho ou publica diretamente | Implementado |
| Ficha estruturada | EFS, país, tipo, setor, resumo, justiça climática, perguntas, critérios, ferramentas, normas, resultados e replicabilidade | Implementado |
| Campos obrigatórios | EFS, país, título, tipo, setor, temas, normas, contato, e-mail, resumo, vínculo com justiça climática e ano | Implementado |
| Campos desejáveis | Pessoa responsável, objetivo, metodologia, ferramentas, resultados, recomendações, replicabilidade, anexos e links | Implementado |
| Modelo padrão para comparação | Formulário estruturado e comparador lado a lado | Implementado |
| Conteúdo proibido | Orientação explícita no formulário e gerenciamento posterior por staff | Implementado no MVP |
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
| Editar antes da publicação | Autor pode editar o próprio rascunho e publicá-lo diretamente | Implementado |
| Confirmação de envio | Página de confirmação e mensagens do sistema | Implementado |
| Publicação sem aprovação | Ação de publicar grava o conteúdo como publicado e o disponibiliza no catálogo sem etapa intermediária | Implementado |
| Estados editoriais legados | Dados permanecem preservados e pesquisáveis, com rótulo visual único `Registro histórico` | Implementado |
| Edição após publicação | Boa prática publicada pode ser editada conforme autorização; alterações salvas são refletidas diretamente | Implementado |
| Solicitações antigas de edição | Registros permanecem no banco, sem painel, comentários ou ações de aprovação na interface | Implementado |
| Perguntas, critérios e ferramentas dentro da experiência | Campos específicos na ficha | Implementado |
| Sem área separada obrigatória para perguntas | Conteúdo principal fica dentro da ficha; banco técnico é apoio complementar | Implementado |
| Relação Guia/plataforma | Texto “A Guia orienta; a plataforma demonstra” e campo de contribuição para Guia | Implementado |
| Anexos opcionais | Até três anexos por experiência | Implementado |
| PDF, JPG e PNG | Validação de extensão, MIME e tamanho | Implementado |
| Links externos | Campo de URL externa em anexos | Implementado |
| Download público dos anexos | Anexos vinculados à ficha pública | Implementado |
| Títulos autoexplicativos para anexos | Orientação textual no formulário | Implementado |
| Portal de conhecimento vivo | Estrutura visual, catálogo, normas, banco técnico, comparação e submissão contínua | Implementado |
| Navegação enxuta e intuitiva | Header com `Meus envios` para o autor e `Gerenciamento de submissões` para staff; a rota antiga de status é mantida somente como redirecionamento compatível | Implementado |
| PT/ES/EN | Estrutura trilíngue nas principais telas e dados demonstrativos | Implementado no MVP |
| Acessibilidade básica | Skip link, foco visual, aria-labels, aria-live e redução de movimento | Implementado |
| Dados demonstrativos executivos | 6 EFS/países, experiências institucionais, normas, temas e banco técnico | Implementado |
| Homologação | Checklist, roteiro de testes e documentação de demonstração | Implementado |

## Observações para produção

- A validação de vínculo real com EFS ainda é declaratória no MVP. Em produção, recomenda-se validação por domínio institucional, aprovação manual ou integração com cadastro oficial.
- A moderação de conteúdo proibido é feita por orientação preventiva e gerenciamento posterior por staff. Em produção, pode-se incluir termo formal de responsabilidade e trilha de auditoria mais robusta.
- Os placeholders de logos devem ser substituídos pelos arquivos oficiais de OLACEFS, COMTEMA, CGID e GIZ.

## NEG-7 pós-deploy — consolidação da navegação — 2026-09-13

- `Meus envios` é a única tela de acompanhamento dos conteúdos do próprio autor.
- `Gerenciamento de submissões` é a tela global, restrita a staff.
- `/status-envio/` foi preservada para links antigos: redireciona conforme o perfil autenticado e não aceita e-mail em query string como autorização.
- Marcos Normativos agora atende integralmente ao placeholder “nome, tema ou ano”, pesquisando tanto ano numérico quanto descrições textuais de período.
- Estados editoriais legados permanecem preservados no banco e nas buscas, mas são identificados na interface somente como `Registro histórico`, sem etapa operacional de revisão ou aprovação.
- Solicitações de edição e comentários de revisão legados permanecem preservados no banco, mas deixaram de ser exibidos em `Meus envios` e no gerenciamento; suas rotas antigas redirecionam para o fluxo consolidado.
- Nenhuma migration ou alteração de dados foi necessária.
