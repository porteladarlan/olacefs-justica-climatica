# Rastreabilidade

Identificadores: `RF`, `RNF`, `RN`, `ADR`, `SEC` e `TC`.

Cada mudança relaciona requisito, regra, decisão, arquivos, migration, testes, evidência, release e rollback.

Fonte: nota conceitual, protótipo, reunião, regra existente, correção, segurança ou infraestrutura.

## 2026-07-31 — Primeira evolução da página inicial

| ID | Requisito | Fonte | Código | Teste | Migration | Rollback |
|---|---|---|---|---|---|---|
| RNF-HOME-01 | Apresentar claramente o propósito e as mensagens institucionais na ordem visual aprovada | requisito aprovado, contexto funcional e `plataforma-justicia-climatica 1.zip` | `templates/praticas/pagina_inicial.html`, `templates/praticas/includes/home_hero.html`, `templates/praticas/includes/home_institutional_messages.html`, `praticas/static/praticas/img/icone-jc.svg`, `praticas/static/praticas/img/camilo-benitez.jpg`, `praticas/static/praticas/img/pamela-calletti.jpg` | `praticas.tests_home_primeira_evolucao` e regressão existente | não aplicável | reverter os includes e assets editoriais da home |
| RNF-HOME-02 | Reproduzir o cabeçalho, hero, fundamentos e rodapé do protótipo sem substituir rotas ou funcionalidades reais | requisito aprovado, correções visuais e `plataforma-justicia-climatica 1.zip` | `templates/praticas/base.html`, `templates/praticas/pagina_inicial.html`, `templates/praticas/includes/home_foundations.html`, `praticas/static/praticas/img/pilar-justicia.jpg`, `praticas/static/praticas/img/pilar-control.jpg`, `praticas/static/praticas/img/pilar-genero.jpg`, `praticas/static/praticas/img/barra-de-logos.svg` | `praticas.tests_home_primeira_evolucao` e `praticas.tests_fase16d` | não aplicável | reverter cabeçalho, fundamentos, rodapé e respectivos assets locais |
| RNF-HOME-03 | Preservar responsividade, acessibilidade, conteúdo trilíngue e preparar mapa e vídeo futuros sem simulação | requisitos de UI/i18n, contexto funcional e `plataforma-justicia-climatica 1.zip` | `templates/praticas/base.html`, `templates/praticas/includes/home_map_future.html`, `templates/praticas/includes/home_video_future.html` | `praticas.tests_home_primeira_evolucao` e validação manual em 320, 768, 1024 e 1440 px | não aplicável | reverter os estilos e includes da Fase 1, preservando as rotas e conteúdos públicos existentes |

## 2026-07-31 — Fase de segurança crítica

| ID | Requisito | Fonte | Código | Teste | Migration | Rollback |
|---|---|---|---|---|---|---|
| SEC-AUTH-01 | Edição, solicitação de edição publicada e status exigem login e autorização por staff ou autor real | auditoria integral, matriz `A-01` a `A-03`, `BUSINESS_RULES.md` e `SECURITY_SSDLC.md` | `praticas/views.py`, `praticas/forms.py`, `templates/praticas/editar_boa_pratica.html`, `templates/praticas/solicitar_edicao_publicada.html`, `templates/praticas/status_envio.html`, `templates/praticas/meus_envios.html` | `praticas.tests_seguranca_fase` e regressão `praticas.tests` | não aplicável | reverter decorators, filtros por `autor` e remoção dos parâmetros de e-mail |
| SEC-REDIR-01 | Favoritos não redireciona para host externo informado pelo usuário | auditoria integral e matriz `A-06` | `praticas/views.py` | `praticas.tests_seguranca_fase` | não aplicável | restaurar o redirecionamento anterior, não recomendado por reabrir a vulnerabilidade |
| SEC-UPLOAD-01 | Validar quantidade, tamanho, extensão, MIME e assinatura real de PDF/JPG/PNG | protótipo, `BUSINESS_RULES.md`, `SECURITY_SSDLC.md` e matriz `S-08`/`S-09` | `praticas/views.py`, `templates/praticas/adicionar_boa_pratica.html`, `templates/praticas/editar_boa_pratica.html` | `praticas.tests_seguranca_fase` e `praticas.tests` | não aplicável | reverter validações e textos em conjunto, não recomendado sem controle equivalente |
| SEC-I18N-01 | Mensagens executáveis não apresentam mojibake | auditoria integral e matriz `G-09` | `praticas/views.py` | `praticas.tests_seguranca_fase` | não aplicável | reverter apenas correções textuais UTF-8 |

## 2026-08-01 — Fase 2A.1: fundação do vínculo usuário–EFS

| ID | Requisito | Fonte | Código | Teste | Migration | Rollback |
|---|---|---|---|---|---|---|
| RF-UEFS-01 | Preservar vínculo canônico usuário–EFS, ciclos históricos e atribuições temporais sem ativar autorização institucional | prompt da Fase 2A.1 e modelagem aprovada em `.local/fase2_modelagem/` | `praticas/models.py`, `praticas/admin.py` | `praticas.tests_fase2a1_vinculo_efs` e `praticas.tests_seguranca_fase` | `0011_fase2a1_vinculo_efs` | reverter a migration para `0010`, desde que não existam registros dependentes; dados utilizados exigem reversão compensatória |
| SEC-IMP-02 | Registrar a estrutura de proveniência por lote e item, sem executar carga real | prompt da Fase 2A.1, `SECURITY_SSDLC.md` e decisão `IMP-01` | `praticas/models.py`, `praticas/admin.py` | `praticas.tests_fase2a1_vinculo_efs` e ensaio em SQLite temporário | `0010_fase2a1_lote_importacao` | reverter para `0009` somente sem carga dependente; lote utilizado deve ser preservado conforme política de auditoria |
| RN-UEFS-AUTH-01 | Vínculo, episódio e papel não concedem permissão nesta subfase; autoria e staff permanecem como regras exclusivas | regras de segurança da Fase 1 e decisões `UEFS-01` a `UEFS-11` ainda pendentes | nenhum consumidor novo em views/forms; cobertura negativa em `praticas/tests_fase2a1_vinculo_efs.py` | `praticas.tests_fase2a1_vinculo_efs` e `praticas.tests_seguranca_fase` | sem migration de autorização ou dados | remover apenas a fundação não altera a autorização vigente |
