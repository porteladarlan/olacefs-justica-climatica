# Fase 15M — Auditoria trilíngue final

Esta fase começa com uma auditoria automática das páginas renderizadas em inglês e espanhol para identificar possíveis resíduos de português.

## Arquivo incluído

- `praticas/management/commands/auditar_traducoes_trilingues.py`

## Como usar

```powershell
python manage.py auditar_traducoes_trilingues
```

O comando percorre páginas públicas e internas principais em:

- `/en/...`
- `/es/...`

e procura termos portugueses que não deveriam aparecer como labels, botões ou textos institucionais.

## Para falhar quando encontrar alertas

```powershell
python manage.py auditar_traducoes_trilingues --falhar
```

## Observação importante

Nem todo alerta é necessariamente erro. Alguns termos podem vir de:

- dados demonstrativos;
- nomes próprios;
- textos cadastrados por usuário;
- nomes de EFS;
- conteúdo administrativo.

Use o resultado como lista de revisão antes de aplicar correções finais.
