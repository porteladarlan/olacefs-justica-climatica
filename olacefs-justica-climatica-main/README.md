# olacefs-justica-climatica

MVP local da **Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática** para a OLACEFS.

## Contexto institucional

A plataforma foi concebida para apoiar o intercâmbio técnico entre Entidades Fiscalizadoras Superiores (EFS) da América Latina e Caribe, com foco em auditorias relacionadas à agenda climática e à justiça climática.

## Objetivo do MVP

Disponibilizar uma base funcional para:

- registrar boas práticas de auditoria;
- consultar experiências por múltiplos filtros;
- visualizar detalhes técnicos das iniciativas;
- concentrar referências metodológicas em um banco técnico;
- apoiar a validação visual e funcional antes de uma futura integração institucional.

## Escopo funcional atual

O MVP está preparado para uso local, com navegação pública, administração via Django Admin e carga de dados fictícios para demonstração.

## Funcionalidades implementadas

- Página inicial com visão geral e métricas.
- Catálogo público de experiências com filtros.
- Página de detalhe de cada experiência.
- Banco técnico com recursos de apoio.
- Página institucional “Sobre”.
- Administração de dados pelo Django Admin.
- Comando de carga de dados fictícios.

## Estrutura do projeto

```text
olacefs-justica-climatica/
├── config/                         # Configuração Django
├── praticas/                       # App principal
│   ├── management/commands/        # Comandos customizados
│   ├── migrations/                 # Migrações
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/praticas/             # Templates HTML
├── manage.py
├── README.md
├── .gitignore
├── .editorconfig
└── .gitattributes
```

## Stack utilizada

- Python
- Django
- SQLite para ambiente local
- Django Templates
- Bootstrap 5 via CDN

## Requisitos locais

- Python 3.10 ou superior
- pip atualizado
- Ambiente virtual com `venv`

## Instalação local

### 1. Clonar o repositório

```powershell
git clone <url-do-repositorio>
cd olacefs-justica-climatica
```

### 2. Criar o ambiente virtual

```powershell
python -m venv venv
```

### 3. Ativar o ambiente virtual no Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a execução do script, rode:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 4. Instalar dependências

```powershell
pip install django
```

Se existir um arquivo `requirements.txt`, use:

```powershell
pip install -r requirements.txt
```

### 5. Rodar as migrações

```powershell
python manage.py migrate
```

### 6. Carregar dados fictícios

```powershell
python manage.py carregar_dados_ficticios
```

### 7. Criar superusuário

```powershell
python manage.py createsuperuser
```

### 8. Rodar o servidor local

```powershell
python manage.py runserver
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8000/
```

## Rotas principais

| Rota | Descrição |
|---|---|
| `/` | Página inicial |
| `/catalogo/` | Catálogo de experiências |
| `/experiencias/<int:pk>/` | Detalhe da experiência |
| `/banco-tecnico/` | Banco técnico |
| `/sobre/` | Sobre a plataforma |
| `/admin/` | Django Admin |

## Como acessar o Django Admin

1. Crie um superusuário:

```powershell
python manage.py createsuperuser
```

2. Rode o servidor:

```powershell
python manage.py runserver
```

3. Acesse:

```text
http://127.0.0.1:8000/admin/
```

4. Entre com o usuário e senha criados.

## Dados fictícios

O comando abaixo popula o banco com conteúdo de demonstração:

```powershell
python manage.py carregar_dados_ficticios
```

Esses dados não representam uma base oficial institucional. Eles servem apenas para validação visual, funcional e técnica do MVP.

Caso seja necessário reiniciar a base local:

```powershell
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
python manage.py migrate
python manage.py carregar_dados_ficticios
```

## Migração futura para PostgreSQL/RDS

Para evolução do ambiente local para ambiente institucional, recomenda-se:

- migrar de SQLite para PostgreSQL;
- externalizar credenciais em variáveis de ambiente;
- preparar o uso de banco gerenciado, como RDS ou equivalente;
- revisar políticas de backup, monitoramento e segurança;
- definir estratégia de armazenamento para anexos e arquivos;
- estruturar ambiente de homologação antes de produção.

## Boas práticas para desenvolvimento local

- Não versionar `venv/`, `db.sqlite3`, `media/`, `__pycache__/` e arquivos temporários.
- Executar `python manage.py check` antes de validar entregas.
- Testar as rotas principais após alterações de templates.
- Evitar mudanças em modelos sem necessidade real de migração.
- Fazer alterações incrementais e fáceis de revisar.
- Preferir VS Code em vez de Bloco de Notas para edições maiores.

## Cuidados com encoding no Windows

Em alguns ambientes Windows podem ocorrer textos com encoding quebrado, por exemplo:

```text
JustiÃ§a
ClimÃ¡tica
Catálogo
Países
```

Recomendações:

- manter arquivos em UTF-8;
- usar VS Code com encoding UTF-8;
- revisar acentuação ao editar templates e comandos;
- nos templates HTML, priorizar entidades HTML quando necessário, como:
  - `&ccedil;`
  - `&aacute;`
  - `&otilde;es`
  - `&agrave;`
  - `&ecirc;`

## Validação antes de commit

Antes de subir alterações para o GitHub, rode:

```powershell
python manage.py check
```

Verifique se há resíduos de encoding:

```powershell
Select-String -Path .\templates\praticas\*.html,.\praticas\*.py,.\praticas\management\commands\*.py -Pattern "Ã","Â","â","�" | Select-Object Path,LineNumber,Line
```

O ideal é esse comando não retornar nenhum resultado.

Depois teste localmente:

```powershell
python manage.py runserver
```

E acesse:

```text
http://127.0.0.1:8000/
```

## Próximos passos sugeridos

- Melhorar o design visual da interface pública.
- Adicionar paginação no catálogo.
- Evoluir filtros com melhorias de performance.
- Adicionar autenticação por perfis de usuário.
- Incorporar trilha de auditoria de alterações.
- Criar fluxo de validação/publicação de experiências.
- Preparar integração com base de dados institucional.
- Avaliar migração para PostgreSQL/RDS.
