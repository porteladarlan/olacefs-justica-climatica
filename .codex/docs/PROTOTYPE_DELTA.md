# Novas implementações do protótipo atualizado

## Mudança principal

A plataforma evolui de catálogo simples para portal regional de conhecimento e apoio à auditoria.

## Áreas novas ou ampliadas

- Home editorial;
- fundamentos e estratégias;
- casos de injustiça climática;
- mapa com seleção múltipla;
- Marcos Normativos;
- Ferramentas;
- Guia de Perguntas;
- Recursos Técnicos;
- Meu Espaço;
- vídeo/tutorial;
- acessibilidade;
- conteúdo trilíngue.

## Formulário ampliado

Além de título, país, setor, e-mail e resumo:

- instituição;
- nome e tipo da iniciativa;
- pessoa responsável;
- descrição e vínculo com justiça climática;
- ano;
- ferramentas;
- tipo de auditoria;
- temas transversais;
- normas;
- objetivo;
- perguntas;
- critérios;
- metodologia, matrizes e instrumentos;
- resultados;
- anexos;
- rascunho.

## Consequência

Revisar o modelo de dados. Evitar guardar classificações centrais somente como texto ou JSON. Avaliar relações com EFS, país, setor, tema, norma e ferramenta.

## Meu Espaço e moderação

A demonstração precisa virar autenticação, autorização, confirmação/recuperação de acesso, estados, histórico, notificações e política de dados.

## Mapa

O protótipo usa D3/TopoJSON. Não introduzir Leaflet/OpenLayers automaticamente; primeiro verificar o código e registrar decisão.

## Design

- roxo `#432054`;
- roxo médio `#695173`;
- lilás `#A999BF`;
- verde `#698D8B`;
- verde claro `#A3BFBA`;
- fonte Raleway;
- cards arredondados;
- largura máxima aproximada de 1200 px.

## Ordem recomendada

1. auditoria do repositório;
2. mapa de lacunas;
3. modelo de dados;
4. autenticação/workflow;
5. módulos de conteúdo;
6. interface/i18n;
7. testes;
8. deploy.
