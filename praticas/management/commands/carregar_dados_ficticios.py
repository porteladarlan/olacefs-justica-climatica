from django.core.management.base import BaseCommand

from praticas.models import (
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    Pais,
    Setor,
    TipoExperiencia,
)


class Command(BaseCommand):
    help = "Carrega dados ficticios trilingues para demonstracao do MVP"

    def handle(self, *args, **options):
        BancoTecnico.objects.all().delete()
        Experiencia.objects.all().delete()

        paises = [
            ("Brasil", "Brasil", "Brazil", "BRA"),
            ("Chile", "Chile", "Chile", "CHL"),
            ("Colombia", "Colombia", "Colombia", "COL"),
            ("Mexico", "Mexico", "Mexico", "MEX"),
            ("Peru", "Peru", "Peru", "PER"),
            ("Costa Rica", "Costa Rica", "Costa Rica", "CRI"),
        ]
        for nome, nome_es, nome_en, sigla in paises:
            Pais.objects.update_or_create(sigla=sigla, defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en})

        setores = [
            ("Infraestrutura", "Infraestructura", "Infrastructure"),
            ("Recursos hidricos", "Recursos hidricos", "Water resources"),
            ("Agricultura", "Agricultura", "Agriculture"),
            ("Energia", "Energia", "Energy"),
            ("Gestao de riscos", "Gestion de riesgos", "Risk management"),
            ("Meio ambiente", "Medio ambiente", "Environment"),
        ]
        for nome, nome_es, nome_en in setores:
            Setor.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        tipos = [
            ("Auditoria de desempenho", "Auditoria de desempeno", "Performance audit"),
            ("Auditoria de conformidade", "Auditoria de cumplimiento", "Compliance audit"),
            ("Avaliacao de politica publica", "Evaluacion de politica publica", "Public policy evaluation"),
            ("Estudo tecnico", "Estudio tecnico", "Technical study"),
            ("Metodologia ou guia", "Metodologia o guia", "Methodology or guide"),
        ]
        for nome, nome_es, nome_en in tipos:
            TipoExperiencia.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        dimensoes = [
            ("Distributiva", "Distributiva", "Distributive"),
            ("Reconhecimento", "Reconocimiento", "Recognition"),
            ("Procedimental", "Procedimental", "Procedural"),
            ("Intergeracional", "Intergeneracional", "Intergenerational"),
            ("Participacao social", "Participacion social", "Social participation"),
            ("Acesso a servicos", "Acceso a servicios", "Access to services"),
        ]
        for nome, nome_es, nome_en in dimensoes:
            DimensaoJusticaClimatica.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        grupos = [
            ("Comunidades indigenas", "Comunidades indigenas", "Indigenous communities"),
            ("Mulheres", "Mujeres", "Women"),
            ("Pescadores artesanais", "Pescadores artesanales", "Small-scale fishers"),
            ("Populacao rural", "Poblacion rural", "Rural population"),
            ("Pessoas em situacao de pobreza", "Personas en situacion de pobreza", "People living in poverty"),
            ("Comunidades costeiras", "Comunidades costeras", "Coastal communities"),
        ]
        for nome, nome_es, nome_en in grupos:
            GrupoVulneravel.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        efs_data = [
            ("Tribunal de Contas da Uniao", "Tribunal de Cuentas de la Union", "Federal Court of Accounts", "TCU", "BRA"),
            ("Contraloria General de la Republica", "Contraloria General de la Republica", "Office of the Comptroller General", "CGR", "CHL"),
            ("Contraloria General de la Republica", "Contraloria General de la Republica", "Office of the Comptroller General", "CGR", "COL"),
            ("Auditoria Superior de la Federacion", "Auditoria Superior de la Federacion", "Superior Audit Office of the Federation", "ASF", "MEX"),
            ("Contraloria General de la Republica", "Contraloria General de la Republica", "Office of the Comptroller General", "CGR", "PER"),
            ("Contraloria General de la Republica", "Contraloria General de la Republica", "Office of the Comptroller General", "CGR", "CRI"),
        ]
        for nome, nome_es, nome_en, sigla, pais_sigla in efs_data:
            pais = Pais.objects.get(sigla=pais_sigla)
            EFS.objects.update_or_create(nome=nome, pais=pais, defaults={"nome_es": nome_es, "nome_en": nome_en, "sigla": sigla})

        comum = {
            "relacao_adaptacao_mitigacao_gestao_desastres": "A iniciativa esta relacionada a adaptacao climatica, reducao de vulnerabilidades, gestao de riscos e melhoria da governanca publica.",
            "relacao_adaptacao_mitigacao_gestao_desastres_es": "La iniciativa se relaciona con adaptacion climatica, reduccion de vulnerabilidades, gestion de riesgos y mejora de la gobernanza publica.",
            "relacao_adaptacao_mitigacao_gestao_desastres_en": "The initiative is related to climate adaptation, vulnerability reduction, risk management and improved public governance.",
            "riscos_climaticos": "Eventos extremos, variabilidade climatica, perdas economicas e danos a infraestrutura.",
            "riscos_climaticos_es": "Eventos extremos, variabilidad climatica, perdidas economicas y danos a la infraestructura.",
            "riscos_climaticos_en": "Extreme events, climate variability, economic losses and infrastructure damage.",
            "enfoque_justica_climatica": "A experiencia considera a distribuicao desigual dos impactos climaticos e a necessidade de priorizar territorios vulneraveis.",
            "enfoque_justica_climatica_es": "La experiencia considera la distribucion desigual de los impactos climaticos y la necesidad de priorizar territorios vulnerables.",
            "enfoque_justica_climatica_en": "The experience considers the unequal distribution of climate impacts and the need to prioritize vulnerable territories.",
            "impactos_diferenciados": "Os impactos tendem a ser maiores em grupos com menor capacidade de resposta e menor acesso a servicos publicos.",
            "impactos_diferenciados_es": "Los impactos tienden a ser mayores en grupos con menor capacidad de respuesta y menor acceso a servicios publicos.",
            "impactos_diferenciados_en": "Impacts tend to be greater among groups with lower response capacity and limited access to public services.",
            "perguntas_chave": "Quem e mais afetado? Como os recursos sao priorizados? Existem criterios de equidade?",
            "perguntas_chave_es": "Quien es mas afectado? Como se priorizan los recursos? Existen criterios de equidad?",
            "perguntas_chave_en": "Who is most affected? How are resources prioritized? Are there equity criteria?",
            "criterios_utilizados": "Efetividade, equidade, transparencia, participacao social e foco territorial.",
            "criterios_utilizados_es": "Efectividad, equidad, transparencia, participacion social y enfoque territorial.",
            "criterios_utilizados_en": "Effectiveness, equity, transparency, social participation and territorial focus.",
            "metodologia": "Analise documental, entrevistas, revisao de bases publicas, matriz de risco e sistematizacao de evidencias.",
            "metodologia_es": "Analisis documental, entrevistas, revision de bases publicas, matriz de riesgo y sistematizacion de evidencias.",
            "metodologia_en": "Document review, interviews, public database review, risk matrix and evidence systematization.",
            "fontes_informacao": "Planos publicos, bases governamentais, relatorios tecnicos e dados territoriais.",
            "fontes_informacao_es": "Planes publicos, bases gubernamentales, informes tecnicos y datos territoriales.",
            "fontes_informacao_en": "Public plans, government databases, technical reports and territorial data.",
            "mudancas_ou_impactos": "A experiencia contribuiu para melhorar a qualidade das recomendacoes e reforcar criterios de justica climatica.",
            "mudancas_ou_impactos_es": "La experiencia contribuyo a mejorar la calidad de las recomendaciones y reforzar criterios de justicia climatica.",
            "mudancas_ou_impactos_en": "The experience helped improve the quality of recommendations and reinforce climate justice criteria.",
            "motivo_boa_pratica": "A experiencia combina abordagem metodologica clara, foco em vulnerabilidade e potencial de replicacao.",
            "motivo_boa_pratica_es": "La experiencia combina enfoque metodologico claro, foco en vulnerabilidad y potencial de replicacion.",
            "motivo_boa_pratica_en": "The experience combines a clear methodological approach, focus on vulnerability and replication potential.",
            "elementos_replicaveis": "Matriz de risco, roteiro de entrevistas, criterios de priorizacao e indicadores de vulnerabilidade.",
            "elementos_replicaveis_es": "Matriz de riesgo, guia de entrevistas, criterios de priorizacion e indicadores de vulnerabilidad.",
            "elementos_replicaveis_en": "Risk matrix, interview guide, prioritization criteria and vulnerability indicators.",
            "dificuldades": "Limitacoes de dados, baixa padronizacao de informacoes e capacidade institucional desigual.",
            "dificuldades_es": "Limitaciones de datos, baja estandarizacion de informacion y capacidad institucional desigual.",
            "dificuldades_en": "Data limitations, low information standardization and uneven institutional capacity.",
            "licoes_aprendidas": "Auditorias climaticas ganham qualidade quando incorporam criterios territoriais e sociais desde o planejamento.",
            "licoes_aprendidas_es": "Las auditorias climaticas mejoran cuando incorporan criterios territoriales y sociales desde la planificacion.",
            "licoes_aprendidas_en": "Climate audits improve when territorial and social criteria are incorporated from the planning stage.",
            "o_que_fariam_diferente": "Ampliar a validacao com atores territoriais e definir indicadores de equidade antes da coleta de dados.",
            "o_que_fariam_diferente_es": "Ampliar la validacion con actores territoriales y definir indicadores de equidad antes de recopilar datos.",
            "o_que_fariam_diferente_en": "Expand validation with territorial actors and define equity indicators before data collection.",
            "necessidades_para_replicacao": "Dados minimos, equipe capacitada, apoio institucional e metodologia adaptavel.",
            "necessidades_para_replicacao_es": "Datos minimos, equipo capacitado, apoyo institucional y metodologia adaptable.",
            "necessidades_para_replicacao_en": "Minimum data, trained team, institutional support and adaptable methodology.",
            "ferramentas_metodologias_uteis": "Matriz de risco climatico, analise de vulnerabilidade e painel de indicadores.",
            "ferramentas_metodologias_uteis_es": "Matriz de riesgo climatico, analisis de vulnerabilidad y panel de indicadores.",
            "ferramentas_metodologias_uteis_en": "Climate risk matrix, vulnerability analysis and indicator dashboard.",
            "temas_sugeridos_para_guia": "Governanca climatica, financiamento climatico, infraestrutura resiliente e adaptacao territorial.",
            "temas_sugeridos_para_guia_es": "Gobernanza climatica, financiamiento climatico, infraestructura resiliente y adaptacion territorial.",
            "temas_sugeridos_para_guia_en": "Climate governance, climate finance, resilient infrastructure and territorial adaptation.",
            "apoio_requerido_pelas_efs": "Capacitacao, intercambio metodologico, modelos de referencia e apoio para sistematizar evidencias.",
            "apoio_requerido_pelas_efs_es": "Capacitacion, intercambio metodologico, modelos de referencia y apoyo para sistematizar evidencias.",
            "apoio_requerido_pelas_efs_en": "Training, methodological exchange, reference models and support for evidence systematization.",
        }

        experiencias = [
            {
                "titulo": "Avaliacao da equidade no acesso a agua em periodos de seca",
                "titulo_es": "Evaluacion de la equidad en el acceso al agua durante periodos de sequia",
                "titulo_en": "Assessment of equity in access to water during drought periods",
                "pais": "BRA", "efs": "Tribunal de Contas da Uniao", "tipo": "Avaliacao de politica publica", "setor": "Recursos hidricos", "ano": 2025,
                "dimensoes": ["Distributiva", "Acesso a servicos"], "grupos": ["Populacao rural", "Pessoas em situacao de pobreza"],
                "descricao": "A experiencia analisou programas publicos de resposta a seca e sua capacidade de atender populacoes rurais com menor acesso a infraestrutura hidrica.",
                "descricao_es": "La experiencia analizo programas publicos de respuesta a la sequia y su capacidad de atender poblaciones rurales con menor acceso a infraestructura hidrica.",
                "descricao_en": "The experience analyzed public drought response programs and their capacity to serve rural populations with limited access to water infrastructure.",
                "problema_climatico": "Secas prolongadas ampliaram a pressao sobre abastecimento humano, agricultura familiar e seguranca alimentar.",
                "problema_climatico_es": "Sequias prolongadas aumentaron la presion sobre abastecimiento humano, agricultura familiar y seguridad alimentaria.",
                "problema_climatico_en": "Prolonged droughts increased pressure on human water supply, family farming and food security.",
                "objetivo": "Avaliar se recursos e medidas de apoio chegam de forma proporcional aos territorios mais vulneraveis.",
                "objetivo_es": "Evaluar si los recursos y medidas de apoyo llegan proporcionalmente a los territorios mas vulnerables.",
                "objetivo_en": "Assess whether resources and support measures reach the most vulnerable territories proportionally.",
                "resultados": "Foram identificadas lacunas de dados territoriais, criterios pouco transparentes e ausencia de monitoramento de impactos diferenciados.",
                "resultados_es": "Se identificaron brechas de datos territoriales, criterios poco transparentes y ausencia de monitoreo de impactos diferenciados.",
                "resultados_en": "Territorial data gaps, low transparency criteria and lack of monitoring of differentiated impacts were identified.",
                "recomendacoes": "Criar criterios publicos de elegibilidade, integrar bases de vulnerabilidade e monitorar atendimento por territorio.",
                "recomendacoes_es": "Crear criterios publicos de elegibilidad, integrar bases de vulnerabilidad y monitorear la atencion por territorio.",
                "recomendacoes_en": "Create public eligibility criteria, integrate vulnerability databases and monitor service delivery by territory.",
                "replicabilidade": "A abordagem pode orientar auditorias sobre agua, saneamento, seguranca alimentar e adaptacao em regioes sujeitas a estiagens.",
                "replicabilidade_es": "El enfoque puede orientar auditorias sobre agua, saneamiento, seguridad alimentaria y adaptacion en regiones sujetas a sequias.",
                "replicabilidade_en": "The approach can guide audits on water, sanitation, food security and adaptation in drought-prone regions.",
            },
            {
                "titulo": "Auditoria sobre infraestrutura resiliente em zonas costeiras",
                "titulo_es": "Auditoria sobre infraestructura resiliente en zonas costeras",
                "titulo_en": "Audit on resilient infrastructure in coastal areas",
                "pais": "CHL", "efs": "Contraloria General de la Republica", "tipo": "Auditoria de desempenho", "setor": "Infraestrutura", "ano": 2024,
                "dimensoes": ["Distributiva", "Reconhecimento", "Participacao social"], "grupos": ["Comunidades costeiras", "Pescadores artesanais"],
                "descricao": "A experiencia avaliou se investimentos em infraestrutura costeira consideravam riscos climaticos e impactos sobre comunidades dependentes da pesca artesanal.",
                "descricao_es": "La experiencia evaluo si las inversiones en infraestructura costera consideraban riesgos climaticos e impactos sobre comunidades dependientes de la pesca artesanal.",
                "descricao_en": "The experience assessed whether coastal infrastructure investments considered climate risks and impacts on communities dependent on small-scale fisheries.",
                "problema_climatico": "Aumento da erosao costeira, elevacao do nivel do mar e maior frequencia de eventos extremos.",
                "problema_climatico_es": "Aumento de la erosion costera, elevacion del nivel del mar y mayor frecuencia de eventos extremos.",
                "problema_climatico_en": "Increased coastal erosion, sea level rise and greater frequency of extreme events.",
                "objetivo": "Verificar se criterios de priorizacao de obras incorporavam vulnerabilidade social, risco climatico e participacao comunitaria.",
                "objetivo_es": "Verificar si los criterios de priorizacion de obras incorporaban vulnerabilidad social, riesgo climatico y participacion comunitaria.",
                "objetivo_en": "Verify whether criteria for prioritizing works incorporated social vulnerability, climate risk and community participation.",
                "resultados": "A auditoria identificou ausencia de criterios uniformes para priorizar territorios vulneraveis e necessidade de fortalecer consultas locais.",
                "resultados_es": "La auditoria identifico ausencia de criterios uniformes para priorizar territorios vulnerables y necesidad de fortalecer consultas locales.",
                "resultados_en": "The audit identified the absence of uniform criteria for prioritizing vulnerable territories and the need to strengthen local consultations.",
                "recomendacoes": "Incluir indicadores de vulnerabilidade social, aperfeicoar mapas de risco e estabelecer protocolos de consulta.",
                "recomendacoes_es": "Incluir indicadores de vulnerabilidad social, mejorar mapas de riesgo y establecer protocolos de consulta.",
                "recomendacoes_en": "Include social vulnerability indicators, improve risk maps and establish consultation protocols.",
                "replicabilidade": "Pode ser replicada por EFS com territorios costeiros, adaptando a matriz de risco para dados locais.",
                "replicabilidade_es": "Puede ser replicada por EFS con territorios costeros, adaptando la matriz de riesgo a datos locales.",
                "replicabilidade_en": "It can be replicated by SAIs with coastal territories by adapting the risk matrix to local data.",
            },
            {
                "titulo": "Metodologia para avaliar planos locais de adaptacao climatica",
                "titulo_es": "Metodologia para evaluar planes locales de adaptacion climatica",
                "titulo_en": "Methodology for assessing local climate adaptation plans",
                "pais": "CRI", "efs": "Contraloria General de la Republica", "tipo": "Metodologia ou guia", "setor": "Agricultura", "ano": 2025,
                "dimensoes": ["Procedimental", "Participacao social"], "grupos": ["Populacao rural", "Mulheres"],
                "descricao": "A metodologia orienta a avaliacao de planos locais de adaptacao, com atencao a agricultura familiar, acesso a assistencia tecnica e capacidade institucional municipal.",
                "descricao_es": "La metodologia orienta la evaluacion de planes locales de adaptacion, con atencion a agricultura familiar, asistencia tecnica y capacidad institucional municipal.",
                "descricao_en": "The methodology guides the assessment of local adaptation plans, focusing on family farming, technical assistance and municipal institutional capacity.",
                "problema_climatico": "Municipios vulneraveis enfrentam perdas na producao agricola e dificuldades para implementar medidas de adaptacao.",
                "problema_climatico_es": "Municipios vulnerables enfrentan perdidas en la produccion agricola y dificultades para implementar medidas de adaptacion.",
                "problema_climatico_en": "Vulnerable municipalities face agricultural production losses and difficulties implementing adaptation measures.",
                "objetivo": "Apoiar equipes de auditoria na avaliacao da qualidade dos planos locais de adaptacao.",
                "objetivo_es": "Apoyar a equipos de auditoria en la evaluacion de la calidad de los planes locales de adaptacion.",
                "objetivo_en": "Support audit teams in assessing the quality of local adaptation plans.",
                "resultados": "A metodologia permitiu organizar perguntas de auditoria, criterios minimos e evidencias para analise territorial.",
                "resultados_es": "La metodologia permitio organizar preguntas de auditoria, criterios minimos y evidencias para analisis territorial.",
                "resultados_en": "The methodology helped organize audit questions, minimum criteria and evidence for territorial analysis.",
                "recomendacoes": "Usar indicadores de vulnerabilidade, consultar atores locais e integrar dados climaticos ao planejamento.",
                "recomendacoes_es": "Usar indicadores de vulnerabilidad, consultar actores locales e integrar datos climaticos a la planificacion.",
                "recomendacoes_en": "Use vulnerability indicators, consult local actors and integrate climate data into planning.",
                "replicabilidade": "Pode ser adaptada para municipios de diferentes portes e setores expostos a riscos climaticos.",
                "replicabilidade_es": "Puede adaptarse a municipios de diferentes tamanos y sectores expuestos a riesgos climaticos.",
                "replicabilidade_en": "It can be adapted to municipalities of different sizes and sectors exposed to climate risks.",
            },
            {
                "titulo": "Estudo tecnico sobre financiamento climatico e grupos vulneraveis",
                "titulo_es": "Estudio tecnico sobre financiamiento climatico y grupos vulnerables",
                "titulo_en": "Technical study on climate finance and vulnerable groups",
                "pais": "COL", "efs": "Contraloria General de la Republica", "tipo": "Estudo tecnico", "setor": "Gestao de riscos", "ano": 2024,
                "dimensoes": ["Distributiva", "Reconhecimento"], "grupos": ["Comunidades indigenas", "Pessoas em situacao de pobreza"],
                "descricao": "O estudo examinou se recursos de financiamento climatico alcançavam territorios e grupos mais expostos a eventos extremos.",
                "descricao_es": "El estudio examino si los recursos de financiamiento climatico llegaban a territorios y grupos mas expuestos a eventos extremos.",
                "descricao_en": "The study examined whether climate finance resources reached territories and groups most exposed to extreme events.",
                "problema_climatico": "Eventos extremos ampliaram desigualdades territoriais e pressionaram politicas de financiamento.",
                "problema_climatico_es": "Eventos extremos ampliaron desigualdades territoriales y presionaron politicas de financiamiento.",
                "problema_climatico_en": "Extreme events increased territorial inequalities and pressured financing policies.",
                "objetivo": "Avaliar criterios de alocacao de recursos e sua aderencia a vulnerabilidades sociais e climaticas.",
                "objetivo_es": "Evaluar criterios de asignacion de recursos y su alineacion con vulnerabilidades sociales y climaticas.",
                "objetivo_en": "Assess resource allocation criteria and their alignment with social and climate vulnerabilities.",
                "resultados": "Foram identificadas oportunidades para melhorar transparencia, rastreabilidade e focalizacao territorial dos recursos.",
                "resultados_es": "Se identificaron oportunidades para mejorar transparencia, trazabilidad y focalizacion territorial de los recursos.",
                "resultados_en": "Opportunities were identified to improve transparency, traceability and territorial targeting of resources.",
                "recomendacoes": "Publicar criterios, criar painel de acompanhamento e vincular recursos a indicadores de vulnerabilidade.",
                "recomendacoes_es": "Publicar criterios, crear panel de seguimiento y vincular recursos a indicadores de vulnerabilidad.",
                "recomendacoes_en": "Publish criteria, create a monitoring dashboard and link resources to vulnerability indicators.",
                "replicabilidade": "O estudo pode apoiar auditorias de financiamento climatico em diferentes paises da regiao.",
                "replicabilidade_es": "El estudio puede apoyar auditorias de financiamiento climatico en diferentes paises de la region.",
                "replicabilidade_en": "The study can support climate finance audits in different countries of the region.",
            },
            {
                "titulo": "Auditoria de resposta a enchentes urbanas",
                "titulo_es": "Auditoria de respuesta a inundaciones urbanas",
                "titulo_en": "Audit of urban flood response",
                "pais": "PER", "efs": "Contraloria General de la Republica", "tipo": "Auditoria de conformidade", "setor": "Gestao de riscos", "ano": 2025,
                "dimensoes": ["Acesso a servicos", "Procedimental"], "grupos": ["Pessoas em situacao de pobreza", "Mulheres"],
                "descricao": "A auditoria avaliou procedimentos de resposta a enchentes em areas urbanas vulneraveis, incluindo abrigos, alertas e assistencia emergencial.",
                "descricao_es": "La auditoria evaluo procedimientos de respuesta a inundaciones en areas urbanas vulnerables, incluidos refugios, alertas y asistencia de emergencia.",
                "descricao_en": "The audit assessed flood response procedures in vulnerable urban areas, including shelters, alerts and emergency assistance.",
                "problema_climatico": "Chuvas intensas provocaram alagamentos recorrentes e impacto desproporcional em populacoes de baixa renda.",
                "problema_climatico_es": "Lluvias intensas provocaron inundaciones recurrentes e impacto desproporcionado en poblaciones de bajos ingresos.",
                "problema_climatico_en": "Heavy rainfall caused recurrent flooding and disproportionate impacts on low-income populations.",
                "objetivo": "Verificar se procedimentos de resposta consideravam necessidades diferenciadas dos grupos vulneraveis.",
                "objetivo_es": "Verificar si los procedimientos de respuesta consideraban necesidades diferenciadas de grupos vulnerables.",
                "objetivo_en": "Verify whether response procedures considered the differentiated needs of vulnerable groups.",
                "resultados": "A auditoria apontou fragilidades em comunicacao de risco, registro de atendimentos e coordenacao interinstitucional.",
                "resultados_es": "La auditoria senalo debilidades en comunicacion de riesgo, registro de atenciones y coordinacion interinstitucional.",
                "resultados_en": "The audit pointed out weaknesses in risk communication, service records and interinstitutional coordination.",
                "recomendacoes": "Melhorar protocolos de alerta, mapear grupos vulneraveis e integrar informacoes de defesa civil.",
                "recomendacoes_es": "Mejorar protocolos de alerta, mapear grupos vulnerables e integrar informacion de defensa civil.",
                "recomendacoes_en": "Improve alert protocols, map vulnerable groups and integrate civil protection information.",
                "replicabilidade": "Pode ser replicada em cidades expostas a enchentes, deslizamentos e outros eventos extremos.",
                "replicabilidade_es": "Puede replicarse en ciudades expuestas a inundaciones, deslizamientos y otros eventos extremos.",
                "replicabilidade_en": "It can be replicated in cities exposed to floods, landslides and other extreme events.",
            },
            {
                "titulo": "Avaliacao de transicao energetica justa",
                "titulo_es": "Evaluacion de transicion energetica justa",
                "titulo_en": "Assessment of just energy transition",
                "pais": "MEX", "efs": "Auditoria Superior de la Federacion", "tipo": "Avaliacao de politica publica", "setor": "Energia", "ano": 2024,
                "dimensoes": ["Intergeracional", "Participacao social"], "grupos": ["Populacao rural", "Comunidades indigenas"],
                "descricao": "A avaliacao analisou se politicas de transicao energetica consideravam impactos sociais, territoriais e economicos sobre comunidades vulneraveis.",
                "descricao_es": "La evaluacion analizo si politicas de transicion energetica consideraban impactos sociales, territoriales y economicos sobre comunidades vulnerables.",
                "descricao_en": "The assessment analyzed whether energy transition policies considered social, territorial and economic impacts on vulnerable communities.",
                "problema_climatico": "A transicao energetica exige reduzir emissoes sem ampliar desigualdades sociais e territoriais.",
                "problema_climatico_es": "La transicion energetica exige reducir emisiones sin ampliar desigualdades sociales y territoriales.",
                "problema_climatico_en": "The energy transition requires reducing emissions without increasing social and territorial inequalities.",
                "objetivo": "Avaliar se programas de energia incorporavam criterios de justica climatica e participacao social.",
                "objetivo_es": "Evaluar si programas de energia incorporaban criterios de justicia climatica y participacion social.",
                "objetivo_en": "Assess whether energy programs incorporated climate justice and social participation criteria.",
                "resultados": "Foram identificadas lacunas em consulta publica, compensacoes territoriais e monitoramento de impactos sociais.",
                "resultados_es": "Se identificaron brechas en consulta publica, compensaciones territoriales y monitoreo de impactos sociales.",
                "resultados_en": "Gaps were identified in public consultation, territorial compensation and monitoring of social impacts.",
                "recomendacoes": "Criar mecanismos de participacao, indicadores sociais e criterios de priorizacao para comunidades afetadas.",
                "recomendacoes_es": "Crear mecanismos de participacion, indicadores sociales y criterios de priorizacion para comunidades afectadas.",
                "recomendacoes_en": "Create participation mechanisms, social indicators and prioritization criteria for affected communities.",
                "replicabilidade": "A abordagem pode apoiar auditorias sobre energia, infraestrutura e politicas de baixo carbono.",
                "replicabilidade_es": "El enfoque puede apoyar auditorias sobre energia, infraestructura y politicas bajas en carbono.",
                "replicabilidade_en": "The approach can support audits on energy, infrastructure and low-carbon policies.",
            },
        ]

        for item in experiencias:
            pais = Pais.objects.get(sigla=item["pais"])
            efs = EFS.objects.get(nome=item["efs"], pais=pais)
            tipo = TipoExperiencia.objects.get(nome=item["tipo"])
            setor = Setor.objects.get(nome=item["setor"])
            experiencia, _ = Experiencia.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "titulo_es": item["titulo_es"],
                    "titulo_en": item["titulo_en"],
                    "efs": efs,
                    "pais": pais,
                    "tipo_experiencia": tipo,
                    "ano_execucao": item["ano"],
                    "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
                    "setor": setor,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    "descricao": item["descricao"],
                    "descricao_es": item["descricao_es"],
                    "descricao_en": item["descricao_en"],
                    "problema_climatico": item["problema_climatico"],
                    "problema_climatico_es": item["problema_climatico_es"],
                    "problema_climatico_en": item["problema_climatico_en"],
                    "objetivo": item["objetivo"],
                    "objetivo_es": item["objetivo_es"],
                    "objetivo_en": item["objetivo_en"],
                    "resultados": item["resultados"],
                    "resultados_es": item["resultados_es"],
                    "resultados_en": item["resultados_en"],
                    "recomendacoes": item["recomendacoes"],
                    "recomendacoes_es": item["recomendacoes_es"],
                    "recomendacoes_en": item["recomendacoes_en"],
                    "replicabilidade": item["replicabilidade"],
                    "replicabilidade_es": item["replicabilidade_es"],
                    "replicabilidade_en": item["replicabilidade_en"],
                    **comum,
                },
            )
            experiencia.dimensoes_consideradas.set(DimensaoJusticaClimatica.objects.filter(nome__in=item["dimensoes"]))
            experiencia.grupos_vulneraveis.set(GrupoVulneravel.objects.filter(nome__in=item["grupos"]))

        recursos = [
            ("Checklist para avaliar planos de adaptacao climatica", "Checklist para evaluar planes de adaptacion climatica", "Checklist for assessing climate adaptation plans", "Lista de verificacao para analisar governanca, metas, indicadores, financiamento e foco em grupos vulneraveis.", "Lista de verificacion para analizar gobernanza, metas, indicadores, financiamiento y foco en grupos vulnerables.", "Checklist to analyze governance, targets, indicators, financing and focus on vulnerable groups.", "Checklist", "Checklist", "Checklist", "Recursos hidricos", ["Distributiva", "Procedimental"]),
            ("Matriz de criterios para avaliacao de vulnerabilidade climatica", "Matriz de criterios para evaluar vulnerabilidad climatica", "Criteria matrix for assessing climate vulnerability", "Modelo de criterios para identificar exposicao, sensibilidade, capacidade adaptativa e prioridade territorial.", "Modelo de criterios para identificar exposicion, sensibilidad, capacidad adaptativa y prioridad territorial.", "Criteria model to identify exposure, sensitivity, adaptive capacity and territorial priority.", "Criterios", "Criterios", "Criteria", "Gestao de riscos", ["Acesso a servicos", "Distributiva"]),
            ("Modelo de ficha tecnica para boas praticas", "Modelo de ficha tecnica para buenas practicas", "Technical profile template for good practices", "Estrutura padronizada para registrar objetivo, metodologia, resultados, licoes aprendidas e potencial de replicacao.", "Estructura estandarizada para registrar objetivo, metodologia, resultados, lecciones aprendidas y potencial de replicacion.", "Standardized structure to record objective, methodology, results, lessons learned and replication potential.", "Modelo", "Modelo", "Template", "Infraestrutura", ["Intergeracional", "Reconhecimento"]),
            ("Roteiro de perguntas para auditoria com enfoque de justica climatica", "Guia de preguntas para auditoria con enfoque de justicia climatica", "Question guide for audits with a climate justice approach", "Perguntas orientadoras para incorporar vulnerabilidade, equidade, participacao e impactos diferenciados no planejamento de auditorias.", "Preguntas orientadoras para incorporar vulnerabilidad, equidad, participacion e impactos diferenciados en la planificacion de auditorias.", "Guiding questions to incorporate vulnerability, equity, participation and differentiated impacts into audit planning.", "Perguntas de auditoria", "Preguntas de auditoria", "Audit questions", "Meio ambiente", ["Participacao social", "Procedimental"]),
            ("Guia para analise de financiamento climatico", "Guia para analisis de financiamiento climatico", "Guide for climate finance analysis", "Referencia para avaliar criterios de alocacao, transparencia e focalizacao de recursos climaticos.", "Referencia para evaluar criterios de asignacion, transparencia y focalizacion de recursos climaticos.", "Reference to assess allocation criteria, transparency and targeting of climate resources.", "Guia", "Guia", "Guide", "Gestao de riscos", ["Distributiva", "Reconhecimento"]),
            ("Modelo de matriz de risco para infraestrutura resiliente", "Modelo de matriz de riesgo para infraestructura resiliente", "Risk matrix template for resilient infrastructure", "Modelo para cruzar exposicao climatica, criticidade da infraestrutura e vulnerabilidade social.", "Modelo para cruzar exposicion climatica, criticidad de infraestructura y vulnerabilidad social.", "Template to cross climate exposure, infrastructure criticality and social vulnerability.", "Matriz", "Matriz", "Matrix", "Infraestrutura", ["Acesso a servicos", "Intergeracional"]),
        ]

        for titulo, titulo_es, titulo_en, desc, desc_es, desc_en, tipo, tipo_es, tipo_en, setor_nome, dims in recursos:
            setor = Setor.objects.get(nome=setor_nome)
            recurso, _ = BancoTecnico.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "titulo_es": titulo_es,
                    "titulo_en": titulo_en,
                    "descricao": desc,
                    "descricao_es": desc_es,
                    "descricao_en": desc_en,
                    "tipo_recurso": tipo,
                    "tipo_recurso_es": tipo_es,
                    "tipo_recurso_en": tipo_en,
                    "setor": setor,
                    "url": "https://www.olacefs.com",
                },
            )
            recurso.dimensoes.set(DimensaoJusticaClimatica.objects.filter(nome__in=dims))

        self.stdout.write(self.style.SUCCESS("Dados ficticios trilingues carregados com sucesso: 6 paises, 6 EFS, 6 experiencias e 6 recursos tecnicos."))
