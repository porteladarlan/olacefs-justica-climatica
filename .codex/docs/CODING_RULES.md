# Regras de código

## Geral

Menor alteração coerente; respeitar padrões; não misturar refatoração ampla; comentários explicam motivo; sem exceção genérica silenciosa.

## Django

Autorização no backend, ORM, constraints, transações, forms no servidor, CSRF, URLs nomeadas, settings por ambiente e sem segredos. Evitar regra em template e signals difíceis de rastrear.

## Banco

Migration pequena, dados separados quando necessário, compatibilidade e rollback. Não apagar coluna/dados sem transição.

## Frontend

Componentes, tokens CSS, JavaScript progressivo, sem `innerHTML` com conteúdo não confiável, i18n e acessibilidade.

## Logs

Não logar senha, token, cookie, arquivo ou dados pessoais desnecessários.

## Antes de concluir

`manage.py check`, testes, revisão de migrations, segurança e documentação.
