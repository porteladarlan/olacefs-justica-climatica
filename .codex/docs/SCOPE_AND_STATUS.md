# Escopo e situação

## Confirmado

- aplicação Django existente;
- consulta pública;
- interface em espanhol, português e inglês;
- servidor dedicado Hetzner AX42-1;
- novo protótipo funcional/visual recebido.

## Implementado nesta evolução

- página inicial institucional reconstruída na ordem aprovada: hero, mensagens, fundamentos, mapa regional funcional, conteúdo audiovisual futuro e rodapé;
- hero aberto em duas colunas, sem contêiner externo arredondado, com CTAs reais para marcos normativos e para a área do mapa;
- mensagens da COMTEMA e da CGID compostas com textos e fotografias locais fornecidos no protótipo;
- fundamentos apresentados nas três abas do protótipo, com ARIA, navegação por teclado, painéis focalizáveis e fotografias locais;
- mapa regional integrado aos cadastros reais de país, EFS, experiências publicadas e normas relacionadas, com seleção múltipla, filtros reais e alternativa textual; conteúdo audiovisual permanece em estado futuro honesto;
- cabeçalho com acessos diretos a Boas Práticas, Marcos Normativos e Ferramentas, além das rotas reais de conta, idiomas e alto contraste;
- rodapé e tipografia alinhados ao protótipo, com Raleway distribuída localmente e fallbacks de sistema;
- implementação em views, templates, CSS, JavaScript e assets locais, sem alteração do modelo de dados.

## Implementado na Fase 2E — mapa regional

- geometrias regionais do `world-atlas` 2.0.2, D3 7.9.0 e TopoJSON Client 3.1.0 distribuídos localmente, com versões, licenças e hashes registrados;
- payload público mínimo sem dados pessoais, rascunhos ou campos internos, montado em três consultas agregadas: uma para países, experiências e contagens; uma de prefetch para EFS; e uma distinta para os pares país–norma, sem consulta individual por país;
- seleção por mouse, teclado ou lista textual, com múltiplos países, chips removíveis, estado anunciado, EFS associadas, contagens reais e ações GET que preservam parâmetros `pais` repetidos;
- catálogos de Boas Práticas e Marcos Normativos reconhecem países existentes sem publicações e retornam zero resultados, em vez de ignorar silenciosamente o filtro;
- nenhuma migration, carga, alteração de banco ou interface do Guia de Perguntas foi criada.

## Implementado na fase de segurança crítica

- edição de boa prática, solicitação de edição publicada e status restritos a usuário autenticado;
- autorização de objeto limitada a staff ou `Experiencia.autor`, sem e-mail em query string ou campo oculto;
- status e propostas filtrados pelo autor real, com registros legados sem autor acessíveis somente a staff;
- redirecionamento de favoritos validado por `obter_destino_seguro`;
- anexos limitados a três itens PDF/JPG/PNG de até 10 MB, com conferência de extensão, MIME informado e assinatura do conteúdo;
- mensagens executáveis sem sequências de mojibake detectadas;
- nenhuma alteração de model, migration ou banco de dados.

## Implementado na Fase 2A.1 — fundação usuário–EFS

- models de lote/item de importação, papel institucional, vínculo canônico usuário–EFS, episódio histórico, atribuição temporal de papel e evento de vínculo;
- constraints de unicidade, datas, decisão, revogação e coerência simples compatíveis com o SQLite atual;
- validações relacionais em Python para impedir autoaprovação, autoatribuição e referências incoerentes entre evento, episódio, atribuição, item e lote;
- duas migrations estruturais sem carga de dados e administração somente para inspeção;
- autorização atual preservada: os novos models não são consultados por views, forms ou serviços de permissão;
- `db.sqlite3` não foi migrado nesta execução; upgrade, rollback e re-upgrade foram ensaiados em banco temporário limpo.

## Implementado na Fase 2C — Ferramentas

- model próprio `Ferramenta`, sem reutilizar `BancoTecnico`, com conteúdo canônico em espanhol, traduções PT/EN opcionais, fallback para o espanhol, situação editorial, setor, responsável, período, URL, ordem e lote de origem;
- migration estrutural `0012_fase2c_ferramenta`, sem `RunPython`, fixture ou carga automática;
- comando idempotente `importar_ferramentas_fase2c`, restrito à fonte cujo SHA-256 foi aprovado, com validação prévia de exatamente 15 ferramentas e oito setores, executor staff, hash do SQLite anterior à carga, códigos canônicos estáveis e ledger por ferramenta e setor; o padrão cria rascunhos, `--publicar` promove somente registro aderente à fonte ou reconciliado na mesma transação com `--atualizar`, e `--reverter-lote` usa snapshots e bloqueios de segurança para lotes concluídos ou com divergências;
- estado local verificado em 3 de agosto de 2026: a migration `0012_fase2c_ferramenta` está aplicada e o lote anterior `48e3a655-c122-4f91-9ec5-7afdc832e4e9`, executado após dry-run pelo importador então vigente, permanece concluído com 15 ferramentas em situação `publicada`, textos literais em espanhol e nenhuma tradução automática; a correção controlada do importador não executou nova carga, publicação, reconciliação ou reversão no `db.sqlite3`;
- catálogo público trilíngue com busca progressiva, filtro por setor, contador real, links externos seguros e estados separados para ausência de publicação e ausência de resultados;
- autorização usuário–EFS e os módulos Home, Boas Práticas, Marcos Normativos e Banco Técnico permaneceram inalterados.

## Implementado no Lote 1 de fidelidade — interface pública e Meu Espaço

- cabeçalho, tipografia e componentes comuns implementados com os tokens e a largura extraídos do protótipo; cabeçalho e geometria das páginas de Boas Práticas e Marcos Normativos foram homologados em navegador;
- estados atuais derivados das rotas Django reais para Home, Boas Práticas, Marcos Normativos, Ferramentas e Meu Espaço;
- catálogos públicos usam filtros e contadores reais no servidor; Boas Práticas publica somente experiências com estado `publicado`, reproduz a sidebar pesquisável do protótipo e não inclui ações extras, enquanto Marcos Normativos apresenta os registros atuais em cards e drawer acessível, sem simular natureza jurídica ou compêndio ainda inexistentes;
- Ferramentas possui catálogo próprio e publica somente registros com situação editorial `publicada`; o banco local verificado contém os 15 registros oficiais da carga anterior com proveniência auditável, sem implicar carga ou publicação automática em outros ambientes;
- login, cadastro, envios, status, detalhe e submissão foram recompostos sem remover campos ou alterar os contratos de autorização, CSRF e upload;
- menus anônimo, autenticado e staff preservam as regras existentes e não prometem vínculo institucional ainda não implementado;
- seletor trilíngue preserva caminho, query string e fragmento, e alto contraste persiste apenas uma preferência booleana local;
- cobertura específica para shell, home, catálogos públicos e Meu Espaço, sem alteração de forms, models, migrations, banco ou autorização.

## Protótipo

- portal de conhecimento;
- fundamentos da justiça climática;
- mapa regional;
- Boas Práticas;
- Marcos Normativos;
- Ferramentas;
- Guia de Perguntas;
- Recursos Técnicos;
- Meu Espaço;
- formulário ampliado;
- acessibilidade;
- vídeo e casos.

## O protótipo não prova

Autenticação, e-mail, banco, moderação, upload seguro, busca no servidor, permissões, PDF, integração externa ou deploy.

## Regra

Antes de implementar, classificar cada requisito como: existente, divergente, parcial, ausente, não aplicável ou pendente.
