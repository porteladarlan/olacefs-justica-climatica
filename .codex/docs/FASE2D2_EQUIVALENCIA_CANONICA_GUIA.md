# Fase 2D.2B — equivalência canônica do Guia

## Objetivo

Garantir que uma fonte institucional codificada não seja aceita apenas por estrutura, códigos e contagens corretas.

A fonte é reconstruída no formato lógico original de `PJC_DATA.guia` e o conteúdo espanhol deve reproduzir exatamente o hash auditado na Fase 2D.0.

Esta subfase não importa, não publica e não escreve no banco.

## Canonicalização reproduzida

A serialização que reproduz o SHA-256 auditado é:

```python
json.dumps(
    guia,
    ensure_ascii=False,
    separators=(",", ":"),
)
```

Regras: UTF-8, sem `sort_keys`, sem indentação, separadores compactos e sem quebra de linha final.

O resultado auditado possui 85.818 bytes e SHA-256:

`8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d`

## Reconstrução

A fonte codificada é reconstruída para os campos originais:

- eixo: `nombre`, `pregCumpl`, `pregGest`, `subejes`;
- subeixo: `nombre`, `cumplimiento`, `gestion`;
- setor: `sector`, `subareas`;
- subárea: `nombre`, `cumplimiento`, `gestion`, `referencias`.

Perguntas e referências voltam a ser strings em espanhol. Códigos e demais metadados institucionais não participam do hash textual.

A ordem lógica é determinada pelo campo `ordem`, e não pela posição física dos itens no JSON.

## Bloqueio

Mesmo preservando as contagens, a fonte é recusada quando houver alteração de texto, mudança de ordem semântica, troca entre `cumplimiento` e `gestion`, alteração de referência, inclusão, remoção ou movimentação de conteúdo.

Correções editoriais em espanhol exigem nova fonte controlada e novos hashes homologados. O validador não corrige conteúdo silenciosamente.

## Limite

A importação real permanece bloqueada até o recebimento de uma fonte institucional codificada que satisfaça o contrato da Fase 2D.2.

## Critérios técnicos verificados

Os testes cobrem serialização compacta UTF-8, divergência textual, alteração de ordem, troca de tipo de auditoria e alteração de referência, sempre sem escrita no banco.
