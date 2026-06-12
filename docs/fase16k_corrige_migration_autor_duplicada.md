# Fase 16K — Correção de migration duplicada do campo autor

## Problema

O teste falhou ao criar o banco de teste com:

```text
sqlite3.OperationalError: duplicate column name: autor_id
```

Isso ocorre quando duas migrations diferentes tentam criar a mesma coluna:

```text
praticas_experiencia.autor_id
```

Ou seja: o campo `Experiencia.autor` já existia em uma migration anterior, mas a Fase 16K criou outra migration adicionando o mesmo campo.

## Correção

O script deste pacote:

1. localiza todas as migrations que adicionam `Experiencia.autor`;
2. mantém a migration mais antiga;
3. remove as migrations duplicadas posteriores;
4. salva backup das duplicadas em `praticas/migrations/_backup_migrations_autor_duplicadas`;
5. ajusta o script da Fase 16K para não recriar a migration de autor se ele for executado novamente.

## Como aplicar

Na raiz do projeto:

```powershell
python scripts/corrigir_fase16k_migration_autor_duplicada.py
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
git add praticas/migrations/
git add scripts/aplicar_fase16k_ajustes_12_06.py
git add scripts/corrigir_fase16k_migration_autor_duplicada.py
git add docs/fase16k_corrige_migration_autor_duplicada.md

git commit -m "Remove migration duplicada do autor de Experiencia"
git push
```

Não faça commit da pasta de backup `_backup_migrations_autor_duplicadas`.
