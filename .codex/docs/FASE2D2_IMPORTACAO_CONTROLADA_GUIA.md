# Fase 2D.2 — importação controlada do Guia

## Estado e contrato técnico

O motor recebe JSON UTF-8 no contrato `guia-fase2d2-v1`, com
`idioma_canonico="es"` obrigatório. A fonte informa versão, proveniência,
`sha256_guia`, contagens, hierarquia codificada e referências. `sha256_guia`
protege o objeto `guia` codificado, serializado com
`json.dumps(..., ensure_ascii=False, separators=(",", ":"))`, sem `sort_keys`.
Separadamente, a equivalência 2D.2B reconstrói o Guia institucional por ordem e
compara seu hash canônico ao hash oficial de produção. Esse hash institucional e
as contagens auditadas permanecem fixos no validador.

Antes de qualquer escrita, o comando valida arquivo regular (limite de 20 MiB),
executor staff ativo, JSON, contrato, hashes, contagens, códigos, ordens,
hierarquia, tipos de auditoria e referências. `--dry-run` também consulta o banco,
calcula o plano, reconhece itens idempotentes e acusa divergências, mas não cria
versão, lote ou item.

## Importação, lote e divergências

Sem `--dry-run`, `importar_guia_fase2d2` executa todo o plano em
`transaction.atomic()`, com bloqueio da versão concorrente. A versão nasce em
rascunho, não vigente e sem data de publicação. Eixos, subeixos, setores próprios
do Guia, subáreas, perguntas, referências e ocorrências são persistidos por código
institucional. Não há associação automática ao setor geral, pergunta–referência ou
`NormaInternacional`, nem preenchimento de traduções.

Cada execução efetiva concluída registra `LoteImportacaoConteudo` e itens no ledger
existente. Reexecução idêntica não duplica conteúdo; diferença de identidade ou de
campo institucional bloqueia a operação, sem estratégia *last write wins*. Uma nova
versão codificada preserva as anteriores.

## Reversão e publicação

`--reverter-lote` exige executor staff ativo e justificativa. A reversão é atômica,
processa itens em ordem inversa e só remove objetos criados pelo lote cujo estado
pós-importação não mudou. Alterações posteriores, dependências protegidas e versões
publicadas ficam bloqueadas e produzem reversão parcial; a operação nunca destrói
uma versão publicada.

`publicar_guia_fase2d2` é uma operação separada. Ela exige rascunho importado, lote
concluído sem divergência e integridade quantitativa no banco. A publicação registra
data e pode tornar a versão explicitamente vigente, desativando a vigência anterior
na mesma transação. Conteúdo publicado permanece imutável pelos models.

## Limites desta entrega

Nenhuma carga real foi executada ou incorporada. A execução institucional continua
bloqueada até existir fonte codificada homologada com o hash auditado. Permanecem
pendentes as decisões GUIA-01, GUIA-05, GUIA-06 e GUIA-08 a GUIA-13; este motor não
define acesso/UX, fallback de tradução, correções editoriais, metadados, busca,
respostas, evidências, indicadores, exportações ou associações curatoriais.
