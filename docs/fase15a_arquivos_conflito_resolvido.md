# Fase 15A — Arquivos com conflitos resolvidos

Pacote preparado para substituir os arquivos que deram conflito na PR:

- `templates/praticas/base.html`
- `templates/praticas/pagina_inicial.html`

Conteúdo mantido:
- menu superior simplificado;
- home trilíngue;
- abas informativas padronizadas;
- correção do erro 500 da página inicial;
- rodapé institucional com imagem oficial;
- sem marcadores de conflito Git.

Depois de substituir, rodar:

```powershell
Select-String -Path templates/praticas/base.html,templates/praticas/pagina_inicial.html -Pattern "<<<<<<<","=======",">>>>>>>"
python manage.py check
python manage.py test
```
