# Changelog da base Codex

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
