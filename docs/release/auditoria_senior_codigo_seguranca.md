# Revisão sênior de código, segurança e alinhamento com a retroalimentação

## Sumário executivo

A plataforma está bem encaminhada para validação externa controlada. O escopo funcional está coerente com a retroalimentação: consulta pública, submissão por usuário autenticado, revisão institucional, suporte trilíngue, recursos técnicos em curadoria, normas como referência interpretativa e dados demonstrativos para apresentação.

Do ponto de vista de segurança, a base está aceitável para ambiente de teste controlado, mas ainda não deve ser considerada pronta para produção institucional sem hardening adicional, principalmente em autenticação/autorização de edição, persistência de dados, storage de anexos e governança de usuários.

## Alinhamento com retroalimentação

### Aderente

- A plataforma está trilíngue em PT/ES/EN.
- O catálogo público está funcional.
- A ficha da boa prática está estruturada.
- A submissão exige login.
- A publicação não é automática; passa por revisão.
- Recursos técnicos aparecem como área em desenvolvimento/curadoria.
- Normas internacionais funcionam como referência interpretativa.
- A mensagem “a Guia orienta; a plataforma demonstra” foi incorporada.
- Dados demonstrativos foram criados para apresentação.
- Há materiais para teste externo.
- Há auditorias automatizadas para tradução, autenticação, fluxo e ambiente.

### Pontos ainda dependentes de decisão

- Cadastro público, controlado ou por convite.
- Validação real de vínculo com EFS.
- Conteúdo final de recursos técnicos e normas.
- Governança editorial: quem revisa, aprova, publica e atualiza.
- Ambiente institucional de produção.
- Política de privacidade, termos de uso e gestão de dados pessoais.

## Achados técnicos

### Achado 1 — README desatualizado

O README ainda descrevia o projeto como “MVP local” e não refletia as fases finais de validação, Render, auditorias e segurança. Foi preparado README atualizado.

**Severidade:** média.  
**Status:** corrigido neste pacote.

### Achado 2 — Artefatos indevidos em templates

Foram identificados arquivos que não deveriam estar em `templates/praticas/`:

- Os artefatos operacionais e a cópia duplicada identificados nessa auditoria
  foram removidos do worktree na Fase 0A; os caminhos canônicos permanecem
  preservados.

**Severidade:** média.  
**Risco:** confusão de manutenção, exposição acidental de documentação operacional, ruído em deploy e revisão.  
**Ação realizada:** saneamento controlado na Fase 0A.

### Achado 3 — SECRET_KEY de fallback

`config/settings.py` possui fallback local para `SECRET_KEY`. Em produção, o `render.yaml` usa `generateValue`, o que reduz o risco no Render. Mesmo assim, produção institucional deve exigir segredo por variável de ambiente.

**Severidade:** média para produção; baixa para validação.  
**Ação recomendada:** em uma fase posterior, fazer settings específicos por ambiente ou falhar quando `SECRET_KEY` não estiver definida e `DEBUG=False`.

### Achado 4 — Edição por validação de e-mail em query string

O fluxo `editar_boa_pratica` e `solicitar_edicao_publicada` permite validação por e-mail informado. Isso é útil para validação, mas fraco para produção.

**Severidade:** alta para produção; média para teste controlado.  
**Ação recomendada:** substituir por vínculo com usuário autenticado, token assinado com expiração ou aprovação manual mais restritiva.

### Achado 5 — Consulta pública de status por e-mail

A página `status-envio` permite consulta por e-mail. Isso pode expor metadados de submissões se alguém souber o e-mail de contato.

**Severidade:** média.  
**Ação recomendada:** exigir login ou token de consulta em produção.

### Achado 6 — Uploads validados por extensão e tamanho

Há limite de extensão, tamanho e número de anexos. Isso é bom para validação, mas produção deve validar MIME, armazenar em storage externo e, idealmente, aplicar varredura antimalware.

**Severidade:** média.  
**Ação recomendada:** storage externo + validação de conteúdo + antivírus antes de produção.

### Achado 7 — Ação de favorito por POST

Foi aplicada proteção para exigir POST na ação de alternar favorito. Isso evita alteração de estado por GET.

**Severidade:** baixa.  
**Status:** corrigido neste pacote.

### Achado 8 — Hardening HTTP complementar

Foram adicionadas configurações defensivas de headers, cookies e limites de upload/payload.

**Severidade:** baixa/média.  
**Status:** parcialmente corrigido neste pacote.

## Avaliação de segurança por área

| Área | Estado atual | Recomendação |
|---|---|---|
| DEBUG | Bom, padrão `False` | manter por ambiente |
| SECRET_KEY | Aceitável no Render; fallback local fraco | endurecer antes de produção |
| ALLOWED_HOSTS | Aceitável para Render | restringir domínio oficial em produção |
| CSRF | Adequado | manter e testar formulários |
| Sessão/cookies | Melhorado | validar em HTTPS real |
| Staff/revisor | Protegido por staff | avaliar grupos/permissões granulares |
| Upload | Básico | storage externo + MIME + antivírus |
| Edição de submissão | Fraco para produção | autenticação/token assinado |
| Status por e-mail | Fraco para produção | login/token |
| Banco | SQLite local; Render pode usar DATABASE_URL | PostgreSQL persistente em produção |
| Anexos | filesystem local | storage persistente |

## Recomendações antes de teste externo

1. Remover artefatos indevidos de `templates/`.
2. Atualizar README.
3. Rodar testes completos.
4. Rodar auditoria pública do Render.
5. Confirmar que dados demonstrativos aparecem no catálogo.
6. Criar usuários de teste com senhas temporárias.
7. Comunicar que o ambiente é de validação.

## Recomendações antes de produção real

1. Banco PostgreSQL persistente.
2. Storage persistente para anexos.
3. Backups testados.
4. Domínio oficial e HTTPS.
5. HSTS habilitado após confirmação do domínio.
6. Política de usuários e permissões.
7. Fluxo de edição baseado em login/token seguro.
8. Validação de vínculo institucional com EFS.
9. Política de privacidade/termos de uso.
10. Logs, monitoramento e rotina de suporte.
