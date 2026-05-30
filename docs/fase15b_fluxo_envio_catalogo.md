# Fase 15B — Fluxo de envio e catálogo de boas práticas

Implementação baseada na retroalimentação da plataforma.

## Escopo

- Envio de boa prática exige login.
- Link "Envie sua prática" pode direcionar usuário anônimo para login com `next`.
- Login preserva o redirecionamento para o formulário.
- Cadastro também preserva o parâmetro `next`.
- Catálogo recebe pop-up "O que é uma boa prática?".
- Catálogo deixa de exibir comparador como destaque.
- Catálogo deixa de exibir o badge/texto "Contribui para a Guia".
- A funcionalidade de comparação não foi removida do backend, apenas ocultada do catálogo.

## Arquivos alterados

- praticas/views.py
- templates/praticas/catalogo_experiencias.html
- templates/praticas/login_usuario.html
- templates/praticas/registrar_usuario.html
- praticas/tests.py
