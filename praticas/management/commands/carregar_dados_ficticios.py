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
    help = "Carrega dados ficticios alinhados ao questionario negocial do MVP"

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
            ("Agua", "Agua", "Water"),
            ("Energia", "Energia", "Energy"),
            ("Meio ambiente", "Medio ambiente", "Environment"),
            ("Tecnologia", "Tecnologia", "Technology"),
        ]
        for nome, nome_es, nome_en in setores:
            Setor.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        tipos = [
            ("Pesquisa", "Investigacion", "Research"),
            ("Avaliacao de Politica Publica", "Evaluacion de Politica Publica", "Public Policy Evaluation"),
            ("Capacitacao ou Treinamento", "Capacitacion o Entrenamiento", "Training"),
            ("Auditoria", "Auditoria", "Audit"),
            ("Ferramenta ou Metodologia", "Herramienta o Metodologia", "Tool or Methodology"),
        ]
        for nome, nome_es, nome_en in tipos:
            TipoExperiencia.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        temas = [
            ("Genero", "Genero", "Gender"),
            ("Mulheres", "Mujeres", "Women"),
            ("Populacoes vulneraveis", "Poblaciones vulnerables", "Vulnerable populations"),
            ("Indigenas", "Pueblos indigenas", "Indigenous peoples"),
            ("Quilombolas", "Afrodescendientes / quilombolas", "Afro-descendant / quilombola communities"),
            ("LGBTQI+", "LGBTQI+", "LGBTQI+"),
            ("Direitos humanos", "Derechos humanos", "Human rights"),
        ]
        for nome, nome_es, nome_en in temas:
            TemaTransversal.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        normas = [
            ("Acordo de Paris", "Acuerdo de Paris", "Paris Agreement", "Marco internacional sobre mudanca climatica, mitigacao, adaptacao e financiamento climatico.", "Marco internacional sobre cambio climatico, mitigacion, adaptacion y financiamiento climatico.", "International framework on climate change, mitigation, adaptation and climate finance.", "https://unfccc.int/process-and-meetings/the-paris-agreement"),
            ("Agenda 2030 e ODS", "Agenda 2030 y ODS", "2030 Agenda and SDGs", "Agenda global de desenvolvimento sustentavel com metas relacionadas a clima, agua, energia, infraestrutura e reducao de desigualdades.", "Agenda global de desarrollo sostenible con metas relacionadas con clima, agua, energia, infraestructura y reduccion de desigualdades.", "Global sustainable development agenda with goals related to climate, water, energy, infrastructure and inequality reduction.", "https://sdgs.un.org/goals"),
            ("Marco de Sendai", "Marco de Sendai", "Sendai Framework", "Referencia internacional para reducao de risco de desastres e fortalecimento de capacidades institucionais.", "Referencia internacional para la reduccion del riesgo de desastres y fortalecimiento de capacidades institucionales.", "International reference for disaster risk reduction and institutional capacity strengthening.", "https://www.undrr.org/implementing-sendai-framework"),
            ("Convencao sobre Diversidade Biologica", "Convenio sobre la Diversidad Biologica", "Convention on Biological Diversity", "Marco para conservacao da biodiversidade, uso sustentavel e reparticao justa de beneficios.", "Marco para conservacion de biodiversidad, uso sostenible y distribucion justa de beneficios.", "Framework for biodiversity conservation, sustainable use and fair benefit sharing.", "https://www.cbd.int/"),
        ]
        for nome, nome_es, nome_en, resumo, resumo_es, resumo_en, url in normas:
            NormaInternacional.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en, "resumo": resumo, "resumo_es": resumo_es, "resumo_en": resumo_en, "url_referencia": url})

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

        experiencias = [
            ("Avaliacao da equidade no acesso a agua em periodos de seca", "Evaluacion de la equidad en el acceso al agua durante periodos de sequia", "Assessment of equity in access to water during drought periods", "BRA", "Tribunal de Contas da Uniao", "Avaliacao de Politica Publica", "Agua", ["Populacoes vulneraveis", "Direitos humanos"], ["Acordo de Paris", "Agenda 2030 e ODS"], 2025),
            ("Auditoria sobre infraestrutura resiliente em zonas costeiras", "Auditoria sobre infraestructura resiliente en zonas costeras", "Audit on resilient infrastructure in coastal areas", "CHL", "Contraloria General de la Republica", "Auditoria", "Infraestrutura", ["Mulheres", "Populacoes vulneraveis"], ["Acordo de Paris", "Marco de Sendai"], 2024),
            ("Metodologia para avaliar planos locais de adaptacao climatica", "Metodologia para evaluar planes locales de adaptacion climatica", "Methodology for assessing local climate adaptation plans", "CRI", "Contraloria General de la Republica", "Ferramenta ou Metodologia", "Meio ambiente", ["Genero", "Direitos humanos"], ["Acordo de Paris", "Agenda 2030 e ODS"], 2025),
            ("Estudo tecnico sobre financiamento climatico e grupos vulneraveis", "Estudio tecnico sobre financiamiento climatico y grupos vulnerables", "Technical study on climate finance and vulnerable groups", "COL", "Contraloria General de la Republica", "Pesquisa", "Tecnologia", ["Indigenas", "Direitos humanos"], ["Acordo de Paris"], 2024),
            ("Auditoria de resposta a enchentes urbanas", "Auditoria de respuesta a inundaciones urbanas", "Audit of urban flood response", "PER", "Contraloria General de la Republica", "Auditoria", "Infraestrutura", ["Mulheres", "Populacoes vulneraveis"], ["Marco de Sendai", "Agenda 2030 e ODS"], 2025),
            ("Capacitacao sobre transicao energetica justa", "Capacitacion sobre transicion energetica justa", "Training on just energy transition", "MEX", "Auditoria Superior de la Federacion", "Capacitacao ou Treinamento", "Energia", ["Indigenas", "Direitos humanos"], ["Acordo de Paris", "Agenda 2030 e ODS"], 2024),
        ]

        for titulo, titulo_es, titulo_en, pais_sigla, efs_nome, tipo_nome, setor_nome, temas_nomes, normas_nomes, ano in experiencias:
            pais = Pais.objects.get(sigla=pais_sigla)
            efs = EFS.objects.get(nome=efs_nome, pais=pais)
            tipo = TipoExperiencia.objects.get(nome=tipo_nome)
            setor = Setor.objects.get(nome=setor_nome)

            experiencia, _ = Experiencia.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "titulo_es": titulo_es,
                    "titulo_en": titulo_en,
                    "efs": efs,
                    "pais": pais,
                    "tipo_experiencia": tipo,
                    "setor": setor,
                    "ano_execucao": ano,
                    "contato_referencia": "Ponto focal tecnico da EFS",
                    "email_contato": "contato@efs.example",
                    "pessoa_responsavel": "Equipe tecnica responsavel",
                    "descricao": "Boa pratica demonstrativa cadastrada para mostrar como a plataforma organiza experiencias, filtros, normativas e ferramentas de auditoria com perspectiva de justica climatica.",
                    "descricao_es": "Buena practica demostrativa registrada para mostrar como la plataforma organiza experiencias, filtros, normativas y herramientas de auditoria con perspectiva de justicia climatica.",
                    "descricao_en": "Demonstration good practice registered to show how the platform organizes experiences, filters, standards and audit tools with a climate justice perspective.",
                    "enfoque_justica_climatica": "A experiencia considera grupos vulneraveis, direitos humanos, impactos diferenciados e criterios de equidade.",
                    "enfoque_justica_climatica_es": "La experiencia considera grupos vulnerables, derechos humanos, impactos diferenciados y criterios de equidad.",
                    "enfoque_justica_climatica_en": "The experience considers vulnerable groups, human rights, differentiated impacts and equity criteria.",
                    "objetivo": "Apoiar a fiscalizacao publica com criterios de justica climatica.",
                    "objetivo_es": "Apoyar la fiscalizacion publica con criterios de justicia climatica.",
                    "objetivo_en": "Support public oversight with climate justice criteria.",
                    "perguntas_chave": "Quem se beneficia? Quem assume os riscos? As decisoes reduzem desigualdades?",
                    "perguntas_chave_es": "Quien se beneficia? Quien asume los riesgos? Las decisiones reducen desigualdades?",
                    "perguntas_chave_en": "Who benefits? Who bears the risks? Do decisions reduce inequalities?",
                    "criterios_utilizados": "Equidade, transparencia, participacao, efetividade e foco em vulnerabilidade.",
                    "criterios_utilizados_es": "Equidad, transparencia, participacion, efectividad y foco en vulnerabilidad.",
                    "criterios_utilizados_en": "Equity, transparency, participation, effectiveness and focus on vulnerability.",
                    "metodologia": "Analise documental, entrevistas, revisao de dados publicos e matriz de risco.",
                    "metodologia_es": "Analisis documental, entrevistas, revision de datos publicos y matriz de riesgo.",
                    "metodologia_en": "Document review, interviews, public data review and risk matrix.",
                    "ferramentas_utilizadas": "Matriz de risco, perguntas orientadoras e checklist de evidencias.",
                    "ferramentas_utilizadas_es": "Matriz de riesgo, preguntas orientadoras y checklist de evidencias.",
                    "ferramentas_utilizadas_en": "Risk matrix, guiding questions and evidence checklist.",
                    "resultados": "A experiencia ajuda a visualizar como uma EFS incorporou justica climatica de maneira pratica.",
                    "resultados_es": "La experiencia ayuda a visualizar como una EFS incorporo justicia climatica de manera practica.",
                    "resultados_en": "The experience helps show how a SAI incorporated climate justice in practice.",
                    "recomendacoes": "Fortalecer dados territoriais, criterios de equidade e mecanismos de participacao.",
                    "recomendacoes_es": "Fortalecer datos territoriales, criterios de equidad y mecanismos de participacion.",
                    "recomendacoes_en": "Strengthen territorial data, equity criteria and participation mechanisms.",
                    "replicabilidade": "Pode ser adaptada por outras EFS a partir dos filtros, perguntas e ferramentas descritas.",
                    "replicabilidade_es": "Puede ser adaptada por otras EFS a partir de los filtros, preguntas y herramientas descritas.",
                    "replicabilidade_en": "It can be adapted by other SAIs based on the filters, questions and tools described.",
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
                    "contribui_para_guia": True,
                    "destacado": True,
                    "relevante": True,
                },
            )
            experiencia.temas_transversais.set(TemaTransversal.objects.filter(nome__in=temas_nomes))
            experiencia.normas_internacionais.set(NormaInternacional.objects.filter(nome__in=normas_nomes))
            experiencia.dimensoes_consideradas.set(DimensaoJusticaClimatica.objects.filter(nome__in=["Distributiva", "Procedimental", "Participacao social"]))
            experiencia.grupos_vulneraveis.set(GrupoVulneravel.objects.filter(nome__in=["Mulheres", "Pessoas em situacao de pobreza"]))

        recursos = [
            ("Checklist para avaliar planos de adaptacao climatica", "Checklist para evaluar planes de adaptacion climatica", "Checklist for assessing climate adaptation plans", "Checklist"),
            ("Matriz de criterios para avaliacao de vulnerabilidade climatica", "Matriz de criterios para evaluar vulnerabilidad climatica", "Criteria matrix for assessing climate vulnerability", "Matriz"),
            ("Roteiro de perguntas para auditoria com enfoque de justica climatica", "Guia de preguntas para auditoria con enfoque de justicia climatica", "Question guide for audits with a climate justice approach", "Perguntas de auditoria"),
        ]
        setor = Setor.objects.get(nome="Meio ambiente")
        for titulo, titulo_es, titulo_en, tipo_recurso in recursos:
            recurso, _ = BancoTecnico.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "titulo_es": titulo_es,
                    "titulo_en": titulo_en,
                    "descricao": "Recurso metodologico demonstrativo vinculado a boas praticas da plataforma.",
                    "descricao_es": "Recurso metodologico demostrativo vinculado a buenas practicas de la plataforma.",
                    "descricao_en": "Demonstration methodological resource linked to platform good practices.",
                    "tipo_recurso": tipo_recurso,
                    "tipo_recurso_es": tipo_recurso,
                    "tipo_recurso_en": tipo_recurso,
                    "setor": setor,
                    "url": "https://www.olacefs.com",
                },
            )
            recurso.dimensoes.set(DimensaoJusticaClimatica.objects.filter(nome__in=["Distributiva", "Procedimental"]))

        self.stdout.write(self.style.SUCCESS("Dados negociais do MVP carregados com sucesso."))
