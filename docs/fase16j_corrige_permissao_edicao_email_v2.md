# Fase 16J — Correção de permissão de edição por e-mail v2

## Problema

O teste `test_autor_edita_e_reenvia` ainda falhava porque a função de permissão continuava bloqueando usuário anônimo antes de validar o e-mail informado.

Falha observada:

```text
'Boa pratica pendente' != 'Boa pratica ajustada'
```

Isso indica que a view não salvou o POST de edição.

## Correção

A função `experiencia_pertence_ao_usuario` foi substituída de forma direta, sem depender de regex frágil.

A ordem correta da validação agora é:

1. Se o e-mail informado no link/formulário for igual ao e-mail da experiência, permite.
2. Se não houver usuário autenticado, bloqueia.
3. Se o usuário autenticado for o autor, permite.
4. Se o e-mail do usuário autenticado for igual ao e-mail da experiência, permite.

## Validação

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia
python manage.py test praticas.tests_fase16j
python manage.py test
```
