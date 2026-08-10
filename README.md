# Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática

Plataforma web trilíngue da OLACEFS/AdaptaInfra para reunir, consultar, submeter e revisar boas práticas de auditoria com perspectiva de justiça climática.

A versão atual é uma **versão de validação** preparada para demonstração institucional, teste externo controlado com EFS e planejamento de ambiente de produção futura. Ela não deve ser tratada como produção institucional definitiva sem a implantação de banco persistente, storage de anexos, backup, domínio oficial, governança editorial e hardening final de segurança.

## Mensagem central

> A Guia orienta; a plataforma demonstra experiências concretas.

## Escopo funcional atual

A plataforma contempla:

- página inicial institucional;
- catálogo público de boas práticas;
- filtros por país, EFS, setor, tipo, tema transversal, dimensão, grupo vulnerável, norma e ano;
- ficha estruturada da boa prática;
- recursos técnicos em curadoria;
- normas internacionais como referências interpretativas;
- cadastro e login de usuários;
- formulário de envio de boa prática;
- salvamento como rascunho e envio para revisão;
- área “Meus envios”;
- painel de revisão para staff/revisor;
- painel de revisão de edições publicadas;
- favoritos por sessão;
- comparação de experiências;
- suporte a português, espanhol e inglês;
- dados demonstrativos para apresentação;
- comandos de auditoria e validação da versão.

## Status da versão

Esta base já passou por uma rodada ampla de retroalimentação e consolidação funcional:

| Fase | Entrega principal |
|---|---|
| 15G | Revisão visual das páginas públicas |
| 15H | Ajustes no formulário de envio |
| 15I | Revisão/aprovação e edições publicadas |
| 15J | Conteúdo institucional, recursos técnicos e normas |
| 15K | Dados demonstrativos para apresentação |
| 15L | Usabilidade e acessibilidade |
| 15M | Auditoria trilíngue final |
| 15N | Autenticação, perfis e permissões |
| 15O | Validação funcional ponta a ponta |
| 15P | Materiais de teste externo |
| 15Q | Documentação técnica de ambiente |
| 15R | Consolidação da versão de validação |
| 15S | Entrega final da versão de validação |
| 16A | Preparação Render/teste externo |
| 16B | Validação pública do Render |

## Stack

- Python 3.12+ / 3.13 em testes locais;
- Django 6.x;
- Django Templates;
- Bootstrap via CDN;
- SQLite em ambiente local;
- PostgreSQL recomendado para teste robusto/produção;
- Gunicorn + WhiteNoise para deploy;
- Render como ambiente atual de teste.

## Estrutura principal

```text
olacefs-justica-climatica/
├── config/                         # Configurações Django
├── praticas/                       # App principal
│   ├── management/commands/        # Comandos de carga, auditoria e validação
│   ├── migrations/                 # Migrações do banco
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── tests*.py
│   ├── urls.py
│   └── views.py
├── templates/praticas/             # Templates HTML
├── static/                         # Arquivos estáticos versionados
├── docs/                           # Documentação funcional, técnica e release
├── .github/workflows/              # GitHub Actions
├── build.sh
├── render.yaml
├── requirements.txt
└── manage.py
```

## Instalação local

### 1. Clonar repositório

```powershell
git clone <url-do-repositorio>
cd olacefs-justica-climatica
```

### 2. Criar e ativar ambiente virtual

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variáveis locais

Para desenvolvimento local simples, as configurações padrão permitem rodar a aplicação. Para simular ambiente mais próximo de teste/produção, defina:

```powershell
$env:SECRET_KEY="dev-secret-key-local"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="127.0.0.1,localhost"
```

Para produção/teste hospedado, use variáveis reais no provedor e mantenha `DEBUG=False`.

### 5. Aplicar migrações

```powershell
python manage.py migrate
```

### 6. Carregar dados demonstrativos

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

### 7. Criar usuário administrador

```powershell
python manage.py createsuperuser
```

### 8. Rodar servidor local

```powershell
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## Rotas principais

| Rota | Descrição |
|---|---|
| `/` | Página inicial |
| `/catalogo/` | Catálogo de boas práticas |
| `/experiencias/<id>/` | Ficha da boa prática |
| `/banco-tecnico/` | Recursos técnicos |
| `/normas-internacionais/` | Normas internacionais |
| `/sobre/` | Sobre a plataforma |
| `/cadastro/` | Cadastro de usuário |
| `/entrar/` | Login |
| `/adicionar-boa-pratica/` | Envio de boa prática, exige login |
| `/meus-envios/` | Envios do usuário autenticado |
| `/painel-revisao/` | Painel de revisão, exige staff |
| `/painel-revisao-edicoes/` | Revisão de edições publicadas, exige staff |
| `/admin/` | Django Admin |
| `/en/` | Versão em inglês |
| `/es/` | Versão em espanhol |

## Comandos úteis

### Testes

```powershell
python manage.py test
```

### Auditoria trilíngue

```powershell
python manage.py auditar_traducoes_trilingues
```

### Auditoria de autenticação e perfis

```powershell
python manage.py auditar_autenticacao_perfis
```

### Validação ponta a ponta

```powershell
python manage.py validar_fluxo_ponta_a_ponta
```

### Checagem técnica de ambiente

```powershell
python manage.py checar_prontidao_ambiente
```

### Validação de release

```powershell
python manage.py validar_release_validacao
```

### Entrega final

```powershell
python manage.py validar_entrega_final
```

### Preparação Render/teste externo

```powershell
python manage.py preparar_checklist_render
```

### Auditoria da URL pública do Render

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```

Se houver cold start no Render gratuito:

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/ --timeout 90 --tentativas 5
```

## Deploy no Render

Arquivos relacionados:

- `render.yaml`;
- `build.sh`;
- `Procfile`;
- `DEPLOY_RENDER.md`;
- `ADMIN_RENDER.md`;
- `docs/render/`.

Comandos executados no build atual:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

O deploy não carrega dados demonstrativos, não aplica retroalimentação e não cria administrador. Essas operações permanecem disponíveis somente para execução manual, consciente e autorizada. O Render é mantido como ambiente legado/teste, sem definir a infraestrutura institucional futura. Ambientes de staging e produção usam PostgreSQL e as variáveis explícitas descritas na Fase 2F.

Para ambiente de teste externo, recomenda-se revisar `docs/render/checklist_render_teste_externo.md`.

## Segurança: estado atual e limites

A base possui controles importantes:

- `DEBUG=False` por padrão;
- `ALLOWED_HOSTS` configurável por ambiente;
- `CSRF_TRUSTED_ORIGINS` configurável;
- cookies seguros quando `DEBUG=False`;
- validação de upload por extensão e tamanho;
- limite de 3 anexos por experiência;
- painéis de revisão protegidos por `staff_member_required`;
- ações de favoritos via POST;
- auditorias automatizadas de autenticação/perfis e fluxo ponta a ponta.

Pontos que ainda exigem atenção antes de produção real:

- substituir edição baseada apenas em e-mail/link por autenticação/autorização mais forte;
- validar vínculo institucional da pessoa usuária com uma EFS;
- migrar para banco persistente;
- configurar storage persistente para anexos;
- revisar política de privacidade/termos de uso;
- definir governança editorial formal;
- habilitar HSTS/SSL redirect apenas após domínio HTTPS definitivo;
- usar antivírus ou serviço de varredura para anexos em produção;
- remover artefatos de desenvolvimento indevidos, se aparecerem em `templates/` ou em diretórios duplicados.

## Dados demonstrativos

Os dados gerados por `carregar_dados_ficticios` são apenas para validação e apresentação. Eles não constituem conteúdo oficial da OLACEFS ou das EFS.

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

## Teste externo

Materiais de apoio:

- `docs/teste_externo/roteiro_teste_externo.md`;
- `docs/teste_externo/checklist_teste_externo.md`;
- `docs/teste_externo/perguntas_feedback_teste_externo.md`;
- `docs/teste_externo/preparacao_ambiente_teste_externo.md`;
- `docs/teste_externo/mensagem_envio_link_teste.md`.

## Checklist antes de enviar link externo

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py validar_entrega_final
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```

## Licença e governança

Definir conforme orientação institucional da OLACEFS/GIZ antes de publicação ampla ou produção oficial.
