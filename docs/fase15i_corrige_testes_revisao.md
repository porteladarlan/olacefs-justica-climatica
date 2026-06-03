# Correção Fase 15I — testes e painel de revisão

Corrige dois pontos encontrados nos testes da Fase 15I:

1. O teste `tests_fase15i.py` tentava criar `PropostaEdicaoExperiencia` usando o argumento `titulo`, mas esse model armazena alterações propostas em `dados_json`.
2. O teste legado do painel de revisão esperava visualizar o e-mail do autor/contato. O card do painel volta a exibir esse dado, mantendo tradução PT/ES/EN.

Arquivos alterados:
- `praticas/tests_fase15i.py`
- `templates/praticas/painel_revisao.html`
