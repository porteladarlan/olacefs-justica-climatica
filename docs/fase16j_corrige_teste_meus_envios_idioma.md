# Fase 16J — Correção do teste de Meus envios por idioma

## Problema

O teste `test_meus_envios_logado_retorna_envios_do_email` estava esperando o texto em inglês:

```text
Pending good practice
```

Mas a página `/meus-envios/` roda no idioma padrão da aplicação, `pt-br`, e renderiza o título em português:

```text
Boa pratica pendente
```

A funcionalidade estava correta: a boa prática aparecia em “Meus envios”. O erro estava na expectativa textual do teste.

## Correção

O teste foi ajustado para procurar o texto exibido na rota PT-BR:

```python
self.assertContains(response, "Boa pratica pendente")
```

## Validação

```powershell
python manage.py test praticas.tests.RotasPublicasTests.test_meus_envios_logado_retorna_envios_do_email
python manage.py test praticas.tests_fase16j
python manage.py test
```
