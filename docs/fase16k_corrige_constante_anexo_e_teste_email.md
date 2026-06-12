# Fase 16K — Correção da constante global de anexos e teste de e-mail

## Problemas corrigidos

1. `NameError: ANEXO_LIMITE_POR_EXPERIENCIA is not defined`

Embora o texto da constante existisse no arquivo, ela não estava disponível no escopo global usado por `obter_anexos_do_request`. O script remove qualquer bloco anterior e reinsere as constantes logo após os imports de `praticas/views.py`.

2. Teste antigo ainda esperando `SAI reference contact`

Após o ajuste de 12.06.2026, o requisito passou a ser manter apenas **E-mail** e eliminar “contato”. O teste foi atualizado para validar `E-mail` e garantir que `SAI reference contact` não apareça mais.

## Aplicar

```powershell
python scripts/corrigir_fase16k_constante_anexo_e_teste_email.py
```

## Validar

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia
python manage.py test praticas.tests_fase15e
python manage.py test
```
