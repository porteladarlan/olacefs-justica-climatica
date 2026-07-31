# Modelo de dados conceitual

O schema real vem do código.

## Entidades

- **Institution/EFS:** nome, sigla, país, domínio institucional, status.
- **Practice:** título, instituição, responsável, ano, descrição, vínculo, objetivo, resultados, status, autor, datas e idioma.
- **PracticeAttachment:** arquivo, nome de exibição, MIME, tamanho, visibilidade e autor.
- **Sector, Theme, AuditType, PracticeType:** classificações traduzíveis.
- **NormativeFramework:** título, descrição, natureza, ano, âmbito, texto/link, países e setores.
- **Tool:** nome, descrição, tipo, arquivo/link, setores, países, idioma e versão.
- **AuditQuestion:** texto, eixo, setor, tipo de auditoria, normas, ordem e traduções.
- **TechnicalResource:** documentos não cobertos pelas entidades anteriores.
- **ModerationEvent:** objeto, estado anterior/novo, responsável, comentário e data.

## Relações prováveis

Practice N:1 EFS; Practice N:N setores, temas, normas e ferramentas; Practice 1:N anexos/eventos; perguntas N:N normas/setores.

## Regras

- `PROTECT` para referências em uso;
- evitar JSON para relações centrais;
- usar constraints e índices;
- traduções consistentes;
- migrations graduais;
- não alterar nullabilidade/tipo sem avaliar registros existentes.
