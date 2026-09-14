# Relatório técnico de segurança e transição para TI

**Sistema:** Plataforma Regional de Boas Práticas em Auditoria com Perspectiva de Justiça Climática  
**Data de referência:** 14 de setembro de 2026  
**Escopo avaliado:** código-fonte e artefatos operacionais versionados  
**Referência de produção observada:** `3bdfb22cba9b0f89cbd0998f2671e5c72f486d01`  
**Pacote de hardening:** branch `security/hardening-evidencias-ti`  

## 1. Conclusão executiva

O sistema dispõe de controles de aplicação para autenticação, autorização por objeto, CSRF, validação de uploads, proteção de configuração, cookies, sessão, redirecionamentos e separação entre conteúdo público e interno. O pacote de hardening acrescenta logout por POST com CSRF, tempos explícitos de sessão e redefinição de senha, CSP progressiva, análise estática, auditoria de dependências, actions fixadas por SHA e atualização automatizada de dependências.

Essas medidas não equivalem a certificação formal nem substituem controles de infraestrutura. A entrada em produção institucional continua condicionada à atuação da TI em TLS/HSTS, banco, storage, backup e restauração, centralização de logs, monitoramento, rate limiting distribuído, antimalware, proteção de branch, gestão de incidentes e governança de identidades e dados pessoais.

O pacote não altera models, migrations, conteúdo do banco ou produção. A implantação depende de revisão, CI verde, aprovação e janela controlada.

## 2. Visão do sistema

- aplicação web monolítica em Django 6, com templates renderizados no servidor;
- Python 3.12/3.13, Gunicorn e WhiteNoise;
- PostgreSQL obrigatório em staging/produção e SQLite restrito a desenvolvimento/testes;
- interface pública e autenticada em português, espanhol e inglês;
- catálogos de boas práticas, marcos normativos, ferramentas e recursos técnicos;
- submissão, edição, favoritos e área “Meu Espaço” para usuários autenticados;
- gerenciamento interno e Django Admin restritos a staff;
- anexos PDF, JPG e PNG validados antes da persistência;
- health check e scripts versionados para backup, restauração e monitoramento.

## 3. Ativos, dados e fronteiras de confiança

| Elemento | Conteúdo ou função | Tratamento esperado |
|---|---|---|
| Identidades | usuário, e-mail, senha com hash, estado ativo e confirmação | acesso mínimo, segredo fora do Git e trilha administrativa |
| Conteúdo | boas práticas, ferramentas, marcos, guia e recursos | publicação conforme estado e autorização no backend |
| Dados pessoais | contatos e autoria informados em submissões | minimização, base legal, retenção e atendimento de direitos |
| Anexos | PDF/JPG/PNG enviados por usuários | validação na aplicação, storage durável e antimalware na infraestrutura |
| Banco | identidades, conteúdo, vínculos, favoritos e histórico | PostgreSQL protegido, backup criptografado e restauração testada |
| Segredos | `SECRET_KEY`, banco, SMTP e integrações | cofre/variáveis protegidas, rotação e acesso por função |
| Logs | eventos da aplicação, proxy, sistema e banco | centralização, retenção, alerta e acesso restrito |

As principais fronteiras são navegador–proxy, proxy–aplicação, aplicação–PostgreSQL, aplicação–storage, aplicação–SMTP e operadores–servidor. Controles em somente um lado não são suficientes; proxy, host, banco e storage devem aplicar defesa em profundidade.

## 4. Matriz de controles e evidências

Legenda: **Atendido** = presente no código e testável; **Parcial** = controle iniciado, com complemento necessário; **TI** = depende de infraestrutura ou decisão institucional.

| ID | Controle | Estado | Evidência técnica | Próxima ação |
|---|---|---|---|---|
| APP-01 | Autenticação no backend | Atendido | Django Auth, login, confirmação de e-mail e redefinição de senha | revisar política de cadastro e MFA |
| APP-02 | Autorização por objeto | Atendido | edição e consulta privada vinculadas ao autor ou staff | definir poderes do vínculo usuário–EFS |
| APP-03 | CSRF em ações de estado | Atendido | middleware CSRF; favoritos e logout por POST; formulário com token | manter testes negativos |
| APP-04 | Logout seguro | Atendido | `/sair/` rejeita GET com 405 e aceita POST autenticado | comunicar incompatibilidade com links antigos |
| APP-05 | Sessão | Atendido | cookie HttpOnly/SameSite=Lax, oito horas, renovação por atividade, expiração ao fechar navegador | TI pode reduzir o prazo por variável |
| APP-06 | Redefinição de senha | Atendido | fluxo Django e token com validade padrão de 24 horas | avaliar prazo institucional menor |
| APP-07 | Redirecionamentos | Atendido | destinos pós-login validados como locais e seguros | manter cobertura de regressão |
| APP-08 | Upload | Parcial | limite, quantidade, extensão, MIME declarado e assinatura básica | TI: quarentena, antimalware e storage privado/durável |
| APP-09 | Configuração segura | Atendido | produção falha sem segredo, hosts, CSRF, PostgreSQL e cookies seguros | TI: injetar valores por cofre e testar rotação |
| APP-10 | Headers HTTP | Parcial | nosniff, referrer policy, COOP, X-Frame-Options e CSP defensiva | TI: TLS/HSTS e validação no proxy real |
| APP-11 | CSP | Parcial | bloqueio aplicado a objetos/base/formulários/enquadramento; política estrita em relatório | remover inline e localizar Bootstrap antes de endurecer |
| APP-12 | SAST | Atendido | Bandit no CI bloqueia alta severidade/alta confiança | revisar os dois achados médios B310 conhecidos |
| APP-13 | SCA | Atendido | `pip-audit` no CI e Dependabot semanal | definir SLA para PRs de segurança |
| APP-14 | Cadeia do CI | Atendido | actions por SHA e credencial do checkout desabilitada | TI: proteger `main` e exigir checks/revisão |
| APP-15 | Integridade de dados | Atendido | migrations versionadas, arquivamento lógico e testes de regressão | aplicar migrations só com backup/rollback |
| INF-01 | TLS, domínio e HSTS | TI | variáveis e gate preparados | validar proxy, certificados e subdomínios antes de HSTS |
| INF-02 | Rate limiting | TI | não implementado em cache local para evitar falsa proteção multiworker | aplicar no proxy/WAF ou Redis compartilhado |
| INF-03 | Banco institucional | TI | aplicação exige PostgreSQL em ambientes implantados | restringir rede, contas, TLS, patching e capacidade |
| INF-04 | Storage de mídia | TI | filesystem local é o backend atual | provisionar storage persistente, backup e política de acesso |
| INF-05 | Backup e restauração | Parcial | scripts/timers e documentação versionados | instalar, criptografar, externalizar e testar restore periódico |
| INF-06 | Logs e monitoramento | Parcial | health check e monitor versionados | centralizar logs, alertar e definir retenção/SIEM |
| INF-07 | Host e rede | TI | documentação de hardening disponível | contas de serviço, firewall, SSH, patching e EDR |
| GOV-01 | Vulnerabilidades | Parcial | scanners e atualização automática preparados | nomear responsável, canal, triagem e SLA |
| GOV-02 | Incidentes | TI | não há processo institucional aprovado no código | definir papéis, contatos, evidências, comunicação e exercícios |
| GOV-03 | Privacidade e retenção | TI | riscos e campos estão inventariados | aprovar base legal, aviso, retenção e canal de direitos |
| GOV-04 | Continuidade | Parcial | backup, restore, health e rollback documentados | definir RPO/RTO e executar teste de recuperação |

## 5. Evidências de validação do pacote

- `python manage.py check` sem apontamentos;
- `python manage.py makemigrations --check --dry-run` sem alterações;
- `python manage.py collectstatic --noinput` concluído;
- testes direcionados de hardening e shell global aprovados;
- suíte completa: 737 testes aprovados, sem falhas ou erros, após coleta de estáticos;
- `pip-audit` sem vulnerabilidades conhecidas nas dependências declaradas;
- Bandit sem achados de alta severidade e alta confiança;
- compilação Python e `git diff --check` aprovados.
- `manage.py check --deploy` sem apontamentos quando HTTPS, HSTS, proxy, cookies, hosts, banco e segredo forte são representados no ambiente de validação.

O link do PR e o resultado do CI remoto devem ser registrados após a publicação da branch. Resultados de scanners são evidência pontual na data; não garantem ausência de vulnerabilidades.

## 6. Ações obrigatórias da TI

### P0 — antes de produção institucional

1. Proteger a branch `main`, exigindo PR, revisão e os jobs de testes e segurança.
2. Provisionar PostgreSQL institucional com rede restrita, TLS, backup e credenciais em cofre.
3. Provisionar storage persistente para anexos, com quarentena e varredura antimalware.
4. Confirmar terminação TLS, cabeçalhos do proxy e redirecionamento HTTPS; só então ativar HSTS.
5. Aplicar rate limiting distribuído em login, cadastro, reenvio de confirmação e recuperação de senha.
6. Instalar e testar backups de banco e mídia; manter cópia externa e registrar evidência de restauração.
7. Centralizar logs e alertas sem registrar senhas, tokens, cookies ou conteúdo sensível.
8. Aprovar responsáveis, canal e procedimento de resposta a incidentes.

### P1 — primeira etapa operacional

1. Localizar Bootstrap e remover scripts/estilos inline apontados pela CSP em relatório.
2. Definir política de cadastro, MFA para administradores e ciclo de revisão de acessos.
3. Definir governança do vínculo usuário–EFS e permissões institucionais.
4. Aprovar política de privacidade, termos, base legal, retenção e descarte.
5. Definir RPO, RTO, janela de manutenção, rollback e teste periódico de desastre.
6. Habilitar proteção adicional do repositório, como secret scanning, CodeQL e revisão de Dependabot.

### P2 — melhoria contínua

1. Executar teste de intrusão após a infraestrutura definitiva.
2. Homologar acessibilidade com tecnologia assistiva e zoom de 200%.
3. Revisar trimestralmente dependências, contas, regras de firewall e riscos aceitos.
4. Exercitar anualmente resposta a incidente e recuperação de desastre.

## 7. Critérios de aceite para implantação

- PR revisado e CI verde;
- inventário e backup prévios, com rollback definido;
- variáveis de produção conferidas sem exposição de valores;
- TLS, proxy, cookies, hosts e CSRF validados no domínio oficial;
- banco e storage persistentes e protegidos;
- antimalware e rate limiting funcionais;
- logs, métricas, health check e alertas recebidos pela equipe responsável;
- teste de login, redefinição, submissão, upload, edição autorizada e acesso staff;
- validação de que dados privados e rascunhos não aparecem no catálogo público;
- registro do SHA implantado, horário, responsável e evidências pós-deploy.

## 8. Responsabilidades sugeridas

| Atividade | Desenvolvimento | TI/Infra | Negócio/Privacidade |
|---|---|---|---|
| Correções de aplicação e testes | responsável | consultado | informado |
| CI, branch protection e dependências | executor conjunto | responsável conjunto | informado |
| Servidor, rede, TLS, banco e storage | consultado | responsável | informado |
| Backup, restore, logs e monitoramento | consultado | responsável | informado |
| Perfis, cadastro e vínculo EFS | executor técnico | consultado | responsável pela regra |
| Privacidade, retenção e termos | consultado | consultado | responsável |
| Incidentes | apoio técnico | responsável operacional | responsável por comunicação/decisão |

## 9. Limites desta avaliação

A revisão cobre o repositório e validações locais automatizadas. Não confirma configuração efetiva do servidor, firewall, DNS, certificados, banco, storage, SMTP, SIEM ou rotinas humanas. Também não é teste de intrusão, auditoria jurídica, DPIA/RIPD ou certificação de conformidade. Esses itens exigem evidência produzida pela TI e pelas áreas institucionais responsáveis.
