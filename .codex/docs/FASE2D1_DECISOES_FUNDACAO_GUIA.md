# Fase 2D.1A — decisões de fundação do Guia de Justiça Climática

## 1. Objetivo e escopo

Este documento registra as decisões GUIA-02, GUIA-03, GUIA-04 e GUIA-07 que orientam a futura fundação estrutural do Guia de Justiça Climática. Esta execução é exclusivamente documental e de planejamento: não cria models, migrations, telas, rotas, importadores ou dados.

As decisões se limitam ao versionamento, à identidade estável, à taxonomia setorial própria e à granularidade confirmada das referências. Funcionalidades não demonstradas pela fonte permanecem fora do escopo.

## 2. Branch e commit-base

- Branch: `feature/fase2d1-implementacao-guia`.
- Commit-base: `b41eba9ce4ba6fd96f705c5082119c2f8fe569cf`.

## 3. Fonte oficial e hashes

A fonte já auditada no levantamento da Fase 2D.0 permanece inalterada:

- arquivo: `.local/design-reference/plataforma-justicia-climatica/index.html`;
- tamanho verificado: 295.520 bytes;
- SHA-256 do arquivo: `CD78B9BECA799AA9C6976AF825C314E57E4A1903BFA832ECEC2FBC3D86B61C67`;
- SHA-256 do objeto `PJC_DATA.guia`, serializado deterministicamente: `8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d`.

O conteúdo canônico das perguntas e referências permanece somente em espanhol. A fonte atual não possui códigos estáveis, portanto uma fonte institucional controlada com esses códigos ainda precisa ser fornecida antes da importação. Nenhum texto espanhol é corrigido e nenhuma tradução PT/EN é criada nesta fase.

## 4. GUIA-02 — versionamento e publicação

Decisão aprovada:

- versões em rascunho podem ser alteradas;
- versões publicadas são imutáveis;
- correções posteriores exigem nova versão;
- múltiplas versões podem permanecer armazenadas para rastreabilidade;
- somente uma versão pode estar vigente por vez;
- a publicação registra data, hash da fonte e lote de origem;
- a importação nunca publica automaticamente conteúdo do Guia.

Consequência: `VersaoGuia` delimitará cada conjunto coerente da hierarquia e deverá representar situação editorial, vigência, proveniência e publicação. A futura implementação precisará impedir alterações em versão publicada e garantir a unicidade da versão vigente.

## 5. GUIA-03 — códigos estáveis

Decisão aprovada:

- eixos, subeixos, setores, subáreas, perguntas e referências terão códigos estáveis explícitos;
- texto, posição e hash não serão usados isoladamente como identidade;
- os códigos deverão existir no arquivo-fonte institucional controlado;
- reordenação ou correção editorial não alterará códigos;
- o futuro importador reconciliará registros por código e versão.

Consequência: os códigos serão identidade editorial controlada dentro de uma versão. Nenhum código será inferido de posição, texto ou similaridade. A fonte atualmente auditada continua válida como evidência de conteúdo, mas não está pronta para carga enquanto não incorporar os códigos aprovados.

## 6. GUIA-04 — taxonomia própria de setores

Decisão aprovada:

- será criada a taxonomia própria `SetorGuia`;
- o model `Setor` existente não será reutilizado diretamente;
- não haverá sincronização automática entre `SetorGuia` e `Setor`;
- eventual mapeamento futuro será explícito, versionado, opcional e aprovado em fase separada.

Consequência: os nove setores do Guia não alterarão a taxonomia usada por Boas Práticas ou Ferramentas. `SubareaGuia` pertencerá a `SetorGuia`, preservando a hierarquia da fonte sem acoplamento entre módulos.

## 7. GUIA-07 — referências no nível de subárea

Decisão aprovada:

- referências permanecem vinculadas a `SubareaGuia`;
- cada ocorrência preserva sua ordem;
- não será criada `PerguntaReferenciaGuia`;
- não serão inferidos vínculos por proximidade, posição ou similaridade textual;
- relação por pergunta somente poderá surgir após fonte institucional explícita e nova decisão de schema.

Consequência: `ReferenciaGuia` preservará a citação e `SubareaReferenciaGuia` representará cada ocorrência ordenada na subárea. A repetição textual não autoriza deduplicação conceitual nem relação com `NormaInternacional`.

## 8. Consequências técnicas consolidadas

- O Guia terá domínio próprio e versionado no monólito Django existente.
- Todos os registros de conteúdo pertencerão direta ou indiretamente a uma versão.
- Publicação e vigência serão operações explícitas, auditáveis e separadas da importação.
- Identidade editorial será baseada em código institucional e versão.
- `SetorGuia` ficará isolado de `Setor`.
- Referências serão modeladas no nível comprovado pela fonte: subárea e ocorrência ordenada.
- `LoteImportacaoConteudo` e `ItemLoteImportacaoConteudo` poderão ser reutilizados como infraestrutura de proveniência; qualquer ajuste de allowlist será explícito e versionado na futura execução estrutural.
- Exclusão ou alteração de dados publicados deverá respeitar imutabilidade e rastreabilidade, sem exclusão física silenciosa.

## 9. Itens explicitamente fora do escopo

Permanecem fora desta fase:

- respostas, indicadores, evidências e progresso;
- autenticação específica do Guia e vínculo usuário–EFS;
- busca, filtros e seleção de perguntas;
- relatório, exportação e impressão;
- página pública e experiência visual;
- traduções do conteúdo;
- links normativos e reconciliação com `NormaInternacional`;
- relação pergunta–referência;
- vínculo automático com `Setor` ou qualquer outro catálogo;
- importação das 407 perguntas e das 224 ocorrências de referências;
- correção editorial da fonte espanhola.

## 10. Modelo conceitual consolidado para a futura Fase 2D.1

### `VersaoGuia`

Raiz editorial da hierarquia. Controlará código da versão, situação de rascunho ou publicada, vigência, idioma canônico espanhol, hash da fonte, data de publicação e lote de origem. Somente uma versão poderá estar vigente e versões publicadas serão imutáveis.

### `EixoGuia`

Representará os três eixos transversais dentro de uma versão, com código estável, nome canônico em espanhol e ordem explícita.

### `SubeixoGuia`

Representará os oito subeixos, pertencendo a um `EixoGuia`, com código estável, nome canônico e ordem.

### `SetorGuia`

Representará os nove setores próprios do Guia dentro de uma versão, com código estável, nome canônico e ordem, sem FK automática para `Setor`.

### `SubareaGuia`

Representará as 47 subáreas, pertencendo a `SetorGuia`, com código estável, nome canônico e ordem contextual.

### `PerguntaGuia`

Representará perguntas de conformidade ou gestão, com código estável, texto canônico em espanhol, ordem e um único escopo hierárquico entre eixo, subeixo ou subárea. As 407 perguntas não serão carregadas na migration estrutural.

### `ReferenciaGuia`

Preservará cada citação canônica em espanhol com código estável e proveniência, sem URL, norma relacionada ou tradução inventada.

### `SubareaReferenciaGuia`

Representará a ocorrência ordenada de uma `ReferenciaGuia` em uma `SubareaGuia`. Não estabelecerá vínculo com pergunta.

## 11. Arquivos previstos para a implementação estrutural

A futura Fase 2D.1 provavelmente alterará somente o necessário entre:

- `praticas/models.py`;
- `praticas/admin.py`;
- uma nova migration estrutural versionada em `praticas/migrations/`;
- um teste direcionado de models e constraints do Guia;
- documentação de modelo, escopo, rastreabilidade, riscos e changelog.

Views, URLs, templates, JavaScript, CSS, importadores e arquivos de dados não pertencem à implementação estrutural inicial.

## 12. Critérios de aceite da próxima execução

1. Criar somente as oito entidades autorizadas, sem dados embutidos na migration.
2. Implementar versionamento, vigência única e imutabilidade de versão publicada com cobertura automatizada.
3. Exigir códigos estáveis nos seis níveis de conteúdo sem derivá-los de texto, posição ou hash.
4. Manter `SetorGuia` independente de `Setor`.
5. Manter referências associadas somente a subáreas por `SubareaReferenciaGuia`, preservando a ordem.
6. Não criar `PerguntaReferenciaGuia` nem relação automática com `NormaInternacional`.
7. Planejar proveniência no ledger existente, incluindo os tipos necessários para setor e ocorrência de referência.
8. Executar `manage.py check`, `makemigrations --check --dry-run`, testes direcionados e suíte completa.
9. Validar upgrade, rollback e novo upgrade em SQLite temporário, sem migrar o `db.sqlite3` real.
10. Confirmar ausência de views, rotas, templates, importadores, carga e publicação automática.

## 13. Rollback documental

O rollback desta fase consiste em remover este registro e reverter somente as referências documentais adicionadas ao levantamento, modelo conceitual, escopo, rastreabilidade, riscos e changelog. Como não há código, migration ou dados, o rollback não exige operação de banco.

## 14. Riscos residuais

- A fonte auditada não possui os códigos estáveis agora exigidos; a importação permanece bloqueada até existir fonte institucional controlada.
- Conteúdo, hierarquia e referências permanecem somente em espanhol; a política PT/EN continua pendente em GUIA-05.
- Grafias e possíveis inconsistências editoriais permanecem literais até decisão GUIA-06.
- A política de acesso público e autenticação continua pendente em GUIA-01.
- Não existe UX funcional homologada para o Guia; GUIA-10 permanece pendente.
- URLs, metadados e eventual reconciliação normativa continuam dependentes de GUIA-08 e GUIA-09.
- A representação estrutural das perguntas-raiz deverá preservar um único modelo de pergunta e ser validada por constraint e teste na próxima execução.

## 15. Rastreabilidade entre decisão, risco e entidade futura

| Decisão | Risco controlado | Entidades futuras afetadas | Evidência/aceite futuro |
|---|---|---|---|
| GUIA-02 | perda de histórico, alteração de conteúdo publicado e múltiplas versões vigentes | `VersaoGuia` e toda a hierarquia versionada | imutabilidade, vigência única, data/hash/lote de publicação e testes de estado |
| GUIA-03 | identidade instável após reordenação ou correção editorial | `EixoGuia`, `SubeixoGuia`, `SetorGuia`, `SubareaGuia`, `PerguntaGuia`, `ReferenciaGuia` | códigos provenientes da fonte institucional e reconciliação por código + versão |
| GUIA-04 | acoplamento e alteração indevida da taxonomia compartilhada | `SetorGuia`, `SubareaGuia` | ausência de FK/sincronização automática com `Setor` |
| GUIA-07 | falsa precisão normativa e vínculos inferidos | `ReferenciaGuia`, `SubareaReferenciaGuia`, `SubareaGuia` | ocorrências ordenadas por subárea e ausência de relação pergunta–referência |
