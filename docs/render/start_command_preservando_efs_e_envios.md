# Render — Start Command sem mutações automáticas

## Problema

Comandos de carga, retroalimentação ou criação de usuários no build/start podem alterar dados e acessos a cada deploy. Essas operações não pertencem ao pipeline automático.

## Start Command recomendado

Use no Render:

```bash
gunicorn config.wsgi:application
```

As migrations e a coleta de arquivos estáticos são executadas pelo `build.sh`.

## Operações manuais

Os comandos abaixo permanecem disponíveis, mas somente devem ser executados manualmente, com autorização e objetivo explícito:

```bash
python manage.py carregar_dados_ficticios
python manage.py aplicar_retroalimentacao_formulario
python manage.py criar_usuarios_teste --confirmar --resetar-senha
python manage.py criar_admin_render
```

## Build Script

O `build.sh` executa apenas:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```
