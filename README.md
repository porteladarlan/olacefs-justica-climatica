# Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática

[![CI](https://github.com/porteladarlan/olacefs-justica-climatica/actions/workflows/ci.yml/badge.svg)](https://github.com/porteladarlan/olacefs-justica-climatica/actions/workflows/ci.yml)

Plataforma web da OLACEFS, impulsionada por COMTEMA e CGID com apoio da GIZ no contexto do projeto AdaptaInfra. O sistema reúne experiências de auditoria, marcos normativos, ferramentas e conteúdos relacionados à justiça climática em português, espanhol e inglês.

## Estado atual

A plataforma está em operação no ambiente institucional:

- **Produção:** <https://olacefs-justiciaclimatica.gizapps.org.br/>
- **Health check:** <https://olacefs-justiciaclimatica.gizapps.org.br/health/>
- **Código de referência:** branch `main`, após pull request e CI aprovados
- **Infraestrutura:** Nginx, Gunicorn/Django e PostgreSQL em servidor Hetzner
- **Arquivos estáticos:** WhiteNoise com manifesto e compressão
- **Mídia:** armazenamento persistente no servidor, com rotina própria de backup
- **Render:** ambiente legado de validação; não é a produção institucional

O merge em `main` não representa deploy automático. A produção é atualizada por uma liberação controlada, com backup, SHA definido, verificações Django, reinício do serviço, smoke test e possibilidade de rollback.

## Funcionalidades

| Módulo | Estado |
|---|---|
| Página inicial | Publicada, trilíngue, responsiva e com vídeo oficial incorporado pelo YouTube em modo de privacidade aprimorada |
| Fundamentos e exemplos | Publicados, com abas acessíveis e casos ilustrativos de injustiça climática |
| Mapa regional | Publicado, com dados agregados, seleção por país e alternativa textual |
| Boas Práticas | Catálogo público, filtros, ficha, comparação, favoritos e anexos |
| Contribuição | Cadastro, confirmação de e-mail, autenticação, rascunho e envio de experiências |
| Meu Espaço | Conteúdos próprios, rascunhos, acompanhamento e favoritos |
| Marcos Normativos | Catálogo público com busca e filtros localizados |
| Ferramentas | Catálogo, criação, edição e arquivamento lógico conforme autorização |
| Recursos Técnicos | Catálogo público curado |
| Gerenciamento | Área interna protegida para usuários `staff` e Django Admin |
| Guia de Perguntas | Estrutura, importação controlada e prévia interna implementadas; publicação pública desabilitada por padrão |
| Internacionalização | Português, espanhol e inglês; espanhol é a referência inicial de parte do conteúdo institucional |

Dados demonstrativos, materiais de teste e conteúdo em rascunho não devem ser tratados como conteúdo institucional homologado.

## Arquitetura

O projeto é um monólito Django com renderização server-side. Não há SPA nem microsserviços.

```text
Navegador
    |
    v
Nginx / TLS
    |
    v
Gunicorn -> Django -> Views / Forms / Services -> ORM -> PostgreSQL
                 |                                  |
                 +-> Templates / WhiteNoise         +-> Dados persistentes
                 |
                 +-> Mídia persistente e SMTP
```

Princípios de manutenção:

- preservar o monólito e fazer a menor alteração suficiente;
- manter autorização no backend, inclusive por objeto;
- versionar migrations e preservar compatibilidade de dados;
- manter português, espanhol e inglês nas mudanças de interface;
- validar acessibilidade, responsividade, uploads e redirecionamentos;
- não confundir protótipo, requisito, dado demonstrativo e comportamento vigente.

## Stack

- Python 3.13 no CI e na linha de desenvolvimento atual;
- Django 6.0;
- PostgreSQL em ambiente implantado e SQLite no desenvolvimento/teste local;
- Gunicorn, Nginx e systemd em produção;
- WhiteNoise para arquivos estáticos;
- templates Django, HTML5, CSS3 e JavaScript;
- GitHub Actions para checks, testes, auditoria de dependências e análise estática;
- `pip-audit`, Bandit e Dependabot no fluxo de segurança.

As faixas efetivas de versões estão em [`requirements.txt`](requirements.txt). Evite documentar ou instalar dependências fora desse arquivo sem registrar a mudança.

## Estrutura do repositório

```text
olacefs-justica-climatica/
├── config/                     # settings, URLs, WSGI, ASGI e health check
├── praticas/                   # domínio, models, forms, views, serviços e testes
│   ├── management/commands/    # importadores, auditorias e gates operacionais
│   ├── migrations/             # evolução versionada do banco
│   └── static/praticas/        # CSS, JavaScript, imagens, fontes e ícones
├── templates/praticas/         # templates funcionais e trilíngues
├── locale/                     # catálogos de tradução do Django
├── docs/                       # documentação humana, testes e histórico
├── ops/                        # backup, restore, monitoramento e units systemd
├── .codex/                     # contexto técnico, decisões e playbooks do projeto
├── .github/workflows/          # CI do GitHub Actions
├── build.sh                    # build do ambiente legado Render
├── render.yaml                 # configuração do ambiente legado Render
├── requirements.txt            # dependências Python
└── manage.py                   # entrada administrativa do Django
```

## Início rápido local

### Pré-requisitos

- Git;
- Python 3.13 recomendado;
- acesso ao PostgreSQL somente quando a tarefa exigir reprodução de ambiente implantado.

O desenvolvimento comum usa SQLite local. Nunca reutilize banco, mídia, credenciais ou dados reais de produção.

### Windows PowerShell

```powershell
git clone https://github.com/porteladarlan/olacefs-justica-climatica.git
Set-Location olacefs-justica-climatica

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$env:DJANGO_ENV = "development"
$env:DEBUG = "True"

python manage.py migrate
python manage.py check
python manage.py runserver
```

Se a política do PowerShell impedir a ativação, use o executável diretamente:

```powershell
$env:DJANGO_ENV = "development"
$env:DEBUG = "True"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### Linux ou macOS

```bash
git clone https://github.com/porteladarlan/olacefs-justica-climatica.git
cd olacefs-justica-climatica

python3.13 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

export DJANGO_ENV=development
export DEBUG=True

python manage.py migrate
python manage.py check
python manage.py runserver
```

A aplicação ficará disponível em <http://127.0.0.1:8000/>.

### Sobre o `.env.example`

O arquivo [`.env.example`](.env.example) documenta as variáveis centrais de configuração, mas **não é carregado automaticamente** pelo Django. Defina as variáveis no terminal, IDE, gerenciador de processos ou serviço de execução. Não adicione segredos ao Git e não copie valores de produção para o ambiente local.

Em `staging` e `production`, a inicialização falha de forma segura quando faltam configurações obrigatórias ou quando são detectados `DEBUG=True`, SQLite, chave fraca, host curinga, origem CSRF sem HTTPS ou cookies inseguros.

## Variáveis de ambiente

| Grupo | Variáveis principais |
|---|---|
| Ambiente | `DJANGO_ENV`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` |
| Banco | `DATABASE_URL` |
| Sessão | `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_AGE`, `SESSION_EXPIRE_AT_BROWSER_CLOSE`, `SESSION_SAVE_EVERY_REQUEST` |
| HTTPS | `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`, `TRUST_X_FORWARDED_PROTO` |
| E-mail | `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL` |
| Arquivos | `STATIC_ROOT`, `MEDIA_ROOT`, `MAX_UPLOAD_SIZE_MB`, `DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_MAX_MEMORY_SIZE` |
| Tradução opcional | `PJC_TRANSLATION_ENDPOINT`, `PJC_TRANSLATION_TOKEN`, `PJC_TRANSLATION_TIMEOUT` |
| Recursos | `GUIA_PUBLICO_HABILITADO` |

Consulte [`.env.example`](.env.example) e [variáveis recomendadas](docs/ambiente/variaveis_ambiente_recomendadas.md) antes de criar ou alterar uma configuração.

## Banco, migrations e dados locais

Para criar ou atualizar somente o banco local de desenvolvimento:

```text
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Regras obrigatórias:

- toda alteração de model deve ter migration versionada e teste correspondente;
- não execute migrations diretamente em produção sem release aprovado, backup e rollback;
- não carregue dados fictícios, importadores ou comandos de publicação em ambiente institucional sem autorização explícita;
- `carregar_dados_ficticios` é destinado a desenvolvimento e demonstração controlada;
- exclusões funcionais devem respeitar arquivamento lógico e regras de proteção existentes.

## Testes e qualidade

Antes de abrir um pull request, execute:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py test
git diff --check
```

Para mudanças focadas, execute primeiro o módulo de teste relacionado e finalize com a suíte completa. Os testes usam banco temporário; não aponte `DATABASE_URL` para um banco real durante a execução local.

O CI possui dois gates:

1. **Django checks and tests:** instalação, system check, migrations, arquivos estáticos e suíte completa;
2. **Dependency and static security analysis:** `pip-audit`, compilação Python e Bandit para achados de alta severidade e alta confiança.

## Fluxo de contribuição

1. Atualize sua referência de `main`.
2. Crie uma branch curta e específica, como `feature/...`, `fix/...`, `security/...` ou `docs/...`.
3. Implemente a menor mudança coerente e adicione ou ajuste testes.
4. Atualize documentação, riscos e [`.codex/CHANGELOG.md`](.codex/CHANGELOG.md) quando aplicável.
5. Execute a validação local.
6. Abra pull request para `main`.
7. Aguarde os dois jobs do CI e a revisão antes do merge.
8. Faça deploy somente do SHA aprovado e com procedimento de rollback.

Não faça commits ou alterações manuais diretamente no código em produção.

## Produção e deploy

A topologia operacional é:

```text
Internet -> DNS/TLS -> Nginx -> Gunicorn/Django -> PostgreSQL
                                      |
                                      +-> staticfiles e mídia persistente
```

Referências operacionais atuais:

- aplicação: `/srv/justica-climatica/app`;
- virtualenv: `/srv/justica-climatica/venv`;
- serviço: `justica-climatica.service`;
- usuário de execução: `deploy`;
- health check público: `/health/`;
- rotinas de backup e monitoramento: [`ops/`](ops/).

O arquivo de ambiente ativo é administrado pelo systemd. Não o imprima, não o copie e não presuma que possa ser carregado com `source`: a sintaxe de `EnvironmentFile` pode não ser válida como script Bash. Para comandos Django no servidor, use o contexto do serviço ou `systemd-run` com o mesmo `EnvironmentFile`, sem expor valores.

Sequência mínima de uma liberação:

1. confirmar PR, CI e SHA aprovado;
2. verificar worktree limpo, serviço e health check;
3. gerar e validar backups de PostgreSQL e mídia;
4. atualizar o checkout para o SHA exato;
5. verificar dependências e migrations;
6. executar `check`, migrations autorizadas e `collectstatic` no ambiente correto;
7. reiniciar o serviço;
8. validar health check, páginas críticas, logs e SHA final;
9. executar rollback do código e restaurar dados somente quando o plano indicar.

Não inclua IPs, chaves SSH, senhas, tokens, conteúdo de arquivos de ambiente ou dados pessoais na documentação e nos logs. Consulte o [guia de deploy](.codex/infrastructure/DEPLOYMENT.md), o [checklist de produção](docs/ambiente/checklist_ambiente_producao.md) e a documentação de [backup e restore](docs/operacao_backup_restore.md).

## Rotas principais

As rotas funcionais recebem `/es/` ou `/en/` quando localizadas; o português usa a rota sem prefixo.

| Rota | Acesso e finalidade |
|---|---|
| `/` | Página inicial pública |
| `/exemplos-injustica-climatica/` | Exemplos públicos de injustiça climática |
| `/catalogo/` | Catálogo público de Boas Práticas |
| `/experiencias/<id>/` | Ficha pública de experiência publicada |
| `/comparar/` | Comparação de experiências |
| `/normas-internacionais/` | Marcos Normativos |
| `/ferramentas/` | Ferramentas |
| `/banco-tecnico/` | Recursos Técnicos |
| `/sobre/` | Informações institucionais |
| `/cadastro/` | Cadastro e confirmação de conta |
| `/entrar/` | Autenticação |
| `/senha/esqueci/` | Recuperação de senha |
| `/meus-envios/` | Conteúdo do usuário autenticado |
| `/adicionar-boa-pratica/` | Nova contribuição autenticada |
| `/painel-revisao/` | Gerenciamento interno para `staff` |
| `/guia/` | Guia público quando `GUIA_PUBLICO_HABILITADO=True` |
| `/guia/preview/` | Prévia interna do Guia |
| `/admin/` | Django Admin |
| `/health/` | Estado da aplicação e do banco |

## Segurança

As referências BSI e o BSI TR-03185 orientam o SSDLC do projeto, mas não representam certificação. Entre os controles implementados estão:

- segredos fora do repositório e configuração fail-closed em ambientes implantados;
- autorização no backend e controle de acesso por objeto;
- CSRF, cookies `HttpOnly`, `Secure` e `SameSite=Lax` conforme ambiente;
- sessão com duração configurável e expiração ao fechar o navegador;
- headers defensivos e Content Security Policy;
- validação de upload por extensão, MIME declarado, assinatura e tamanho;
- redirecionamentos locais seguros;
- separação entre conteúdo público, rascunhos e dados internos;
- logout por `POST` com CSRF;
- análise de dependências, SAST e testes de regressão no CI;
- backups com checksum e scripts de restore controlado;
- monitoramento e health check com verificação do banco.

Pontos que continuam exigindo evolução institucional ou operacional:

- rate limiting distribuído;
- antivírus e quarentena de anexos;
- centralização de logs e observabilidade ampliada;
- redução gradual das exceções identificadas pela CSP em modo de relatório;
- política formal de privacidade, retenção e atendimento aos titulares;
- governança editorial, licenças e autorização de ativos;
- homologação ampliada com tecnologias assistivas.

Consulte [Segurança e SSDLC](.codex/docs/SECURITY_SSDLC.md), [Proteção de dados](.codex/docs/DATA_PROTECTION.md) e o [relatório de controles para TI](docs/seguranca/relatorio_controles_ti_2026-09-14.md).

## Regras funcionais importantes

- somente conteúdo publicado aparece nos catálogos públicos;
- autoria ou perfil `staff` controla edição e arquivamento conforme o fluxo;
- o arquivamento é lógico e preserva registro, anexos, relações e histórico;
- favoritos e logout usam `POST` com CSRF;
- traduções automáticas, quando configuradas, preenchem apenas campos vazios;
- português usa campos canônicos, enquanto espanhol e inglês usam campos localizados do domínio;
- falha do provedor de tradução não deve impedir a publicação;
- vínculos institucionais registrados não concedem autorização automaticamente;
- o Guia público permanece condicionado à configuração e a uma versão publicada válida.

## Documentação

Comece por:

- [Índice da documentação](docs/README.md);
- [Contexto do projeto](.codex/docs/PROJECT_CONTEXT.md);
- [Módulos](.codex/docs/MODULES.md);
- [Arquitetura](.codex/docs/ARCHITECTURE.md);
- [Modelo de dados](.codex/docs/DATA_MODEL.md);
- [Regras de negócio](.codex/docs/BUSINESS_RULES.md);
- [Estratégia de testes](.codex/docs/TEST_STRATEGY.md);
- [Segurança e SSDLC](.codex/docs/SECURITY_SSDLC.md);
- [Checklist de homologação](docs/checklist_homologacao_mvp.md).

Documentos de fases anteriores preservam rastreabilidade, mas não devem ser tratados isoladamente como contrato atual. Em caso de divergência, priorize requisito aprovado, comportamento coberto por teste, código em `main` e documentação marcada como vigente.

## Governança e licença

A governança editorial, a licença pública do código e as políticas institucionais de privacidade e uso ainda dependem de definição formal. Até essa decisão, não presuma autorização para redistribuição, reutilização de conteúdo institucional ou publicação de dados e ativos fora do escopo aprovado.
