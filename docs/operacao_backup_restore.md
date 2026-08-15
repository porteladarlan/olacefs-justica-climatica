# Operação de backup, restore e health check

Este documento descreve os artefatos versionados da Fase 17B. Eles ainda não
estão instalados no servidor e não substituem a definição institucional de
backup externo, criptografia, responsáveis, alertas e testes periódicos.

## Diretórios e variáveis

Os scripts usam os seguintes defaults:

- aplicação: `/srv/justica-climatica/app`;
- media: `/srv/justica-climatica/media`;
- backups PostgreSQL: `/srv/justica-climatica/backups/postgres`;
- backups de media: `/srv/justica-climatica/backups/media`;
- retenção: `BACKUP_RETENTION_DAYS=14`.

Para testes controlados, podem ser sobrescritos `POSTGRES_BACKUP_DIR`,
`MEDIA_BACKUP_SOURCE`, `MEDIA_BACKUP_DIR`, `BACKUP_RETENTION_DAYS` e os caminhos
dos executáveis documentados no início de cada script. Caminhos de dados devem
ser absolutos. `DATABASE_URL` é lida somente do ambiente, removida antes dos
demais subprocessos e fornecida ao cliente libpq como `PGDATABASE`. Ela nunca é
incluída em argumentos de processo, comandos versionados, documentação ou logs.

## Backup PostgreSQL

`ops/backup-postgres.sh` usa `pg_dump -Fc`, timestamp UTC e arquivo temporário no
próprio destino. O dump só recebe o nome final depois de `pg_dump` concluir, o
arquivo ser validado como não vazio e o SHA-256 ser calculado. O par gerado é:

```text
justica-climatica-AAAAMMDDTHHMMSSZ.dump
justica-climatica-AAAAMMDDTHHMMSSZ.dump.sha256
```

O script falha se `DATABASE_URL` não estiver definida, não imprime a conexão e
usa `flock` para impedir duas execuções simultâneas. A retenção remove somente
arquivos regulares que correspondam exatamente aos dois padrões acima e estejam
mais antigos que `BACKUP_RETENTION_DAYS`.

O stderr integral de `pg_dump` não é enviado ao journald porque mensagens do
cliente podem revelar host ou usuário. Em falha, o script registra categorias
operacionais sanitizadas; detalhes adicionais devem ser consultados apenas nos
logs protegidos do PostgreSQL e na verificação de espaço/permissões do destino.

## Backup de media

`ops/backup-media.sh` cria um `tar.gz` mesmo quando o diretório de media está
vazio. Ele não segue o diretório de origem quando este é link simbólico, impede
que o destino fique dentro da origem e aplica os mesmos controles de temporário,
SHA-256, `flock` e retenção. O par gerado é:

```text
justica-climatica-media-AAAAMMDDTHHMMSSZ.tar.gz
justica-climatica-media-AAAAMMDDTHHMMSSZ.tar.gz.sha256
```

## Timers systemd

As units em `ops/systemd/` são modelos versionados e ainda não estão instaladas:

- PostgreSQL: diariamente às 02:15 UTC, com atraso aleatório de até 10 minutos;
- media: diariamente às 03:15 UTC, com atraso aleatório de até 10 minutos;
- ambos: `Persistent=true`, usuário/grupo `deploy` e `UMask=0077`;
- PostgreSQL: `EnvironmentFile=/etc/justica-climatica/backup-postgres.env`;
- media: usa os defaults do script e não recebe o ambiente sensível da aplicação.

`backup-postgres.env` é operacional, mínimo e não versionado. Deve conter apenas:

```text
DATABASE_URL=<valor protegido>
BACKUP_RETENTION_DAYS=14
POSTGRES_BACKUP_DIR=/srv/justica-climatica/backups/postgres
```

`POSTGRES_BACKUP_DIR` é opcional. Não incluir `SECRET_KEY`, SMTP,
`EMAIL_HOST_PASSWORD` ou outras credenciais da aplicação. O arquivo deve ser
`root:deploy` com modo `0640`.

O backup de media não precisa de arquivo de ambiente. Se os defaults precisarem
ser alterados futuramente, deve ser criado um EnvironmentFile operacional
específico, sem `DATABASE_URL`, segredos Django, SMTP ou outras credenciais.

Os fontes permanecem no checkout em `/srv/justica-climatica/app/ops/`. As cópias
executadas pelos services devem ficar no diretório operacional separado:

```text
/srv/justica-climatica/app/ops/*.sh
                 ↓ sudo install
/srv/justica-climatica/ops/*.sh
```

Uma conta dedicada de backup poderá substituir `deploy` futuramente, mas somente
junto com política explícita de permissões e ACL para banco, media, backups e
scripts. Não se deve assumir essa conta antes da política ser aprovada.

Sequência de instalação futura, após revisão e aprovação operacional:

1. criar `/srv/justica-climatica/ops`;
2. criar os diretórios de backup PostgreSQL e media;
3. aplicar owner, group e permissões restritivas;
4. copiar os scripts versionados para o diretório operacional;
5. preparar `/etc/justica-climatica/backup-postgres.env` mínimo e protegido;
6. instalar as units e os timers;
7. executar `systemctl daemon-reload`;
8. executar manualmente os backups e validar os checksums;
9. testar o restore em banco temporário e somente então habilitar os timers.

```bash
sudo install -d -o root -g deploy -m 0750 /srv/justica-climatica/ops
sudo install -d -o deploy -g deploy -m 0700 \
  /srv/justica-climatica/backups/postgres \
  /srv/justica-climatica/backups/media
sudo install -o root -g deploy -m 0750 \
  /srv/justica-climatica/app/ops/*.sh \
  /srv/justica-climatica/ops/
if [ ! -e /etc/justica-climatica/backup-postgres.env ]; then
  sudo install -o root -g deploy -m 0640 /dev/null \
    /etc/justica-climatica/backup-postgres.env
else
  sudo chown root:deploy /etc/justica-climatica/backup-postgres.env
  sudo chmod 0640 /etc/justica-climatica/backup-postgres.env
fi
sudoedit /etc/justica-climatica/backup-postgres.env
sudo install -m 0644 \
  /srv/justica-climatica/app/ops/systemd/*.service \
  /srv/justica-climatica/app/ops/systemd/*.timer \
  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start justica-backup-postgres.service
sudo systemctl start justica-backup-media.service
```

Esse procedimento cria o EnvironmentFile somente quando ele não existe e nunca
deve sobrescrever o conteúdo de um arquivo já configurado.

Após os backups manuais, validar cada `.sha256` no respectivo diretório:

```bash
cd /srv/justica-climatica/backups/postgres
sha256sum --check justica-climatica-AAAAMMDDTHHMMSSZ.dump.sha256
cd /srv/justica-climatica/backups/media
sha256sum --check justica-climatica-media-AAAAMMDDTHHMMSSZ.tar.gz.sha256
```

Em seguida, testar o restore PostgreSQL em banco temporário separado e revisar os
logs. Somente depois dessas validações habilitar os timers:

```bash
sudo systemctl enable --now \
  justica-backup-postgres.timer \
  justica-backup-media.timer
```

Esses comandos não foram executados nesta fase. A sequência futura é: criar os
três diretórios, aplicar owner/group/permissões restritivas, copiar os scripts,
preparar o arquivo de ambiente mínimo, instalar as units, executar
`daemon-reload`, testar backups manuais, validar os checksums, testar restore
isolado e apenas então habilitar os timers.

Consulta futura de agenda, estado e últimas execuções:

```bash
systemctl list-timers 'justica-backup-*'
systemctl status justica-backup-postgres.timer justica-backup-media.timer
journalctl -u justica-backup-postgres.service --since today
journalctl -u justica-backup-media.service --since today
```

Os scripts escrevem somente em stdout/stderr, destinados ao journald. Não foi
criada regra em `ops/logrotate/`: não existem logs próprios desses scripts e o
Ubuntu já fornece rotação para os arquivos do Nginx. Duplicar essa regra poderia
causar conflito ou perda de logs.

## Health check operacional

`ops/healthcheck.sh` consulta por padrão:

```text
https://olacefs-justiciaclimatica.gizapps.org.br/health/
```

A URL pode ser sobrescrita por `HEALTHCHECK_URL`. O script aceita somente HTTP ou
HTTPS sem credenciais embutidas, aplica timeout, exige HTTP 200 e valida tanto
`status: ok` quanto `database: ok` sem imprimir o corpo. Falhas retornam código
diferente de zero. Nesta fase não há envio de e-mail nem instalação de monitor
externo.

## Restore PostgreSQL

`ops/restore-postgres.sh` exige simultaneamente:

1. um caminho explícito para arquivo regular e não vazio;
2. `DATABASE_URL` no ambiente;
3. `ALLOW_DATABASE_RESTORE=yes`;
4. dump reconhecido por `pg_restore --list`.

O arquivo `.sha256` correspondente é obrigatório por padrão, e seu nome e hash
devem corresponder ao dump. A exceção exige simultaneamente
`ALLOW_DATABASE_RESTORE=yes` e `ALLOW_RESTORE_WITHOUT_CHECKSUM=yes`, além de
registrar aviso explícito. O restore usa `--single-transaction`,
`--exit-on-error`, `--no-owner`, `--no-privileges` e `--no-password`. Ele não usa
`--clean`, `--create` nem executa `DROP DATABASE`.

A conexão também é fornecida ao `pg_restore` via `PGDATABASE`, nunca por argumento
de processo. O stderr integral é suprimido porque pode conter host ou usuário; a
mensagem sanitizada indica as categorias prováveis, e o diagnóstico detalhado
deve usar somente logs protegidos do PostgreSQL.

O primeiro teste de restore deve ocorrer em banco PostgreSQL temporário, vazio e
separado de staging. A URL desse banco deve ser fornecida por mecanismo protegido
somente durante o teste. Exemplo sem credenciais:

```bash
ALLOW_DATABASE_RESTORE=yes \
DATABASE_URL='<URL protegida do banco temporário>' \
/srv/justica-climatica/ops/restore-postgres.sh \
  /srv/justica-climatica/backups/postgres/justica-climatica-AAAAMMDDTHHMMSSZ.dump
```

Depois do restore, executar migrations em modo de verificação, `manage.py check`,
a suíte de testes aplicável e smoke tests funcionais antes de qualquer promoção.
O restore real não foi executado nesta fase.

Para media, validar primeiro o checksum e listar o conteúdo com `tar -tzf`. A
extração deve ocorrer em diretório temporário separado; somente depois da revisão
de permissões e conteúdo deve haver promoção controlada.

## Rollback e teste periódico

Antes de alterar banco ou media, preservar o estado corrente e registrar a
release em uso. Se o teste restaurado falhar, descartar apenas o banco/diretório
temporário, manter staging inalterado e investigar o backup. Nunca sobrescrever o
banco ou media atual como primeiro teste.

Periodicamente, registrar:

- arquivo e checksum verificados;
- data e duração do restore em ambiente isolado;
- resultado de checks e smoke tests;
- responsável pela execução e aprovação;
- lacunas de cópia externa, criptografia e alertas.
