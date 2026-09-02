# Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática

## Visão geral

A plataforma regional da OLACEFS, impulsionada por COMTEMA e CGID com apoio da GIZ no contexto AdaptaInfra, reúne experiências de auditoria e conteúdos relacionados à justiça climática. O sistema organiza consulta pública, contribuição institucional, referências normativas, ferramentas e uma futura Guia de Perguntas em português, espanhol e inglês.

Esta é uma versão de validação para desenvolvimento e teste. Ainda não é a produção institucional definitiva. A publicação oficial depende de governança editorial, infraestrutura persistente, operação, proteção de dados e homologação institucional.

## Escopo e situação atual

O repositório mantém um monólito Django com templates server-side, catálogo público, fluxos autenticados e painéis de curadoria.

| Módulo | Estado real |
|---|---|
| Início | Implementado |
| Fundamentos | Implementado, com conteúdo trilíngue e abas acessíveis |
| Mapa regional | Implementado, com dados públicos agregados, seleção por país e alternativa textual |
| Boas Práticas | Implementado, com catálogo, filtros, ficha, anexos e relações |
| Contribuição | Implementado, com autenticação, formulário, rascunho e envio |
| Meu Espaço | Implementado, com login, cadastro, status, rascunhos e favoritos |
| Marcos Normativos | Implementado, com catálogo, fontes e filtros disponíveis |
| Ferramentas | Implementado, com catálogo próprio e curadoria |
| Guia de Perguntas | Fundação estrutural implementada; publicação pública desabilitada por padrão e conteúdo editorial pendente |
| Recursos Técnicos | Implementado como catálogo curado |
| Administração/curadoria | Interno, protegido por staff e Django Admin |
| i18n e acessibilidade | Implementado na interface atual; auditoria completa com tecnologia assistiva permanece pendente |
| Vídeo e casos audiovisuais | Desabilitado/futuro |

A aplicação não presume que protótipo, dados demonstrativos ou materiais de teste sejam conteúdo institucional homologado.

### Contrato dos filtros de Marcos Normativos

Os filtros públicos mantêm os parâmetros `setor` e `natureza`, enquanto seus
valores usam chaves canônicas estáveis e labels localizados em PT, ES e EN.
Setores usam as chaves estáveis do catálogo
operacional (`agua_energia`, `infraestrutura`, `biodiversidade_ecossistemas`,
`saude`, `alimentacao_agricultura`, `industria_extrativa`,
`gestao_riscos_desastres`, `genero_direitos_humanos` e `pobreza_desigualdade`);
`binding` e `non_binding` identificam a natureza jurídica. Rótulos localizados
continuam aceitos para compatibilidade, mas cada idioma exibe e consulta apenas
seus próprios campos traduzidos.

## Stack e ambientes

- Python 3.12/3.13;
- Django 6.x;
- templates server-side do Django;
- PostgreSQL em staging/production institucional;
- SQLite para desenvolvimento e testes locais;
- Gunicorn e WhiteNoise;
- Bootstrap carregado por CDN na configuração atual;
- Render mantido como ambiente legado/teste;
- Hetzner AX42-1 como infraestrutura institucional futura, ainda pendente de configuração, operação e homologação.

## Estrutura canônica

~~~text
olacefs-justica-climatica/
├── config/                  # settings e URLs do projeto
├── praticas/                # app, models, forms, views, admin, serviços e testes
│   ├── management/commands/
│   ├── migrations/
│   └── static/
├── templates/praticas/      # templates HTML funcionais
├── static/                  # CSS, JavaScript e assets versionados
├── docs/                    # documentação humana
├── ops/                     # operação e backups canônicos
├── .codex/                  # contexto e memória dos agentes
├── .github/workflows/       # CI
├── build.sh
├── render.yaml
├── Procfile
├── requirements.txt
├── runtime.txt
└── manage.py
~~~

## Instalação local

Use uma cópia do arquivo [.env.example](.env.example). Ele documenta somente variáveis reconhecidas por config/settings.py; não coloque valores reais nele.

### Windows PowerShell

~~~powershell
git clone <url-do-repositorio>
Set-Location olacefs-justica-climatica

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Copy-Item .env.example .env

python manage.py check
python manage.py runserver
~~~

Se o PowerShell bloquear a ativação, use diretamente o executável:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
~~~

### Linux/Bash

~~~bash
git clone <url-do-repositorio>
cd olacefs-justica-climatica

python3.13 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
cp .env.example .env

python manage.py check
python manage.py runserver
~~~

Para um ambiente institucional, configure as variáveis no provedor ou no serviço de execução, sem versionar segredos. Staging e production exigem PostgreSQL.

## Validação

Execute na ordem:

~~~text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py test
git diff --check
~~~

Não execute migrate, cargas ou importadores contra o banco local real sem plano, backup e autorização. Os testes criam banco temporário.

## Rotas atuais

As rotas abaixo podem receber o prefixo /en/ ou /es/:

| Rota | Situação |
|---|---|
| / | Início |
| /catalogo/ | Catálogo público de Boas Práticas |
| /experiencias/<id>/ | Ficha pública |
| /comparar/ | Comparação de experiências |
| /favoritos/ | Favoritos |
| /banco-tecnico/ | Recursos Técnicos |
| /normas-internacionais/ | Marcos Normativos |
| /ferramentas/ | Ferramentas |
| /sobre/ | Sobre a plataforma |
| /guia/ | Guia pública quando GUIA_PUBLICO_HABILITADO=True |
| /guia/preview/ | Prévia interna da Guia |
| /cadastro/ | Cadastro |
| /entrar/ | Login |
| /adicionar-boa-pratica/ | Contribuição autenticada |
| /editar-boa-pratica/<id>/ | Edição autorizada |
| /meus-envios/ | Meu Espaço |
| /status-envio/ | Status do envio |
| /painel-revisao/ | Curadoria staff |
| /painel-revisao-edicoes/ | Curadoria de edições |
| /admin/ | Django Admin |
| /health/ | Health check |
| /i18n/ | Seleção de idioma |

## Segurança implementada

A base atual inclui:

- autorização no backend para áreas autenticadas e staff;
- controle de acesso por objeto para experiências;
- proteção CSRF e cookies HTTP-only;
- DEBUG=False como padrão;
- ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS configuráveis;
- validação de uploads por extensão, MIME informado, assinatura e tamanho;
- limite de anexos por experiência;
- redirecionamento seguro;
- catálogo público restrito a conteúdo publicado;
- separação entre dados públicos e campos internos;
- migrations versionadas e testes de regressão.

## Pendências de segurança e operação

Antes da produção institucional ainda são necessários:

- autenticação e rate limiting mais robustos;
- autorização institucional usuário–EFS;
- aviso de privacidade, base legal, retenção e canal de direitos;
- antivírus, quarentena e análise avançada de uploads;
- CSP e hardening complementar de headers;
- storage persistente para mídia;
- PostgreSQL institucional provisionado;
- backups e restauração testados;
- logs centralizados e monitoramento;
- hardening operacional do Hetzner;
- domínio oficial, TLS e HSTS validados;
- homologação com tecnologia assistiva e zoom;
- governança editorial, licença e autorização de assets.

## Render e Hetzner

O Render permanece documentado para validação e teste externo legado. Seus arquivos de build podem executar instalação, coleta de estáticos e migration conforme a configuração do ambiente, mas isso não representa produção institucional.

A futura operação no Hetzner requer configuração deliberada de PostgreSQL, storage, backups, TLS, observabilidade, usuários de serviço, firewall e procedimento de rollback. Nenhuma dessas etapas é executada por este repositório automaticamente.

## Dados demonstrativos

carregar_dados_ficticios produz dados locais para validação e apresentação. Esses registros não são conteúdo oficial da OLACEFS ou das EFS e não devem ser carregados em ambiente institucional sem autorização explícita.

## Documentação

- [Índice da documentação](docs/README.md);
- [Índice operacional dos agentes](.codex/00_PROJECT_INDEX.md);
- [Contexto do projeto](.codex/docs/PROJECT_CONTEXT.md);
- [Arquitetura](.codex/docs/ARCHITECTURE.md);
- [Segurança SSDLC](.codex/docs/SECURITY_SSDLC.md);
- [Proteção de dados](.codex/docs/DATA_PROTECTION.md);
- [Estratégia de testes](.codex/docs/TEST_STRATEGY.md).

## Governança e licença

Governança editorial, licença, termos de uso e política de privacidade permanecem pendentes de definição e aprovação institucional.
