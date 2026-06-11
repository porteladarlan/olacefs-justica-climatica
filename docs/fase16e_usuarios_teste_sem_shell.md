# Fase 16E — Criação de usuários de teste sem Shell

Esta fase adiciona um comando seguro e controlado para criar usuários temporários de teste no Render, mesmo quando o ambiente não oferece Shell/SSH.

## Arquivos incluídos

- `praticas/management/commands/criar_usuarios_teste.py`
- `praticas/tests_fase16e.py`
- `docs/render/fase16e_usuarios_teste_sem_shell.md`

## Comando

```powershell
python manage.py criar_usuarios_teste --confirmar --resetar-senha
```

## Segurança

Em ambiente com `DEBUG=False`, o comando só executa quando a variável abaixo estiver ativa:

```text
PERMITIR_CRIACAO_USUARIOS_TESTE=true
```

Isso evita criação acidental de usuários temporários em produção.

## Testes

```powershell
python manage.py test praticas.tests_fase16e
python manage.py test
```
