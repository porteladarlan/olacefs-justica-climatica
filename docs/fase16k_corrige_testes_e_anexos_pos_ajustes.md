# Fase 16K — Correção pós-ajustes: anexos, testes e ficha

Corrige pontos residuais após os ajustes de 12.06.2026:

1. `NameError: ANEXO_LIMITE_POR_EXPERIENCIA is not defined`;
2. testes antigos ainda procurando `contato_referencia`;
3. testes antigos esperando `TCU`, enquanto a interface em inglês mostra `Federal Court of Accounts`;
4. ficha de boa prática sem exibir o ano `2026`.

## Aplicar

```powershell
python scripts/corrigir_fase16k_testes_e_anexos_pos_ajustes.py
```

## Validar

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia
python manage.py test praticas.tests_fase15e
python manage.py test praticas.tests_fase15c
python manage.py test
```
