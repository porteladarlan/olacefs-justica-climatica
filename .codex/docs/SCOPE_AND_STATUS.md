# Escopo e situação

## Confirmado

- aplicação Django existente;
- consulta pública;
- interface em espanhol, português e inglês;
- servidor dedicado Hetzner AX42-1;
- novo protótipo funcional/visual recebido.

## Implementado nesta evolução

- página inicial institucional reconstruída na ordem aprovada: hero, mensagens, fundamentos, área futura do mapa, conteúdo audiovisual futuro e rodapé;
- hero aberto em duas colunas, sem contêiner externo arredondado, com CTAs reais para marcos normativos e para a área do mapa;
- mensagens da COMTEMA e da CGID compostas com textos e fotografias locais fornecidos no protótipo;
- fundamentos apresentados nas três abas do protótipo, com ARIA, navegação por teclado, painéis focalizáveis e fotografias locais;
- seções semanticamente preparadas para o futuro mapa regional e conteúdo audiovisual, sem D3, TopoJSON, dados ou interações simuladas;
- cabeçalho com acessos diretos a Boas Práticas e Marcos Normativos, indicação acessível da futura rota de Ferramentas, rotas reais de conta, idiomas e alto contraste;
- rodapé e tipografia alinhados ao protótipo, usando assets e fallbacks locais;
- implementação somente em templates, CSS e JavaScript existente, sem alteração do modelo de dados.

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
