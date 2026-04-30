from django.core.management.base import BaseCommand

from praticas.models import (
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class Command(BaseCommand):
    help = "Carrega dados demonstrativos institucionais para apresentação executiva do MVP."

    def handle(self, *args, **options):
        paises = self.criar_paises()
        efs = self.criar_efs(paises)
        tipos = self.criar_tipos()
        setores = self.criar_setores()
        temas = self.criar_temas()
        normas = self.criar_normas()
        dimensoes = self.criar_dimensoes()
        grupos = self.criar_grupos()
        self.criar_experiencias(efs, paises, tipos, setores, temas, normas, dimensoes, grupos)
        self.criar_banco_tecnico(setores, dimensoes)

        self.stdout.write(self.style.SUCCESS("Dados executivos de demonstração carregados com sucesso."))

    def criar_paises(self):
        dados = [
            ("BRA", "Brasil", "Brasil", "Brazil"),
            ("CHL", "Chile", "Chile", "Chile"),
            ("COL", "Colômbia", "Colombia", "Colombia"),
            ("ECU", "Equador", "Ecuador", "Ecuador"),
            ("PRY", "Paraguai", "Paraguay", "Paraguay"),
            ("MEX", "México", "México", "Mexico"),
        ]
        objetos = {}
        for sigla, nome, nome_es, nome_en in dados:
            obj, _ = Pais.objects.update_or_create(
                sigla=sigla,
                defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en},
            )
            objetos[sigla] = obj
        return objetos

    def criar_efs(self, paises):
        dados = [
            ("TCU", "Tribunal de Contas da União", "Tribunal de Cuentas de la Unión", "Federal Court of Accounts", "BRA"),
            ("CGR Chile", "Contraloría General de la República do Chile", "Contraloría General de la República de Chile", "Office of the Comptroller General of Chile", "CHL"),
            ("CGR Colombia", "Contraloría General de la República da Colômbia", "Contraloría General de la República de Colombia", "Office of the Comptroller General of Colombia", "COL"),
            ("CGE Ecuador", "Contraloría General del Estado do Equador", "Contraloría General del Estado del Ecuador", "Office of the Comptroller General of Ecuador", "ECU"),
            ("CGR Paraguay", "Contraloría General de la República do Paraguai", "Contraloría General de la República del Paraguay", "Office of the Comptroller General of Paraguay", "PRY"),
            ("ASF", "Auditoría Superior de la Federación do México", "Auditoría Superior de la Federación de México", "Superior Audit Office of Mexico", "MEX"),
        ]
        objetos = {}
        for sigla, nome, nome_es, nome_en, pais_sigla in dados:
            obj, _ = EFS.objects.update_or_create(
                sigla=sigla,
                defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en, "pais": paises[pais_sigla]},
            )
            objetos[sigla] = obj
        return objetos

    def criar_taxonomia(self, modelo, dados):
        objetos = {}
        for nome, nome_es, nome_en in dados:
            obj, _ = modelo.objects.update_or_create(
                nome=nome,
                defaults={"nome_es": nome_es, "nome_en": nome_en},
            )
            objetos[nome] = obj
        return objetos

    def criar_tipos(self):
        return self.criar_taxonomia(TipoExperiencia, [
            ("Auditoria", "Auditoría", "Audit"),
            ("Avaliação de política pública", "Evaluación de política pública", "Public policy evaluation"),
            ("Pesquisa", "Investigación", "Research"),
            ("Capacitação/treinamento", "Capacitación/entrenamiento", "Training"),
            ("Ferramenta/metodologia", "Herramienta/metodología", "Tool/methodology"),
        ])

    def criar_setores(self):
        return self.criar_taxonomia(Setor, [
            ("Infraestrutura", "Infraestructura", "Infrastructure"),
            ("Água", "Agua", "Water"),
            ("Energia", "Energía", "Energy"),
            ("Meio ambiente", "Medio ambiente", "Environment"),
            ("Tecnologia", "Tecnología", "Technology"),
        ])

    def criar_temas(self):
        return self.criar_taxonomia(TemaTransversal, [
            ("Gênero", "Género", "Gender"),
            ("Mulheres", "Mujeres", "Women"),
            ("Populações vulneráveis", "Poblaciones vulnerables", "Vulnerable populations"),
            ("Povos indígenas", "Pueblos indígenas", "Indigenous peoples"),
            ("Comunidades quilombolas", "Comunidades quilombolas", "Quilombola communities"),
            ("LGBTQI+", "LGBTQI+", "LGBTQI+"),
            ("Direitos humanos", "Derechos humanos", "Human rights"),
        ])

    def criar_dimensoes(self):
        return self.criar_taxonomia(DimensaoJusticaClimatica, [
            ("Distributiva", "Distributiva", "Distributive"),
            ("Procedimental", "Procedimental", "Procedural"),
            ("Reconhecimento", "Reconocimiento", "Recognition"),
            ("Intergeracional", "Intergeneracional", "Intergenerational"),
        ])

    def criar_grupos(self):
        return self.criar_taxonomia(GrupoVulneravel, [
            ("Famílias de baixa renda", "Familias de bajos ingresos", "Low-income households"),
            ("Comunidades rurais", "Comunidades rurales", "Rural communities"),
            ("Povos indígenas", "Pueblos indígenas", "Indigenous peoples"),
            ("Mulheres chefes de família", "Mujeres jefas de hogar", "Women heads of household"),
            ("População em áreas de risco", "Población en zonas de riesgo", "Population in risk areas"),
        ])

    def criar_normas(self):
        dados = [
            (
                "Acordo de Paris",
                "Acuerdo de París",
                "Paris Agreement",
                "Marco global para fortalecer a resposta à mudança do clima, incluindo adaptação, mitigação e financiamento climático.",
                "Marco global para fortalecer la respuesta al cambio climático, incluyendo adaptación, mitigación y financiamiento climático.",
                "Global framework to strengthen the response to climate change, including adaptation, mitigation and climate finance.",
                "https://unfccc.int/process-and-meetings/the-paris-agreement",
            ),
            (
                "Agenda 2030 — ODS 13",
                "Agenda 2030 — ODS 13",
                "2030 Agenda — SDG 13",
                "Objetivo de Desenvolvimento Sustentável voltado à ação contra a mudança global do clima.",
                "Objetivo de Desarrollo Sostenible orientado a la acción contra el cambio climático.",
                "Sustainable Development Goal focused on climate action.",
                "https://sdgs.un.org/goals/goal13",
            ),
            (
                "Marco de Sendai para Redução do Risco de Desastres",
                "Marco de Sendai para la Reducción del Riesgo de Desastres",
                "Sendai Framework for Disaster Risk Reduction",
                "Marco internacional para reduzir riscos de desastres e perdas associadas em vidas, meios de subsistência e infraestrutura.",
                "Marco internacional para reducir riesgos de desastres y pérdidas asociadas en vidas, medios de vida e infraestructura.",
                "International framework to reduce disaster risk and related losses in lives, livelihoods and infrastructure.",
                "https://www.undrr.org/implementing-sendai-framework/what-sendai-framework",
            ),
            (
                "Acordo de Escazú",
                "Acuerdo de Escazú",
                "Escazú Agreement",
                "Acordo regional sobre acesso à informação, participação pública e justiça em assuntos ambientais na América Latina e Caribe.",
                "Acuerdo regional sobre acceso a la información, participación pública y justicia en asuntos ambientales en América Latina y el Caribe.",
                "Regional agreement on access to information, public participation and justice in environmental matters in Latin America and the Caribbean.",
                "https://www.cepal.org/en/escazuagreement",
            ),
            (
                "ISSAI 140 — Gestão da qualidade",
                "ISSAI 140 — Gestión de la calidad",
                "ISSAI 140 — Quality Management",
                "Norma da INTOSAI para apoiar a qualidade dos trabalhos das Entidades Fiscalizadoras Superiores.",
                "Norma de INTOSAI para apoyar la calidad de los trabajos de las Entidades Fiscalizadoras Superiores.",
                "INTOSAI standard to support quality management in Supreme Audit Institutions.",
                "https://www.issai.org/",
            ),
        ]

        objetos = {}
        for nome, nome_es, nome_en, resumo, resumo_es, resumo_en, url in dados:
            obj, _ = NormaInternacional.objects.update_or_create(
                nome=nome,
                defaults={
                    "nome_es": nome_es,
                    "nome_en": nome_en,
                    "resumo": resumo,
                    "resumo_es": resumo_es,
                    "resumo_en": resumo_en,
                    "url_referencia": url,
                },
            )
            objetos[nome] = obj
        return objetos

    def criar_experiencias(self, efs, paises, tipos, setores, temas, normas, dimensoes, grupos):
        experiencias = [
            {
                "titulo": "Auditoria da resiliência climática em obras de drenagem urbana",
                "titulo_es": "Auditoría de resiliencia climática en obras de drenaje urbano",
                "titulo_en": "Audit of climate resilience in urban drainage works",
                "efs": efs["TCU"], "pais": paises["BRA"], "tipo": tipos["Auditoria"], "setor": setores["Infraestrutura"], "ano": 2025,
                "descricao": "Avaliação de projetos de drenagem urbana em municípios expostos a enchentes, com foco na incorporação de riscos climáticos e impactos sobre populações vulneráveis.",
                "descricao_es": "Evaluación de proyectos de drenaje urbano en municipios expuestos a inundaciones, con foco en la incorporación de riesgos climáticos e impactos sobre poblaciones vulnerables.",
                "descricao_en": "Assessment of urban drainage projects in municipalities exposed to floods, focusing on climate risk integration and impacts on vulnerable populations.",
                "enfoque": "A auditoria considerou a distribuição territorial dos benefícios da obra, a exposição de famílias de baixa renda e a transparência dos critérios de priorização.",
                "enfoque_es": "La auditoría consideró la distribución territorial de los beneficios de la obra, la exposición de familias de bajos ingresos y la transparencia de los criterios de priorización.",
                "enfoque_en": "The audit considered the territorial distribution of project benefits, the exposure of low-income households and transparency in prioritization criteria.",
                "objetivo": "Verificar se obras de drenagem financiadas com recursos públicos incorporam cenários climáticos e critérios de justiça climática.",
                "perguntas": "Os projetos usam cenários de chuva extrema? Os bairros mais vulneráveis foram priorizados? Há participação social documentada?",
                "criterios": "Acordo de Paris, Marco de Sendai, planos municipais de adaptação e normas técnicas de drenagem urbana.",
                "metodologia": "Análise documental, mapas de risco, entrevistas com gestores e cruzamento entre localização das obras e indicadores socioambientais.",
                "ferramentas": "Matriz de risco climático, checklist de justiça climática e painel geoespacial de obras.",
                "resultados": "Foram identificadas fragilidades na justificativa técnica de priorização e ausência de análise sistemática de vulnerabilidade social em parte dos projetos.",
                "recomendacoes": "Incluir análise de risco climático nos estudos preliminares e adotar critérios públicos de priorização de áreas vulneráveis.",
                "replicabilidade": "Alta. A metodologia pode ser aplicada a obras de saneamento, macrodrenagem, contenção de encostas e infraestrutura urbana.",
                "contato": "Equipe de Auditoria de Infraestrutura Climática", "email": "infra.clima@tcu.gov.br", "responsavel": "Coordenação de Auditoria de Infraestrutura",
                "temas": ["Populações vulneráveis", "Direitos humanos"], "normas": ["Acordo de Paris", "Marco de Sendai para Redução do Risco de Desastres"], "dimensoes": ["Distributiva", "Procedimental"], "grupos": ["Famílias de baixa renda", "População em áreas de risco"], "destacado": True, "relevante": True,
            },
            {
                "titulo": "Avaliação de tarifas sociais de água em contexto de seca",
                "titulo_es": "Evaluación de tarifas sociales de agua en contexto de sequía",
                "titulo_en": "Evaluation of social water tariffs in drought contexts",
                "efs": efs["CGR Chile"], "pais": paises["CHL"], "tipo": tipos["Avaliação de política pública"], "setor": setores["Água"], "ano": 2025,
                "descricao": "Avaliação da cobertura e efetividade de subsídios tarifários para garantir acesso à água em territórios afetados por estiagem prolongada.",
                "descricao_es": "Evaluación de la cobertura y efectividad de subsidios tarifarios para garantizar acceso al agua en territorios afectados por sequía prolongada.",
                "descricao_en": "Evaluation of the coverage and effectiveness of tariff subsidies to ensure access to water in territories affected by prolonged drought.",
                "enfoque": "A experiência analisou se mulheres chefes de família, comunidades rurais e domicílios de baixa renda acessam o benefício de forma equitativa.",
                "enfoque_es": "La experiencia analizó si mujeres jefas de hogar, comunidades rurales y hogares de bajos ingresos acceden al beneficio de forma equitativa.",
                "enfoque_en": "The experience analyzed whether women heads of household, rural communities and low-income households access the benefit equitably.",
                "objetivo": "Avaliar se a política de tarifa social protege grupos vulneráveis durante eventos de escassez hídrica.",
                "perguntas": "A cobertura alcança os domicílios mais vulneráveis? Existem barreiras administrativas? O benefício considera riscos climáticos?",
                "criterios": "ODS 6, ODS 13, Acordo de Paris e diretrizes nacionais de segurança hídrica.",
                "metodologia": "Análise de bases administrativas, entrevistas, amostragem de beneficiários e mapa de áreas em déficit hídrico.",
                "ferramentas": "Painel de elegibilidade, matriz de barreiras de acesso e roteiro de entrevista com usuários.",
                "resultados": "A cobertura era menor em localidades rurais dispersas e havia baixa integração entre cadastro social e informação climática.",
                "recomendacoes": "Aprimorar busca ativa, simplificar recadastramento e cruzar informações tarifárias com mapas de seca.",
                "replicabilidade": "Média a alta, especialmente para EFS interessadas em avaliar programas sociais sensíveis ao clima.",
                "contato": "Unidade de Auditoria de Recursos Hídricos", "email": "agua.clima@contraloria.cl", "responsavel": "Equipe de Avaliação de Políticas Hídricas",
                "temas": ["Mulheres", "Populações vulneráveis", "Gênero"], "normas": ["Agenda 2030 — ODS 13", "Acordo de Paris"], "dimensoes": ["Distributiva", "Reconhecimento"], "grupos": ["Mulheres chefes de família", "Comunidades rurais"], "destacado": True, "relevante": True,
            },
            {
                "titulo": "Metodologia para auditar transição energética justa",
                "titulo_es": "Metodología para auditar la transición energética justa",
                "titulo_en": "Methodology for auditing a just energy transition",
                "efs": efs["CGR Colombia"], "pais": paises["COL"], "tipo": tipos["Ferramenta/metodologia"], "setor": setores["Energia"], "ano": 2024,
                "descricao": "Desenvolvimento de matriz de auditoria para avaliar programas de transição energética, considerando impactos econômicos e sociais em territórios dependentes de atividades intensivas em carbono.",
                "descricao_es": "Desarrollo de una matriz de auditoría para evaluar programas de transición energética, considerando impactos económicos y sociales en territorios dependientes de actividades intensivas en carbono.",
                "descricao_en": "Development of an audit matrix to assess energy transition programs, considering economic and social impacts in territories dependent on carbon-intensive activities.",
                "enfoque": "A abordagem incorpora emprego, reconversão produtiva, participação social e proteção de comunidades afetadas pela mudança da matriz energética.",
                "enfoque_es": "El enfoque incorpora empleo, reconversión productiva, participación social y protección de comunidades afectadas por el cambio de la matriz energética.",
                "enfoque_en": "The approach incorporates employment, productive reconversion, social participation and protection of communities affected by energy matrix changes.",
                "objetivo": "Oferecer uma metodologia replicável para auditorias sobre transição energética justa.",
                "perguntas": "Há planejamento territorial? Grupos afetados participaram? Existem medidas de proteção social e econômica?",
                "criterios": "Acordo de Paris, ODS 7, ODS 13 e diretrizes de transição justa.",
                "metodologia": "Construção de matriz multicritério com dimensões ambiental, social, econômica e institucional.",
                "ferramentas": "Matriz de transição justa, guia de entrevistas e checklist de participação social.",
                "resultados": "A metodologia permitiu identificar lacunas em mecanismos de compensação e em indicadores de acompanhamento social.",
                "recomendacoes": "Incluir metas sociais mensuráveis e indicadores de transição justa nos programas de energia.",
                "replicabilidade": "Alta para auditorias em energia, mineração, transporte e infraestrutura de baixo carbono.",
                "contato": "Grupo de Auditoria de Energia e Clima", "email": "energia.justicia@contraloria.gov.co", "responsavel": "Direção de Estudos Setoriais",
                "temas": ["Direitos humanos", "Populações vulneráveis"], "normas": ["Acordo de Paris", "Agenda 2030 — ODS 13"], "dimensoes": ["Procedimental", "Intergeracional"], "grupos": ["Comunidades rurais", "Famílias de baixa renda"], "destacado": False, "relevante": True,
            },
            {
                "titulo": "Monitoramento geoespacial de infraestrutura crítica exposta a deslizamentos",
                "titulo_es": "Monitoreo geoespacial de infraestructura crítica expuesta a deslizamientos",
                "titulo_en": "Geospatial monitoring of critical infrastructure exposed to landslides",
                "efs": efs["CGE Ecuador"], "pais": paises["ECU"], "tipo": tipos["Pesquisa"], "setor": setores["Tecnologia"], "ano": 2024,
                "descricao": "Pesquisa aplicada para priorizar auditorias em estradas, pontes e equipamentos públicos localizados em áreas com suscetibilidade a deslizamentos e chuvas extremas.",
                "descricao_es": "Investigación aplicada para priorizar auditorías en carreteras, puentes y equipamientos públicos ubicados en áreas con susceptibilidad a deslizamientos y lluvias extremas.",
                "descricao_en": "Applied research to prioritize audits of roads, bridges and public facilities located in areas susceptible to landslides and extreme rainfall.",
                "enfoque": "A análise combinou exposição física da infraestrutura com presença de comunidades isoladas e grupos com menor capacidade de resposta.",
                "enfoque_es": "El análisis combinó exposición física de la infraestructura con presencia de comunidades aisladas y grupos con menor capacidad de respuesta.",
                "enfoque_en": "The analysis combined physical infrastructure exposure with the presence of isolated communities and groups with lower response capacity.",
                "objetivo": "Apoiar seleção de auditorias baseada em risco climático e vulnerabilidade territorial.",
                "perguntas": "Quais ativos estão em áreas críticas? Quem depende desses ativos? Há planos de manutenção e contingência?",
                "criterios": "Marco de Sendai, planos nacionais de gestão de risco e normas de infraestrutura resiliente.",
                "metodologia": "Cruzamento de camadas geoespaciais, índice de criticidade e validação com equipes técnicas.",
                "ferramentas": "SIG, mapa de calor, matriz de criticidade e lista de verificação de manutenção.",
                "resultados": "Foram identificados corredores críticos com elevada exposição climática e baixa redundância de acesso.",
                "recomendacoes": "Priorizar auditorias em corredores de acesso único e exigir planos de manutenção baseados em risco.",
                "replicabilidade": "Alta para EFS com acesso a dados geoespaciais de infraestrutura e ameaças climáticas.",
                "contato": "Equipe GeoProCGE", "email": "geopro.clima@contraloria.gob.ec", "responsavel": "Coordenação de Tecnologia e Auditoria",
                "temas": ["Populações vulneráveis", "Povos indígenas"], "normas": ["Marco de Sendai para Redução do Risco de Desastres", "Acordo de Escazú"], "dimensoes": ["Distributiva", "Reconhecimento"], "grupos": ["Povos indígenas", "Comunidades rurais"], "destacado": True, "relevante": True,
            },
            {
                "titulo": "Capacitação em auditoria climática com enfoque de gênero",
                "titulo_es": "Capacitación en auditoría climática con enfoque de género",
                "titulo_en": "Training on climate audit with a gender perspective",
                "efs": efs["CGR Paraguay"], "pais": paises["PRY"], "tipo": tipos["Capacitação/treinamento"], "setor": setores["Meio ambiente"], "ano": 2023,
                "descricao": "Programa de formação para equipes auditoras sobre justiça climática, gênero e desenho de perguntas de auditoria sensíveis a desigualdades.",
                "descricao_es": "Programa de formación para equipos auditores sobre justicia climática, género y diseño de preguntas de auditoría sensibles a desigualdades.",
                "descricao_en": "Training program for audit teams on climate justice, gender and audit questions sensitive to inequalities.",
                "enfoque": "A capacitação fortaleceu a capacidade institucional para reconhecer impactos diferenciados de políticas climáticas sobre mulheres e grupos vulneráveis.",
                "enfoque_es": "La capacitación fortaleció la capacidad institucional para reconocer impactos diferenciados de políticas climáticas sobre mujeres y grupos vulnerables.",
                "enfoque_en": "The training strengthened institutional capacity to recognize differentiated impacts of climate policies on women and vulnerable groups.",
                "objetivo": "Desenvolver competências práticas para incorporar justiça climática em auditorias ambientais e de infraestrutura.",
                "perguntas": "Como formular perguntas com enfoque de gênero? Que evidências demonstram desigualdade climática? Como registrar achados sensíveis a direitos?",
                "criterios": "ODS 5, ODS 13, Acordo de Paris e compromissos nacionais de igualdade.",
                "metodologia": "Oficinas práticas, estudo de casos, exercícios de matriz de achados e revisão coletiva de perguntas.",
                "ferramentas": "Modelo de matriz de perguntas, checklist de gênero e roteiro de análise de partes interessadas.",
                "resultados": "Equipes desenvolveram propostas de auditoria com abordagem de gênero e justiça climática.",
                "recomendacoes": "Institucionalizar capacitações periódicas e criar banco de perguntas aplicáveis a diferentes setores.",
                "replicabilidade": "Alta. O desenho pode ser adaptado a oficinas regionais ou nacionais.",
                "contato": "Escola de Controle e Auditoria", "email": "capacitacion.clima@contraloria.gov.py", "responsavel": "Coordenação de Capacitação Técnica",
                "temas": ["Gênero", "Mulheres", "Direitos humanos"], "normas": ["Agenda 2030 — ODS 13", "Acordo de Escazú"], "dimensoes": ["Reconhecimento", "Procedimental"], "grupos": ["Mulheres chefes de família", "Famílias de baixa renda"], "destacado": False, "relevante": True,
            },
            {
                "titulo": "Auditoria de compras públicas sustentáveis para infraestrutura escolar resiliente",
                "titulo_es": "Auditoría de compras públicas sostenibles para infraestructura escolar resiliente",
                "titulo_en": "Audit of sustainable public procurement for resilient school infrastructure",
                "efs": efs["ASF"], "pais": paises["MEX"], "tipo": tipos["Auditoria"], "setor": setores["Infraestrutura"], "ano": 2023,
                "descricao": "Auditoria sobre critérios de sustentabilidade, adaptação climática e inclusão social em compras públicas para reforma de escolas expostas a ondas de calor e eventos extremos.",
                "descricao_es": "Auditoría sobre criterios de sostenibilidad, adaptación climática e inclusión social en compras públicas para reforma de escuelas expuestas a olas de calor y eventos extremos.",
                "descricao_en": "Audit on sustainability, climate adaptation and social inclusion criteria in public procurement for school renovations exposed to heat waves and extreme events.",
                "enfoque": "O trabalho verificou se escolas em áreas de maior vulnerabilidade social recebiam prioridade e se os projetos incorporavam conforto térmico e acessibilidade.",
                "enfoque_es": "El trabajo verificó si escuelas en áreas de mayor vulnerabilidad social recibían prioridad y si los proyectos incorporaban confort térmico y accesibilidad.",
                "enfoque_en": "The work verified whether schools in areas of greater social vulnerability were prioritized and whether projects incorporated thermal comfort and accessibility.",
                "objetivo": "Avaliar se compras públicas de infraestrutura escolar incorporam critérios de resiliência climática e equidade.",
                "perguntas": "Os editais incluem critérios climáticos? A priorização considera vulnerabilidade social? Há monitoramento de desempenho das obras?",
                "criterios": "ODS 4, ODS 13, Acordo de Paris e normas de contratação pública sustentável.",
                "metodologia": "Revisão de editais, análise de contratos, visitas amostrais e matriz de critérios sustentáveis.",
                "ferramentas": "Checklist de compras sustentáveis, matriz de priorização e roteiro de inspeção física.",
                "resultados": "Parte dos editais não incluía critérios objetivos de desempenho térmico e resiliência a eventos extremos.",
                "recomendacoes": "Padronizar critérios mínimos de resiliência climática em compras para infraestrutura educacional.",
                "replicabilidade": "Alta para auditorias de obras públicas, compras sustentáveis e infraestrutura social.",
                "contato": "Direção de Auditoria de Contratações Públicas", "email": "compras.sustentables@asf.gob.mx", "responsavel": "Equipe de Auditoria de Infraestrutura Social",
                "temas": ["Populações vulneráveis", "Direitos humanos"], "normas": ["Agenda 2030 — ODS 13", "Acordo de Paris"], "dimensoes": ["Distributiva", "Intergeracional"], "grupos": ["Famílias de baixa renda", "População em áreas de risco"], "destacado": False, "relevante": True,
            },
        ]

        for item in experiencias:
            obj, _ = Experiencia.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "titulo_es": item["titulo_es"], "titulo_en": item["titulo_en"],
                    "efs": item["efs"], "pais": item["pais"], "tipo_experiencia": item["tipo"], "setor": item["setor"], "ano_execucao": item["ano"],
                    "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    "descricao": item["descricao"], "descricao_es": item["descricao_es"], "descricao_en": item["descricao_en"],
                    "enfoque_justica_climatica": item["enfoque"], "enfoque_justica_climatica_es": item["enfoque_es"], "enfoque_justica_climatica_en": item["enfoque_en"],
                    "objetivo": item["objetivo"], "perguntas_chave": item["perguntas"], "criterios_utilizados": item["criterios"], "metodologia": item["metodologia"], "ferramentas_utilizadas": item["ferramentas"],
                    "resultados": item["resultados"], "recomendacoes": item["recomendacoes"], "replicabilidade": item["replicabilidade"],
                    "contato_referencia": item["contato"], "email_contato": item["email"], "pessoa_responsavel": item["responsavel"],
                    "contribui_para_guia": True, "destacado": item["destacado"], "relevante": item["relevante"],
                },
            )
            obj.temas_transversais.set([temas[nome] for nome in item["temas"]])
            obj.normas_internacionais.set([normas[nome] for nome in item["normas"]])
            obj.dimensoes_consideradas.set([dimensoes[nome] for nome in item["dimensoes"]])
            obj.grupos_vulneraveis.set([grupos[nome] for nome in item["grupos"]])

    def criar_banco_tecnico(self, setores, dimensoes):
        dados = [
            {
                "titulo": "Checklist de justiça climática para auditorias de infraestrutura",
                "titulo_es": "Checklist de justicia climática para auditorías de infraestructura",
                "titulo_en": "Climate justice checklist for infrastructure audits",
                "descricao": "Instrumento prático para verificar se projetos de infraestrutura incorporam vulnerabilidade social, participação e adaptação climática.",
                "descricao_es": "Instrumento práctico para verificar si proyectos de infraestructura incorporan vulnerabilidad social, participación y adaptación climática.",
                "descricao_en": "Practical tool to verify whether infrastructure projects incorporate social vulnerability, participation and climate adaptation.",
                "tipo": "Checklist", "tipo_es": "Checklist", "tipo_en": "Checklist",
                "setor": setores["Infraestrutura"], "dimensoes": ["Distributiva", "Procedimental"],
            },
            {
                "titulo": "Matriz de perguntas para auditoria de adaptação climática",
                "titulo_es": "Matriz de preguntas para auditoría de adaptación climática",
                "titulo_en": "Question matrix for climate adaptation audits",
                "descricao": "Banco inicial de perguntas para estruturar auditorias sobre adaptação, risco climático e grupos vulneráveis.",
                "descricao_es": "Banco inicial de preguntas para estructurar auditorías sobre adaptación, riesgo climático y grupos vulnerables.",
                "descricao_en": "Initial set of questions to structure audits on adaptation, climate risk and vulnerable groups.",
                "tipo": "Matriz", "tipo_es": "Matriz", "tipo_en": "Matrix",
                "setor": setores["Meio ambiente"], "dimensoes": ["Distributiva", "Reconhecimento"],
            },
            {
                "titulo": "Roteiro de análise de participação social em políticas climáticas",
                "titulo_es": "Guía de análisis de participación social en políticas climáticas",
                "titulo_en": "Guide for analyzing public participation in climate policies",
                "descricao": "Roteiro para avaliar transparência, consulta pública e inclusão de comunidades afetadas em políticas climáticas.",
                "descricao_es": "Guía para evaluar transparencia, consulta pública e inclusión de comunidades afectadas en políticas climáticas.",
                "descricao_en": "Guide to assess transparency, public consultation and inclusion of affected communities in climate policies.",
                "tipo": "Roteiro metodológico", "tipo_es": "Guía metodológica", "tipo_en": "Methodological guide",
                "setor": setores["Tecnologia"], "dimensoes": ["Procedimental", "Reconhecimento"],
            },
        ]

        for item in dados:
            obj, _ = BancoTecnico.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "titulo_es": item["titulo_es"], "titulo_en": item["titulo_en"],
                    "descricao": item["descricao"], "descricao_es": item["descricao_es"], "descricao_en": item["descricao_en"],
                    "tipo_recurso": item["tipo"], "tipo_recurso_es": item["tipo_es"], "tipo_recurso_en": item["tipo_en"],
                    "setor": item["setor"],
                },
            )
            obj.dimensoes.set([dimensoes[nome] for nome in item["dimensoes"]])
