# Fase 15N — refinamento da auditoria de autenticação

Após corrigir o host da auditoria, o comportamento real da aplicação ficou claro:

- páginas públicas principais retornam `200`;
- envio e meus envios redirecionam anônimo para login;
- usuário comum acessa áreas de autor;
- usuário comum não acessa painéis de revisão;
- staff/revisor acessa painéis de revisão;
- `status-envio` e `favoritos` retornam `200` para anônimo, então foram tratados como páginas públicas/semi-públicas;
- `/registrar/` retornou `404`, então a auditoria passou a procurar candidatos de rota de cadastro.

## Arquivo ajustado

- `praticas/management/commands/auditar_autenticacao_perfis.py`

## Como rodar

```powershell
python manage.py auditar_autenticacao_perfis
python manage.py test
```

## Observação

Se a auditoria ainda alertar ausência de rota pública de cadastro, isso indica que a plataforma possui login, mas talvez não tenha rota pública ativa de cadastro de usuário. Esse ponto deve ser decidido funcionalmente.
