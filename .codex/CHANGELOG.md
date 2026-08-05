# Changelog da base Codex

## Não lançado — 2026-08-01

- Registradas as decisões GUIA-02, GUIA-03, GUIA-04 e GUIA-07 para a futura fundação estrutural do Guia, sem código, migration ou carga de dados.
- Implementado o mapa regional funcional da Fase 2E com D3 7.9.0, TopoJSON Client 3.1.0 e `world-atlas` 2.0.2 servidos localmente, seleção múltipla acessível, alternativa textual sem JavaScript, EFS e contagens derivadas somente de experiências publicadas e URLs reais para Boas Práticas e Marcos Normativos; nenhuma alteração de model, migration ou banco foi realizada.
- Documentado o levantamento controlado da Fase 2D.0 do Guia de Justiça Climática, confirmando no protótipo oficial 407 perguntas, 224 ocorrências de referências e a ausência de tela ou interação funcional do módulo; foram registrados o inventário estrutural, as lacunas de idioma, o modelo conceitual candidato, as decisões pendentes e as subfases futuras, sem alteração de código ou banco.
- Refinado o shell global trilíngue com os tokens extraídos do protótipo: Raleway local, navegação com estado atual, menus por perfil, idioma preservando rota/filtros/fragmento, contraste persistente e menu móvel acessível; cabeçalho e geometria foram homologados em navegador nas páginas de Boas Práticas e Marcos Normativos.
- Recompostos e homologados visualmente os catálogos públicos de Boas Práticas e Marcos Normativos em 1440 × 900, com hierarquia, espaçamentos, sidebar, toolbar, grids, cards e drawer equivalentes ao protótipo. Filtros e contadores usam QuerySets reais, ícones são SVGs sem ligaturas visíveis e Boas Práticas não exibe ações adicionais ausentes do desenho oficial. Marcos mantém indisponíveis, sem simulação, o compêndio e a natureza jurídica ainda não suportados pelo schema. Criada também a rota funcional de Ferramentas com estado vazio honesto enquanto não existe situação editorial para os registros da Fase 2C.
- Alinhadas ao protótipo as páginas de login, cadastro, envios, status e formulário de submissão, preservando campos, CSRF, uploads, autoria e autorização existentes.
- Mantidos Bootstrap 5.3.3, comportamento de logout e contratos de negócio existentes; nenhuma alteração de schema ou dado foi realizada no Lote 1 de fidelidade.
- Criada a fundação de dados da Fase 2A.1 para vínculo usuário–EFS, com catálogo vazio de papéis, vínculo canônico, episódios históricos, atribuições temporais, eventos imutáveis e ledger de importação.
- Adicionadas as migrations `0010_fase2a1_lote_importacao` e `0011_fase2a1_vinculo_efs`, sem `RunPython`, papéis, vínculos ou qualquer carga inicial.
- Mantida integralmente a autorização vigente por `Experiencia.autor` ou staff; e-mail, domínio, vínculo, episódio e papel institucional ainda não concedem permissão.
- Implementado o catálogo funcional da Fase 2C com model próprio `Ferramenta`, situação editorial, setor, ordenação, traduções institucionais opcionais com fallback para o espanhol e administração de curadoria. A migration `0012_fase2c_ferramenta` é somente estrutural; o comando `importar_ferramentas_fase2c` valida o SHA-256 oficial, usa códigos canônicos independentes da ordem, cria rascunhos por padrão, exige `--publicar` e `--atualizar` para ações explícitas, bloqueia a publicação de registro divergente sem reconciliação, oferece dry-run com contagens e reversão segura de lotes concluídos ou com divergências e registra ferramentas e setores em ledger auditável. A rota pública oferece busca progressiva, filtro por setor, contador real, links externos seguros e estados distintos para catálogo sem publicação e filtro sem resultados.

## Não lançado — 2026-07-31

- Reconstruídos o cabeçalho e a página inicial conforme o `index.html` do protótipo `plataforma-justicia-climatica 1.zip`, mantendo as rotas e funcionalidades existentes.
- Removidos da home a busca, a navegação genérica, os três cards intermediários e a composição de quatro abas com nove estratégias que não pertenciam ao protótipo aprovado.
- Integrados hero aberto, mensagens institucionais, três abas acessíveis de fundamentos, preparação visual do mapa e do conteúdo audiovisual e rodapé com assets locais do material de design.
- Preservados layout responsivo, navegação por teclado e conteúdo em espanhol, português e inglês, com cobertura de regressão para cabeçalho, ordem das seções, CTAs, abas, rotas e assets.
- Removida a autorização por e-mail informado em query string; edição, solicitação de edição publicada e consulta de status agora exigem autenticação e vínculo real de autoria ou perfil staff.
- Corrigido o redirecionamento de favoritos para aceitar somente destinos locais seguros.
- Anexos alinhados a três posições, PDF/JPG/PNG e 10 MB por arquivo, com validação de extensão, MIME declarado, assinatura real e tentativas de contornar o limite.
- Corrigidas mensagens com mojibake no backend e adicionados testes negativos específicos de segurança.
- Nenhuma alteração de modelo de dados ou migration.

## 1.0.0 — 2026-07-31

Base criada com contexto, delta do protótipo, infraestrutura Hetzner, SSDLC/BSI, Skills, playbooks e regras para redução de tokens.
