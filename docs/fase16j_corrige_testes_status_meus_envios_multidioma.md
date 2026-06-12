# Fase 16J — Correção dos testes de status e meus envios para ambiente multilíngue

## Problema

Os testes estavam validando um texto fixo em um único idioma, mas a aplicação pode renderizar as rotas em inglês dependendo do idioma ativo no contexto de teste.

Falhas observadas:

```text
test_consulta_status_por_email
test_meus_envios_logado_retorna_envios_do_email
```

Em ambos os casos a funcionalidade estava correta: a boa prática aparecia na página. A diferença era apenas o idioma exibido:

- PT-BR: `Boa pratica pendente`
- EN: `Pending good practice`

## Correção

Os testes passam a aceitar os dois textos, validando a presença da boa prática independentemente do idioma ativo.

## Validação

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_consulta_status_por_email
python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email
python manage.py test praticas.tests_fase16j
python manage.py test
```
