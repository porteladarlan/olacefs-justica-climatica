# Fase 16B — Validação pública do ambiente Render

Esta fase adiciona uma auditoria para impedir regressão de termos antigos na versão pública hospedada no Render.

## Contexto

Durante a revisão do ambiente público, a plataforma foi conferida em:

- Home;
- Catálogo;
- Recursos Técnicos;
- Normas Internacionais;
- Sobre;
- Cadastro;
- Login;
- versões EN/ES.

A versão pública atual não deve exibir termos como:

- `MVP local`;
- `Marcadores de logo`;
- `Marcadores de logo para o MVP`;
- `Ambiente de demonstração`.

## Arquivos adicionados

- `praticas/management/commands/auditar_render_publico.py`
- `praticas/tests_fase16b.py`
- `docs/render/fase16b_validacao_render_publico.md`

## Como validar localmente

```powershell
python manage.py test praticas.tests_fase16b
python manage.py test
```

## Como validar a URL pública do Render

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```

Para fazer a auditoria falhar se encontrar alerta:

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/ --falhar
```

## Observação

O comando usa a URL pública real e deve ser executado localmente antes de enviar o link às pessoas testadoras. Os testes automatizados não dependem da internet; eles validam apenas as páginas renderizadas localmente.
