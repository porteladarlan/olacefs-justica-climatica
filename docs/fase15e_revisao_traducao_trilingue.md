# Fase 15E — Revisão geral de tradução trilíngue

Revisão aplicada para corrigir textos que permaneciam em português quando a interface era alternada para inglês ou espanhol.

## Problemas identificados

- Labels do formulário de envio vinham de `forms.py` e estavam fixos em português.
- Help texts do formulário estavam fixos em português.
- Mensagens de validação obrigatória estavam fixas em português.
- Labels de anexo em `adicionar_boa_pratica.html` e `editar_boa_pratica.html` estavam fixos em português (`Arquivo`, `Link externo`).
- Alguns textos em telas de revisão e meus envios estavam fixos em português.

## Correções

- `ExperienciaSubmissaoForm` agora aplica labels e help texts conforme `LANGUAGE_CODE`/idioma ativo.
- `AnexoSubmissaoForm`, `RevisaoExperienciaForm`, `ConsultaStatusForm`, `PropostaEdicaoPublicadaForm` e `RevisaoPropostaEdicaoForm` receberam labels dinâmicos.
- Templates de envio, edição, revisão, cadastro e meus envios receberam condicionais ES/PT/EN onde havia texto fixo.
- Criado teste específico `praticas/tests_fase15e.py` para validar labels em inglês, espanhol e página de envio em inglês.

## Arquivos alterados

- `praticas/forms.py`
- `templates/praticas/adicionar_boa_pratica.html`
- `templates/praticas/editar_boa_pratica.html`
- `templates/praticas/registrar_usuario.html`
- `templates/praticas/meus_envios.html`
- `templates/praticas/revisar_experiencia.html`
- `templates/praticas/revisar_edicao_publicada.html`
- `praticas/tests_fase15e.py`
