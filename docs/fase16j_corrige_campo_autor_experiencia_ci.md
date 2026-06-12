# Fase 16J — Correção do campo autor ausente no CI

## Problema

No GitHub Actions, os testes falharam com:

```text
Cannot resolve keyword 'autor' into field
```

Isso indica que `praticas/views.py` já estava usando `Experiencia.objects.filter(autor=...)`, mas o campo `autor` não estava presente no model `Experiencia` no código enviado ao GitHub.

## Correção

Este pacote adiciona de forma segura:

```python
Experiencia.autor
```

com:

```python
related_name="boas_praticas_enviadas"
```

Também remove, caso exista, o campo `autor` indevido em `BancoTecnico`.

## Como aplicar

Na raiz do projeto:

```powershell
python scripts/corrigir_fase16j_campo_autor_experiencia_ci.py
```

Depois validar:

```powershell
python manage.py makemigrations --check
python manage.py migrate
python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email
python manage.py test praticas.tests_fase16j
python manage.py test
```

## Commit

```powershell
git add praticas/models.py
git add praticas/migrations/
git add scripts/corrigir_fase16j_campo_autor_experiencia_ci.py
git add docs/fase16j_corrige_campo_autor_experiencia_ci.md
git commit -m "Corrige campo autor de Experiencia no CI"
git push
```
