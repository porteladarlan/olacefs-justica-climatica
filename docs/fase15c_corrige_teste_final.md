# Correção Fase 15C — teste final da ficha

Corrige definitivamente o teste da ficha para não depender do valor específico dos campos traduzidos.

Motivo:
- Quando o idioma ativo é espanhol, o template exibe `Sequias e inseguridad hidrica`.
- Quando o idioma ativo é português, exibe `Secas e inseguranca hidrica`.
- O objetivo do teste é validar a estrutura da nova ficha e a remoção da referência à Guia, não validar uma string específica de idioma.

A nova versão valida:
- estrutura principal da ficha;
- dados essenciais da experiência;
- presença dos blocos de justiça climática e metodologias;
- ausência de `Insumo para`.
