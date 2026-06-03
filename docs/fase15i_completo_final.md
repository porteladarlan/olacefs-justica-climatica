# Fase 15I — Pacote completo final

Este pacote consolida a Fase 15I com as correções acumuladas.

## Inclui

- Ajustes no fluxo de revisão e aprovação.
- Painel de revisão trilíngue.
- Tela de revisão da experiência reorganizada.
- Painel de edições publicadas.
- Tela de revisão de edição publicada.
- Choices dos formulários de revisão conforme idioma ativo.
- Correções de testes finais da Fase 15I.
- GitHub Actions para execução automática de testes Django.

## Arquivos principais

- `praticas/forms.py`
- `templates/praticas/painel_revisao.html`
- `templates/praticas/revisar_experiencia.html`
- `templates/praticas/painel_revisao_edicoes.html`
- `templates/praticas/revisar_edicao_publicada.html`
- `praticas/tests.py`
- `praticas/tests_fase15i.py`
- `.github/workflows/django-tests.yml`

## Comandos de validação

```powershell
python manage.py test praticas.tests_fase15i
python manage.py test praticas.tests.RotasPublicasTests.test_painel_revisao_staff_retorna_200
python manage.py test
```
