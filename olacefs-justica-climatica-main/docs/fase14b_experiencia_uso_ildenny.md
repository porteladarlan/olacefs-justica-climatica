# Fase 14B — Experiência de uso e redução de rolagem

## Escopo

Esta fase complementa a Fase 14A e implementa ajustes mais focados na experiência de uso:

- Ficha da experiência organizada em abas:
  - Visão geral
  - Justiça climática
  - Insumos de auditoria
  - Resultados
  - Anexos
- Resumo inicial mais compacto na ficha.
- Metadados em cards menores.
- Status com cores, ícones e textos mais claros:
  - 🟡 Aguardando revisão técnica
  - 🟢 Publicado na plataforma
  - 🔴 Necessita de ajustes / correções
- Legenda de status na página de acompanhamento.
- Mais espaçamento em normas e banco técnico.

## Arquivos alterados

- templates/praticas/base.html
- templates/praticas/detalhe_experiencia.html
- templates/praticas/status_envio.html
- templates/praticas/meus_envios.html
- templates/praticas/banco_tecnico.html
- templates/praticas/normas_internacionais.html

## Testes

```powershell
python manage.py check
python manage.py test
```

Com banco limpo:

```powershell
Remove-Item db.sqlite3 -Force -ErrorAction SilentlyContinue
python manage.py migrate
python manage.py carregar_dados_ficticios
python manage.py check
python manage.py test
```
