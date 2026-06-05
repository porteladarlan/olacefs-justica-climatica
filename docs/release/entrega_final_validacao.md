# Entrega final da versão de validação

## Objetivo

Este documento organiza a entrega final da versão de validação da plataforma após a retroalimentação.

A versão está preparada para:

- demonstração interna;
- reunião executiva;
- teste externo controlado;
- coleta de feedback das EFS;
- planejamento de ambiente de produção futura.

## Estado da versão

A versão consolidada inclui:

- visual público revisado;
- fluxo de envio ajustado;
- fluxo de revisão e aprovação validado;
- recursos técnicos e normas alinhados;
- dados demonstrativos para apresentação;
- usabilidade e acessibilidade refinadas;
- auditoria trilíngue;
- auditoria de autenticação e perfis;
- validação ponta a ponta;
- materiais para teste externo;
- documentação técnica de ambiente;
- consolidação final de release.

## Checklist antes da apresentação

Executar:

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py validar_release_validacao
python manage.py exibir_roteiro_teste_externo
```

Resultado esperado:

- testes passando;
- auditoria trilíngue sem alertas;
- auditoria de autenticação/perfis sem alertas;
- validação ponta a ponta sem alertas;
- checagem de ambiente sem alertas críticos;
- documentos de release encontrados;
- materiais de teste externo encontrados.

## Preparação de dados demonstrativos

Para ambiente de teste/demonstração:

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

## Sugestão de tag Git

Após merge da última PR na `main`, criar uma tag de versão de validação:

```powershell
git checkout main
git pull origin main
python manage.py test
git tag -a v0.15-validacao-retroalimentacao -m "Versao de validacao apos retroalimentacao"
git push origin v0.15-validacao-retroalimentacao
```

## Observação

A tag deve ser criada somente depois que:

- a PR final estiver mergeada;
- o GitHub Actions estiver verde;
- a `main` local estiver atualizada;
- `python manage.py test` passar.
