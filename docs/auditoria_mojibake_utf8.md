# Auditoria de mojibake / erro de codificação UTF-8

## Objetivo

Localizar textos quebrados do tipo:

```text
prática
revisão
até
descrição
```

Esses erros normalmente aparecem quando um texto UTF-8 foi interpretado como Latin-1/Windows-1252.

## Como usar

Na raiz do projeto:

```powershell
python scripts/auditar_mojibake_utf8.py
```

Esse comando só lista os arquivos e linhas suspeitas.

## Correção automática segura

Depois de revisar a lista, rode:

```powershell
python scripts/auditar_mojibake_utf8.py --corrigir
```

A correção automática só substitui padrões explícitos e seguros, como:

- `prática` → `prática`
- `revisão` → `revisão`
- `descrição` → `descrição`
- `publicação` → `publicação`

## Validar depois

```powershell
python manage.py check
python manage.py test
```

## Commit

```powershell
git add .
git commit -m "Corrige textos com erro de codificacao"
git push
```

## Observação

Nem todo alerta precisa ser corrigido automaticamente. O script mostra linhas suspeitas para revisão antes do commit.
