# Admin automático no Render Free

Este pacote adiciona um comando Django para criar/atualizar um superusuário durante o deploy no Render.

## Arquivos

- `praticas/management/commands/criar_admin_render.py`
- `build.sh`

## Variáveis obrigatórias no Render

No Web Service, em Environment, adicione:

```text
DJANGO_SUPERUSER_USERNAME = admin_teste
DJANGO_SUPERUSER_EMAIL = seu-email@exemplo.com
DJANGO_SUPERUSER_PASSWORD = uma-senha-forte
```

Depois clique em:

```text
Manual Deploy > Deploy latest commit
```

Ao final, acesse:

```text
https://SEU-LINK.onrender.com/admin/
```

Use o usuário e senha definidos nas variáveis.
