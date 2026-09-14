# Regras de negócio

## Público e conta

- conteúdo publicado é público;
- conteúdo não publicado não pode aparecer por URL, API ou busca;
- contribuição exige conta/e-mail institucional, salvo decisão posterior;
- usuário pertence a uma EFS;
- permissões são validadas no backend.

## Fluxo editorial vigente

`RASCUNHO -> PUBLICADA -> ARQUIVADA`, com recuperação de `ARQUIVADA` para `PUBLICADA`.

O usuário autenticado pode salvar rascunho ou publicar diretamente, sem etapa de revisão ou aprovação. Estados editoriais antigos continuam preservados no banco e nas buscas como histórico, mas a interface os apresenta apenas como `Registro histórico`. Solicitações de edição e comentários de revisão legados não são exibidos.

## Campos da prática

- instituição, país, nome, tipo, responsável, e-mail e ano;
- descrição, vínculo com justiça climática, objetivo e resultados;
- setor, tipo de auditoria, temas, normas e ferramentas;
- perguntas, critérios, metodologia, matrizes e instrumentos;
- anexos.

## Anexos

PDF/JPG/PNG, até 10 MB por arquivo conforme protótipo. Quantidade total é pendente. Validar MIME, tamanho, autorização e armazenamento seguro.

## Classificações do protótipo

Setores: água/energia, infraestrutura, biodiversidade/ecossistemas, saúde, alimentação/agricultura, indústria extrativa, riscos/desastres, direitos humanos, gênero e outro.

Tipos: conformidade, desempenho/gestão, financeira, coordenada, estudo/diagnóstico, guia/metodologia e outro.

Temas: quilombolas, crianças, direitos humanos, gênero, idosos, LGBTQI+, mulheres, populações vulneráveis, povos indígenas e outro.

## Governança e rastreabilidade

Decisões têm responsável, data e justificativa. Publicação e alterações devem ser rastreáveis. A interface não permite exclusão física de boas práticas: a ação padrão é o arquivamento lógico, preservando registro, anexos, relacionamentos e histórico. Favoritos continuam usando POST/CSRF; o arquivamento exige autorização do autor ou de staff, e a rota antiga permanece somente por compatibilidade.
