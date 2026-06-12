# Fase 16K — Remoção de `contato_referencia` do formulário público

## Objetivo

Corrigir as falhas do GitHub Actions em `tests_fase15e`, causadas pela permanência do campo legado `contato_referencia` no formulário público de envio de boa prática.

A Fase 16K definiu que a tela pública deve manter apenas **E-mail**, eliminando a ideia de “contato” do formulário e da visualização pública.

## O que o script faz

- Localiza a classe principal de formulário em `praticas/forms.py`.
- Substitui ou adiciona o método `__init__`.
- Remove `contato_referencia` de `self.fields`.
- Padroniza `email_contato` como:
  - label: `E-mail`
  - help text: `Provide the institutional e-mail to track the submission and receive review guidance.`
- Ajusta `praticas/tests_fase15e.py` para validar que o campo legado não aparece mais.

## Como aplicar

Na raiz do projeto:

```powershell
python scripts/corrigir_fase16k_remove_contato_referencia_form.py
```

## Como validar

```powershell
python manage.py check
python manage.py test praticas.tests_fase15e
python manage.py test
```

## Commit

```powershell
git add praticas/forms.py
git add praticas/tests_fase15e.py
git add scripts/corrigir_fase16k_remove_contato_referencia_form.py
git add docs/fase16k_remove_contato_referencia_form.md

git commit -m "Remove contato referencia do formulario publico"
git push
```
