# Correção Fase 16B — timeout na Home do Render

Durante a auditoria pública, as páginas internas carregaram corretamente, mas a Home (`/`) retornou timeout na primeira tentativa.

Isso é compatível com ambiente gratuito do Render, que pode demorar na primeira requisição por cold start.

## Ajuste realizado

O comando `auditar_render_publico` passa a ter:

- aquecimento inicial do serviço;
- `--timeout`, com padrão de 45 segundos;
- `--tentativas`, com padrão de 3 tentativas;
- intervalo curto entre tentativas.

## Como rodar

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```

Se ainda houver timeout:

```powershell
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/ --timeout 90 --tentativas 5
```

## Observação

Se apenas a primeira requisição falhar e as demais páginas carregarem, o problema tende a ser cold start/latência do ambiente gratuito, não erro funcional da plataforma.
