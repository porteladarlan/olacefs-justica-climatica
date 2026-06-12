# Fase 16I — Exclusão administrativa de boas práticas

## Objetivo

Adicionar uma função para que usuários staff/admin possam excluir boas práticas cadastradas na plataforma, especialmente registros de teste criados durante a validação.

## Escopo implementado

- Nova rota restrita: `/excluir-boa-pratica/<id>/`.
- Acesso permitido somente a usuários `is_staff=True`.
- Tela de confirmação antes da exclusão.
- Exclusão somente por POST com CSRF.
- Remoção de anexos vinculados quando houver arquivo salvo.
- Botão de exclusão no catálogo, visível apenas para staff/admin.
- Botão de exclusão na ficha detalhada, visível apenas para staff/admin.
- Botão de exclusão no painel de revisão.
- Testes automatizados da permissão, tela de confirmação, exclusão e botão no catálogo.

## Segurança

A exclusão não fica disponível para usuários comuns. A rota usa `staff_member_required`, exige confirmação via POST e valida destino de redirecionamento para evitar redirect externo indevido.

## Atenção

A exclusão é permanente pela interface da plataforma. Em produção institucional, recomenda-se avaliar uma política de arquivamento lógico antes de adotar exclusão física definitiva.
