# Fase 16E — Usuários de teste sem Shell do Render

## Objetivo

Criar usuários temporários para apresentação e teste externo controlado mesmo quando o plano do Render não disponibiliza Shell/SSH.

## Usuários criados

| Usuário | Perfil | Finalidade |
|---|---|---|
| `admin_teste` | superusuário | acessar `/admin/` e administrar a base de teste |
| `revisor_teste` | staff/revisor | acessar painéis de revisão e publicação |
| `usuario_teste` | usuário comum | testar envio de boas práticas, rascunhos e meus envios |

## Variáveis de ambiente recomendadas no Render

Defina temporariamente:

```text
PERMITIR_CRIACAO_USUARIOS_TESTE=true
SENHA_USUARIOS_TESTE=<senha forte temporária>
USUARIO_TESTE_ADMIN_EMAIL=<seu e-mail institucional>
USUARIO_TESTE_REVISOR_EMAIL=<e-mail do revisor de teste>
USUARIO_TESTE_COMUM_EMAIL=<e-mail do usuário comum de teste>
```

A variável `SENHA_USUARIOS_TESTE` é opcional, mas recomendada. Se ela não for definida, o comando gera uma senha temporária e mostra nos logs.

## Execução local

```powershell
python manage.py criar_usuarios_teste --confirmar --resetar-senha
```

## Execução no Render sem Shell

Não inclua criação de usuários no Build Command nem no Start Command, mesmo temporariamente. Use somente um mecanismo de execução manual e controlada disponibilizado pelo provedor. Se o ambiente não oferecer esse mecanismo, a criação deve ser coordenada com a operação responsável antes do teste.

### 1. Comando manual

```bash
python manage.py criar_usuarios_teste --confirmar --resetar-senha
```

### 2. Confirmar nos logs

Verifique nos logs se apareceu:

```text
OK  admin_teste
OK  revisor_teste
OK  usuario_teste
```

### 3. Desativar variável de criação

Depois da criação, remova ou altere:

```text
PERMITIR_CRIACAO_USUARIOS_TESTE=false
```

## Acessos para teste

- Login da plataforma: `/entrar/`
- Cadastro público: `/cadastro/`
- Envio de prática: `/adicionar-boa-pratica/`
- Meus envios: `/meus-envios/`
- Painel de revisão: `/painel-revisao/`
- Admin Django: `/admin/`

## Observação de segurança

Esses usuários são apenas para validação controlada. Não devem permanecer ativos com senha compartilhada em ambiente institucional final.

Antes de produção definitiva:

- remover ou desativar usuários temporários;
- usar banco persistente;
- configurar gestão formal de usuários;
- aplicar política de senhas e governança de perfis;
- evitar senha compartilhada entre pessoas.
