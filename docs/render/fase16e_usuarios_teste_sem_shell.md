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

Como o plano gratuito pode não permitir Shell/SSH, use o Start Command temporariamente.

### 1. Start Command temporário

No serviço do Render, altere temporariamente o Start Command para algo semelhante a:

```bash
python manage.py migrate && python manage.py criar_usuarios_teste --confirmar --resetar-senha && gunicorn config.wsgi:application
```

Depois faça redeploy.

### 2. Confirmar nos logs

Verifique nos logs se apareceu:

```text
OK  admin_teste
OK  revisor_teste
OK  usuario_teste
```

### 3. Reverter Start Command

Depois que os usuários forem criados, volte o Start Command ao padrão do projeto, por exemplo:

```bash
gunicorn config.wsgi:application
```

ou ao comando que já estava configurado no Render.

### 4. Desativar variável de criação

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
