# Fase 16J — Correção de conflito de related_name

## Problema

Ao rodar `python manage.py migrate`, o Django identificou conflito entre os campos:

- `praticas.Experiencia.autor`
- `praticas.BancoTecnico.autor`

Ambos usavam o mesmo `related_name`:

```python
related_name="experiencias_enviadas"
```

Isso gerava erro `fields.E304` e `fields.E305`, porque o Django tentava criar o mesmo accessor reverso em `User`.

## Correção aplicada

O campo `Experiencia.autor` passa a usar:

```python
related_name="boas_praticas_enviadas"
```

O campo `BancoTecnico.autor` permanece com o comportamento anterior.

## Validação

Rodar:

```powershell
python manage.py migrate
python manage.py test praticas.tests_fase16j
python manage.py test
```
