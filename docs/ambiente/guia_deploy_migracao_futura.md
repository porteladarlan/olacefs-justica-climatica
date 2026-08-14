# Guia técnico de deploy e migração futura

## Situação atual

A plataforma pode continuar sendo validada em ambiente gratuito/de teste, desde que as limitações sejam comunicadas:

- possível inatividade automática;
- banco ou arquivos podem não ser persistentes, dependendo da configuração;
- recursos computacionais limitados;
- domínio temporário;
- logs e monitoramento limitados.

## Deploy em ambiente gratuito/teste

Fluxo recomendado:

```powershell
git checkout main
git pull origin main
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
```

Depois, no ambiente hospedado:

```powershell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py carregar_dados_ficticios --limpar-demo
```

## Migração para produção futura

### Etapa 1 — Planejamento

Definir:

- provedor;
- domínio;
- banco;
- storage de arquivos;
- backup;
- responsáveis técnicos;
- responsáveis editoriais;
- política de usuários;
- política de publicação.

### Etapa 2 — Infraestrutura

Configurar:

- aplicação web;
- banco PostgreSQL ou equivalente;
- storage persistente;
- variáveis de ambiente;
- HTTPS;
- logs;
- backup;
- monitoramento.

#### Limites de upload no proxy

`MAX_UPLOAD_SIZE_MB` limita individualmente cada arquivo depois que o upload
multipart chega ao Django. Esse controle valida a regra da aplicação, mas não
protege sozinho o servidor contra um corpo HTTP excessivamente grande.

O reverse proxy escolhido para staging/produção deve limitar o request completo
para um valor compatível com até três anexos multiplicados por
`MAX_UPLOAD_SIZE_MB`, acrescido do overhead do formulário multipart. Se Nginx
for adotado, esse requisito deve ser aplicado por `client_max_body_size` na
configuração da infraestrutura. O valor definitivo depende do limite configurado
no ambiente e não deve ser fixado no código Django.

`DATA_UPLOAD_MAX_MEMORY_SIZE` não substitui esse controle porque o Django calcula
esse limite sem os dados de arquivos presentes em `request.FILES`.
`FILE_UPLOAD_MAX_MEMORY_SIZE` também não limita o request: ele apenas define a
partir de que tamanho o arquivo deixa de permanecer em memória e passa a ser
processado por arquivo temporário. Portanto, o proxy limita o volume HTTP total
antes da aplicação, enquanto `MAX_UPLOAD_SIZE_MB` rejeita cada arquivo que
ultrapasse a regra funcional da plataforma.

### Etapa 3 — Dados

Planejar:

- migração de boas práticas;
- migração de usuários;
- migração de anexos;
- revisão de dados demonstrativos;
- limpeza de dados de teste.

### Etapa 4 — Segurança

Validar:

- `DEBUG=False`;
- `ALLOWED_HOSTS`;
- CSRF;
- permissões;
- uploads;
- usuários staff;
- acesso administrativo;
- exposição pública de contatos.

### Etapa 5 — Entrada em operação

Antes de publicar:

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta --falhar
```

## Rollback

Antes de cada mudança relevante:

- registrar versão/commit;
- confirmar backup do banco;
- confirmar backup de anexos;
- documentar comando ou procedimento de retorno.

## Pós-deploy

Após publicação:

- testar Home;
- testar Catálogo;
- testar ficha;
- testar login;
- testar envio;
- testar revisão;
- testar idiomas;
- testar download/upload de anexos;
- verificar logs.
