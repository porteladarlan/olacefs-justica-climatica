# Checklist para teste externo

## Checklist da equipe interna

Antes de convidar pessoas externas, confirmar:

- [ ] PRs das fases anteriores foram mergeadas na `main`.
- [ ] GitHub Actions está verde.
- [ ] `python manage.py test` passa localmente.
- [ ] Dados demonstrativos foram carregados no ambiente de teste.
- [ ] O ambiente Render está atualizado.
- [ ] Home, catálogo, ficha, formulário e revisão carregam sem erro.
- [ ] PT/ES/EN estão funcionando.
- [ ] Login/cadastro funcionam.
- [ ] Usuário comum não acessa painel de revisão.
- [ ] Staff/revisor acessa painel de revisão.
- [ ] Existe orientação clara para as pessoas testadoras.

## Comandos recomendados antes do teste

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py carregar_dados_ficticios --limpar-demo
```

## Checklist da pessoa testadora

### Página inicial

- [ ] Entendi o objetivo da plataforma.
- [ ] Entendi a relação entre justiça climática e auditoria.
- [ ] Entendi que a plataforma demonstra experiências e a Guia orienta.
- [ ] A navegação principal está clara.

### Catálogo

- [ ] Consegui acessar o catálogo.
- [ ] Consegui usar busca/filtros.
- [ ] Entendi os cards de boas práticas.
- [ ] Consegui abrir a ficha completa.
- [ ] A ficha tem informações suficientes.

### Ficha da boa prática

- [ ] O vínculo com justiça climática está claro.
- [ ] O problema climático está claro.
- [ ] Os riscos climáticos estão claros.
- [ ] As metodologias e instrumentos estão claros.
- [ ] Resultados e replicabilidade estão claros.
- [ ] Contato e anexos estão fáceis de encontrar.

### Envio de boa prática

- [ ] Entendi por que preciso fazer login.
- [ ] O formulário é claro.
- [ ] Os campos obrigatórios estão compreensíveis.
- [ ] Os textos de ajuda ajudam no preenchimento.
- [ ] Entendi a diferença entre rascunho e envio para revisão.
- [ ] Entendi que a publicação não é automática.

### Idiomas

- [ ] A versão em português está clara.
- [ ] A versão em espanhol está clara.
- [ ] A versão em inglês está clara.
- [ ] Não encontrei textos misturados entre idiomas.
- [ ] Os termos técnicos são consistentes.

### Celular

- [ ] Menu funciona em tela pequena.
- [ ] Filtros são usáveis.
- [ ] Formulário é preenchível.
- [ ] Botões são fáceis de tocar.
- [ ] Os textos são legíveis.

## Resultado final

- [ ] A plataforma está pronta para nova rodada de validação.
- [ ] A plataforma precisa de ajustes pequenos.
- [ ] A plataforma precisa de ajustes estruturais antes de nova validação.
