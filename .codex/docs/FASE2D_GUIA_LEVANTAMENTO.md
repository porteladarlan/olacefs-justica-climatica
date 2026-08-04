# Fase 2D.0 — levantamento controlado do Guia de Justiça Climática

## 1. Resumo executivo

O protótipo oficial contém um conjunto de dados do Guia dentro de `window.PJC_DATA.guia`, com hierarquia e conteúdo canônico em espanhol. Foram confirmadas **407 perguntas** e **224 ocorrências de referências**. As perguntas se dividem em 60 perguntas de eixos transversais e 347 perguntas setoriais; as referências estão agrupadas por subárea, não vinculadas individualmente a perguntas.

O Guia, contudo, **não é uma tela funcional do protótipo**. Não existe `page-guia`, entrada de navegação, função de renderização, acesso JavaScript a `PJC_DATA.guia`, rota, filtro, seleção, resultado ou persistência. Há apenas dados, textos trilíngues de interface não utilizados e duas regras CSS responsivas sem elemento correspondente. Portanto, o protótipo confirma o conteúdo e parte da terminologia, mas não confirma uma experiência visual ou funcional do módulo.

O repositório Django também não possui models, view, URL, template ou comando do Guia. O ledger de importação já enumera entidades futuras do módulo, mas isso não equivale a um modelo de domínio implementado. O conjunto mínimo futuro deverá ser próprio, versionado e importado de forma controlada, sem misturar o Guia com Ferramentas, Marcos Normativos, Boas Práticas, Banco Técnico, autenticação ou vínculo usuário–EFS.

Este documento é exclusivamente um levantamento. Nenhuma decisão de implementação, tradução ausente ou correção de conteúdo foi aplicada.

## 2. Fontes e método de verificação

### 2.1 Fonte oficial

- Arquivo: `.local/design-reference/plataforma-justicia-climatica/index.html`.
- Tamanho verificado: 295.520 bytes.
- SHA-256 do arquivo: `CD78B9BECA799AA9C6976AF825C314E57E4A1903BFA832ECEC2FBC3D86B61C67`.
- SHA-256 do objeto `PJC_DATA.guia`, serializado de modo determinístico: `8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d`.

O arquivo foi inspecionado integralmente em suas quatro camadas relevantes: HTML, CSS, JavaScript/I18N e `PJC_DATA`. O objeto JavaScript foi decodificado e todos os arrays do Guia foram percorridos para calcular as contagens, duplicidades e campos efetivamente existentes.

### 2.2 Repositório comparado

Foram inspecionados, sem alteração:

- `praticas/models.py` e migrations existentes;
- `praticas/views.py` e `praticas/urls.py`;
- templates de `templates/praticas/`;
- comandos em `praticas/management/commands/`;
- documentação indexada em `.codex`, especialmente `MODULES.md`, `DATA_MODEL.md`, `ARCHITECTURE.md`, `PROTOTYPE_DELTA.md`, `BUSINESS_RULES.md`, `UI_GUIDELINES.md` e `I18N_ACCESSIBILITY.md`.

As classificações usadas neste levantamento são: **explicitamente implementado**, **apenas visualmente representado**, **simulado**, **incompleto**, **ausente** e **dependente de dados externos**. Conteúdo presente em um objeto JavaScript, mas sem interface que o consuma, é classificado como dado explicitamente presente e funcionalidade ausente.

## 3. Inventário de telas e estados

### 3.1 Contagem de telas

O protótipo possui nove contêineres gerais de página: `home`, `recursos`, `practicas`, `marcos`, `herramientas`, `submit`, `space`, `ejemplos` e `practica`.

Para o Guia, a contagem exata é:

| Elemento | Quantidade | Estado | Evidência |
|---|---:|---|---|
| Tela/página do Guia | 0 | Ausente | Não existe `id="page-guia"`. |
| Estado de navegação do Guia | 0 | Ausente | `showPage()` não possui ramo para Guia. |
| Função de renderização do Guia | 0 | Ausente | Não existe `renderGuia` nem acesso a `PJC_DATA.guia`. |
| Entrada visível no cabeçalho | 0 | Ausente | A navegação contém somente Boas Práticas, Marcos Normativos e Ferramentas. |
| Card visível de acesso ao Guia | 0 | Ausente | As chaves `recCard3T` e `recCard3D` só aparecem nas três definições de idioma. |
| Modos funcionais confirmados | 0 | Ausente | Não há controle executável de eixo, setor ou tipo de auditoria. |

Os dados permitem inferir combinações futuras entre dois blocos de conteúdo e dois tipos de auditoria, mas essas combinações **não são estados de interface implementados** e não devem ser contadas como telas.

### 3.2 Resíduos incompletos de interface

- `navGuia`, `recCard3T`, `recCard3D`, `recCatGuia` e as chaves `guia*` existem em ES/PT/EN, mas cada chave aparece somente nas três definições do dicionário I18N; nenhuma está conectada ao DOM.
- `.guia-layout` e `.guia-side` aparecem apenas em duas regras dentro do breakpoint responsivo. Não há regra-base nem elemento HTML com essas classes.
- `recDocsData()` contém o comentário `// guía como recurso`, mas retorna apenas Marcos e Ferramentas.
- Não há simulação, modal, localStorage, evento ou requisição relacionado ao Guia.

### 3.3 Auditoria funcional dos 30 itens solicitados

| # | Item | Estado no protótipo | Achado confirmado |
|---:|---|---|---|
| 1 | Nome PT/ES/EN | Explicitamente implementado no I18N, não renderizado | PT `Guia de Perguntas`; ES `Guía de Preguntas`; EN `Question Guide`. |
| 2 | Rotas ou estados | Ausente | Nenhuma rota ou chamada `showPage('guia')`. |
| 3 | Telas ou estados | Ausente | Zero telas e zero estados funcionais do Guia. |
| 4 | Perguntas | Explicitamente presentes nos dados | 407 strings de pergunta. |
| 5 | Referências | Explicitamente presentes nos dados | 224 ocorrências, 223 strings únicas. |
| 6 | Dimensões | Ausente | Não existe campo ou coleção `dimensao/dimensión`. |
| 7 | Categorias | Ausente como entidade | Há dois blocos estruturais (`transversales` e `sectores`), sem campo `categoria`. |
| 8 | Subcategorias | Ausente como entidade | `subejes` e `subareas` são níveis nomeados próprios, não subcategorias genéricas. |
| 9 | Grupos | Ausente | Não existe campo ou coleção de grupos. |
| 10 | Eixos | Explicitamente presentes nos dados | 3 eixos transversais. |
| 11 | Etapas | Ausente | Não há fluxo por etapas. |
| 12 | Blocos | Explicitamente presentes nos dados | 2 blocos de topo: eixos transversais e setores. |
| 13 | Tipos de resposta | Ausente | `cumplimiento` e `gestion` são tipos de pergunta/auditoria, não tipos de resposta. |
| 14 | Textos explicativos | Explicitamente definidos no I18N, não renderizados | Descrição do módulo e nota do eixo transversal. |
| 15 | Títulos | Explicitamente definidos no I18N e nos dados | Título da interface e nomes de eixos, subeixos, setores e subáreas. |
| 16 | Descrições | Incompleto | Há descrição geral da interface; nós e perguntas não têm descrição própria. |
| 17 | Instruções | Incompleto | Existem rótulos de tipo de auditoria/setor e nota transversal; não há fluxo executável. |
| 18 | Filtros | Ausente | Nenhum filtro do Guia. |
| 19 | Busca | Ausente | Nenhuma busca do Guia. |
| 20 | Contadores | Ausente | Nenhum contador de perguntas, referências ou seleção. |
| 21 | Ordenação | Incompleto | A ordem existe apenas pela posição nos arrays; não há campo nem controle de ordenação. |
| 22 | Navegação | Ausente | Sem menu, sidebar, breadcrumb ou navegação interna do Guia. |
| 23 | Expansão/recolhimento | Ausente | Nenhum acordeão ou controle equivalente. |
| 24 | Progresso | Ausente | Nenhum indicador ou cálculo de progresso. |
| 25 | Seleção de perguntas | Ausente | Nenhuma seleção ou lista de escolhidas. |
| 26 | Geração de resultado | Ausente | Nenhuma síntese, relatório ou cálculo. |
| 27 | Exportação | Ausente | Nenhuma exportação. |
| 28 | Impressão | Ausente | Nenhuma ação ou estilo específico de impressão do Guia. |
| 29 | Links externos | Ausente no Guia | As 224 referências não têm URL; não há link de Guia. |
| 30 | Relações pergunta–referência | Incompleto/contextual | Perguntas e referências coexistem na mesma subárea, sem IDs nem relação explícita por pergunta. |

Nenhum item do Guia depende de dados externos em tempo de execução: todo o conteúdo está embutido no HTML. A futura validação normativa das citações, porém, dependerá de curadoria e fontes oficiais externas.

## 4. Inventário de dados e contagens confirmadas

### 4.1 Totais

| Estrutura | Quantidade confirmada |
|---|---:|
| Blocos de topo | 2 |
| Eixos transversais | 3 |
| Subeixos | 8 |
| Setores | 9 |
| Subáreas | 47 |
| Perguntas-raiz de eixo | 6 |
| Perguntas detalhadas em subeixos | 54 |
| Perguntas de eixos transversais | 60 |
| Perguntas setoriais | 347 |
| Perguntas de conformidade | 224 |
| Perguntas de gestão | 183 |
| Perguntas totais | **407** |
| Ocorrências de referências | **224** |
| Referências textuais únicas por igualdade exata | 223 |
| Perguntas únicas por igualdade exata | 407 |

As 224 referências são ocorrências em listas de subárea, não 224 entidades identificadas. A diferença entre 224 ocorrências e 223 textos únicos decorre de uma repetição exata documentada na seção 6.

### 4.2 Eixos transversais

| Ordem | Eixo | Subeixos | Conformidade, incluindo raiz | Gestão, incluindo raiz | Total |
|---:|---|---:|---:|---:|---:|
| 1 | Gobernanza | 5 | 20 | 17 | 37 |
| 2 | Recursos | 2 | 6 | 9 | 15 |
| 3 | Seguimiento de acciones implementadas | 1 | 4 | 4 | 8 |
|  | **Total** | **8** | **30** | **30** | **60** |

Perguntas-raiz, preservadas literalmente:

| Eixo | Conformidade | Gestão |
|---|---|---|
| Gobernanza | ¿Existe una estructura de gobernanza para garantizar el acceso justo y equitativo al sector auditado? | ¿En qué medida la estructura de gobernanza está preparada, en términos de economía, eficiencia y eficacia, para el logro del acceso justo y equitativo en el sector auditado? |
| Recursos | ¿El organismo auditado cuenta con los recursos presupuestarios, humanos y materiales formalmente asignados para la ejecución de sus funciones vinculadas al sector auditado? | ¿El organismo auditado dispone de los recursos presupuestarios, humanos, técnicos y materiales suficientes y adecuados para la gestión del sector auditado? |
| Seguimiento de acciones implementadas | ¿El organismo auditado mide los resultados de la gestión del sector y utiliza esa información para la toma de decisiones? | ¿El organismo auditado mide adecuada, oportuna y periódicamente los resultados de la gestión del sector y utiliza efectivamente esa información para la toma de decisiones y la mejora continua? |

### 4.3 Subeixos

| Eixo | Ordem | Subeixo | Conformidade | Gestão | Total |
|---|---:|---|---:|---:|---:|
| Gobernanza | 1 | Marco normativo y regulatorio | 5 | 3 | 8 |
| Gobernanza | 2 | Estructura organizativa y coordinación | 6 | 4 | 10 |
| Gobernanza | 3 | Planificación | 3 | 3 | 6 |
| Gobernanza | 4 | Participación ciudadana | 3 | 3 | 6 |
| Gobernanza | 5 | Comunicación y transparencia | 2 | 3 | 5 |
| Recursos | 1 | Financiamiento y presupuesto | 3 | 4 | 7 |
| Recursos | 2 | Capacidades técnicas e materiales | 2 | 4 | 6 |
| Seguimiento de acciones implementadas | 1 | Seguimiento de metas y resultados | 3 | 3 | 6 |

`Capacidades técnicas e materiales` é a grafia literal da fonte. Não foi corrigida neste levantamento.

### 4.4 Setores

| Ordem | Setor | Subáreas | Conformidade | Gestão | Perguntas | Referências |
|---:|---|---:|---:|---:|---:|---:|
| 1 | AGUA Y ENERGÍA | 6 | 25 | 19 | 44 | 28 |
| 2 | INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 6 | 21 | 18 | 39 | 28 |
| 3 | BIODIVERSIDAD Y ECOSISTEMAS | 5 | 22 | 16 | 38 | 28 |
| 4 | SALUD | 5 | 20 | 15 | 35 | 23 |
| 5 | ALIMENTACIÓN Y AGRICULTURA | 5 | 20 | 19 | 39 | 24 |
| 6 | INDUSTRIA EXTRACTIVA | 5 | 21 | 17 | 38 | 22 |
| 7 | GESTIÓN DE RIESGO Y DESASTRES | 5 | 25 | 16 | 41 | 31 |
| 8 | GÉNERO Y DERECHOS HUMANOS | 5 | 20 | 17 | 37 | 20 |
| 9 | POBREZA Y DESIGUALDAD | 5 | 20 | 16 | 36 | 20 |
|  | **Total** | **47** | **194** | **153** | **347** | **224** |

### 4.5 Subáreas

| Setor | Ordem | Subárea | Conformidade | Gestão | Total | Referências |
|---|---:|---|---:|---:|---:|---:|
| AGUA Y ENERGÍA | 1 | Acceso al Agua Potable y Saneamiento | 4 | 3 | 7 | 5 |
| AGUA Y ENERGÍA | 2 | Gestión Integrada de Recursos Hídricos | 3 | 3 | 6 | 4 |
| AGUA Y ENERGÍA | 3 | Transición Energética y Energías Renovables | 5 | 3 | 8 | 4 |
| AGUA Y ENERGÍA | 4 | Pobreza Energética y Acceso | 4 | 3 | 7 | 5 |
| AGUA Y ENERGÍA | 5 | Calidad del Agua y Contaminación | 4 | 3 | 7 | 4 |
| AGUA Y ENERGÍA | 6 | Justicia Climática e Inclusión | 5 | 4 | 9 | 6 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 1 | Diagnóstico de Vulnerabilidad de Infraestructura | 3 | 2 | 5 | 4 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 2 | Resiliencia Climática en Diseño y Construcción | 3 | 4 | 7 | 4 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 3 | Movilidad Urbana Sostenible | 4 | 3 | 7 | 4 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 4 | Vivienda Social Resiliente | 3 | 2 | 5 | 5 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 5 | Ordenamiento Territorial y Ciudades Sostenibles | 3 | 3 | 6 | 5 |
| INFRAESTRUCTURA, VIVIENDA, TRANSPORTE Y CIUDADES | 6 | Justicia Climática e Inclusión | 5 | 4 | 9 | 6 |
| BIODIVERSIDAD Y ECOSISTEMAS | 1 | Gestión de Áreas Protegidas | 5 | 3 | 8 | 5 |
| BIODIVERSIDAD Y ECOSISTEMAS | 2 | Control de Deforestación y Degradación | 4 | 3 | 7 | 6 |
| BIODIVERSIDAD Y ECOSISTEMAS | 3 | Restauración de Ecosistemas | 4 | 2 | 6 | 5 |
| BIODIVERSIDAD Y ECOSISTEMAS | 4 | Biodiversidad y Actividades Productivas | 4 | 4 | 8 | 5 |
| BIODIVERSIDAD Y ECOSISTEMAS | 5 | Justicia Climática e Inclusión | 5 | 4 | 9 | 7 |
| SALUD | 1 | Vigilancia de Enfermedades Sensibles al Clima | 4 | 3 | 7 | 4 |
| SALUD | 2 | Salud Ambiental | 4 | 3 | 7 | 5 |
| SALUD | 3 | Adaptación del Sistema de Salud al Cambio Climático | 4 | 3 | 7 | 5 |
| SALUD | 4 | Salud Mental y Comunidades Afectadas por el Clima | 3 | 3 | 6 | 4 |
| SALUD | 5 | Justicia Climática e Inclusión en Salud | 5 | 3 | 8 | 5 |
| ALIMENTACIÓN Y AGRICULTURA | 1 | Diagnóstico de Vulnerabilidad Agroclimática | 3 | 4 | 7 | 4 |
| ALIMENTACIÓN Y AGRICULTURA | 2 | Adaptación de Sistemas de Producción | 4 | 4 | 8 | 5 |
| ALIMENTACIÓN Y AGRICULTURA | 3 | Seguridad Alimentaria y Cambio Climático | 4 | 4 | 8 | 5 |
| ALIMENTACIÓN Y AGRICULTURA | 4 | Agricultura Sostenible y Reducción de Emisiones | 4 | 4 | 8 | 5 |
| ALIMENTACIÓN Y AGRICULTURA | 5 | Justicia Climática e Inclusión | 5 | 3 | 8 | 5 |
| INDUSTRIA EXTRACTIVA | 1 | Diagnóstico Ambiental y Social de Operaciones | 4 | 3 | 7 | 4 |
| INDUSTRIA EXTRACTIVA | 2 | Gestión de Pasivos Ambientales Mineros | 4 | 4 | 8 | 4 |
| INDUSTRIA EXTRACTIVA | 3 | Impactos en Comunidades y Pueblos Indígenas | 4 | 3 | 7 | 4 |
| INDUSTRIA EXTRACTIVA | 4 | Transición Post-Extractiva y Diversificación Económica | 4 | 4 | 8 | 5 |
| INDUSTRIA EXTRACTIVA | 5 | Justicia Climática e Inclusión | 5 | 3 | 8 | 5 |
| GESTIÓN DE RIESGO Y DESASTRES | 1 | Prevención y Reducción del Riesgo | 5 | 3 | 8 | 6 |
| GESTIÓN DE RIESGO Y DESASTRES | 2 | Preparación y Respuesta a Emergencias | 5 | 3 | 8 | 6 |
| GESTIÓN DE RIESGO Y DESASTRES | 3 | Rehabilitación y Reconstrucción Post-Desastre | 5 | 4 | 9 | 6 |
| GESTIÓN DE RIESGO Y DESASTRES | 4 | Riesgo de Desastres y Cambio Climático | 4 | 3 | 7 | 5 |
| GESTIÓN DE RIESGO Y DESASTRES | 5 | Justicia Climática e Inclusión | 6 | 3 | 9 | 8 |
| GÉNERO Y DERECHOS HUMANOS | 1 | Transversalización del Enfoque de Género en la Acción Climática | 4 | 4 | 8 | 4 |
| GÉNERO Y DERECHOS HUMANOS | 2 | Derechos de Acceso: Información y Participación (Acuerdo de Escazú) | 4 | 3 | 7 | 4 |
| GÉNERO Y DERECHOS HUMANOS | 3 | Protección de Personas Defensoras Ambientales | 4 | 3 | 7 | 4 |
| GÉNERO Y DERECHOS HUMANOS | 4 | Consulta Previa, Libre e Informada y Derechos de los Pueblos Indígenas | 4 | 4 | 8 | 4 |
| GÉNERO Y DERECHOS HUMANOS | 5 | Grupos en Situación de Vulnerabilidad y Movilidad Humana por Motivos Climáticos | 4 | 3 | 7 | 4 |
| POBREZA Y DESIGUALDAD | 1 | Protección Social Adaptativa ante Choques Climáticos | 4 | 3 | 7 | 4 |
| POBREZA Y DESIGUALDAD | 2 | Focalización y Acceso de los Hogares de Menores Ingresos a los Programas Climáticos | 4 | 3 | 7 | 4 |
| POBREZA Y DESIGUALDAD | 3 | Empleo y Transición Justa | 4 | 4 | 8 | 4 |
| POBREZA Y DESIGUALDAD | 4 | Diseño Distributivo de Tarifas, Subsidios e Instrumentos Fiscales de la Transición | 4 | 3 | 7 | 4 |
| POBREZA Y DESIGUALDAD | 5 | Pérdidas y Daños y Recuperación de los Hogares Vulnerables | 4 | 3 | 7 | 4 |

## 5. Estrutura real das perguntas

### 5.1 Formatos encontrados

O protótipo utiliza quatro formatos JSON:

| Nível | Campos efetivamente encontrados |
|---|---|
| Bloco do Guia | `transversales`, `sectores` |
| Eixo transversal | `nombre`, `pregCumpl`, `pregGest`, `subejes` |
| Subeixo | `nombre`, `cumplimiento`, `gestion` |
| Setor | `sector`, `subareas` |
| Subárea | `nombre`, `cumplimiento`, `gestion`, `referencias` |
| Pergunta individual | Uma string dentro de `pregCumpl`, `pregGest`, `cumplimiento` ou `gestion` |

Para cada uma das 407 perguntas, o único campo intrínseco confirmado é o **texto em espanhol**. Tipo de auditoria, posição e localização hierárquica são herdados do nome do array e do caminho percorrido no JSON; não são campos da pergunta.

### 5.2 Campos confirmados e ausentes

| Campo candidato | Situação real |
|---|---|
| Identificador | Ausente. |
| Código | Ausente. |
| Ordem | Ausente como campo; apenas posição no array. |
| Idioma | Ausente como campo; o texto está somente em espanhol. |
| Texto | Presente como string. |
| Dimensão | Ausente. |
| Categoria/subcategoria/grupo | Ausentes. |
| Eixo/subeixo/setor/subárea | Contexto herdado, não FK ou ID. |
| Tipo de auditoria | Contexto herdado: `cumplimiento` ou `gestion`. |
| Orientação | Ausente. |
| Justificativa | Ausente. |
| Critério | Ausente. |
| Referência da pergunta | Ausente; existe apenas lista compartilhada na subárea. |
| Resposta esperada | Ausente. |
| Tipo de resposta | Ausente. |
| Obrigatoriedade | Ausente. |
| Dependências | Ausente. |
| Visibilidade condicional | Ausente. |
| Observações | Ausente. |

### 5.3 Identidade e duplicidade

- Não há identificador estável, slug, código ou chave natural declarada.
- A posição no array é o único modo de reconstruir a ordem. Ela é posicional e pode mudar quando itens forem inseridos ou removidos.
- Não há código derivado explicitamente da ordem.
- As 407 strings de pergunta são únicas por igualdade exata.
- Igualdade textual não constitui identidade editorial estável e não deve ser usada isoladamente para versionamento ou autorização.

## 6. Estrutura real das referências

### 6.1 Campos encontrados

Cada referência é uma string no array `referencias` de uma subárea. Não existe objeto de referência.

| Campo candidato | Situação real |
|---|---|
| Identificador | Ausente. |
| Título/citação | Presente como uma única string não estruturada. |
| Instituição | Ausente como campo; às vezes aparece incorporada no texto. |
| Tipo | Ausente como campo. |
| Ano | Ausente como campo; às vezes aparece incorporado no texto. |
| URL | Ausente em todas as 224 ocorrências. |
| Idioma | Ausente como campo; textos em espanhol. |
| Descrição | Ausente como campo. |
| Seção/artigo/página | Ausente como campo; às vezes aparece incorporado na citação. |
| Relação com pergunta | Ausente. A lista pertence à subárea. |
| Ordem | Ausente como campo; apenas posição no array. |

### 6.2 Qualidade e relações

- Ocorrências: 224.
- Strings únicas por igualdade exata: 223.
- Referências sem URL: 224.
- URLs repetidas: não aplicável, pois não existe URL.
- URLs inválidas: não avaliável, pois não existe URL.
- Relação muitos-para-muitos explícita: ausente.
- Relação contextual: todas as perguntas de uma subárea compartilham visualmente o mesmo array de referências, sem indicação de qual citação sustenta qual pergunta.
- Há diversos títulos semelhantes do mesmo instrumento com artigos ou recortes diferentes. Sem identificador normalizado, não é seguro consolidá-los automaticamente.
- Algumas perguntas citam instrumentos em seu próprio texto, mas isso também não cria uma relação estruturada.

A única duplicidade exata é:

`Resolución AG ONU 76/300: derecho humano a un medio ambiente limpio, saludable y sostenible`

Ela ocorre em:

1. `GÉNERO Y DERECHOS HUMANOS` → `Protección de Personas Defensoras Ambientales`;
2. `GÉNERO Y DERECHOS HUMANOS` → `Grupos en Situación de Vulnerabilidad y Movilidad Humana por Motivos Climáticos`.

Essa repetição pode representar uma mesma referência usada por duas subáreas, mas a fonte não fornece identidade que confirme a deduplicação conceitual.

## 7. Idiomas

### 7.1 Textos oficiais de interface

Os textos abaixo são reproduzidos literalmente. Eles existem no dicionário I18N, mas não são renderizados por uma tela do Guia.

| Chave/uso | ES | PT | EN |
|---|---|---|---|
| Nome na navegação | Guía de Preguntas | Guia de Perguntas | Question Guide |
| Card — título | Guía de Preguntas | Guia de Perguntas | Question Guide |
| Card — descrição | Contenido técnico orientador para el diseño y ejecución de auditorías en sectores con alta relevancia para la acción climática. | Conteúdo técnico orientador para o desenho e execução de auditorias em setores de alta relevância para a ação climática. | Technical guidance for designing and running audits in climate-relevant sectors. |
| Categoria do recurso | Guía metodológica | Guia metodológica | Methodological guide |
| Eyebrow | Contenido orientador | Conteúdo orientador | Guiding content |
| Título | Guía de preguntas de auditoría | Guia de perguntas de auditoria | Audit question guide |
| Descrição | Preguntas orientadoras para el diseño y ejecución de auditorías, organizadas por ejes transversales y sectores de alta relevancia climática. | Perguntas orientadoras para o desenho e execução de auditorias, organizadas por eixos transversais e setores de alta relevância climática. | Guiding questions for designing and running audits, organized by cross-cutting axes and climate-relevant sectors. |
| Tipo de auditoria | Tipo de auditoría: | Tipo de auditoria: | Audit type: |
| Conformidade | Cumplimiento | Conformidade | Compliance |
| Gestão | Gestión | Gestão | Performance |
| Nota transversal | Este eje es transversal: sus preguntas aplican a cualquier sector auditado. | Este eixo é transversal: suas perguntas se aplicam a qualquer setor auditado. | This axis is cross-cutting: its questions apply to any audited sector. |
| Pergunta do eixo | Pregunta de auditoría del eje | Pergunta de auditoria do eixo | Audit question for the axis |
| Seleção de setor | Sector a auditar: | Setor a auditar: | Sector to audit: |
| Referências | Referencias normativas | Referências normativas | Normative references |
| Eixos | Ejes transversales | Eixos transversais | Cross-cutting axes |
| Setores | Sectores | Setores | Sectors |

`Guia metodológica` é o texto português literal do protótipo. Não foi corrigido.

### 7.2 Separação entre interface e conteúdo

| Camada | ES | PT | EN | Fallback real |
|---|---|---|---|---|
| Interface | Presente | Presente | Presente | `translate(k)` retorna a própria chave quando a tradução não existe. |
| Perguntas | Presente | Ausente | Ausente | Não há mecanismo de fallback; os dados permanecem em espanhol independentemente de `currentLang`. |
| Referências | Presente | Ausente | Ausente | Não há mecanismo de fallback; os dados permanecem em espanhol. |
| Nomes de eixos/subeixos/setores/subáreas | Presente | Ausente | Ausente | Não há campos traduzidos nem função de tradução de conteúdo. |

O espanhol é o único conteúdo disponível. A simples exibição da string espanhola em PT/EN seria um fallback de fato, mas esse comportamento não está formalizado porque não existe renderização do Guia.

## 8. Interações e persistência

Não foram encontradas interações funcionais do Guia. Em particular, não existem:

- busca, filtros ou ordenação controlável;
- navegação entre eixos e setores;
- seleção de tipo de auditoria;
- expansão/recolhimento de subeixos ou subáreas;
- seleção, marcação ou priorização de perguntas;
- resposta, comentário, evidência ou indicador;
- progresso, resultado, relatório, exportação ou impressão;
- links normativos externos;
- persistência em localStorage, sessão, API ou banco;
- dependência de login, usuário, EFS, papel ou autorização.

Os controles sugeridos pelos rótulos I18N são apenas intenção incompleta. Não há comportamento simulado a preservar.

## 9. Comparação com o repositório Django

### 9.1 Inventário atual

- Models de conteúdo relacionados por tema: `Setor`, `NormaInternacional`, `Experiencia`, `BancoTecnico` e `Ferramenta`.
- Infraestrutura de proveniência: `LoteImportacaoConteudo` e `ItemLoteImportacaoConteudo`.
- O enum do item de lote já prevê `versao_guia`, `eixo`, `subeixo`, `subarea`, `pergunta`, `referencia` e `experiencia_pergunta_guia`.
- Não existem models de domínio do Guia.
- Não existe URL, view, template, static específico ou management command do Guia.
- `Experiencia.perguntas_chave*` e `Experiencia.criterios_utilizados*` são textos livres de uma Boa Prática; não são perguntas canônicas do Guia.

### 9.2 Respostas às questões de compatibilidade

| Questão | Resposta baseada no código atual |
|---|---|
| 1. Existe model parcialmente compatível? | Apenas o ledger é compatível para proveniência. Nenhum model representa a hierarquia e as perguntas do Guia. |
| 2. Alguma entidade pode ser reutilizada sem acoplamento indevido? | `LoteImportacaoConteudo` e `ItemLoteImportacaoConteudo`, sim, como infraestrutura. A reutilização de `Setor` exige mapeamento aprovado dos nove setores e não está comprovada. |
| 3. `NormaInternacional` representa as referências? | Não diretamente. Ela modela uma norma identificável com nomes/resumos traduzíveis e URL; as referências do Guia são citações livres, sem URL, agrupadas por subárea. Pode ser destino opcional de reconciliação curada futura, não substituto automático. |
| 4. `BancoTecnico` representa parte do Guia? | Não. É catálogo de documentos/recursos com título, descrição, tipo, setor, dimensões e URL; não representa versão, hierarquia, pergunta ou citação. |
| 5. `Ferramenta` tem relação real com o Guia? | Não no protótipo. Não há FK, código compartilhado, recomendação ou referência de ferramenta nas perguntas. |
| 6. É necessário novo conjunto de models? | Sim, se a implementação for aprovada. O conjunto precisa preservar versão, hierarquia, perguntas, referências e proveniência. |
| 7. Há risco de conflito de nomes? | Sim. `Setor`, `NormaInternacional`, campos livres de `Experiencia` e os nomes genéricos do ledger podem induzir reutilização indevida. Nomes e related names devem ser definidos após decisão de integração. |
| 8. Há dependência com usuário, EFS ou autorização? | Nenhuma no conteúdo/protótipo atual. Curadoria futura exigirá autoria e autorização administrativa, mas isso é uma funcionalidade nova. |
| 9. O Guia é público, autenticado ou misto? | O dataset está embutido em um HTML público, mas não existe tela. A intenção de consulta pública é uma inferência coerente com a plataforma, não um comportamento confirmável do módulo; a decisão deve ser registrada. |
| 10. Há persistência de respostas? | Não. Há apenas conteúdo de consulta embutido. |

### 9.3 Compatibilidade que não deve ser presumida

- Os nove rótulos setoriais do Guia são compostos e não foram reconciliados com os registros atuais de `Setor` usados por Boas Práticas e Ferramentas.
- As 223 citações únicas não equivalem automaticamente aos registros de `NormaInternacional`.
- A lista de entidades permitidas no ledger não aprova schema, cardinalidades, publicação ou telas.
- A menção conceitual `AuditQuestion` em `.codex/docs/DATA_MODEL.md` é uma proposta resumida, não código nem regra suficiente para implementação.

## 10. Modelo conceitual candidato

O modelo abaixo é deliberadamente mínimo. “Confirmado” significa que a informação existe na fonte; “inferido” significa necessidade técnica para persistência segura. Nenhuma entidade está autorizada para implementação nesta etapa.

### 10.1 `VersaoGuia`

**Finalidade:** delimitar um conjunto coerente e publicável do Guia.

**Campos confirmados:** nenhum campo de versão existe no protótipo.

**Relacionamentos confirmados:** o objeto `guia` agrega toda a hierarquia.

**Campos inferidos:** código da versão, situação editorial, idioma canônico `es`, hash da fonte, datas de criação/publicação, ordem/vigência e lote de origem.

**Riscos:** atualizar conteúdo sem versão tornaria impossível reproduzir as 407 perguntas auditadas.

**Decisão registrada:** GUIA-02 aprovou rascunho editável, versão publicada imutável, coexistência histórica, vigência única e publicação explícita com data, hash e lote, sem publicação automática pela importação.

### 10.2 `EixoGuia`

**Finalidade:** representar os três eixos transversais.

**Campos confirmados:** nome em espanhol, posição, pergunta-raiz de conformidade e pergunta-raiz de gestão, coleção de subeixos.

**Relacionamentos confirmados:** pertence ao Guia e possui subeixos.

**Campos inferidos:** código estável, versão, ordem explícita, traduções opcionais e situação ativa.

**Riscos:** transformar a posição atual em identidade quebra rastreabilidade após reordenação.

**Decisão pendente:** se perguntas-raiz serão registros de `PerguntaGuia` ou campos do eixo. A primeira opção preserva uma única semântica de pergunta.

### 10.3 `SubeixoGuia`

**Finalidade:** representar os oito agrupamentos dos eixos transversais.

**Campos confirmados:** nome em espanhol, posição, listas de perguntas de conformidade e gestão.

**Relacionamentos confirmados:** pertence a um eixo.

**Campos inferidos:** código estável, ordem explícita, traduções opcionais e situação ativa.

**Riscos:** a fonte contém grafias que precisam de validação negocial antes de qualquer saneamento.

**Decisão registrada:** GUIA-03 aprovou códigos estáveis fornecidos por fonte institucional controlada. Correções editoriais permanecem pendentes em GUIA-06.

### 10.4 `SetorGuia`

**Finalidade:** representar os nove agrupamentos setoriais do Guia.

**Campos confirmados:** nome em espanhol, posição e coleção de subáreas.

**Relacionamentos confirmados:** pertence ao Guia e possui subáreas.

**Campos inferidos:** código estável, versão, ordem e traduções opcionais.

**Riscos:** reutilizar `Setor` sem mapeamento pode renomear ou ampliar indevidamente taxonomias compartilhadas por outros módulos; criar outra entidade pode duplicar conceitos.

**Decisão registrada:** GUIA-04 aprovou taxonomia própria `SetorGuia`, sem reutilização ou sincronização automática com `Setor`; eventual mapeamento será explícito, opcional, versionado e decidido em fase separada.

### 10.5 `SubareaGuia`

**Finalidade:** representar as 47 subdivisões setoriais.

**Campos confirmados:** nome em espanhol, posição, perguntas de conformidade, perguntas de gestão e lista de referências.

**Relacionamentos confirmados:** pertence a um setor; agrupa perguntas e referências.

**Campos inferidos:** código estável, ordem explícita, traduções opcionais e situação ativa.

**Riscos:** nomes iguais, como `Justicia Climática e Inclusión`, aparecem em setores diferentes; unicidade global por nome seria incorreta.

**Decisão pendente:** escopo de unicidade e política de tradução.

### 10.6 `PerguntaGuia`

**Finalidade:** persistir cada pergunta preservando seu contexto e tipo de auditoria.

**Campos confirmados:** texto espanhol; tipo `conformidade` ou `gestao` herdado; localização em eixo, subeixo ou subárea; posição herdada.

**Relacionamentos confirmados:** cada pergunta aparece em exatamente um nó da hierarquia na fonte.

**Campos inferidos:** código estável, versão, tipo explícito, texto PT/EN opcional, ordem explícita, situação ativa e exatamente um escopo entre eixo, subeixo e subárea.

**Riscos:** não há identidade estável entre revisões; hash ou texto não bastam para decidir continuidade sem curadoria.

**Decisão registrada:** GUIA-03 definiu identidade por código institucional + versão. A exigência de traduções para publicação permanece pendente em GUIA-05.

### 10.7 `ReferenciaGuia`

**Finalidade:** preservar uma citação da fonte sem fingir metadados inexistentes.

**Campos confirmados:** texto espanhol da citação.

**Relacionamentos confirmados:** nenhuma relação direta com pergunta; ocorrência dentro de uma subárea.

**Campos inferidos:** código estável, texto PT/EN opcional, URL oficial opcional após validação, vínculo opcional e curado com `NormaInternacional`, status de verificação.

**Riscos:** deduplicação automática pode fundir recortes normativos diferentes; URL ou ano inventado comprometeria a evidência.

**Decisão pendente:** granularidade de normalização e critérios de reconciliação com Marcos Normativos.

### 10.8 `SubareaReferenciaGuia`

**Finalidade:** registrar a relação e a ordem realmente confirmadas entre subárea e referência.

**Campos confirmados:** subárea, referência textual e posição da ocorrência.

**Relacionamentos confirmados:** uma subárea possui várias ocorrências; a mesma citação textual pode aparecer em mais de uma subárea.

**Campos inferidos:** FKs, ordem, lote/item de origem e eventual nota de curadoria.

**Riscos:** criar diretamente `PerguntaReferenciaGuia` atribuiria uma precisão que a fonte não possui.

**Decisão registrada:** GUIA-07 mantém a relação no nível de subárea e veda `PerguntaReferenciaGuia`; eventual relação por pergunta exige fonte institucional explícita e nova decisão de schema.

### 10.9 Infraestrutura reutilizável

`LoteImportacaoConteudo` e `ItemLoteImportacaoConteudo` são candidatos comprovados para proveniência, contagens, divergências, snapshots e rollback. A allowlist atual já contém os principais nomes do Guia. Antes da implementação, será necessário confirmar se ela deve incluir separadamente setor do Guia e a relação subárea–referência; isso é uma alteração de schema futura, não parte deste levantamento.

### 10.10 Fora do modelo mínimo

Não estão confirmados pelo protótipo e não devem entrar na fundação sem decisão:

- respostas, indicadores, evidências e progresso;
- formulários autenticados ou autorização por EFS;
- associação com Boas Práticas, Ferramentas ou Marcos por similaridade textual;
- recomendação automatizada;
- exportação, impressão ou geração de relatório;
- busca, filtros e seleção persistida.

## 11. Decisões e pendências

| ID | Decisão necessária | Motivo | Bloqueia |
|---|---|---|---|
| GUIA-01 | Confirmar se a consulta será pública e se alguma função futura exigirá autenticação. | O protótipo não tem tela nem autorização do Guia. | Rota e política de acesso. |
| GUIA-02 | **Aprovada:** rascunhos são editáveis; versões publicadas são imutáveis; somente uma versão pode estar vigente; publicação registra data, hash e lote e nunca ocorre automaticamente na importação. | A fonte não possui versão ou histórico. | Resolvido para a fundação estrutural; detalhes em `FASE2D1_DECISOES_FUNDACAO_GUIA.md`. |
| GUIA-03 | **Aprovada:** eixos, subeixos, setores, subáreas, perguntas e referências terão códigos estáveis fornecidos por fonte institucional controlada e reconciliados por código + versão. | A fonte atual só possui ordem posicional e ainda não fornece os códigos. | Schema resolvido; importação permanece bloqueada até a fonte codificada. |
| GUIA-04 | **Aprovada:** criar `SetorGuia`, sem reutilização ou sincronização automática com `Setor`; eventual mapeamento será explícito, opcional e aprovado separadamente. | Não há compatibilidade comprovada com os catálogos atuais. | Resolvido para o schema de setor/subárea. |
| GUIA-05 | Definir política PT/EN para hierarquia, perguntas e referências. | Somente a interface está traduzida. | Publicação trilíngue. |
| GUIA-06 | Validar correções editoriais do espanhol, sem saneamento silencioso. | Há anomalias literais na fonte. | Carga institucional final. |
| GUIA-07 | **Aprovada:** referências permanecem no nível de subárea por ocorrência ordenada; não criar relação pergunta–referência nem inferir vínculos. | A fonte não contém relação pergunta–referência. | Resolvido para a fundação estrutural; nova relação exige fonte e decisão próprias. |
| GUIA-08 | Definir critérios de deduplicação e reconciliação com `NormaInternacional`. | 224 ocorrências, 223 textos únicos e títulos semelhantes sem IDs. | Normalização normativa. |
| GUIA-09 | Fornecer/validar URLs oficiais e metadados das referências, se necessários. | Nenhuma referência possui URL estruturada. | Links públicos e verificação. |
| GUIA-10 | Homologar a UX do Guia. | Não existe página visual oficial executável para transportar. | Templates, interações e fidelidade visual. |
| GUIA-11 | Confirmar se haverá seleção de perguntas, resultado, exportação ou impressão. | Todas essas funções estão ausentes. | Fases de interação. |
| GUIA-12 | Confirmar explicitamente se respostas serão persistidas no futuro. | O protótipo é apenas conteúdo embutido. | Qualquer fase de respostas/indicadores. |
| GUIA-13 | Confirmar se haverá associações curadas com Boas Práticas ou Ferramentas. | Não há relação real na fonte. | Entidades associativas futuras. |

## 12. Riscos principais

1. **Identidade instável:** ordem e texto são os únicos marcadores atuais; reordenações podem ser interpretadas como novos registros.
2. **Fonte monolíngue:** perguntas, referências e taxonomias estão apenas em espanhol; tradução automática ou inventada é vedada.
3. **Sem fonte visual funcional:** os poucos tokens/CSS não definem layout, estados, foco, responsividade ou acessibilidade do Guia.
4. **Referências não normalizadas:** as citações não possuem IDs, URLs ou metadados separados e sua relação é apenas por subárea.
5. **Acoplamento indevido:** reutilizar `NormaInternacional`, `BancoTecnico`, `Ferramenta`, `Experiencia.perguntas_chave` ou `Setor` sem mapeamento altera a semântica de outros módulos.
6. **Saneamento silencioso:** grafias e possíveis erros do protótipo precisam de validação institucional antes de mudança.
7. **Carga incompleta ou duplicada:** 407 perguntas e 224 ocorrências exigem validações exatas, hashes, lote persistente e rollback auditável.
8. **Publicação sem curadoria:** a ausência de situação editorial no protótipo não autoriza publicação direta do conteúdo importado.
9. **Acessibilidade não especificada:** seleção, hierarquia e grandes listas precisarão de desenho próprio testado com teclado, foco, zoom e tecnologia assistiva.
10. **Privacidade futura:** o conteúdo atual não trata dados pessoais; persistir respostas, evidências ou autoria criaria um novo risco e exige fase e decisão próprias.

## 13. Subfases recomendadas

| Subfase | Objetivo | Arquivos prováveis | Migration | Risco/dependências | Testes necessários | Critério de aceite |
|---|---|---|---|---|---|---|
| 2D.1 — fundação de dados | Criar versão, hierarquia, perguntas e referências no nível confirmado. | `praticas/models.py`, `praticas/admin.py`, nova migration, testes de models e documentação. | Sim, somente estrutural. | GUIA-02, 03, 04 e 07 registradas em `FASE2D1_DECISOES_FUNDACAO_GUIA.md`; permanece o risco de cardinalidade errada. | Constraints, unicidade contextual, exclusão, publicação, imutabilidade e SQLite limpo. | Schema representa 3/8/9/47 e dois tipos sem dados embutidos na migration. |
| 2D.2 — importação controlada | Importar o conteúdo espanhol com códigos aprovados, hash, lote, itens, dry-run e reversão. | Novo management command, arquivo-fonte institucional controlado, testes do importador e documentação. | Não, salvo ajuste previamente aprovado do ledger. | Depende de GUIA-03, 06 e hash/fonte homologados; risco de divergência posicional. | Dry-run, idempotência, contagens 407/224, falha/rollback, divergência, segunda reversão, preservação de traduções. | Uma versão rascunho reproduz exatamente as contagens e cada item tem proveniência. |
| 2D.3 — catálogo público | Criar rota pública de consulta e estado editorial honesto. | `praticas/views.py`, `praticas/urls.py`, template, CSS, testes de view/i18n. | Não prevista. | Depende de GUIA-01, 05 e 10; sem visual oficial completo. | Acesso público, somente versão publicada, PT/ES/EN com fallback aprovado, estados vazio/indisponível. | Conteúdo não publicado não vaza; a página comunica claramente idioma e versão. |
| 2D.4 — detalhe e navegação | Navegar por eixos, subeixos, setores, subáreas e tipo de auditoria. | Views/URLs, includes, CSS, JavaScript progressivo e testes. | Não prevista. | Depende de GUIA-10 e desenho acessível; listas longas. | Teclado, foco, ARIA, URL/estado, 320–1440 px, zoom 200%, ausência de rolagem horizontal. | Toda pergunta é alcançável e o estado é compreensível sem JavaScript quando aplicável. |
| 2D.5 — referências | Exibir citações preservadas e reconciliar apenas vínculos aprovados. | Models/serviço/importador se a reconciliação exigir schema; templates e testes. | Possível, conforme GUIA-07 a 09. | Risco de consolidar instrumentos distintos ou criar URL não oficial. | Deduplicação explícita, escopo por subárea, links seguros, ausência de vínculo automático. | 224 ocorrências permanecem rastreáveis; qualquer norma/URL é curada e auditável. |
| 2D.6 — interações | Implementar somente busca, filtros, seleção ou saída que forem homologados. | Views, forms se necessários, template, JS/CSS e testes. | Não prevista para estado efêmero; possível se houver persistência. | Totalmente dependente de GUIA-10 e 11; não há comportamento de referência. | Busca/filtros, estado na URL, teclado, foco, redução de movimento, resultados e impressão/exportação se aprovadas. | Cada interação possui requisito e desenho homologados, sem simulação. |
| 2D.7 — persistência opcional | Persistir respostas/indicadores somente após confirmação formal. | Novos models, migrations, forms, views, autorização, templates e testes de segurança. | Sim, se autorizada. | Depende de GUIA-01 e 12; amplia privacidade, autorização e vínculo institucional. | Autorização por objeto no backend, isolamento entre autores/EFS, histórico, concorrência, proteção de dados. | Não iniciar sem requisitos completos; nenhuma resposta existe por padrão. |
| 2D.8 — fidelidade visual e QA | Homologar o módulo completo em navegador e consolidar regressões. | CSS/templates/JS e testes direcionados; documentação de riscos. | Não. | Depende da homologação visual GUIA-10 e da conclusão das fases aprovadas. | Comparação visual 320/768/1024/1440, teclado, zoom, leitor de tela manual, contraste, suíte completa e `diff --check`. | Fidelidade aprovada, nenhum erro de console, contagens e idiomas preservados, auditoria manual pendente registrada quando aplicável. |

As fases 2D.6 e 2D.7 não são compromissos de escopo. Elas existem para isolar funcionalidades ausentes do protótipo e só devem ser abertas após decisão explícita.

## 14. Critérios de aceite para iniciar implementação

Antes de 2D.1:

1. **Atendido:** decisões GUIA-02, GUIA-03, GUIA-04 e GUIA-07 registradas em `FASE2D1_DECISOES_FUNDACAO_GUIA.md`;
2. aprovar a fonte e seu hash, sem correção silenciosa;
3. **Atendido:** política de publicação e versão definida em GUIA-02;
4. demonstrar que o schema não reutiliza models incompatíveis;
5. preservar o ledger existente e planejar rollback em SQLite e PostgreSQL.

Antes de publicar qualquer tela:

1. registrar GUIA-01, GUIA-05 e GUIA-10;
2. definir fallback explícito para conteúdo sem PT/EN;
3. mostrar somente versão publicada;
4. preservar as contagens e a hierarquia da versão importada;
5. testar acessibilidade, responsividade e ausência de conteúdo fictício.

Antes de referências com links ou relações por pergunta:

1. registrar GUIA-07, GUIA-08 e GUIA-09;
2. não inferir vínculos por similaridade textual;
3. manter a citação original e a proveniência mesmo após normalização;
4. usar somente URLs oficiais validadas.

Antes de qualquer persistência de respostas:

1. registrar GUIA-01 e GUIA-12;
2. definir finalidade, perfis, autorização por objeto, retenção, histórico e privacidade;
3. criar uma fase independente com migration, testes de segurança e rollback;
4. não acoplar automaticamente resposta a vínculo usuário–EFS sem regra aprovada.

## 15. Conclusão do levantamento

O protótipo confirma uma base de conhecimento relevante e extensa: 3 eixos, 8 subeixos, 9 setores, 47 subáreas, 407 perguntas e 224 ocorrências de referências. Ele não confirma uma implementação de interface do Guia. A próxima decisão segura é aprovar identidade, versionamento, taxonomia setorial, granularidade das referências e política de idiomas antes de criar qualquer model ou migration.
