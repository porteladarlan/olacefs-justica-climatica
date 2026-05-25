# Correção — Rodapé com logo sem erro de manifest

Corrige o erro de testes:

`Missing staticfiles manifest entry for 'praticas/img/barra-logos-comtema-cgid.png'`

A imagem continua no rodapé, mas o template deixa de resolver o arquivo via tag `{% static %}` durante a renderização dos testes. O caminho usado passa a ser:

`/static/praticas/img/barra-logos-comtema-cgid.png`

Em produção, o Render continuará servindo o arquivo após `collectstatic`.
