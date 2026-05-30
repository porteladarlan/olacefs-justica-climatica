# Correção Fase 15E — teste de tradução com usuário autenticado

Corrige o teste `test_pagina_envio_em_ingles_nao_exibe_labels_portugueses_principais`.

Motivo:
- A rota `/en/adicionar-boa-pratica/` exige login.
- O teste acessava a página sem autenticação e recebia HTTP 302 para login.
- A correção cria um usuário de teste e usa `force_login` antes de validar os labels em inglês.

Não altera regra de negócio, template ou formulário. Apenas corrige o teste.
