# Correção Fase 15A — erro 500 na página inicial

Corrige um `{% endfor %}` solto no template `templates/praticas/pagina_inicial.html`.

Esse fechamento de loop não tinha um `{% for %}` correspondente e causava erro 500 ao abrir `/`.

Arquivos alterados:
- templates/praticas/pagina_inicial.html
