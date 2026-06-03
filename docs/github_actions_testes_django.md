# GitHub Actions — Testes automatizados Django

Este pacote adiciona um workflow para rodar os testes automaticamente no GitHub.

## Arquivo incluído

- `.github/workflows/django-tests.yml`

## Quando roda

O workflow roda em:

- Pull Requests para `main`;
- push na `main`;
- push em branches iniciadas com `fase`, como:
  - `fase15i-revisao-aprovacao`;
  - `fase15h-ajustes-formulario-envio`;
  - `fase15g-revisao-visual-publica`.

## O que executa

- instala Python 3.13;
- instala dependências do `requirements.txt`;
- executa `python manage.py check`;
- executa `python manage.py test`.

## Observação

O workflow usa variáveis de ambiente próprias para teste:

- `DJANGO_SETTINGS_MODULE=config.settings`;
- `SECRET_KEY=github-actions-test-secret-key`;
- `DEBUG=False`;
- `ALLOWED_HOSTS=localhost,127.0.0.1,testserver`.

Isso ajuda a validar a aplicação sem depender do ambiente local.
