# Correção Fase 15I — testes finais de revisão

Ajusta dois pontos identificados nos testes locais:

- Corrige a URL do teste da tela de revisão de submissão em inglês de `/en/revisao/<id>/` para `/en/painel-revisao/<id>/`, que é a rota real do projeto.
- Corrige o teste legado do painel de revisão para aceitar o título da submissão conforme o idioma ativo da página, mantendo a validação do e-mail do autor/contato e do ano.

Não altera regra de negócio.
