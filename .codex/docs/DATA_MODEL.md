# Modelo de dados conceitual

O schema real vem do código.

## Entidades

- **Institution/EFS:** nome, sigla, país, domínio institucional, status.
- **Practice:** título, instituição, responsável, ano, descrição, vínculo, objetivo, resultados, status, autor, datas e idioma.
- **PracticeAttachment:** arquivo, nome de exibição, MIME, tamanho, visibilidade e autor.
- **Sector, Theme, AuditType, PracticeType:** classificações traduzíveis.
- **NormativeFramework:** título, descrição, natureza, ano, âmbito, texto/link, países e setores.
- **Tool/Ferramenta:** código, título e descrição canônicos em espanhol, traduções PT/EN opcionais, responsável, período, setor, URL externa, situação editorial, ordem e lote de origem; o setor é o badge canônico e não existe campo de tipo duplicado.
- **VersaoGuia:** delimita a hierarquia editorial do Guia, com rascunho editável, publicação imutável, vigência única, hash da fonte e lote de origem.
- **EixoGuia, SubeixoGuia, SetorGuia e SubareaGuia:** hierarquia própria e versionada, com códigos estáveis institucionais; `SetorGuia` não reutiliza nem sincroniza automaticamente o `Setor` compartilhado.
- **PerguntaGuia:** código estável, texto canônico em espanhol, tipo de auditoria, ordem e escopo único em eixo, subeixo ou subárea.
- **ReferenciaGuia e SubareaReferenciaGuia:** citação canônica e ocorrência ordenada no nível de subárea, sem relação inferida com pergunta ou `NormaInternacional`.
- **TechnicalResource:** documentos não cobertos pelas entidades anteriores.
- **ModerationEvent:** objeto, estado anterior/novo, responsável, comentário e data.

## Relações prováveis

Practice N:1 EFS; Practice N:N setores, temas, normas e ferramentas; Practice 1:N anexos/eventos. O Guia possui hierarquia própria por versão; referências relacionam-se a subáreas por ocorrência ordenada, não a perguntas.

## Regras

- `PROTECT` para referências em uso;
- evitar JSON para relações centrais;
- usar constraints e índices;
- traduções consistentes;
- migrations graduais;
- não alterar nullabilidade/tipo sem avaliar registros existentes.
