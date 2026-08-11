# Variáveis de ambiente recomendadas

## Ambiente de desenvolvimento local

Exemplo básico:

```env
DJANGO_ENV=development
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Ambiente de teste/homologação

```env
DJANGO_ENV=staging
SECRET_KEY=<valor-seguro>
DEBUG=False
ALLOWED_HOSTS=<dominio-do-ambiente>
CSRF_TRUSTED_ORIGINS=https://<dominio-do-ambiente>
DATABASE_URL=<url-do-banco-persistente>
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=<True-somente-apos-confirmar-HTTPS>
TRUST_X_FORWARDED_PROTO=<True-somente-com-proxy-confiavel>
```

## Ambiente de produção futura

```env
DJANGO_ENV=production
SECRET_KEY=<valor-seguro-e-unico>
DEBUG=False
ALLOWED_HOSTS=<dominio-oficial>
CSRF_TRUSTED_ORIGINS=https://<dominio-oficial>
DATABASE_URL=<url-do-banco-producao>
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=<True-somente-apos-confirmar-HTTPS>
TRUST_X_FORWARDED_PROTO=<True-somente-com-proxy-confiavel>
SECURE_HSTS_SECONDS=<definir-apos-validar-HTTPS-e-rollback>
SECURE_HSTS_INCLUDE_SUBDOMAINS=<avaliar>
SECURE_HSTS_PRELOAD=<avaliar>
STATIC_ROOT=<caminho-ou-configuracao-static>
MEDIA_ROOT=<caminho-ou-configuracao-media>
```

## Variáveis para anexos/storage externo

Caso a produção use storage externo, prever variáveis como:

```env
STORAGE_BACKEND=<backend>
AWS_ACCESS_KEY_ID=<valor>
AWS_SECRET_ACCESS_KEY=<valor>
AWS_STORAGE_BUCKET_NAME=<valor>
AWS_S3_REGION_NAME=<valor>
```

ou equivalentes para Azure Blob, Google Cloud Storage ou infraestrutura institucional.

## Variáveis de e-mail

Se houver envio de notificações:

```env
EMAIL_HOST=<host>
EMAIL_PORT=<porta>
EMAIL_HOST_USER=<usuario>
EMAIL_HOST_PASSWORD=<senha>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=<email-institucional>
```

## Observações

- Nunca commitar `.env` com valores reais.
- Manter segredos no painel do provedor de hospedagem ou cofre institucional.
- Separar variáveis de desenvolvimento, teste e produção.
- Não reutilizar `SECRET_KEY` entre ambientes.
- `staging` e `production` recusam inicialização sem `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `DATABASE_URL` explícitos.
- `staging` e `production` recusam `DEBUG=True`, chave fraca, SQLite, host curinga, origem CSRF sem HTTPS e cookies inseguros.
- HSTS e confiança em `X-Forwarded-Proto` exigem validação prévia da terminação TLS e do proxy; não habilitar por suposição.

## Gate de prontidão

`python manage.py checar_prontidao_ambiente --falhar` audita a configuração Django já carregada. Em `development` e `test`, SQLite e defaults locais são válidos e as variáveis de implantação não são exigidas. Em `staging` e `production`, falhas críticas de DEBUG, segredo, hosts, CSRF, banco, cookies ou proxy explicitamente habilitado fazem o comando retornar erro.

HTTPS/HSTS ainda não habilitados são avisos operacionais enquanto domínio e TLS não estiverem definidos. PostgreSQL institucional, storage, backup, domínio/TLS, logs e monitoramento são apresentados separadamente como dependências externas, sem serem confundidos com falhas do código.
