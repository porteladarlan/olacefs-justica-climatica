# Observabilidade básica e integração contínua

## Health check

O endpoint público `GET /health/` verifica se a aplicação Django responde e se
a conexão com o banco de dados está disponível.

- `200`: aplicação e banco disponíveis;
- `503`: banco, uma dependência essencial, indisponível.

A resposta é um JSON mínimo, possui diretivas para impedir cache e não inclui
configurações, credenciais nem detalhes da infraestrutura. Outros métodos HTTP
retornam `405`.

## GitHub Actions

O workflow `.github/workflows/ci.yml` executa automaticamente em pull requests
para `main` e em pushes para `main`. Ele usa Python 3.13, SQLite e variáveis
exclusivas de teste para executar:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py test
```

O workflow não faz deploy, não acessa servidores e não utiliza credenciais de
staging ou produção.
