# Render — Start Command preservando EFS oficiais e envios

## Problema

Quando o comando `carregar_dados_ficticios --limpar-demo` é usado em deploy/start, dados cadastrados manualmente podem ser removidos.

Quando o comando `aplicar_retroalimentacao_formulario` não é executado, a lista oficial/ampliada de EFS pode não aparecer no formulário, ficando apenas a lista demonstrativa reduzida.

## Start Command recomendado

Use no Render:

```bash
python manage.py migrate && python manage.py aplicar_retroalimentacao_formulario && python manage.py criar_usuarios_teste --confirmar --resetar-senha && gunicorn config.wsgi:application
```

## O que cada parte faz

```bash
python manage.py migrate
```

Aplica as migrations.

```bash
python manage.py aplicar_retroalimentacao_formulario
```

Garante a lista oficial/ampliada de países, EFS e taxonomias no formulário.

```bash
python manage.py criar_usuarios_teste --confirmar --resetar-senha
```

Garante os usuários de teste, sem recriar boas práticas.

```bash
gunicorn config.wsgi:application
```

Inicia a aplicação.

## Evitar no Start Command

Não use no Start Command:

```bash
python manage.py carregar_dados_ficticios --limpar-demo
```

Esse comando deve ser usado apenas quando a intenção for resetar a base demonstrativa.

## Build Script

O `build.sh` pode executar:

```bash
python manage.py carregar_dados_ficticios
python manage.py aplicar_retroalimentacao_formulario
```

sem `--limpar-demo`, para garantir dados básicos e lista oficial de EFS.
