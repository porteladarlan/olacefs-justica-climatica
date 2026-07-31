# Deploy

Proposta: Internet -> DNS/TLS/Nginx -> Gunicorn/Django -> PostgreSQL -> mídia.

Sequência: release aprovada, backup, atualizar código, dependências, check, collectstatic, revisar/aplicar migrations, reiniciar, validar Nginx, smoke test, logs e registro.

Proibido: editar código em produção, `DEBUG=True`, executar como root, migration sem backup ou deploy sem commit/rollback.
