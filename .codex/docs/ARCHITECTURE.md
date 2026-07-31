# Arquitetura

## Diretriz

Preservar o monólito Django modular existente. Não converter para microsserviços, SPA ou reescrever o projeto sem necessidade comprovada e ADR.

## Fluxo recomendado

```text
Navegador -> Nginx -> Gunicorn/Django -> Views/Forms/Services -> ORM -> PostgreSQL
```

Ajustar ao estado real.

## Responsabilidades

- models: integridade e domínio próximo ao dado;
- forms: entrada e validação;
- views: HTTP, autorização e orquestração;
- services: fluxos complexos/transações;
- selectors: consultas complexas reutilizáveis;
- templates: apresentação;
- static: comportamento visual;
- admin: curadoria.

## Apps conceituais

Core, contas/EFS, práticas, conhecimento, normas, ferramentas, perguntas, geografia e moderação. Não criar apps apenas para seguir esta lista; mapear primeiro a estrutura atual.

## Banco

- SQLite pode permanecer no desenvolvimento atual;
- PostgreSQL é recomendado para produção;
- migrations versionadas;
- constraints;
- índices orientados a filtros;
- exclusão protegida;
- relações explícitas.

## Arquivos

Separar static/media, validar uploads, evitar nomes físicos fornecidos pelo usuário e coordenar backup de banco/mídia.

## Princípios

Menor mudança suficiente, compatibilidade, migrations graduais, autorização no backend, testes por risco e configuração por ambiente.
