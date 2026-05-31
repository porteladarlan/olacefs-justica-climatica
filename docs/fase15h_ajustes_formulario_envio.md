# Fase 15H — Ajustes do formulário de envio

Esta fase refina o formulário de envio de boas práticas sem alterar regra de negócio ou banco de dados.

## Alterações

- Reforça visualmente a diferença entre salvar rascunho, enviar para revisão e publicação após aprovação.
- Adiciona indicação visual de campos obrigatórios para envio.
- Move `Pessoa responsável` para o bloco de identificação/contato, pois é informação institucional e não detalhe técnico.
- Ajusta o texto da classificação para focar organização e localização no catálogo, sem reforçar o comparador.
- Remove o campo `contribui_para_guia` do formulário de submissão e edição, mantendo o campo no model apenas por compatibilidade histórica.
- Mantém o formulário trilíngue em PT/ES/EN.
- Adiciona testes específicos da Fase 15H.

## Arquivos

- `praticas/forms.py`
- `templates/praticas/adicionar_boa_pratica.html`
- `templates/praticas/editar_boa_pratica.html`
- `praticas/tests_fase15h.py`
