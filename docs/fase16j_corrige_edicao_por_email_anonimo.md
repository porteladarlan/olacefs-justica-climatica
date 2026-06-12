# Fase 16J — Correção de edição por e-mail validado

## Problema

Após a inclusão do vínculo `Experiencia.autor`, o fluxo de edição legado por e-mail ficou bloqueado para usuários anônimos.

O teste `test_autor_edita_e_reenvia` acessa a edição usando o e-mail validado na URL/campo oculto:

```text
/editar/<id>/?email=autor@example.org
```

A view redirecionava antes de salvar porque a função de permissão retornava `False` para usuário não autenticado, mesmo quando o e-mail informado conferia com `email_contato`.

Resultado observado:

```text
'Boa pratica pendente' != 'Boa pratica ajustada'
```

## Correção

A função `experiencia_pertence_ao_usuario` foi ajustada para aceitar três caminhos válidos:

1. vínculo direto por `Experiencia.autor`;
2. e-mail do usuário autenticado igual ao e-mail de contato;
3. e-mail informado no link/formulário igual ao e-mail de contato, mantendo compatibilidade com envios antigos.

## Validação

Rodar:

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia
python manage.py test praticas.tests_fase16j
python manage.py test
```
