# Fase 15I — Pacote para corrigir GitHub Actions

Este pacote consolida novamente os arquivos da Fase 15I porque a PR apresentou falhas nos checks do GitHub Actions.

## Falhas observadas no GitHub Actions

- `painel_revisao.html` ainda renderizava rótulos de status em português na página `/en/painel-revisao/`.
- `painel_revisao_edicoes.html` ainda renderizava título e textos em português na página `/en/painel-revisao-edicoes/`.
- `revisar_experiencia.html` ainda renderizava textos internos em português na página `/en/painel-revisao/<id>/`.

## Arquivos incluídos

- `praticas/forms.py`
- `praticas/tests.py`
- `praticas/tests_fase15i.py`
- `templates/praticas/painel_revisao.html`
- `templates/praticas/revisar_experiencia.html`
- `templates/praticas/painel_revisao_edicoes.html`
- `templates/praticas/revisar_edicao_publicada.html`
- `.github/workflows/django-tests.yml`

## Verificação sugerida antes do commit

```powershell
Select-String -Path templates/praticas/painel_revisao.html -Pattern "Review published content edits"
Select-String -Path templates/praticas/revisar_experiencia.html -Pattern "Save review decision"
Select-String -Path templates/praticas/painel_revisao_edicoes.html -Pattern "Edit proposals"
```

## Testes

```powershell
python manage.py test praticas.tests_fase15i
python manage.py test
```
