# Fase 16C — Revisão sênior, README e segurança

Esta fase consolida uma revisão sênior do projeto antes do envio ampliado para teste externo.

## Arquivos alterados

- `README.md`
- `config/settings.py`
- `praticas/views.py`

## Arquivos adicionados

- `docs/release/auditoria_senior_codigo_seguranca.md`
- `docs/ambiente/checklist_hardening_producao.md`
- `docs/release/limpeza_artefatos_recomendados.md`
- `docs/fase16c_revisao_senior_readme_seguranca.md`
- `praticas/tests_fase16c.py`

## Ajustes principais

- README atualizado para refletir a versão de validação, não mais uma descrição local antiga.
- Documentação de auditoria sênior e segurança.
- Checklist de hardening para produção futura.
- Recomendação explícita de limpeza de artefatos indevidos.
- Headers/configurações defensivas adicionais em `settings.py`.
- `alternar_favorito` passa a exigir POST.

## Validação

```powershell
python manage.py test praticas.tests_fase16c
python manage.py test
```
