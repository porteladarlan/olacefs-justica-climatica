# Fase 16D — Polimento editorial da Home para apresentação

Esta fase aplica um ajuste pequeno e focado na Home antes do envio do link para teste externo.

## Ajustes realizados

- Remove textos com aparência de conteúdo incompleto, como `Link pendente`, `Link pending` e `Link pendiente`.
- Substitui esses textos por indicação institucional de curadoria técnica.
- Corrige a linha de ODS na Home em português para `ODS 13, 16 e 17`.
- Mantém a versão em espanhol como `ODS 13, 16 y 17`.
- Mantém a versão em inglês como `SDGs 13, 16 and 17`.
- Padroniza `LGBTQIAPN+` para `LGBTQI+`, conforme a taxonomia consolidada usada na plataforma.
- Adiciona testes para evitar regressão desses textos na Home.

## Arquivos alterados

- `templates/praticas/pagina_inicial.html`
- `praticas/tests_fase16d.py`
- `docs/render/fase16d_polimento_home_apresentacao.md`

## Validação

```powershell
python manage.py test praticas.tests_fase16d
python manage.py test
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```

## Observação

Esta fase não altera model, migration, view ou regra de negócio. O foco é apenas remover sinais de conteúdo incompleto antes de apresentação e teste externo.
