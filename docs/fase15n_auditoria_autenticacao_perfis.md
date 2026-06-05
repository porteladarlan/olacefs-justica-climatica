# Fase 15N — Auditoria de autenticação, perfis e permissões

Esta fase começa com uma auditoria automática do comportamento atual de autenticação e permissões antes de alterar views, templates ou regras.

## Arquivo incluído

- `praticas/management/commands/auditar_autenticacao_perfis.py`

## O que o comando verifica

1. Acesso anônimo a páginas públicas.
2. Acesso anônimo a páginas restritas.
3. Acesso de usuário comum a áreas de autor.
4. Bloqueio de usuário comum em áreas de revisão.
5. Acesso de usuário staff/revisor às áreas internas.
6. Rotas em PT, EN e ES.

## Como rodar

```powershell
python manage.py auditar_autenticacao_perfis
```

## Para falhar se encontrar alertas

```powershell
python manage.py auditar_autenticacao_perfis --falhar
```

## Observação

Nem todo alerta é necessariamente erro. O objetivo é mapear o comportamento real da aplicação antes de corrigir UX, mensagens ou permissões.

Após rodar o comando, revise especialmente:

- se usuário anônimo é redirecionado corretamente para login;
- se usuário comum não acessa painel de revisão;
- se staff/revisor acessa painéis internos;
- se rotas EN/ES seguem o mesmo comportamento das rotas PT.
