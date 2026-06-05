# Checklist técnico para ambiente de teste e produção futura

## Objetivo

Este checklist consolida os pontos mínimos para evolução da plataforma de um ambiente gratuito/de teste para um ambiente institucional mais robusto.

## 1. Código e versionamento

- [ ] Branch `main` atualizada.
- [ ] GitHub Actions verde.
- [ ] `python manage.py test` passando.
- [ ] Migrações aplicadas.
- [ ] Dependências registradas em `requirements.txt`.
- [ ] Variáveis sensíveis fora do código.
- [ ] Documentação de deploy atualizada.

## 2. Variáveis de ambiente

Obrigatórias ou recomendadas:

- [ ] `SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS`
- [ ] `CSRF_TRUSTED_ORIGINS`
- [ ] `DATABASE_URL` ou configuração equivalente
- [ ] `STATIC_ROOT`
- [ ] `MEDIA_ROOT` ou configuração de storage externo
- [ ] credenciais de e-mail, se houver envio de mensagens
- [ ] variáveis de storage de anexos, se houver uso de S3, Azure Blob, GCS ou equivalente

## 3. Banco de dados

Para ambiente gratuito/teste:

- [ ] validar se o banco é persistente;
- [ ] evitar depender de SQLite efêmero;
- [ ] documentar como recriar dados demonstrativos.

Para produção futura:

- [ ] usar banco persistente;
- [ ] preferencialmente PostgreSQL;
- [ ] definir política de backup;
- [ ] definir rotina de restore;
- [ ] proteger acesso ao banco;
- [ ] controlar permissões administrativas;
- [ ] monitorar tamanho e performance.

## 4. Arquivos e anexos

- [ ] definir onde anexos serão armazenados;
- [ ] evitar armazenamento local efêmero;
- [ ] configurar limite de tamanho;
- [ ] validar tipos permitidos;
- [ ] definir política de retenção;
- [ ] documentar backup dos arquivos;
- [ ] revisar permissões de download público.

## 5. Segurança

- [ ] `DEBUG=False`;
- [ ] `SECRET_KEY` segura e fora do Git;
- [ ] HTTPS ativo;
- [ ] `ALLOWED_HOSTS` restrito;
- [ ] CSRF configurado;
- [ ] cookies seguros em produção;
- [ ] revisar permissões de staff/admin;
- [ ] revisar criação de usuários;
- [ ] revisar upload de arquivos;
- [ ] revisar exposição de dados pessoais e contatos;
- [ ] registrar política de revisão/publicação.

## 6. Operação e manutenção

- [ ] definir responsável técnico;
- [ ] definir responsável editorial;
- [ ] definir periodicidade de backup;
- [ ] definir processo de atualização;
- [ ] definir monitoramento básico;
- [ ] definir canal para reporte de erro;
- [ ] definir rotina de atualização de normas, recursos técnicos e boas práticas.

## 7. Deploy e infraestrutura

Ambiente atual/free:

- [ ] validar limitações de sono/inatividade;
- [ ] validar persistência do banco;
- [ ] validar persistência de arquivos;
- [ ] validar tempo de inicialização;
- [ ] validar logs disponíveis;
- [ ] validar domínio temporário.

Produção futura:

- [ ] definir provedor institucional;
- [ ] definir domínio oficial;
- [ ] definir banco persistente;
- [ ] definir storage de anexos;
- [ ] definir backup;
- [ ] definir monitoramento;
- [ ] definir logs;
- [ ] definir processo de rollback;
- [ ] definir política de atualização.

## 8. Critérios mínimos para ir a teste externo

- [ ] GitHub Actions verde.
- [ ] Auditoria trilíngue sem alertas.
- [ ] Auditoria de autenticação/perfis sem alertas.
- [ ] Validação ponta a ponta sem alertas.
- [ ] Dados demonstrativos carregados.
- [ ] Roteiro de teste externo disponível.
- [ ] Usuários de teste preparados.
- [ ] Limitações do ambiente comunicadas.

## 9. Critérios mínimos para produção real

- [ ] ambiente institucional definido;
- [ ] banco persistente configurado;
- [ ] storage persistente para anexos;
- [ ] backups testados;
- [ ] domínio oficial configurado;
- [ ] HTTPS configurado;
- [ ] política de usuários/perfis validada;
- [ ] governança editorial formalizada;
- [ ] termo de uso/política de privacidade avaliados, se aplicável;
- [ ] processo de suporte e manutenção definido.
