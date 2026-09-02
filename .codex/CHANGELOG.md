# Changelog da base Codex

## Hotfix — filtros trilíngues de Marcos Normativos — 2026-09-02

- Filtros de setor e natureza jurídica passaram a usar chaves canônicas e
  rótulos do idioma atual, com compatibilidade para valores localizados legados
  e sem leitura do JSON operacional por requisição.

## Não lançado — 2026-08-01

- Integradas notificações editoriais trilíngues para submissão, revisão, publicação e edição de boas práticas, enviadas após commit e sem bloquear o fluxo em falhas SMTP.

- Alinhada a estrutura semântica dos Fundamentos em PT/ES/EN e criada suíte rápida de invariantes públicos.

- Estruturado o Lote 2 de Marcos Normativos com 34 registros extraídos das fichas negociais, natureza jurídica, introdução em espanhol, cobertura própria por país/status, fontes seguras e carga idempotente.

### Fase 0A — saneamento seguro e documentação

- Removidos artefatos duplicados/deslocados do worktree; corrigido o contrato de variáveis do `.env.example`; adicionados padrões específicos ao `.gitignore`; reconstruído o README e criado o índice documental.
- Nenhum código funcional, model, migration, banco ou comportamento da plataforma foi alterado. Baseline e validação final aprovados com 596 testes, 0 falhas, 0 erros e 0 testes ignorados.

- Implementada e encerrada a Fase 2D.1 com oito models próprios e versionados do Guia, proteção de versões publicadas, administração de curadoria, ledger ampliado e migration estrutural `0013_fase2d1_fundacao_guia`, sem carga das 407 perguntas ou das 224 ocorrências de referências; foram aprovados 21 testes direcionados, 278 testes na regressão completa e o ciclo `0012 → 0013 → 0012 → 0013` em SQLite temporário, preservando integralmente o banco real.

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
# 2026-08-09 — Fase 2D.2: motor de importação controlada do Guia

- Implementados validação e dry-run da fonte institucional codificada, sem carga real.
- Implementados importação atômica em rascunho, idempotência, divergências, lote e ledger.
- Implementadas reversão conservadora por lote e publicação/versionamento em operação separada.
- Adicionada cobertura direcionada com fixture sintética; nenhuma migration foi necessária.
# 2026-08-09 — Fase 2D.3: preview interna do Guia

- Criada preview interna somente leitura, restrita a staff/revisor.
- Implementada navegação por eixos, subeixos, setores, subáreas, perguntas e referências da versão publicada vigente.
- Preservado o conteúdo institucional em espanhol, sem tradução ou fallback definitivo.
- Adicionados isolamento por versão, validação hierárquica, estados vazios e testes sintéticos, sem migration.
- Permanecem pendentes GUIA-01, GUIA-05, GUIA-06 e GUIA-08 a GUIA-13.

# 2026-08-09 — Fase 2D.4: hardening técnico do Guia

- Reforçado o isolamento explícito por versão nos relacionamentos da preview e restringidas suas views a GET/HEAD, com cobertura para métodos rejeitados, versão e hierarquia, sem migration.

# 2026-08-10 — Fase 2D.5: Guia público MVP

- Publicada a navegação somente leitura do Guia por eixos, subeixos, setores e subáreas, reutilizando seletores e interface da preview, com conteúdo institucional preservado em espanhol e sem migration.

# 2026-08-10 — Fase 2F: preparação técnica para homologação

- Tornada explícita e fail-closed a configuração de staging/produção para segredos, hosts, CSRF, banco, cookies e proxy HTTPS, preservando desenvolvimento local com SQLite e sem definir infraestrutura institucional.

# 2026-08-10 — Fase 2G: hardening do pipeline de deploy

- Restrito o build automático a dependências, arquivos estáticos e migrations; cargas, retroalimentação e criação de administradores permanecem somente como operações manuais controladas.

# 2026-08-10 — Fase 2H: fechamento do feedback negocial da Home e mapa

- Reordenadas as Presidências, alinhados mapa/fundamentos à paleta roxa e incluídos microterritórios e destaque visual de auditorias coordenadas com relação explícita de EFS participantes.

# 2026-08-12 — Correção negocial de Fundamentos e estratégias

- Atualizado o conteúdo em português, reposicionados os CTAs e publicada a página trilíngue de exemplos com o acervo do protótipo oficial.

# 2026-08-12 — Lote 1 de correções negociais

- Tornada unitária a seleção manual do mapa, ajustados o seletor coordenado e a nomenclatura pública, reposicionado o contato da Boa Prática e preparado o player oficial via MEDIA.

# 2026-08-11 — Fase 2I: gate de prontidão para homologação

- Atualizado o diagnóstico por ambiente para separar falhas críticas, avisos de HTTPS/HSTS e dependências institucionais, com propagação testada pelo gate consolidado.
