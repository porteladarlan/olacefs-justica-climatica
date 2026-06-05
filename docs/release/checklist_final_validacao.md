# Checklist final de validação da versão

## Código e testes

- [ ] Branch `main` atualizada.
- [ ] GitHub Actions verde.
- [ ] `python manage.py test` executado com sucesso.
- [ ] Sem arquivos pendentes no Git.
- [ ] Dados demonstrativos carregados no ambiente de teste.

## Auditorias

Executar:

```powershell
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
```

Resultado esperado:

- [ ] auditoria trilíngue sem alertas relevantes;
- [ ] auditoria de autenticação/perfis sem alertas;
- [ ] validação ponta a ponta sem alertas;
- [ ] checagem de ambiente sem alertas críticos.

## Páginas públicas

Validar em PT/ES/EN:

- [ ] Home;
- [ ] Catálogo;
- [ ] Ficha da boa prática;
- [ ] Recursos Técnicos;
- [ ] Normas Internacionais;
- [ ] Sobre;
- [ ] Login;
- [ ] Cadastro.

## Fluxos principais

- [ ] Anônimo é redirecionado ao tentar enviar boa prática.
- [ ] Usuário autenticado acessa formulário.
- [ ] Usuário acessa Meus Envios.
- [ ] Usuário comum não acessa painel de revisão.
- [ ] Staff/revisor acessa painel de revisão.
- [ ] Catálogo público carrega em PT/ES/EN.
