# Monitoramento operacional e alertas

Este runbook descreve os artefatos versionados da Fase 17C-1. A instalação no
staging depende de revisão humana e deve ser executada separadamente. Nada nesta
fase instala units, acessa o servidor ou envia e-mail real.

## Arquitetura

`ops/monitor.py` é um monitor independente do Django, escrito somente com a
biblioteca padrão do Python. A unit `justica-monitor.timer` inicia o service
oneshot aproximadamente a cada cinco minutos. O processo consulta systemd, o
endpoint HTTPS, os diretórios de backup e o filesystem; registra resultados
sanitizados no journald; persiste somente o estado antispam; e envia alertas por
SMTP quando há mudança de estado ou expira o intervalo de repetição.

O monitor é observacional. Ele não reinicia services, habilita timers, executa
backup/restore, altera banco nem remove arquivos.

## Checks e estados

Cada check produz identificador, `OK`, `WARNING` ou `CRITICAL`, mensagem
sanitizada e timestamp UTC. O estado global é `CRITICAL` se houver qualquer
critical, `WARNING` se não houver critical e houver warning, e `OK` nos demais
casos.

Os checks são:

- `justica-climatica.service`: unit carregada e `active`;
- `nginx.service`: unit carregada e `active`;
- endpoint público HTTPS `/health/`: resposta HTTP 200 com validação TLS normal;
- timers PostgreSQL e media: `enabled`, `active` e, quando disponível, próxima
  execução agendada;
- último backup PostgreSQL e media: nome institucional exato, arquivo não vazio,
  checksum correspondente e idade dentro do limite;
- último `Result` dos services oneshot de backup, sem considerar o estado normal
  `inactive (dead)` como falha após sucesso;
- ocupação do filesystem que contém `/srv/justica-climatica`.

O monitor não recalcula o SHA-256 a cada ciclo. A criação e a validação
criptográfica continuam sob responsabilidade dos scripts e do runbook da Fase
17B; este check detecta ausência e atraso. Uma tolerância de até 300 segundos é
aplicada para pequeno desvio de relógio. Timestamp mais de cinco minutos no
futuro é `CRITICAL` e não pode mascarar um backup atrasado.

## Thresholds e exit codes

Defaults:

- timeout de rede/comando: 10 segundos;
- idade máxima dos backups: 129600 segundos (36 horas);
- disco: warning a partir de 80% e critical a partir de 90%;
- repetição de alerta persistente: 21600 segundos (6 horas).

Os limites de disco devem satisfazer `0 < warning < critical <= 100`.
Configuração inválida falha antes dos checks.

Exit codes:

- `0`: todos os checks estão `OK` e não houve falha no alerta;
- `1`: há `WARNING`/`CRITICAL` operacional ou o envio SMTP falhou;
- `2`: configuração inválida ou impossibilidade de persistir o estado.

Uma unit oneshot com exit 1 ficará `failed` até a próxima execução; isso é
intencional para dar visibilidade ao incidente. O timer continua agendado.

## EnvironmentFile protegido

O arquivo real deve ficar fora do Git em
`/etc/justica-climatica/monitoring.env`, com owner `root`, group `deploy` e modo
`0640`. Ele contém segredo SMTP e nunca deve ser copiado para o repositório,
documentação, ticket ou log.

Exemplo sem valores reais:

```text
MONITOR_ENVIRONMENT=staging
MONITOR_HEALTH_URL=https://olacefs-justiciaclimatica.gizapps.org.br/health/
MONITOR_ALERT_RECIPIENTS=responsavel1@example.org,responsavel2@example.org
MONITOR_SMTP_HOST=smtp.example.org
MONITOR_SMTP_PORT=587
MONITOR_SMTP_USE_TLS=true
MONITOR_SMTP_USER=monitor@example.org
MONITOR_SMTP_PASSWORD=<secret-operacional>
MONITOR_FROM_EMAIL=monitor@example.org
MONITOR_TIMEOUT_SECONDS=10
MONITOR_BACKUP_MAX_AGE_SECONDS=129600
MONITOR_DISK_WARNING_PERCENT=80
MONITOR_DISK_CRITICAL_PERCENT=90
MONITOR_ALERT_REPEAT_SECONDS=21600
MONITOR_STATE_FILE=/srv/justica-climatica/ops-state/monitor-state.json
MONITOR_POSTGRES_BACKUP_DIR=/srv/justica-climatica/backups/postgres
MONITOR_MEDIA_BACKUP_DIR=/srv/justica-climatica/backups/media
MONITOR_DISK_PATH=/srv/justica-climatica
```

Não incluir `DATABASE_URL`, `SECRET_KEY`, credenciais Django ou outros segredos
da aplicação. O monitor não lê nem registra esses valores. O endereço de health
deve ser HTTPS e não pode conter credenciais. Com `MONITOR_SMTP_USE_TLS=true`, o
cliente exige STARTTLS com validação de certificado. STARTTLS é obrigatório, não
existe modo SMTP plaintext e `MONITOR_SMTP_USE_TLS=false` é rejeitado como erro
de configuração sanitizado.

## Instalação futura

Os comandos abaixo são um roteiro para execução futura após aprovação. Não
foram executados nesta fase.

1. Criar o diretório operacional e o diretório de estado.
2. Copiar o monitor versionado para `/srv/justica-climatica/ops`.
3. Criar ou revisar de modo não destrutivo o EnvironmentFile.
4. Instalar somente as duas novas units.
5. Fazer `daemon-reload`.
6. Executar o service manualmente e revisar o journald.
7. Simular alerta e recuperação de forma controlada.
8. Somente depois habilitar o timer.

```bash
sudo install -d -o root -g deploy -m 0750 /srv/justica-climatica/ops
sudo install -d -o deploy -g deploy -m 0700 \
  /srv/justica-climatica/ops-state
sudo install -o root -g deploy -m 0750 \
  /srv/justica-climatica/app/ops/monitor.py \
  /srv/justica-climatica/ops/monitor.py
sudo install -d -o root -g deploy -m 0750 /etc/justica-climatica
if [ ! -e /etc/justica-climatica/monitoring.env ]; then
  sudo install -o root -g deploy -m 0640 /dev/null \
    /etc/justica-climatica/monitoring.env
else
  sudo chown root:deploy /etc/justica-climatica/monitoring.env
  sudo chmod 0640 /etc/justica-climatica/monitoring.env
fi
sudoedit /etc/justica-climatica/monitoring.env
sudo install -o root -g root -m 0644 \
  /srv/justica-climatica/app/ops/systemd/justica-monitor.service \
  /srv/justica-climatica/app/ops/systemd/justica-monitor.timer \
  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start justica-monitor.service
sudo systemctl status justica-monitor.service
sudo journalctl -u justica-monitor.service -n 100 --no-pager
sudo systemctl enable --now justica-monitor.timer
```

O bloco condicional nunca trunca um EnvironmentFile existente. Preencher os
valores reais somente via `sudoedit`, conferir os destinatários antes do teste e
não usar credenciais da aplicação se uma credencial SMTP operacional dedicada
estiver disponível.

## Estado antispam e alertas

O estado fica em
`/srv/justica-climatica/ops-state/monitor-state.json`, fora do checkout. O
diretório deve ser `deploy:deploy` e `0700`; o JSON é gravado atomicamente com
modo `0600`. Ele contém apenas estados, timestamp do último alerta e
identificadores dos checks com problema — nunca credenciais.

Fluxo para `WARNING` e `CRITICAL`:

- `OK -> degradado`: envia `ALERTA OPERACIONAL`;
- surgimento de qualquer novo check degradado: envia alerta imediato, mesmo que
  o estado global continue `WARNING` ou `CRITICAL`;
- degradado persistente: suprime mensagens até
  `MONITOR_ALERT_REPEAT_SECONDS`, então envia lembrete;
- mudança de warning para critical ou de critical para warning: envia alerta da
  nova severidade;
- degradado -> `OK`: envia `RECUPERADO`.

Se o SMTP falhar, o incidente original permanece no journald, a falha é
registrada apenas como `SMTP_ALERT_FAILED`, e o estado não finge que o alerta foi
entregue. O horário da tentativa é persistido para evitar uma nova tentativa a
cada ciclo; a entrega pode ser tentada novamente somente após o intervalo de
repetição. Um state file ausente começa em estado seguro. Um arquivo corrompido
é ignorado, gera warning sanitizado e é reconstruído atomicamente.

## Teste manual e recuperação

Antes de habilitar o timer, executar o service e confirmar `STATUS=OK`. Para um
teste de alerta, usar uma janela controlada e uma falha reversível, como uma URL
HTTPS de health deliberadamente inexistente no EnvironmentFile de teste. Nunca
parar Nginx, Django ou backups apenas para testar o monitor. Restaurar a URL e
executar novamente para confirmar o e-mail de recuperação.

```bash
sudo systemctl start justica-monitor.service
sudo systemctl status justica-monitor.service
sudo journalctl -u justica-monitor.service --since today
sudo systemctl list-timers justica-monitor.timer \
  justica-backup-postgres.timer justica-backup-media.timer
```

Para desativar somente o agendamento, sem alterar os demais componentes:

```bash
sudo systemctl disable --now justica-monitor.timer
```

## Runbook mínimo de incidentes

### Health endpoint falhou

```bash
sudo systemctl status justica-climatica.service
sudo journalctl -u justica-climatica.service --since today
sudo systemctl status nginx.service
sudo journalctl -u nginx.service --since today
```

Não desativar validação TLS. Verificar DNS, certificado e conectividade sem
registrar headers, cookies ou resposta completa.

### Backup PostgreSQL atrasado ou falhou

```bash
sudo systemctl status justica-backup-postgres.timer
sudo systemctl status justica-backup-postgres.service
sudo journalctl -u justica-backup-postgres.service --since today
```

Seguir o runbook da Fase 17B. Não executar restore no banco ativo e não remover
backups para silenciar o alerta.

### Backup de media atrasado ou falhou

```bash
sudo systemctl status justica-backup-media.timer
sudo systemctl status justica-backup-media.service
sudo journalctl -u justica-backup-media.service --since today
```

### Disco acima do limite

Identificar o filesystem e os diretórios consumidores com ferramentas de leitura
apropriadas. Não automatizar exclusão de backups, media, logs ou dados. Qualquer
limpeza deve ter alvo validado, retenção aprovada e rollback quando aplicável.

### SMTP falhou

Consultar o erro sanitizado no journald, revisar permissões e nomes das variáveis
do EnvironmentFile protegido e testar conectividade TLS. Não imprimir o arquivo,
a senha ou a sessão SMTP no terminal/log. Corrigir a causa e iniciar o service
novamente; como o alerta não foi marcado como entregue, ele será tentado outra
vez.

## Troubleshooting e segurança

- `CONFIG_ERROR`: verificar presença e formato das variáveis, sem imprimir
  valores secretos;
- `STATE_WRITE_FAILED`: verificar owner/mode de `ops-state` e se a unit preserva
  `ReadWritePaths`;
- timer ativo com service `failed`: consultar os checks no journald; o próximo
  ciclo continua agendado;
- backup não encontrado: confirmar o padrão exato de nome e o `.sha256`; locks,
  temporários e links simbólicos são ignorados;
- service/timer não encontrado: confirmar instalação das units e executar
  `daemon-reload`; o monitor não corrige isso automaticamente.

Os logs devem conter apenas estado global, identificadores, mensagens
sanitizadas e timestamps. Nunca anexar EnvironmentFiles, URIs de banco, senhas,
cookies, headers ou chaves privadas a incidentes.
