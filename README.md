# Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática

MVP local em Django para reunir, organizar e consultar experiências de Entidades Fiscalizadoras Superiores (EFS) relacionadas à justiça climática.

## Objetivo do MVP

Validar fluxo funcional e visual da plataforma com dados fictícios, incluindo:

- catálogo de experiências;
- filtros de consulta;
- páginas públicas institucionais;
- painel administrativo para cadastro e atualização.

A arquitetura foi mantida simples para execução local com SQLite e preparada para futura migração para PostgreSQL/RDS.

## Requisitos

- Python 3.12+
- pip
- virtualenv (recomendado)

## Instalação

```bash
git clone https://github.com/porteladarlan/olacefs-justica-climatica.git
cd olacefs-justica-climatica
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install django
```

## Configuração inicial

```bash
python manage.py makemigrations
python manage.py migrate
```

## Como rodar localmente

```bash
python manage.py runserver
```

Acesse:

- aplicação: http://127.0.0.1:8000/
- admin: http://127.0.0.1:8000/admin/

## Como criar superusuário

```bash
python manage.py createsuperuser
```

## Como carregar dados fictícios

```bash
python manage.py carregar_dados_ficticios
```

O comando popula:

- países;
- EFS;
- tipos de experiência;
- setores;
- dimensões de justiça climática;
- grupos vulneráveis;
- pelo menos 6 experiências publicadas;
- recursos de banco técnico.

## Funcionalidades disponíveis

### Modelagem de dados

- Pais
- EFS
- TipoExperiencia
- Setor
- DimensaoJusticaClimatica
- GrupoVulneravel
- Experiencia
- Anexo
- BancoTecnico

### Páginas públicas

- página inicial;
- catálogo de experiências;
- detalhe de experiência;
- banco técnico;
- sobre a plataforma.

### Filtros do catálogo

- país;
- EFS;
- tipo de experiência;
- setor;
- dimensão de justiça climática;
- grupo vulnerável;
- ano;
- busca por palavra-chave.

### Administração

O Django Admin permite cadastro, edição e consulta de todos os modelos, com filtros e busca para facilitar a operação do MVP.
