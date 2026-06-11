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
    help = "Carrega dados demonstrativos institucionais para apresentação e validação da plataforma."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar-demo",
            action="store_true",
            help="Remove experiências e recursos demonstrativos conhecidos antes de recriar os dados.",
        )

    def handle(self, *args, **options):
        if options.get("limpar_demo"):
            self.limpar_dados_demonstrativos()

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

        self.stdout.write(self.style.SUCCESS("Dados demonstrativos carregados com sucesso."))

    def limpar_dados_demonstrativos(self):
        titulos = [
            "Auditoria da resiliência climática em obras de drenagem urbana",
            "Avaliação de tarifas sociais de água em contexto de seca",
            "Metodologia para auditar transição energética justa",
            "Monitoramento geoespacial de infraestrutura crítica exposta a deslizamentos",
            "Capacitação em auditoria climática com enfoque de gênero",
            "Auditoria de compras públicas sustentáveis para infraestrutura escolar resiliente",
            "Avaliação de planos locais de adaptação em zonas costeiras",
            "Painel de priorização de auditorias climáticas em infraestrutura viária",
        ]
        Experiencia.objects.filter(titulo__in=titulos).delete()
        BancoTecnico.objects.filter(
            titulo__in=[
                "Checklist de justiça climática para auditorias de infraestrutura",
                "Matriz de perguntas para auditoria de adaptação climática",
                "Roteiro de análise de participação social em políticas climáticas",
                "Modelo de ficha de boa prática em justiça climática",
            ]
        ).delete()

    def criar_paises(self):
        dados = [
            ("BRA", "Brasil", "Brasil", "Brazil"),
            ("CHL", "Chile", "Chile", "Chile"),
            ("COL", "Colômbia", "Colombia", "Colombia"),
            ("ECU", "Equador", "Ecuador", "Ecuador"),
            ("PRY", "Paraguai", "Paraguay", "Paraguay"),
            ("MEX", "México", "México", "Mexico"),
            ("CRI", "Costa Rica", "Costa Rica", "Costa Rica"),
            ("CUW", "Curaçao", "Curazao", "Curaçao"),
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
            ("TCU", "Tribunal de Cuentas de la Unión de Brasil", "Tribunal de Cuentas de la Unión de Brasil", "Tribunal de Cuentas de la Unión de Brasil", "BRA"),
            ("CGR Chile", "Contraloria General de la República de Chile", "Contraloria General de la República de Chile", "Contraloria General de la República de Chile", "CHL"),
            ("CGR Colombia", "Contraloria General de la República de Colombia", "Contraloria General de la República de Colombia", "Contraloria General de la República de Colombia", "COL"),
            ("CGE Ecuador", "Contraloría General del Estado de Ecuador", "Contraloría General del Estado de Ecuador", "Contraloría General del Estado de Ecuador", "ECU"),
            ("CGR Paraguay", "Contraloría General de la República de Paraguay", "Contraloría General de la República de Paraguay", "Contraloría General de la República de Paraguay", "PRY"),
            ("ASF", "Auditoría Superior de la Federación de México", "Auditoría Superior de la Federación de México", "Auditoría Superior de la Federación de México", "MEX"),
            ("CGR Costa Rica", "Contraloria General de la República de Costa Rica", "Contraloria General de la República de Costa Rica", "Contraloria General de la República de Costa Rica", "CRI"),
            ("SOAB Curaçao", "Contraloria General de la República de Curazao", "Contraloria General de la República de Curazao", "Contraloria General de la República de Curazao", "CUW"),
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
            ("Comunidades costeiras", "Comunidades costeras", "Coastal communities"),
            ("Pessoas com deficiência", "Personas con discapacidad", "Persons with disabilities"),
        ])

    def criar_normas(self):
        dados = [
            ("Acordo de Paris", "Acuerdo de París", "Paris Agreement", "Marco global para fortalecer adaptação, mitigação e financiamento climático.", "Marco global para fortalecer adaptación, mitigación y financiamiento climático.", "Global framework to strengthen adaptation, mitigation and climate finance.", "https://unfccc.int/process-and-meetings/the-paris-agreement"),
            ("Agenda 2030 — ODS 13", "Agenda 2030 — ODS 13", "2030 Agenda — SDG 13", "Objetivo de Desenvolvimento Sustentável voltado à ação climática.", "Objetivo de Desarrollo Sostenible orientado a la acción climática.", "Sustainable Development Goal focused on climate action.", "https://sdgs.un.org/goals/goal13"),
            ("Marco de Sendai para Redução do Risco de Desastres", "Marco de Sendai para la Reducción del Riesgo de Desastres", "Sendai Framework for Disaster Risk Reduction", "Marco internacional para reduzir riscos de desastres e perdas associadas.", "Marco internacional para reducir riesgos de desastres y pérdidas asociadas.", "International framework to reduce disaster risk and related losses.", "https://www.undrr.org/implementing-sendai-framework/what-sendai-framework"),
            ("Acordo de Escazú", "Acuerdo de Escazú", "Escazú Agreement", "Acordo regional sobre acesso à informação, participação pública e justiça ambiental.", "Acuerdo regional sobre acceso a la información, participación pública y justicia ambiental.", "Regional agreement on access to information, public participation and environmental justice.", "https://www.cepal.org/en/escazuagreement"),
            ("ISSAI 140 — Gestão da qualidade", "ISSAI 140 — Gestión de la calidad", "ISSAI 140 — Quality Management", "Norma da INTOSAI para apoiar a qualidade dos trabalhos das EFS.", "Norma de INTOSAI para apoyar la calidad de los trabajos de las EFS.", "INTOSAI standard to support quality management in SAIs.", "https://www.issai.org/"),
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
        experiencias = self.dados_experiencias(efs, paises, tipos, setores)
        for item in experiencias:
            obj, _ = Experiencia.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "titulo_es": item["titulo_es"],
                    "titulo_en": item["titulo_en"],
                    "efs": item["efs"],
                    "pais": item["pais"],
                    "tipo_experiencia": item["tipo"],
                    "setor": item["setor"],
                    "ano_execucao": item["ano"],
                    "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    "descricao": item["descricao"],
                    "descricao_es": item["descricao_es"],
                    "descricao_en": item["descricao_en"],
                    "problema_climatico": item["problema"],
                    "problema_climatico_es": item["problema_es"],
                    "problema_climatico_en": item["problema_en"],
                    "riscos_climaticos": item["riscos"],
                    "riscos_climaticos_es": item["riscos_es"],
                    "riscos_climaticos_en": item["riscos_en"],
                    "enfoque_justica_climatica": item["enfoque"],
                    "enfoque_justica_climatica_es": item["enfoque_es"],
                    "enfoque_justica_climatica_en": item["enfoque_en"],
                    "objetivo": item["objetivo"],
                    "objetivo_es": item["objetivo_es"],
                    "objetivo_en": item["objetivo_en"],
                    "perguntas_chave": item["perguntas"],
                    "perguntas_chave_es": item["perguntas_es"],
                    "perguntas_chave_en": item["perguntas_en"],
                    "criterios_utilizados": item["criterios"],
                    "criterios_utilizados_es": item["criterios_es"],
                    "criterios_utilizados_en": item["criterios_en"],
                    "metodologia": item["metodologia"],
                    "metodologia_es": item["metodologia_es"],
                    "metodologia_en": item["metodologia_en"],
                    "ferramentas_utilizadas": item["instrumentos"],
                    "ferramentas_utilizadas_es": item["instrumentos_es"],
                    "ferramentas_utilizadas_en": item["instrumentos_en"],
                    "resultados": item["resultados"],
                    "resultados_es": item["resultados_es"],
                    "resultados_en": item["resultados_en"],
                    "recomendacoes": item["recomendacoes"],
                    "recomendacoes_es": item["recomendacoes_es"],
                    "recomendacoes_en": item["recomendacoes_en"],
                    "replicabilidade": item["replicabilidade"],
                    "replicabilidade_es": item["replicabilidade_es"],
                    "replicabilidade_en": item["replicabilidade_en"],
                    "motivo_boa_pratica": item["motivo"],
                    "motivo_boa_pratica_es": item["motivo_es"],
                    "motivo_boa_pratica_en": item["motivo_en"],
                    "licoes_aprendidas": item["licoes"],
                    "licoes_aprendidas_es": item["licoes_es"],
                    "licoes_aprendidas_en": item["licoes_en"],
                    "contato_referencia": item["contato"],
                    "email_contato": item["email"],
                    "pessoa_responsavel": item["responsavel"],
                    "contribui_para_guia": False,
                    "destacado": item["destacado"],
                    "relevante": item["relevante"],
                },
            )
            obj.temas_transversais.set([temas[nome] for nome in item["temas"]])
            obj.normas_internacionais.set([normas[nome] for nome in item["normas"]])
            obj.dimensoes_consideradas.set([dimensoes[nome] for nome in item["dimensoes"]])
            obj.grupos_vulneraveis.set([grupos[nome] for nome in item["grupos"]])

    def dados_experiencias(self, efs, paises, tipos, setores):
        base = [
            {
                "titulo": "Auditoria da resiliência climática em obras de drenagem urbana",
                "titulo_es": "Auditoría de resiliencia climática en obras de drenaje urbano",
                "titulo_en": "Audit of climate resilience in urban drainage works",
                "efs": efs["TCU"], "pais": paises["BRA"], "tipo": tipos["Auditoria"], "setor": setores["Infraestrutura"], "ano": 2025,
                "descricao": "Avaliação de obras de drenagem em municípios expostos a enchentes, com foco em risco climático e vulnerabilidade social.",
                "descricao_es": "Evaluación de obras de drenaje en municipios expuestos a inundaciones, con foco en riesgo climático y vulnerabilidad social.",
                "descricao_en": "Assessment of drainage works in flood-exposed municipalities, focusing on climate risk and social vulnerability.",
                "problema": "Chuvas extremas aumentaram a frequência de alagamentos em bairros periféricos com baixa capacidade de resposta.",
                "problema_es": "Las lluvias extremas aumentaron la frecuencia de inundaciones en barrios periféricos con baja capacidad de respuesta.",
                "problema_en": "Extreme rainfall increased flooding in peripheral neighborhoods with limited response capacity.",
                "riscos": "Inundações, perdas materiais, interrupção de serviços públicos e aumento de riscos sanitários.",
                "riscos_es": "Inundaciones, pérdidas materiales, interrupción de servicios públicos y aumento de riesgos sanitarios.",
                "riscos_en": "Flooding, material losses, disruption of public services and increased health risks.",
                "enfoque": "A análise verificou se os bairros mais vulneráveis foram priorizados e se houve participação social documentada.",
                "enfoque_es": "El análisis verificó si los barrios más vulnerables fueron priorizados y si hubo participación social documentada.",
                "enfoque_en": "The analysis verified whether the most vulnerable neighborhoods were prioritized and whether public participation was documented.",
                "objetivo": "Verificar se projetos financiados com recursos públicos incorporam cenários climáticos e critérios de justiça climática.",
                "objetivo_es": "Verificar si proyectos financiados con recursos públicos incorporan escenarios climáticos y criterios de justicia climática.",
                "objetivo_en": "Verify whether publicly funded projects incorporate climate scenarios and climate justice criteria.",
                "perguntas": "Os projetos usam cenários de chuva extrema? Bairros vulneráveis foram priorizados? Houve consulta pública?",
                "perguntas_es": "¿Los proyectos usan escenarios de lluvia extrema? ¿Se priorizaron barrios vulnerables? ¿Hubo consulta pública?",
                "perguntas_en": "Do projects use extreme rainfall scenarios? Were vulnerable neighborhoods prioritized? Was public consultation held?",
                "criterios": "Acordo de Paris, Marco de Sendai e planos municipais de adaptação.",
                "criterios_es": "Acuerdo de París, Marco de Sendai y planes municipales de adaptación.",
                "criterios_en": "Paris Agreement, Sendai Framework and municipal adaptation plans.",
                "metodologia": "Análise documental, mapas de risco, entrevistas e cruzamento entre obras e indicadores socioambientais.",
                "metodologia_es": "Análisis documental, mapas de riesgo, entrevistas y cruce entre obras e indicadores socioambientales.",
                "metodologia_en": "Document review, risk maps, interviews and overlay of works with socio-environmental indicators.",
                "instrumentos": "Matriz de risco climático, checklist de justiça climática e painel geoespacial de obras.",
                "instrumentos_es": "Matriz de riesgo climático, checklist de justicia climática y panel geoespacial de obras.",
                "instrumentos_en": "Climate risk matrix, climate justice checklist and geospatial dashboard of works.",
                "resultados": "Fragilidades foram encontradas na priorização técnica e na análise de vulnerabilidade social.",
                "resultados_es": "Se encontraron debilidades en la priorización técnica y en el análisis de vulnerabilidad social.",
                "resultados_en": "Weaknesses were found in technical prioritization and social vulnerability analysis.",
                "recomendacoes": "Incluir análise de risco climático nos estudos preliminares e critérios públicos de priorização.",
                "recomendacoes_es": "Incluir análisis de riesgo climático en estudios preliminares y criterios públicos de priorización.",
                "recomendacoes_en": "Include climate risk analysis in preliminary studies and public prioritization criteria.",
                "replicabilidade": "Alta para obras de saneamento, macrodrenagem, encostas e infraestrutura urbana.",
                "replicabilidade_es": "Alta para saneamiento, macrodrenaje, laderas e infraestructura urbana.",
                "replicabilidade_en": "High for sanitation, macro-drainage, slopes and urban infrastructure.",
                "motivo": "Combina dados territoriais, risco climático e equidade na seleção de achados.",
                "motivo_es": "Combina datos territoriales, riesgo climático y equidad en la selección de hallazgos.",
                "motivo_en": "Combines territorial data, climate risk and equity in audit findings.",
                "licoes": "A visualização territorial ajuda a explicar desigualdades de exposição climática.",
                "licoes_es": "La visualización territorial ayuda a explicar desigualdades de exposición climática.",
                "licoes_en": "Territorial visualization helps explain inequalities in climate exposure.",
                "contato": "Equipe de Auditoria de Infraestrutura Climática", "email": "infra.clima@tcu.gov.br", "responsavel": "Coordenação de Auditoria de Infraestrutura",
                "temas": ["Populações vulneráveis", "Direitos humanos"], "normas": ["Acordo de Paris", "Marco de Sendai para Redução do Risco de Desastres"], "dimensoes": ["Distributiva", "Procedimental"], "grupos": ["Famílias de baixa renda", "População em áreas de risco"], "destacado": True, "relevante": True,
            },
            {
                "titulo": "Avaliação de tarifas sociais de água em contexto de seca",
                "titulo_es": "Evaluación de tarifas sociales de agua en contexto de sequía",
                "titulo_en": "Evaluation of social water tariffs in drought contexts",
                "efs": efs["CGR Chile"], "pais": paises["CHL"], "tipo": tipos["Avaliação de política pública"], "setor": setores["Água"], "ano": 2025,
                "descricao": "Avaliação da cobertura de subsídios tarifários para garantir acesso à água em áreas afetadas por seca prolongada.",
                "descricao_es": "Evaluación de la cobertura de subsidios tarifarios para garantizar acceso al agua en zonas afectadas por sequía prolongada.",
                "descricao_en": "Evaluation of tariff subsidy coverage to ensure access to water in areas affected by prolonged drought.",
                "problema": "A escassez hídrica aumenta custos e aprofunda desigualdades no acesso a serviços essenciais.",
                "problema_es": "La escasez hídrica aumenta costos y profundiza desigualdades en el acceso a servicios esenciales.",
                "problema_en": "Water scarcity increases costs and deepens inequalities in access to essential services.",
                "riscos": "Desabastecimento, aumento de despesas familiares e exclusão de domicílios rurais dispersos.",
                "riscos_es": "Desabastecimiento, aumento del gasto familiar y exclusión de hogares rurales dispersos.",
                "riscos_en": "Shortages, increased household expenses and exclusion of dispersed rural households.",
                "enfoque": "A avaliação verificou acesso de mulheres chefes de família, comunidades rurais e domicílios de baixa renda.",
                "enfoque_es": "La evaluación verificó el acceso de mujeres jefas de hogar, comunidades rurales y hogares de bajos ingresos.",
                "enfoque_en": "The evaluation verified access by women heads of household, rural communities and low-income households.",
                "objetivo": "Avaliar se a tarifa social protege grupos vulneráveis durante eventos de escassez hídrica.",
                "objetivo_es": "Evaluar si la tarifa social protege a grupos vulnerables durante eventos de escasez hídrica.",
                "objetivo_en": "Assess whether the social tariff protects vulnerable groups during water scarcity events.",
                "perguntas": "A cobertura alcança os domicílios vulneráveis? Existem barreiras administrativas? O benefício considera riscos climáticos?",
                "perguntas_es": "¿La cobertura llega a los hogares vulnerables? ¿Existen barreras administrativas? ¿El beneficio considera riesgos climáticos?",
                "perguntas_en": "Does coverage reach vulnerable households? Are there administrative barriers? Does the benefit consider climate risks?",
                "criterios": "ODS 6, ODS 13, Acordo de Paris e diretrizes nacionais de segurança hídrica.",
                "criterios_es": "ODS 6, ODS 13, Acuerdo de París y directrices nacionales de seguridad hídrica.",
                "criterios_en": "SDG 6, SDG 13, Paris Agreement and national water security guidelines.",
                "metodologia": "Análise de bases administrativas, entrevistas e mapa de áreas em déficit hídrico.",
                "metodologia_es": "Análisis de bases administrativas, entrevistas y mapa de áreas con déficit hídrico.",
                "metodologia_en": "Administrative data analysis, interviews and mapping of water deficit areas.",
                "instrumentos": "Painel de elegibilidade, matriz de barreiras de acesso e roteiro de entrevista.",
                "instrumentos_es": "Panel de elegibilidad, matriz de barreras de acceso y guía de entrevista.",
                "instrumentos_en": "Eligibility dashboard, access-barrier matrix and interview guide.",
                "resultados": "A cobertura era menor em localidades rurais e havia baixa integração entre cadastro social e dados climáticos.",
                "resultados_es": "La cobertura era menor en localidades rurales y había baja integración entre registro social y datos climáticos.",
                "resultados_en": "Coverage was lower in rural areas and social registry data was poorly integrated with climate data.",
                "recomendacoes": "Aprimorar busca ativa, simplificar recadastramento e cruzar informações tarifárias com mapas de seca.",
                "recomendacoes_es": "Mejorar búsqueda activa, simplificar recertificación y cruzar información tarifaria con mapas de sequía.",
                "recomendacoes_en": "Improve active outreach, simplify recertification and cross tariff information with drought maps.",
                "replicabilidade": "Média a alta para programas sociais sensíveis ao clima.",
                "replicabilidade_es": "Media a alta para programas sociales sensibles al clima.",
                "replicabilidade_en": "Medium to high for climate-sensitive social programs.",
                "motivo": "Mostra como instrumentos sociais podem ser avaliados sob risco climático.",
                "motivo_es": "Muestra cómo instrumentos sociales pueden evaluarse bajo riesgo climático.",
                "motivo_en": "Shows how social instruments can be assessed under climate risk.",
                "licoes": "Dados de vulnerabilidade precisam dialogar com dados climáticos para orientar cobertura.",
                "licoes_es": "Los datos de vulnerabilidad deben dialogar con datos climáticos para orientar la cobertura.",
                "licoes_en": "Vulnerability data must connect with climate data to guide coverage.",
                "contato": "Unidade de Auditoria de Recursos Hídricos", "email": "agua.clima@contraloria.cl", "responsavel": "Equipe de Avaliação de Políticas Hídricas",
                "temas": ["Mulheres", "Populações vulneráveis", "Gênero"], "normas": ["Agenda 2030 — ODS 13", "Acordo de Paris"], "dimensoes": ["Distributiva", "Reconhecimento"], "grupos": ["Mulheres chefes de família", "Comunidades rurais"], "destacado": True, "relevante": True,
            },
        ]

        adicionais = [
            ("Metodologia para auditar transição energética justa", "Metodología para auditar la transición energética justa", "Methodology for auditing a just energy transition", efs["CGR Colombia"], paises["COL"], tipos["Ferramenta/metodologia"], setores["Energia"], 2024, "transição energética justa", "transición energética justa", "just energy transition", ["Direitos humanos", "Populações vulneráveis"], ["Acordo de Paris", "Agenda 2030 — ODS 13"], ["Procedimental", "Intergeracional"], ["Comunidades rurais", "Famílias de baixa renda"], False, True),
            ("Monitoramento geoespacial de infraestrutura crítica exposta a deslizamentos", "Monitoreo geoespacial de infraestructura crítica expuesta a deslizamientos", "Geospatial monitoring of critical infrastructure exposed to landslides", efs["CGE Ecuador"], paises["ECU"], tipos["Pesquisa"], setores["Tecnologia"], 2024, "infraestrutura crítica e risco de deslizamentos", "infraestructura crítica y riesgo de deslizamientos", "critical infrastructure and landslide risk", ["Populações vulneráveis", "Povos indígenas"], ["Marco de Sendai para Redução do Risco de Desastres", "Acordo de Escazú"], ["Distributiva", "Reconhecimento"], ["Povos indígenas", "Comunidades rurais"], True, True),
            ("Capacitação em auditoria climática com enfoque de gênero", "Capacitación en auditoría climática con enfoque de género", "Training on climate audit with a gender perspective", efs["CGR Paraguay"], paises["PRY"], tipos["Capacitação/treinamento"], setores["Meio ambiente"], 2023, "formação de equipes em gênero e justiça climática", "formación de equipos en género y justicia climática", "training teams on gender and climate justice", ["Gênero", "Mulheres", "Direitos humanos"], ["Agenda 2030 — ODS 13", "Acordo de Escazú"], ["Reconhecimento", "Procedimental"], ["Mulheres chefes de família", "Famílias de baixa renda"], False, True),
            ("Auditoria de compras públicas sustentáveis para infraestrutura escolar resiliente", "Auditoría de compras públicas sostenibles para infraestructura escolar resiliente", "Audit of sustainable public procurement for resilient school infrastructure", efs["ASF"], paises["MEX"], tipos["Auditoria"], setores["Infraestrutura"], 2023, "compras sustentáveis para escolas resilientes", "compras sostenibles para escuelas resilientes", "sustainable procurement for resilient schools", ["Populações vulneráveis", "Direitos humanos"], ["Agenda 2030 — ODS 13", "Acordo de Paris"], ["Distributiva", "Intergeracional"], ["Famílias de baixa renda", "População em áreas de risco"], False, True),
            ("Avaliação de planos locais de adaptação em zonas costeiras", "Evaluación de planes locales de adaptación en zonas costeras", "Evaluation of local adaptation plans in coastal zones", efs["CGR Costa Rica"], paises["CRI"], tipos["Avaliação de política pública"], setores["Meio ambiente"], 2025, "adaptação costeira e comunidades expostas", "adaptación costera y comunidades expuestas", "coastal adaptation and exposed communities", ["Populações vulneráveis", "Direitos humanos"], ["Acordo de Paris", "Acordo de Escazú"], ["Procedimental", "Reconhecimento"], ["Comunidades costeiras", "População em áreas de risco"], True, True),
            ("Painel de priorização de auditorias climáticas em infraestrutura viária", "Panel de priorización de auditorías climáticas en infraestructura vial", "Prioritization dashboard for climate audits of road infrastructure", efs["SOAB Curaçao"], paises["CUW"], tipos["Ferramenta/metodologia"], setores["Tecnologia"], 2025, "infraestrutura viária exposta a tempestades e inundações costeiras", "infraestructura vial expuesta a tormentas e inundaciones costeras", "road infrastructure exposed to storms and coastal flooding", ["Populações vulneráveis", "Direitos humanos"], ["Marco de Sendai para Redução do Risco de Desastres", "Acordo de Paris"], ["Distributiva", "Intergeracional"], ["Comunidades costeiras", "Pessoas com deficiência"], True, True),
        ]

        for titulo, titulo_es, titulo_en, efs_obj, pais_obj, tipo, setor, ano, foco, foco_es, foco_en, temas, normas, dimensoes, grupos, destacado, relevante in adicionais:
            base.append({
                "titulo": titulo,
                "titulo_es": titulo_es,
                "titulo_en": titulo_en,
                "efs": efs_obj,
                "pais": pais_obj,
                "tipo": tipo,
                "setor": setor,
                "ano": ano,
                "descricao": f"Experiência demonstrativa sobre {foco}, estruturada para evidenciar vínculos entre auditoria, risco climático e justiça climática.",
                "descricao_es": f"Experiencia demostrativa sobre {foco_es}, estructurada para evidenciar vínculos entre auditoría, riesgo climático y justicia climática.",
                "descricao_en": f"Demonstration experience on {foco_en}, structured to show links between audit work, climate risk and climate justice.",
                "problema": f"O caso aborda {foco} em contextos nos quais impactos climáticos afetam grupos com diferentes capacidades de adaptação.",
                "problema_es": f"El caso aborda {foco_es} en contextos donde los impactos climáticos afectan a grupos con diferentes capacidades de adaptación.",
                "problema_en": f"The case addresses {foco_en} in contexts where climate impacts affect groups with different adaptive capacities.",
                "riscos": "Eventos extremos, perdas econômicas, interrupção de serviços essenciais e aprofundamento de desigualdades territoriais.",
                "riscos_es": "Eventos extremos, pérdidas económicas, interrupción de servicios esenciales y profundización de desigualdades territoriales.",
                "riscos_en": "Extreme events, economic losses, disruption of essential services and deepening territorial inequalities.",
                "enfoque": "O enfoque de justiça climática considera distribuição de benefícios, participação social e reconhecimento de grupos vulneráveis.",
                "enfoque_es": "El enfoque de justicia climática considera distribución de beneficios, participación social y reconocimiento de grupos vulnerables.",
                "enfoque_en": "The climate justice perspective considers distribution of benefits, public participation and recognition of vulnerable groups.",
                "objetivo": "Demonstrar como uma EFS pode estruturar análise de risco climático com critérios de equidade.",
                "objetivo_es": "Demostrar cómo una EFS puede estructurar análisis de riesgo climático con criterios de equidad.",
                "objetivo_en": "Demonstrate how an SAI can structure climate risk analysis with equity criteria.",
                "perguntas": "Quem é mais afetado? Há critérios transparentes de priorização? Existem evidências climáticas e sociais integradas?",
                "perguntas_es": "¿Quiénes son más afectados? ¿Hay criterios transparentes de priorización? ¿Existen evidencias climáticas y sociales integradas?",
                "perguntas_en": "Who is most affected? Are prioritization criteria transparent? Are climate and social evidence integrated?",
                "criterios": "Acordo de Paris, Agenda 2030, Marco de Sendai, Acordo de Escazú e marcos nacionais aplicáveis.",
                "criterios_es": "Acuerdo de París, Agenda 2030, Marco de Sendai, Acuerdo de Escazú y marcos nacionales aplicables.",
                "criterios_en": "Paris Agreement, 2030 Agenda, Sendai Framework, Escazú Agreement and applicable national frameworks.",
                "metodologia": "Revisão documental, entrevistas, matriz de critérios, análise territorial e validação técnica com equipe auditora.",
                "metodologia_es": "Revisión documental, entrevistas, matriz de criterios, análisis territorial y validación técnica con equipo auditor.",
                "metodologia_en": "Document review, interviews, criteria matrix, territorial analysis and technical validation with the audit team.",
                "instrumentos": "Matriz de perguntas, checklist de justiça climática, mapa de risco e ficha estruturada de achados.",
                "instrumentos_es": "Matriz de preguntas, checklist de justicia climática, mapa de riesgo y ficha estructurada de hallazgos.",
                "instrumentos_en": "Question matrix, climate justice checklist, risk map and structured findings template.",
                "resultados": "A experiência demonstrou lacunas de informação, oportunidades de priorização territorial e recomendações replicáveis.",
                "resultados_es": "La experiencia demostró brechas de información, oportunidades de priorización territorial y recomendaciones replicables.",
                "resultados_en": "The experience showed information gaps, opportunities for territorial prioritization and replicable recommendations.",
                "recomendacoes": "Integrar dados climáticos e sociais, fortalecer critérios públicos e documentar participação das comunidades afetadas.",
                "recomendacoes_es": "Integrar datos climáticos y sociales, fortalecer criterios públicos y documentar participación de comunidades afectadas.",
                "recomendacoes_en": "Integrate climate and social data, strengthen public criteria and document participation by affected communities.",
                "replicabilidade": "Alta, desde que a EFS disponha de dados mínimos de território, clima, política pública e grupos afetados.",
                "replicabilidade_es": "Alta, siempre que la EFS cuente con datos mínimos de territorio, clima, política pública y grupos afectados.",
                "replicabilidade_en": "High, provided the SAI has minimum data on territory, climate, public policy and affected groups.",
                "motivo": "É uma boa prática porque traduz justiça climática em perguntas, evidências e critérios auditáveis.",
                "motivo_es": "Es una buena práctica porque traduce justicia climática en preguntas, evidencias y criterios auditables.",
                "motivo_en": "It is a good practice because it translates climate justice into auditable questions, evidence and criteria.",
                "licoes": "A clareza da ficha e dos metadados facilita comparação entre países, setores e tipos de experiência.",
                "licoes_es": "La claridad de la ficha y de los metadatos facilita comparación entre países, sectores y tipos de experiencia.",
                "licoes_en": "Clear templates and metadata make it easier to compare countries, sectors and types of experience.",
                "contato": "Equipe demonstrativa de auditoria climática",
                "email": "demo.justica.climatica@olacefs.org",
                "responsavel": "Ponto focal demonstrativo da EFS",
                "temas": temas,
                "normas": normas,
                "dimensoes": dimensoes,
                "grupos": grupos,
                "destacado": destacado,
                "relevante": relevante,
            })

        return base

    def criar_banco_tecnico(self, setores, dimensoes):
        dados = [
            ("Checklist de justiça climática para auditorias de infraestrutura", "Checklist de justicia climática para auditorías de infraestructura", "Climate justice checklist for infrastructure audits", "Instrumento prático para verificar vulnerabilidade social, participação e adaptação climática em projetos de infraestrutura.", "Instrumento práctico para verificar vulnerabilidad social, participación y adaptación climática en proyectos de infraestructura.", "Practical tool to verify social vulnerability, participation and climate adaptation in infrastructure projects.", "Checklist", "Checklist", "Checklist", setores["Infraestrutura"], ["Distributiva", "Procedimental"]),
            ("Matriz de perguntas para auditoria de adaptação climática", "Matriz de preguntas para auditoría de adaptación climática", "Question matrix for climate adaptation audits", "Banco inicial de perguntas para estruturar auditorias sobre adaptação, risco climático e grupos vulneráveis.", "Banco inicial de preguntas para estructurar auditorías sobre adaptación, riesgo climático y grupos vulnerables.", "Initial question bank to structure audits on adaptation, climate risk and vulnerable groups.", "Matriz", "Matriz", "Matrix", setores["Meio ambiente"], ["Distributiva", "Reconhecimento"]),
            ("Roteiro de análise de participação social em políticas climáticas", "Guía de análisis de participación social en políticas climáticas", "Guide for analyzing public participation in climate policies", "Roteiro para avaliar transparência, consulta pública e inclusão de comunidades afetadas em políticas climáticas.", "Guía para evaluar transparencia, consulta pública e inclusión de comunidades afectadas en políticas climáticas.", "Guide to assess transparency, public consultation and inclusion of affected communities in climate policies.", "Roteiro metodológico", "Guía metodológica", "Methodological guide", setores["Tecnologia"], ["Procedimental", "Reconhecimento"]),
            ("Modelo de ficha de boa prática em justiça climática", "Modelo de ficha de buena práctica en justicia climática", "Climate justice good practice template", "Modelo para registrar boas práticas com metadados, vínculo normativo, metodologia, resultados e replicabilidade.", "Modelo para registrar buenas prácticas con metadatos, vínculo normativo, metodología, resultados y replicabilidad.", "Template to register good practices with metadata, normative links, methodology, results and replicability.", "Modelo", "Modelo", "Template", setores["Meio ambiente"], ["Procedimental", "Intergeracional"]),
        ]

        for titulo, titulo_es, titulo_en, descricao, descricao_es, descricao_en, tipo, tipo_es, tipo_en, setor, dims in dados:
            obj, _ = BancoTecnico.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "titulo_es": titulo_es,
                    "titulo_en": titulo_en,
                    "descricao": descricao,
                    "descricao_es": descricao_es,
                    "descricao_en": descricao_en,
                    "tipo_recurso": tipo,
                    "tipo_recurso_es": tipo_es,
                    "tipo_recurso_en": tipo_en,
                    "setor": setor,
                },
            )
            obj.dimensoes.set([dimensoes[nome] for nome in dims])
