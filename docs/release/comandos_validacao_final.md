# Comandos finais de validação

## Atualizar base local

```powershell
git checkout main
git pull origin main
git status
```

## Rodar testes

```powershell
python manage.py test
```

## Rodar auditorias

```powershell
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py validar_release_validacao
```

## Conferir materiais de teste externo

```powershell
python manage.py exibir_roteiro_teste_externo
```

## Carregar dados demonstrativos

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

## Rodar comando consolidado

```powershell
python manage.py validar_entrega_final
```

## Resultado esperado

A entrega final deve indicar:

- auditorias concluídas sem alertas relevantes;
- documentos encontrados;
- materiais de teste externo encontrados;
- fluxo público, autor e revisão funcionando;
- 68 ou mais testes passando, conforme a versão atual do projeto.
