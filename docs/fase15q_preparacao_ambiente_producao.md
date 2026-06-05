# Fase 15Q — Preparação técnica para ambiente de teste e produção futura

Esta fase adiciona documentação e uma checagem técnica para orientar a evolução da plataforma para ambiente de teste robusto e produção futura.

## Arquivos adicionados

- `docs/ambiente/checklist_ambiente_producao.md`
- `docs/ambiente/variaveis_ambiente_recomendadas.md`
- `docs/ambiente/guia_deploy_migracao_futura.md`
- `docs/ambiente/limitacoes_ambiente_gratuito.md`
- `docs/fase15q_preparacao_ambiente_producao.md`
- `praticas/management/commands/checar_prontidao_ambiente.py`
- `praticas/tests_fase15q.py`

## Objetivo

Documentar:

- variáveis de ambiente;
- banco persistente;
- storage de anexos;
- backup;
- domínio;
- segurança;
- logs;
- monitoramento;
- limitações do ambiente gratuito;
- critérios mínimos para teste externo;
- critérios mínimos para produção real.

## Como rodar a checagem

```powershell
python manage.py checar_prontidao_ambiente
```

## Validação

```powershell
python manage.py test praticas.tests_fase15q
python manage.py test
```
