# Checklist de Homologação do MVP — Plataforma Regional OLACEFS

## Objetivo

Validar se o MVP atende aos requisitos negociais definidos para a Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática.

## 1. Navegação pública

- [ ] Página inicial abre corretamente.
- [ ] Catálogo de boas práticas abre corretamente.
- [ ] Página de normas internacionais abre corretamente.
- [ ] Banco técnico/ferramentas abre corretamente.
- [ ] Página de comparação abre corretamente.
- [ ] Página de favoritos abre corretamente.
- [ ] O menu superior está organizado, sem excesso de abas visíveis.
- [ ] O seletor de idioma PT / ES / EN funciona sem quebrar a navegação.

## 2. Catálogo de experiências

- [ ] Lista apenas experiências publicadas.
- [ ] Exibe EFS, país, tipo, setor e ano.
- [ ] Exibe temas transversais.
- [ ] Exibe normas internacionais relacionadas.
- [ ] Permite busca textual.
- [ ] Permite filtros principais.
- [ ] Permite selecionar experiências para comparação.
- [ ] Limita comparação a até três experiências.
- [ ] Permite favoritar experiências.

## 3. Ficha da experiência

- [ ] Abre a página detalhada da experiência.
- [ ] Mostra resumo da boa prática.
- [ ] Mostra vínculo com justiça climática.
- [ ] Mostra perguntas de auditoria, critérios e ferramentas quando cadastrados.
- [ ] Mostra resultados, recomendações e replicabilidade.
- [ ] Exibe anexos e links externos quando existentes.
- [ ] Permite favoritar/remover dos favoritos.

## 4. Submissão mediante cadastro

- [ ] Usuário não autenticado é redirecionado para login ao tentar enviar boa prática.
- [ ] Página de cadastro funciona.
- [ ] Página de login funciona.
- [ ] Logout funciona.
- [ ] Usuário autenticado acessa “Meus envios”.
- [ ] Formulário de envio vem com nome/e-mail preenchidos quando possível.
- [ ] Usuário consegue salvar rascunho.
- [ ] Usuário consegue enviar para revisão.
- [ ] Confirmação de envio é exibida.

## 5. Status e edição pelo autor

- [ ] Usuário consegue consultar status pelo e-mail.
- [ ] Rascunhos aparecem na consulta.
- [ ] Envios pendentes aparecem na consulta.
- [ ] Comentário do revisor aparece quando existir.
- [ ] Autor consegue editar envio antes da publicação.
- [ ] Autor consegue reenviar para revisão.

## 6. Revisão e publicação

- [ ] Painel de revisão exige usuário staff.
- [ ] Revisor consegue ver envios pendentes.
- [ ] Revisor consegue marcar como em revisão.
- [ ] Revisor consegue aprovar.
- [ ] Revisor consegue publicar.
- [ ] Revisor consegue devolver para ajustes.
- [ ] Revisor consegue rejeitar.
- [ ] Experiência publicada aparece no catálogo.

## 7. Edição de conteúdo publicado

- [ ] Autor consegue solicitar edição de experiência publicada.
- [ ] Versão publicada continua visível enquanto a edição é revisada.
- [ ] Painel de edições publicadas lista propostas pendentes.
- [ ] Tela de revisão mostra comparação “valor atual x valor proposto”.
- [ ] Campos alterados aparecem destacados.
- [ ] Revisor consegue aprovar e aplicar a edição.
- [ ] Revisor consegue rejeitar a edição.
- [ ] Comentário do revisor aparece no acompanhamento.

## 8. Anexos

- [ ] Aceita PDF.
- [ ] Aceita Word.
- [ ] Aceita Excel.
- [ ] Rejeita extensões não permitidas.
- [ ] Limita a até três anexos por experiência.
- [ ] Rejeita arquivo acima do limite definido.
- [ ] Permite link externo válido.
- [ ] Rejeita link externo inválido.
- [ ] Permite remover anexo na edição.

## 9. Acessibilidade e usabilidade

- [ ] Menu funciona em desktop.
- [ ] Menu funciona em mobile.
- [ ] Navegação por teclado funciona.
- [ ] Foco visual é perceptível.
- [ ] Textos possuem contraste adequado.
- [ ] Botões têm nomes claros.
- [ ] Formulários exibem mensagens de erro legíveis.
- [ ] Tabelas de comparação são legíveis em telas menores.

## 10. Testes técnicos

Executar:

```powershell
python manage.py check
python manage.py test
```

Teste com banco limpo:

```powershell
Remove-Item db.sqlite3 -Force -ErrorAction SilentlyContinue
python manage.py migrate
python manage.py carregar_dados_ficticios
python manage.py check
python manage.py test
```

## Resultado esperado

- [ ] Todos os testes automatizados passam.
- [ ] Banco limpo migra sem erro.
- [ ] Dados fictícios carregam sem erro.
- [ ] Fluxos manuais principais foram validados.
