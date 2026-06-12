# Fase 16J — Revisão do fluxo de submissão, rascunho e revisão

## Objetivo

Corrigir inconsistências observadas no teste de uso da plataforma, especialmente:

- rascunhos aparecendo para revisor;
- boas práticas criadas pelo usuário não aparecendo em “Meus envios” em alguns cenários;
- confusão entre conteúdo salvo como rascunho, enviado para revisão e publicado;
- necessidade de reforçar a rastreabilidade do envio por usuário autenticado.

## Ajustes realizados

### 1. Vínculo da boa prática com o usuário autor

Foi adicionado o campo `autor` em `Experiencia`, vinculado ao usuário autenticado que cria o envio.

Isso evita depender apenas do e-mail digitado no formulário para identificar o dono do envio.

### 2. Meus envios mais confiável

A tela `Meus envios` passa a listar experiências vinculadas por:

- usuário autor autenticado; ou
- e-mail institucional do usuário, para compatibilidade com registros antigos.

### 3. Rascunho privado do autor

O painel de revisão deixa de listar rascunhos.

Rascunho passa a ser tratado como etapa privada do autor, visível em `Meus envios`.

### 4. Painel de revisão mais correto

O painel de revisão lista apenas status editoriais relevantes:

- enviado;
- em revisão;
- aprovado;
- rejeitado.

Conteúdos publicados continuam no catálogo.
Rascunhos ficam apenas com o autor.

### 5. Edição protegida

A edição de envio não publicado agora permite acesso quando:

- o usuário autenticado é o autor; ou
- o e-mail informado corresponde ao e-mail do envio.

Isso preserva compatibilidade com o fluxo antigo, mas melhora a segurança para usuários logados.

### 6. Experiência de usuário

Ao salvar um rascunho novo, a pessoa é redirecionada para `Meus envios`, onde consegue visualizar imediatamente o registro salvo.

## Validação esperada

```powershell
python manage.py test praticas.tests_fase16j
python manage.py test
```

## Observação

O catálogo público continua exibindo somente boas práticas publicadas.
Boas práticas enviadas para revisão não devem aparecer no catálogo até aprovação/publicação.
