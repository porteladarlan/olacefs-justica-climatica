# Índice da documentação

Esta é a entrada da documentação humana do projeto. A entrada principal do repositório é [README.md](../README.md). O índice operacional dos agentes é [\.codex/00_PROJECT_INDEX.md](../.codex/00_PROJECT_INDEX.md).

Legenda: **VIGENTE** é referência atual; **HISTÓRICO** registra implementação anterior; **REFERÊNCIA** apoia operação ou teste; **PENDENTE DE REVISÃO** exige validação; **CANDIDATO A ARQUIVAMENTO** é legado a avaliar, sem exclusão nesta fase.

## Visão geral e requisitos

- [Matriz de requisitos negociais](matriz_requisitos_negociais_mvp.md) — **REFERÊNCIA**
- [Checklist de homologação MVP](checklist_homologacao_mvp.md) — **REFERÊNCIA**
- [Roteiro de testes MVP](roteiro_testes_mvp.md) — **REFERÊNCIA**
- [Roteiro de demonstração executiva](roteiro_demo_executiva.md) — **REFERÊNCIA**
- [Dados demonstrativos](dados_demo_executiva.md) — **REFERÊNCIA**

## Arquitetura, segurança e proteção de dados

- [Contexto do projeto](../.codex/docs/PROJECT_CONTEXT.md) — **VIGENTE**
- [Módulos](../.codex/docs/MODULES.md) — **VIGENTE**
- [Arquitetura](../.codex/docs/ARCHITECTURE.md) — **VIGENTE**
- [Segurança SSDLC](../.codex/docs/SECURITY_SSDLC.md) — **VIGENTE**
- [Proteção de dados](../.codex/docs/DATA_PROTECTION.md) — **VIGENTE**
- [Auditoria de mojibake/UTF-8](auditoria_mojibake_utf8.md) — **REFERÊNCIA**
- [Correção de logo sem manifesto](correcao_footer_logo_sem_manifest.md) — **HISTÓRICO**
- [Correção do logo no rodapé](correcao_logo_rodape_app_static.md) — **HISTÓRICO**

## Ambiente e infraestrutura

- [Checklist de ambiente de produção](ambiente/checklist_ambiente_producao.md) — **VIGENTE**
- [Variáveis de ambiente recomendadas](ambiente/variaveis_ambiente_recomendadas.md) — **VIGENTE**
- [Guia de deploy e migration futura](ambiente/guia_deploy_migracao_futura.md) — **REFERÊNCIA**
- [Checklist de hardening](ambiente/checklist_hardening_producao.md) — **PENDENTE DE REVISÃO**
- [Limitações do ambiente gratuito](ambiente/limitacoes_ambiente_gratuito.md) — **REFERÊNCIA**
- [Backup e restore](operacao_backup_restore.md) — **REFERÊNCIA**
- [Monitoramento e alertas](operacao_monitoramento_alertas.md) — **REFERÊNCIA**

## Operação e testes

- [Estratégia de testes](../.codex/docs/TEST_STRATEGY.md) — **VIGENTE**
- [GitHub Actions e testes Django](github_actions_testes_django.md) — **REFERÊNCIA**
- [Roteiro de teste externo](teste_externo/roteiro_teste_externo.md) — **VIGENTE**
- [Checklist de teste externo](teste_externo/checklist_teste_externo.md) — **VIGENTE**
- [Perguntas de feedback](teste_externo/perguntas_feedback_teste_externo.md) — **VIGENTE**
- [Preparação do ambiente de teste externo](teste_externo/preparacao_ambiente_teste_externo.md) — **VIGENTE**
- [Mensagem para envio do link](teste_externo/mensagem_envio_link_teste.md) — **REFERÊNCIA**

## Release atual

- [Checklist final de validação](release/checklist_final_validacao.md) — **VIGENTE**
- [Comandos de validação final](release/comandos_validacao_final.md) — **VIGENTE**
- [Entrega final de validação](release/entrega_final_validacao.md) — **REFERÊNCIA**
- [Versão de validação e retroalimentação](release/versao_validacao_retroalimentacao.md) — **REFERÊNCIA**
- [Pendências e próximos passos](release/pendencias_e_proximos_passos.md) — **VIGENTE**
- [Roteiro de apresentação](release/roteiro_apresentacao_plataforma.md) — **REFERÊNCIA**
- [Auditoria sênior de código e segurança](release/auditoria_senior_codigo_seguranca.md) — **REFERÊNCIA**
- [Limpeza de artefatos recomendada](release/limpeza_artefatos_recomendados.md) — **REFERÊNCIA**

## Render e teste externo legado

- [Checklist Render](render/checklist_render_teste_externo.md) — **REFERÊNCIA**
- [Comandos pós-deploy](render/comandos_pos_deploy.md) — **REFERÊNCIA**
- [Usuários de teste](render/usuarios_teste.md) — **REFERÊNCIA**
- [Correção de timeout da home](render/fase16b_corrige_timeout_home_render.md) — **HISTÓRICO**
- [Validação pública do Render](render/fase16b_validacao_render_publico.md) — **HISTÓRICO**
- [Polimento da home de apresentação](render/fase16d_polimento_home_apresentacao.md) — **HISTÓRICO**
- [Usuários de teste sem shell](render/fase16e_usuarios_teste_sem_shell.md) — **HISTÓRICO**
- [Start command preservando EFS e envios](render/start_command_preservando_efs_e_envios.md) — **HISTÓRICO**

## Histórico de implementação

Os documentos abaixo preservam decisões e correções de rodadas anteriores. Não são o contrato atual isoladamente.

- Fase 14: [home modal](correcao_fase14_home_modal.md), [contraste e acordeão](correcao_fase14d_contraste_acordeao.md), [ajustes visuais](fase14a_ajustes_visuais_ildenny.md), [experiência de uso](fase14b_experiencia_uso_ildenny.md), [correção estética](fase14c_correcao_estetica_ildenny.md) — **HISTÓRICO**
- Fase 15A: [arquivos de conflito](fase15a_arquivos_conflito_resolvido.md), [erro 500 da home](fase15a_corrige_500_home.md), [abas padronizadas](fase15a_corrige_abas_padronizadas.md), [home trilíngue](fase15a_home_trilingue.md), [navegação da home](fase15a_nova_home_navegacao.md) — **HISTÓRICO**
- Fase 15B–15F: [envio e catálogo](fase15b_fluxo_envio_catalogo.md), [teste final](fase15c_corrige_teste_final.md), [teste multilíngue](fase15c_corrige_teste_multidioma.md), [recursos técnicos](fase15d_recursos_tecnicos.md), [login](fase15e_corrige_teste_login.md), [revisão trilíngue](fase15e_revisao_traducao_trilingue.md), [comparativo](fase15f_corrige_teste_comparativo_multidioma.md), [revisão final de saneamento](fase15f_revisao_final_saneamento.md), [textos públicos](fase15f_saneamento_textos_publicos.md) — **HISTÓRICO**
- Fase 15G–15I: [sintaxe](fase15g_corrige_teste_syntax.md), [revisão visual](fase15g_revisao_visual_publica.md), [formulário](fase15h_ajustes_formulario_envio.md), [entrega completa](fase15i_completo_final.md), [ações](fase15i_corrige_actions_green_v2.md), [testes finais](fase15i_corrige_testes_finais.md), [testes de revisão](fase15i_corrige_testes_revisao.md), [revisão/aprovação](fase15i_revisao_aprovacao.md) — **HISTÓRICO**
- Fase 15J–15S: [conteúdo institucional](fase15j_conteudo_institucional_normas.md), [correções de conteúdo](fase15j_corrige_consultoria_auditora_v2.md), [laboratório](fase15j_corrige_laboratorio_justica_climatica.md), [recursos e status](fase15j_corrige_recursos_tecnicos_status.md), [dados demonstrativos](fase15k_dados_demonstrativos.md), [acessibilidade](fase15l_usabilidade_acessibilidade.md), [auditoria trilíngue](fase15m_auditoria_trilingue.md), [autenticação e perfis](fase15n_auditoria_autenticacao_perfis.md), [rotas](fase15n_refina_auditoria_rotas.md), [ponta a ponta](fase15o_validacao_ponta_a_ponta.md), [teste externo](fase15p_preparacao_teste_externo.md), [ambiente](fase15q_preparacao_ambiente_producao.md), [consolidação](fase15r_consolidacao_versao_validacao.md), [entrega](fase15s_entrega_final_validacao.md) — **HISTÓRICO**
- Fase 16A–16L: [Render](fase16a_preparacao_render_teste_externo.md), [usuários](fase16e_usuarios_teste_sem_shell.md), [migrações](fase16f_correcao_testes_migracao.md), [formulário](fase16f_corrige_edicao_campos_novos.md), [taxonomias](fase16f_retroalimentacao_formulario_taxonomias.md), [EFS](fase16g_corrige_lista_oficial_efs.md), [testes](fase16g_corrige_teste_fase16f.md), [testes anteriores](fase16h_corrige_testes_anteriores.md), [taxonomias trilíngues](fase16h_taxonomias_trilingues.md), [exclusão no Admin](fase16i_exclusao_admin.md), [Banco Técnico](fase16j_corrige_bancotecnico_autor_indevido.md), [campo autor](fase16j_corrige_campo_autor_experiencia_ci.md), [edição anônima](fase16j_corrige_edicao_por_email_anonimo.md), [permissão de edição](fase16j_corrige_permissao_edicao_email_v2.md), [related name](fase16j_corrige_related_name_autor.md), [Meu Espaço](fase16j_corrige_teste_meus_envios_idioma.md), [status multilíngue](fase16j_corrige_testes_status_meus_envios_multidioma.md), [submissão e revisão](fase16j_revisao_fluxo_submissao_revisao.md), [ajustes de 12/06](fase16k_ajustes_12_06_plataforma.md), [anexos e e-mail](fase16k_corrige_constante_anexo_e_teste_email.md), [migration de autor](fase16k_corrige_migration_autor_duplicada.md), [sintaxe das views](fase16k_corrige_syntax_views_constantes.md), [testes e anexos](fase16k_corrige_testes_e_anexos_pos_ajustes.md), [contato de referência](fase16k_remove_contato_referencia_form.md), [EFS oficiais](fase16l_preserva_efs_oficiais_render.md) — **HISTÓRICO**

## Candidatos a consolidação ou arquivamento

Os documentos históricos permanecem no lugar nesta fase. A consolidação física e eventual arquivamento serão avaliados na Fase 0B, preservando rastreabilidade:

- documentos de fases 14, 15 e 16 que repetem a mesma decisão — **CANDIDATO A ARQUIVAMENTO**;
- documentos de correções pontuais já absorvidas pelo código atual — **CANDIDATO A ARQUIVAMENTO**;
- documentos do Render que descrevem o ambiente legado/teste — **REFERÊNCIA**;
- documentos de release e segurança ainda usados na validação — **VIGENTE** ou **REFERÊNCIA**, conforme indicado acima.

As referências internas de segurança e proteção de dados permanecem em [.codex/docs/SECURITY_SSDLC.md](../.codex/docs/SECURITY_SSDLC.md) e [.codex/docs/DATA_PROTECTION.md](../.codex/docs/DATA_PROTECTION.md).
