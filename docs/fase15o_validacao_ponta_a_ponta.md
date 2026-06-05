# Fase 15O — Validação funcional ponta a ponta

Esta fase adiciona uma validação automatizada do fluxo funcional principal da plataforma.

## Arquivos incluídos

- `praticas/management/commands/validar_fluxo_ponta_a_ponta.py`
- `praticas/tests_fase15o.py`
- `docs/fase15o_validacao_ponta_a_ponta.md`

## O que o comando valida

1. Consulta pública:
   - Home;
   - Catálogo;
   - Recursos técnicos;
   - Normas internacionais;
   - Sobre.

2. Fluxo de autor:
   - usuário anônimo é bloqueado/redirecionado em envio e meus envios;
   - usuário autenticado acessa envio e meus envios.

3. Fluxo de revisão:
   - usuário comum não acessa painel de revisão;
   - staff/revisor acessa painel de revisão e painel de edições publicadas.

4. Catálogo:
   - valida se a página pública do catálogo carrega em PT/ES/EN;
   - informa quantas experiências publicadas existem na base atual.

## Como rodar

```powershell
python manage.py validar_fluxo_ponta_a_ponta
python manage.py test praticas.tests_fase15o
python manage.py test
```

## Para falhar se encontrar alertas

```powershell
python manage.py validar_fluxo_ponta_a_ponta --falhar
```

## Observação

Se não houver dados demonstrativos carregados localmente, o comando não falha automaticamente. Para carregar exemplos de apresentação, rode:

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```
