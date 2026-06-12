# Fase 16J — Correção de campo autor indevido em BancoTecnico

## Problema

A correção da Fase 16J adicionou corretamente o campo `autor` em `Experiencia`, mas também deixou um campo `autor` indevido em `BancoTecnico`.

Como a migration `0009_autor_experiencia.py` cria apenas o campo de `Experiencia`, o modelo `BancoTecnico` passou a esperar uma coluna que não existe no banco:

```text
no such column: praticas_bancotecnico.autor_id
```

## Correção

Este pacote remove o campo `BancoTecnico.autor` de `praticas/models.py`.

O vínculo de autoria deve ficar somente em `Experiencia`, pois o problema funcional era:

- boas práticas sumindo de “Meus envios”;
- rascunhos aparecendo indevidamente para revisor;
- falta de vínculo confiável entre boa prática e usuário autor.

`BancoTecnico` não precisa desse campo nesta fase.

## Como aplicar

Na raiz do projeto:

```powershell
python scripts/corrigir_fase16j_bancotecnico_autor.py
```

Depois rode:

```powershell
python manage.py makemigrations --check
python manage.py test praticas.tests_fase16j
python manage.py test
```

Se passar:

```powershell
git add praticas/models.py
git add scripts/corrigir_fase16j_bancotecnico_autor.py
git add docs/fase16j_corrige_bancotecnico_autor_indevido.md
git commit -m "Remove autor indevido de BancoTecnico"
git push -u origin fase16j-revisao-fluxo-submissao-revisao
```
