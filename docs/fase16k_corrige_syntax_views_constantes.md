# Fase 16K — Corrige SyntaxError em views.py

## Problema

O erro atual é:

```text
SyntaxError: invalid syntax
praticas/views.py, line 27
ANEXO_LIMITE_POR_EXPERIENCIA = 5
```

Isso indica que as constantes de anexos foram inseridas dentro de um bloco de importação multilinha, provavelmente dentro de `from .models import (...)` ou outro import com parênteses.

## Correção

O script remove o bloco de constantes mal posicionado e reinsere as constantes logo após o fim real dos imports, no escopo global do arquivo.

Também atualiza o teste antigo de tradução que ainda esperava `SAI reference contact`, pois o requisito da Fase 16K é manter apenas **E-mail**.

## Aplicar

```powershell
python scripts/corrigir_fase16k_syntax_views_constantes.py
```

## Validar

```powershell
python manage.py check
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_invalido_nao_e_aceito_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_anexo_pdf_valido_e_salvo_no_envio
python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia
python manage.py test praticas.tests_fase15e
python manage.py test
```
