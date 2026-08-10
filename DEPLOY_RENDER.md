# Deploy legado/teste no Render — Plataforma OLACEFS Justiça Climática

O Render permanece documentado apenas como ambiente legado/teste. Esta configuração não define a infraestrutura institucional futura.

## Arquivos deste pacote

- `config/settings.py`
- `requirements.txt`
- `build.sh`
- `Procfile`
- `runtime.txt`
- `render.yaml`

## Como aplicar

Extraia o ZIP na raiz do projeto:

```text
C:\Projetos\olacefs-justica-climatica\
```

Aceite substituir os arquivos.

## Teste local antes do commit

```powershell
pip install -r requirements.txt
python manage.py check
python manage.py test
python manage.py collectstatic --no-input
```

## Commit

```powershell
git status
git add config/settings.py requirements.txt build.sh Procfile runtime.txt render.yaml DEPLOY_RENDER.md
git commit -m "Prepara projeto para deploy no Render"
git push -u origin deploy-render
```

## No Render

Você pode usar o `render.yaml` como Blueprint ou criar manualmente.

### Opção manual

Web Service:

```text
Runtime: Python
Build Command: bash build.sh
Start Command: gunicorn config.wsgi:application
```

Variáveis:

```text
SECRET_KEY = gerar automaticamente ou colar uma chave Django
DEBUG = False
DJANGO_ENV = staging
TRUST_X_FORWARDED_PROTO = True
ALLOWED_HOSTS = .onrender.com,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS = https://*.onrender.com
DATABASE_URL = Internal Database URL do PostgreSQL
PYTHON_VERSION = 3.12.7
```

Banco:

```text
PostgreSQL
Name: olacefs-justica-db
```

O `build.sh` executa somente instalação de dependências, coleta de arquivos estáticos e migrations. O deploy não carrega dados demonstrativos, não aplica retroalimentação e não cria administradores ou usuários. Cargas e criação de usuários são operações manuais, conscientes e autorizadas; os comandos de gestão continuam disponíveis para esse uso controlado.

## Observação importante sobre anexos

Para teste e homologação, funciona. Para produção com anexos persistentes, depois será melhor configurar storage externo, como S3, Google Cloud Storage ou Cloudinary.
