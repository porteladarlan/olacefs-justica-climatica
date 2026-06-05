# Correção Fase 15N — auditoria com host de teste

A primeira execução da auditoria retornou `400` em todas as rotas. Isso indica problema de host/ALLOWED_HOSTS no `Client()` usado pelo comando, não necessariamente problema real de autenticação.

## Ajuste realizado

Em `praticas/management/commands/auditar_autenticacao_perfis.py`:

- adiciona `@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])`;
- força as requisições do `Client()` com `HTTP_HOST="testserver"`.

## Motivo

O Django pode retornar `400 Bad Request` quando o host usado pelo cliente de teste não está permitido. A correção permite que a auditoria avalie o comportamento real das rotas.
