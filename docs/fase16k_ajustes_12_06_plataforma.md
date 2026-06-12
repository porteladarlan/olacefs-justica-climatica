# Fase 16K — Ajustes Plataforma JC 12.06.2026

## Base dos ajustes

Pacote criado a partir da lista de ajustes de 12.06.2026:

- manter apenas **E-mail** e eliminar “contato” no envio e na visualização final;
- adicionar possibilidade de o **revisor editar** a boa prática;
- garantir que o **rascunho salvo** fique disponível para edição posterior pelo usuário;
- garantir que as boas práticas fiquem disponíveis no **painel de revisão** até aprovação;
- garantir que, após aprovação, as boas práticas sejam incorporadas à versão aberta da plataforma.

## Como aplicar

Na raiz do projeto:

```powershell
python scripts/aplicar_fase16k_ajustes_12_06.py
```

Depois:

```powershell
python manage.py makemigrations --check
python manage.py migrate
python manage.py test praticas.tests_fase16k
python manage.py test
```

## Commit sugerido

```powershell
git add praticas/models.py
git add praticas/migrations/
git add praticas/forms.py
git add praticas/views.py
git add praticas/tests_fase16k.py
git add templates/praticas/
git add scripts/aplicar_fase16k_ajustes_12_06.py
git add docs/fase16k_ajustes_12_06_plataforma.md

git commit -m "Aplica ajustes da plataforma de 12-06"
git push
```
