# Correção Fase 15C — teste multidoma da ficha

Corrige o teste `test_ficha_usa_breve_descricao_e_campos_de_justica_climatica` para funcionar quando o Django renderizar a ficha em português, espanhol ou inglês.

O erro anterior ocorria porque o teste procurava `Riscos clim`, mas em ambiente com idioma espanhol a página renderiza `Riesgos climáticos identificados`.

A nova versão valida alternativas equivalentes por idioma:
- Riscos clim
- Riesgos clim
- climate risks

Também mantém a validação de que `Insumo para` não aparece na ficha.
