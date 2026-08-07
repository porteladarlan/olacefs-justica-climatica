# Fase 2D.2 — contrato da fonte codificada do Guia

## Objetivo

Definir o contrato mínimo e bloqueante da fonte institucional que poderá alimentar a importação controlada do Guia de Justiça Climática.

Esta etapa não importa conteúdo e não publica versões.

## Proveniência obrigatória

A fonte codificada deve declarar como origem o material auditado na Fase 2D.0:

- SHA-256 do arquivo HTML: `CD78B9BECA799AA9C6976AF825C314E57E4A1903BFA832ECEC2FBC3D86B61C67`;
- SHA-256 determinístico do objeto original `PJC_DATA.guia`: `8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d`;
- idioma canônico: `es`.

A declaração desses hashes registra proveniência. A equivalência textual integral entre o JSON codificado e o conteúdo auditado é verificada pela subfase 2D.2B antes de qualquer importação efetiva.

## Formato

O arquivo institucional deve ser JSON UTF-8 e declarar:

`formato = guia-justica-climatica-fase2d2-v1`

Estrutura de topo:

- `formato`;
- `idioma_canonico`;
- `fonte_origem`;
- `versao`;
- `eixos`;
- `setores`.

## Identidade institucional

São obrigatórios códigos explícitos e estáveis para:

- eixo;
- subeixo;
- setor;
- subárea;
- pergunta;
- referência.

Os códigos não são gerados a partir do texto, da ordem, de hashes ou de `slugify`.

A ausência de qualquer código bloqueia a fonte.

## Contagens obrigatórias

A fonte codificada deve preservar:

- 3 eixos;
- 8 subeixos;
- 9 setores;
- 47 subáreas;
- 6 perguntas-raiz de eixo;
- 54 perguntas de subeixo;
- 347 perguntas de subárea;
- 407 perguntas no total;
- 224 perguntas de `cumplimiento`;
- 183 perguntas de `gestion`;
- 224 ocorrências de referências;
- 223 referências textuais únicas por igualdade exata;
- 407 perguntas textualmente únicas por igualdade exata.

## Ordenação

Toda coleção ordenada deve declarar `ordem` explicitamente.

Dentro de cada coleção irmã, as ordens devem ser:

- inteiras;
- positivas;
- únicas;
- contíguas;
- iniciadas em 1.

## Referências

As referências continuam vinculadas à subárea por ocorrência ordenada.

Não existe vínculo pergunta–referência.

Um mesmo código de referência pode aparecer em mais de uma subárea apenas quando preservar exatamente a mesma citação.

Esta regra não resolve a futura reconciliação com `NormaInternacional`, que permanece dependente de decisão própria.

## Política de segurança

O validador:

- não escreve no banco;
- não cria códigos;
- não corrige textos;
- não traduz;
- não publica;
- não cria associação com `Setor`;
- não cria associação com `NormaInternacional`;
- não aceita o HTML legado como substituto da fonte institucional codificada.

## Comando

Validação:

`python manage.py validar_fonte_guia_fase2d2 --arquivo <fonte.json>`

A aprovação desse comando significa que o contrato estrutural e a equivalência canônica da subfase 2D.2B foram atendidos.

Ela não autoriza publicação e, isoladamente, ainda não autoriza a importação efetiva.
