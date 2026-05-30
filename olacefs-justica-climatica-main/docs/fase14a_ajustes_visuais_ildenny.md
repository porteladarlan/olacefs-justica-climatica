# Fase 14A — Ajustes visuais globais segundo proposta da Ildenny

## Escopo

Esta fase implementa a primeira rodada visual, sem alterar backend/regra de negócio:

- Poppins como fonte principal.
- Paleta de Justiça Climática:
  - #432054
  - #A999BF
  - #695173
  - #698D8B
  - #A3BFBA
- Menos degradê e mais cores sólidas.
- Mais espaço em branco.
- Rodapé institucional com OLACEFS / COMTEMA / CGID / GIZ.
- Home mais limpa.
- Modal inicial explicando justiça climática e finalidade da plataforma.
- Badges de tipo de boa prática com cores diferentes.
- Formulários com blocos numerados e dicas por ícone de informação.

## Arquivos alterados

- templates/praticas/base.html
- templates/praticas/pagina_inicial.html
- templates/praticas/catalogo_experiencias.html
- templates/praticas/adicionar_boa_pratica.html
- templates/praticas/editar_boa_pratica.html

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
