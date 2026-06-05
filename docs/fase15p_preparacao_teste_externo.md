# Fase 15P — Preparação para teste externo

Esta fase prepara materiais de apoio para validação externa da plataforma.

## Arquivos adicionados

- `docs/teste_externo/roteiro_teste_externo.md`
- `docs/teste_externo/checklist_teste_externo.md`
- `docs/teste_externo/perguntas_feedback_teste_externo.md`
- `docs/teste_externo/preparacao_ambiente_teste_externo.md`
- `docs/fase15p_preparacao_teste_externo.md`
- `praticas/management/commands/exibir_roteiro_teste_externo.py`
- `praticas/tests_fase15p.py`

## Objetivo

Permitir que a equipe conduza uma rodada de teste externo com pessoas das EFS, observando:

- clareza institucional;
- navegação;
- catálogo;
- formulário;
- ficha da boa prática;
- recursos técnicos;
- normas internacionais;
- tradução;
- acessibilidade;
- uso em celular;
- fluxo de autenticação e revisão.

## Como consultar pelo terminal

```powershell
python manage.py exibir_roteiro_teste_externo
```

## Validação

```powershell
python manage.py test praticas.tests_fase15p
python manage.py test
```
