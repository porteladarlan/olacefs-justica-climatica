# Fase 15J — Conteúdo institucional, normas e referências

Esta fase ajusta o conteúdo institucional relacionado a recursos técnicos, normas internacionais e referências metodológicas.

## Objetivo

Deixar claro que a plataforma já possui uma área preparada para apoio técnico e normativo, mas que a curadoria final dos materiais será definida em etapa posterior, após a consultoria auditora especializada e o laboratório de justiça climática.

## Arquivos alterados

- `templates/praticas/banco_tecnico.html`
- `templates/praticas/normas_internacionais.html`
- `templates/praticas/sobre_plataforma.html`
- `praticas/tests_fase15j.py`

## Principais ajustes

- Reposiciona Recursos Técnicos como área de apoio técnico e normativo em preparação.
- Evita apresentar materiais provisórios como definitivos.
- Explica que normas e marcos funcionam como metadados e âncoras interpretativas conectadas às boas práticas.
- Reforça que a plataforma não é repositório jurídico separado.
- Reforça a relação: a Guia orienta; a plataforma demonstra.
- Mantém suporte trilíngue PT/ES/EN.

## Validação esperada

Executar:

```powershell
python manage.py test praticas.tests_fase15j
python manage.py test
```
