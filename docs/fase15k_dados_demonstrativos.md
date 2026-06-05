# Fase 15K — Dados demonstrativos para apresentação

Esta fase melhora os dados de demonstração carregados pelo comando `carregar_dados_ficticios`.

## Ajustes realizados

- Atualiza o comando `praticas/management/commands/carregar_dados_ficticios.py`.
- Remove a referência a MVP do texto de ajuda do comando.
- Cria dados demonstrativos institucionais para 8 boas práticas publicadas.
- Inclui exemplos para Brasil, Chile, Colômbia, Equador, Paraguai, México, Costa Rica e Curaçao.
- Mantém taxonomias trilíngues para países, EFS, tipos, setores, temas, dimensões, grupos e normas.
- Preenche campos importantes para catálogo, ficha detalhada e filtros:
  - EFS;
  - país;
  - tipo;
  - setor;
  - ano;
  - breve descrição;
  - problema climático;
  - riscos climáticos;
  - enfoque de justiça climática;
  - perguntas;
  - critérios;
  - metodologias e instrumentos;
  - resultados;
  - recomendações;
  - replicabilidade.
- Mantém `contribui_para_guia=False` nos dados demonstrativos, respeitando a retroalimentação de que a plataforma demonstra experiências e a Guia orienta.
- Adiciona recurso técnico demonstrativo extra: `Modelo de ficha de boa prática em justiça climática`.
- Adiciona opção `--limpar-demo` para recriar os dados demonstrativos conhecidos.

## Como carregar localmente

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

## Validação

```powershell
python manage.py test praticas.tests_fase15k
python manage.py test
```
