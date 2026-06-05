# Correção Fase 15L — testes sem namespace

Esta correção ajusta `praticas/tests_fase15l.py`.

## Problema

Os testes usavam:

```python
reverse("praticas:pagina_inicial")
```

mas o projeto não registra o namespace `praticas`.

## Correção

Os testes passam a acessar diretamente:

```python
self.client.get("/")
```

Isso mantém a validação de usabilidade/acessibilidade sem depender de namespace inexistente.
