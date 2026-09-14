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
- [ ] Usuário consegue publicar diretamente.
- [ ] Confirmação de envio é exibida.

## 5. Meus envios e edição pelo autor

- [ ] Usuário visualiza somente conteúdos ligados à própria conta autenticada.
- [ ] Rascunhos, publicados e arquivados aparecem em “Meus envios”.
- [ ] Estados legados aparecem apenas como “Registro histórico”.
- [ ] Comentários de revisão e solicitações antigas de edição não aparecem.
- [ ] Autor consegue editar o próprio rascunho e publicar diretamente.
- [ ] Autor consegue arquivar e recuperar boa prática própria sem exclusão física.

## 6. Gerenciamento de submissões

- [ ] Gerenciamento global exige usuário staff.
- [ ] Painel exibe somente os indicadores Publicado e Arquivado.
- [ ] Busca geral encontra boas práticas e ferramentas por nome, país, EFS, e-mail e responsável.
- [ ] Boas práticas e ferramentas usam cartões consistentes.
- [ ] Staff consegue editar, arquivar e recuperar conteúdos sem exclusão física.
- [ ] Não existem ações operacionais de revisão, aprovação, devolução ou rejeição.
- [ ] Experiência publicada aparece no catálogo.

## 7. Edição e compatibilidade histórica

- [ ] Autor consegue editar boa prática publicada própria e a alteração é refletida diretamente.
- [ ] Usuário comum edita ferramenta própria somente enquanto rascunho; staff gerencia os demais estados.
- [ ] A rota antiga de status redireciona conforme o perfil autenticado.
- [ ] A rota antiga de edições publicadas redireciona para o gerenciamento consolidado.
- [ ] Solicitações antigas continuam preservadas no banco sem serem exibidas.

## 8. Anexos

- [ ] Aceita PDF.
- [ ] Aceita JPG e PNG.
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
