# Roteiro de Testes Manuais — MVP

## Preparação

```powershell
cd C:\Projetos\olacefs-justica-climatica
.\venv\Scripts\Activate.ps1
git status
python manage.py check
python manage.py test
python manage.py runserver
```

Acessar:

```text
http://127.0.0.1:8000/
```

## Fluxo 1 — Navegação pública

1. Abrir página inicial.
2. Abrir catálogo.
3. Aplicar filtros no catálogo.
4. Abrir uma experiência.
5. Abrir normas internacionais.
6. Abrir ferramentas/banco técnico.
7. Trocar idioma para ES.
8. Trocar idioma para EN.
9. Voltar para PT.

## Fluxo 2 — Comparação

1. Abrir catálogo.
2. Marcar até três experiências.
3. Clicar em “Comparar selecionadas”.
4. Confirmar tabela lado a lado.
5. Abrir `/comparar/`.
6. Selecionar experiências pelos cards.
7. Confirmar que não é necessário segurar Ctrl.

## Fluxo 3 — Favoritos

1. Abrir catálogo.
2. Favoritar uma experiência.
3. Favoritar uma segunda experiência.
4. Abrir `/favoritos/`.
5. Remover uma experiência dos favoritos.
6. Comparar favoritas.

## Fluxo 4 — Cadastro e envio

1. Sair do sistema, se estiver autenticado.
2. Acessar `/adicionar-boa-pratica/`.
3. Confirmar redirecionamento para login.
4. Criar conta em `/cadastro/`.
5. Acessar “Meus envios”.
6. Enviar nova boa prática.
7. Salvar como rascunho.
8. Consultar em “Meus envios”.
9. Editar e reenviar.

## Fluxo 5 — Revisão

1. Entrar com superusuário/staff.
2. Acessar `/painel-revisao/`.
3. Abrir envio pendente.
4. Marcar como em revisão.
5. Aprovar.
6. Publicar.
7. Confirmar que aparece no catálogo.

## Fluxo 6 — Edição de publicado

1. Consultar status pelo e-mail do autor.
2. Solicitar edição de experiência publicada.
3. Alterar título ou resultados.
4. Enviar proposta.
5. Entrar como revisor.
6. Abrir `/painel-revisao-edicoes/`.
7. Abrir proposta.
8. Conferir comparação “valor atual x valor proposto”.
9. Aprovar e aplicar.
10. Confirmar alteração no catálogo/ficha.

## Fluxo 7 — Anexos

1. Entrar como usuário autenticado.
2. Enviar boa prática com PDF.
3. Confirmar aceite.
4. Tentar enviar `.exe`.
5. Confirmar bloqueio.
6. Editar envio.
7. Remover anexo existente.
8. Adicionar link externo válido.
9. Tentar link externo inválido.
10. Confirmar erro.

## Critério de aceite final

O MVP pode ser demonstrado quando:

- navegação pública funciona;
- submissão exige cadastro;
- revisão funciona;
- publicação funciona;
- edição publicada exige aprovação;
- comparação funciona;
- favoritos funcionam;
- anexos são validados;
- testes automatizados passam.
