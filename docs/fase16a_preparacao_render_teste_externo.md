# Fase 16A — Preparação Render/teste externo

Esta fase organiza a preparação prática do ambiente Render/teste externo após a consolidação da versão de validação.

## Arquivos adicionados

- `docs/render/checklist_render_teste_externo.md`
- `docs/render/comandos_pos_deploy.md`
- `docs/render/usuarios_teste.md`
- `docs/teste_externo/mensagem_envio_link_teste.md`
- `docs/fase16a_preparacao_render_teste_externo.md`
- `praticas/management/commands/preparar_checklist_render.py`
- `praticas/tests_fase16a.py`

## Objetivo

Apoiar a equipe a:

- validar a branch/tag que será disponibilizada;
- preparar deploy no Render;
- rodar comandos pós-deploy;
- carregar dados demonstrativos;
- criar usuários de teste;
- validar URL pública;
- comunicar limitações do ambiente;
- enviar link para pessoas testadoras.

## Comando

```powershell
python manage.py preparar_checklist_render
```

## Testes

```powershell
python manage.py test praticas.tests_fase16a
python manage.py test
```
