# Fase 16F — Retroalimentação do formulário e taxonomias

Esta fase incorpora a revisão recebida no documento de retroalimentação do formulário.

## Itens atendidos

- Inclusão/ampliação da lista de EFS com denominações oficiais usadas pela OLACEFS.
- Inclusão/ampliação da lista de países.
- Inclusão de `Outro` em Setor.
- Inclusão de `Outro`, `Crianças` e `Idosos` em Temas transversais.
- Explicação do campo `Critérios utilizados`, evitando interpretação restrita a normas.
- Diferenciação entre `Metodologia` e `Metodologias, matrizes ou instrumentos utilizados`.
- Inclusão de campo final `Informações adicionais`.

## Nota sobre nomes das EFS

As denominações oficiais das EFS foram mantidas em espanhol/oficial nas três línguas para evitar tradução indevida de nomes institucionais. A tradução multilíngue permanece aplicada aos rótulos da interface, países, setores e temas.

## Comandos recomendados

```bash
python manage.py migrate
python manage.py aplicar_retroalimentacao_formulario
python manage.py test praticas.tests_fase16f
python manage.py test
```

## Observação

A migration já cria os dados principais. O comando `aplicar_retroalimentacao_formulario` serve como reforço operacional para ambiente Render ou ambientes onde seja necessário reexecutar a carga de taxonomias.
