# Instruções do repositório — Plataforma de Justiça Climática

## Rotina econômica em tokens

1. Leia `.codex/00_PROJECT_INDEX.md`.
2. Leia somente os documentos indicados para a tarefa.
3. Inspecione código, migrations, configurações e testes antes de propor mudança.
4. Não leia toda a pasta `.codex` sem necessidade.
5. Diferencie: estado real, requisito confirmado, protótipo, proposta e pendência.

## Prioridade

1. requisito aprovado e decisão registrada;
2. comportamento existente validado por teste;
3. protótipo atualizado;
4. recomendação técnica;
5. suposição do agente.

## Regras obrigatórias

- Nunca grave segredos no Git, documentação, logs ou resposta.
- Nunca exponha credenciais do servidor Hetzner.
- Não execute deploy, migration destrutiva ou remoção de dados sem plano, impacto e rollback.
- Preserve o Django existente; não reescreva sem decisão formal.
- Autorização deve existir no backend.
- Conteúdo publicado deve continuar público quando essa for a regra do módulo.
- Preserve espanhol, português e inglês; espanhol é a referência inicial.
- Preserve acessibilidade, responsividade e identidade do protótipo.
- Valide uploads por tamanho, extensão, MIME e autorização.
- Use migrations versionadas, constraints e transações.
- Execute testes e `python manage.py check`.
- Ao terminar, informe arquivos, migrations, testes, resultado e riscos.

## Estado real

Nomes de apps, models, URLs e settings devem ser obtidos do repositório. Não invente estruturas com base apenas na documentação.

## Memória

Após mudança relevante, atualize `.codex/CHANGELOG.md`, decisões, riscos e documentação funcional.
