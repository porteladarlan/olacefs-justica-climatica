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
    help = "Carrega dados ficticios mais realistas para demonstracao do MVP"

    def handle(self, *args, **options):
        paises_data = [
            ("Brasil", "BRA"),
            ("Chile", "CHL"),
            ("Colombia", "COL"),
            ("Mexico", "MEX"),
            ("Peru", "PER"),
            ("Costa Rica", "CRI"),
        ]

        for nome, sigla in paises_data:
            Pais.objects.get_or_create(sigla=sigla, defaults={"nome": nome})

        tipos_data = [
            "Auditoria de desempenho",
            "Auditoria de conformidade",
            "Avaliacao de politica publica",
            "Estudo tecnico",
            "Metodologia ou guia",
            "Auditoria coordenada",
        ]

        for nome in tipos_data:
            TipoExperiencia.objects.get_or_create(nome=nome)

        setores_data = [
            "Infraestrutura",
            "Recursos hidricos",
            "Agricultura",
            "Energia",
            "Saude",
            "Gestao de riscos",
            "Meio ambiente",
        ]

        for nome in setores_data:
            Setor.objects.get_or_create(nome=nome)

        dimensoes_data = [
            "Distributiva",
            "Reconhecimento",
            "Procedimental",
            "Intergeracional",
            "Participacao social",
            "Acesso a servicos",
        ]

        for nome in dimensoes_data:
            DimensaoJusticaClimatica.objects.get_or_create(nome=nome)

        grupos_data = [
            "Comunidades indigenas",
            "Mulheres",
            "Pescadores artesanais",
            "Populacao rural",
            "Pessoas em situacao de pobreza",
            "Comunidades costeiras",
        ]

        for nome in grupos_data:
            GrupoVulneravel.objects.get_or_create(nome=nome)

        efs_data = [
            ("Tribunal de Contas da Uniao", "TCU", "BRA"),
            ("Contraloria General de la Republica", "CGR", "CHL"),
            ("Contraloria General de la Republica", "CGR", "COL"),
            ("Auditoria Superior de la Federacion", "ASF", "MEX"),
            ("Contraloria General de la Republica", "CGR", "PER"),
            ("Contraloria General de la Republica", "CGR", "CRI"),
        ]

        for nome, sigla, pais_sigla in efs_data:
            pais = Pais.objects.get(sigla=pais_sigla)
            EFS.objects.get_or_create(
                nome=nome,
                pais=pais,
                defaults={"sigla": sigla},
            )

        experiencias_data = [
            {
                "titulo": "Auditoria sobre infraestrutura resiliente em zonas costeiras",
                "pais": "CHL",
                "efs": "Contraloria General de la Republica",
                "tipo": "Auditoria de desempenho",
                "setor": "Infraestrutura",
                "ano": 2024,
                "status": Experiencia.StatusIniciativa.CONCLUIDA,
                "dimensoes": ["Distributiva", "Reconhecimento", "Participacao social"],
                "grupos": ["Comunidades costeiras", "Pescadores artesanais"],
                "descricao": "A experiencia avaliou se investimentos em infraestrutura costeira consideravam riscos climaticos, exposicao territorial e impactos sobre comunidades dependentes da pesca artesanal.",
                "problema_climatico": "Aumento da erosao costeira, elevacao do nivel do mar e maior frequencia de eventos extremos em municipios litoraneos.",
                "objetivo": "Verificar se os criterios de priorizacao de obras costeiras incorporavam vulnerabilidade social, risco climatico e participacao das comunidades afetadas.",
                "resultados": "A auditoria identificou ausencia de criterios uniformes para priorizar territorios vulneraveis, baixa integracao entre planejamento urbano e adaptacao climatica e necessidade de fortalecer consultas locais.",
                "recomendacoes": "Incluir indicadores de vulnerabilidade social nos planos de investimento, aperfeicoar mapas de risco e estabelecer protocolos de consulta a comunidades costeiras.",
                "replicabilidade": "Pode ser replicada por EFS com territorios costeiros ou ilhas, adaptando a matriz de risco para dados locais de exposicao e capacidade adaptativa.",
            },
            {
                "titulo": "Avaliacao da equidade no acesso a agua em periodos de seca",
                "pais": "BRA",
                "efs": "Tribunal de Contas da Uniao",
                "tipo": "Avaliacao de politica publica",
                "setor": "Recursos hidricos",
                "ano": 2025,
                "status": Experiencia.StatusIniciativa.EXECUCAO,
                "dimensoes": ["Distributiva", "Acesso a servicos", "Intergeracional"],
                "grupos": ["Populacao rural", "Pessoas em situacao de pobreza"],
                "descricao": "A experiencia analisou programas publicos de resposta a seca e sua capacidade de atender populacoes rurais com menor acesso a infraestrutura hidrica.",
                "problema_climatico": "Secas prolongadas ampliaram a pressao sobre abastecimento humano, agricultura familiar e seguranca alimentar.",
                "objetivo": "Avaliar se recursos, obras emergenciais e medidas de apoio estavam chegando de forma proporcional aos territorios mais vulneraveis.",
                "resultados": "Foram identificadas lacunas de dados territoriais, criterios pouco transparentes de priorizacao e ausencia de monitoramento sobre impactos diferenciados.",
                "recomendacoes": "Criar criterios publicos de elegibilidade, integrar bases de vulnerabilidade e monitorar atendimento por municipio, genero e condicao socioeconomica.",
                "replicabilidade": "A abordagem pode orientar auditorias sobre agua, saneamento, seguranca alimentar e adaptacao em regioes sujeitas a estiagens.",
            },
            {
                "titulo": "Monitoramento de obras de drenagem em areas urbanas vulneraveis",
                "pais": "PER",
                "efs": "Contraloria General de la Republica",
                "tipo": "Auditoria de conformidade",
                "setor": "Gestao de riscos",
                "ano": 2023,
                "status": Experiencia.StatusIniciativa.CONCLUIDA,
                "dimensoes": ["Acesso a servicos", "Procedimental"],
                "grupos": ["Pessoas em situacao de pobreza", "Mulheres"],
                "descricao": "A experiencia monitorou obras de drenagem urbana em bairros expostos a enchentes recorrentes, com foco em prazos, qualidade da execucao e beneficios para areas vulneraveis.",
                "problema_climatico": "Chuvas intensas e alagamentos recorrentes afetaram moradias, mobilidade, acesso a saude e continuidade escolar.",
                "objetivo": "Verificar se obras de drenagem priorizavam areas com maior risco e se os cronogramas respondiam a periodos criticos de chuva.",
                "resultados": "O trabalho apontou atrasos, fragilidade na fiscalizacao contratual e falta de indicadores para medir reducao efetiva do risco em comunidades vulneraveis.",
                "recomendacoes": "Fortalecer fiscalizacao fisica das obras, publicar cronogramas atualizados e vincular pagamentos a evidencias de execucao e reducao de risco.",
                "replicabilidade": "Pode ser adaptada para monitoramento de obras contra enchentes, contencao de encostas e infraestrutura resiliente.",
            },
            {
                "titulo": "Auditoria sobre financiamento climatico e distribuicao territorial",
                "pais": "COL",
                "efs": "Contraloria General de la Republica",
                "tipo": "Estudo tecnico",
                "setor": "Meio ambiente",
                "ano": 2024,
                "status": Experiencia.StatusIniciativa.CONCLUIDA,
                "dimensoes": ["Distributiva", "Procedimental", "Participacao social"],
                "grupos": ["Comunidades indigenas", "Populacao rural"],
                "descricao": "O estudo avaliou como recursos de financiamento climatico foram distribuidos entre territorios e se havia alinhamento com vulnerabilidades socioambientais.",
                "problema_climatico": "Territorios com maior exposicao a desmatamento, seca e eventos extremos nem sempre recebiam apoio proporcional ao risco enfrentado.",
                "objetivo": "Examinar transparencia, rastreabilidade e coerencia territorial na alocacao de recursos climaticos.",
                "resultados": "Foram observadas dificuldades de rastrear recursos, baixa padronizacao de informacoes e ausencia de criterios claros de justica climatica.",
                "recomendacoes": "Criar classificacao orcamentaria climatica, publicar dados territoriais e explicitar criterios de priorizacao.",
                "replicabilidade": "A metodologia e replicavel para auditorias sobre fundos climaticos, orcamentos verdes e programas de adaptacao.",
            },
            {
                "titulo": "Auditoria de transicao energetica justa em territorios vulneraveis",
                "pais": "MEX",
                "efs": "Auditoria Superior de la Federacion",
                "tipo": "Auditoria coordenada",
                "setor": "Energia",
                "ano": 2022,
                "status": Experiencia.StatusIniciativa.CONCLUIDA,
                "dimensoes": ["Reconhecimento", "Intergeracional", "Participacao social"],
                "grupos": ["Mulheres", "Comunidades indigenas"],
                "descricao": "A auditoria analisou se programas de transicao energetica consideravam efeitos sociais, acesso a beneficios e mecanismos de participacao em territorios vulneraveis.",
                "problema_climatico": "Mudancas na matriz energetica podem gerar beneficios ambientais, mas tambem riscos de exclusao se nao considerarem desigualdades locais.",
                "objetivo": "Avaliar governanca, participacao social e criterios de equidade em politicas de transicao energetica.",
                "resultados": "A auditoria identificou oportunidades para fortalecer consulta previa, indicadores de impacto social e mecanismos de compensacao territorial.",
                "recomendacoes": "Incluir metricas sociais nos programas energeticos, mapear impactos diferenciados e ampliar participacao de comunidades afetadas.",
                "replicabilidade": "Pode apoiar outras EFS em auditorias sobre energia renovavel, descarbonizacao e justica na transicao.",
            },
            {
                "titulo": "Metodologia para avaliar planos locais de adaptacao climatica",
                "pais": "CRI",
                "efs": "Contraloria General de la Republica",
                "tipo": "Metodologia ou guia",
                "setor": "Agricultura",
                "ano": 2025,
                "status": Experiencia.StatusIniciativa.EXECUCAO,
                "dimensoes": ["Procedimental", "Acesso a servicos", "Reconhecimento"],
                "grupos": ["Populacao rural", "Mulheres"],
                "descricao": "A metodologia orienta a avaliacao de planos locais de adaptacao, com atencao a agricultura familiar, acesso a assistencia tecnica e capacidade institucional municipal.",
                "problema_climatico": "Mudancas no regime de chuvas e eventos extremos afetam producao agricola, renda rural e seguranca alimentar.",
                "objetivo": "Criar um roteiro de avaliacao para verificar qualidade, implementacao e enfoque de equidade em planos locais de adaptacao.",
                "resultados": "O metodo permite classificar maturidade dos planos, identificar lacunas de dados e priorizar recomendacoes para municipios com maior vulnerabilidade.",
                "recomendacoes": "Aplicar matriz de maturidade, incluir indicadores sociais e promover validacao participativa dos planos.",
                "replicabilidade": "Pode ser usado como guia por outras EFS para avaliar politicas subnacionais de adaptacao climatica.",
            },
        ]

        texto_comum = {
            "relacao_adaptacao_mitigacao_gestao_desastres": "A iniciativa esta relacionada a adaptacao climatica, reducao de vulnerabilidades, gestao de riscos e melhoria da governanca publica.",
            "riscos_climaticos": "Eventos extremos, variabilidade climatica, perdas economicas, danos a infraestrutura e impactos diferenciados sobre grupos vulneraveis.",
            "enfoque_justica_climatica": "A experiencia considera a distribuicao desigual dos impactos climaticos, a participacao de grupos afetados e a necessidade de priorizar territorios vulneraveis.",
            "impactos_diferenciados": "Os impactos tendem a ser maiores em grupos com menor capacidade de resposta, menor acesso a servicos publicos e maior dependencia de recursos naturais.",
            "perguntas_chave": "Quem e mais afetado? Como os recursos sao priorizados? Existem criterios de equidade? Os grupos vulneraveis participam das decisoes?",
            "criterios_utilizados": "Efetividade, equidade, transparencia, participacao social, capacidade institucional e foco territorial.",
            "metodologia": "Analise documental, entrevistas, revisao de bases publicas, matriz de risco e sistematizacao de evidencias.",
            "fontes_informacao": "Planos publicos, bases governamentais, relatorios tecnicos, dados territoriais e documentos institucionais.",
            "mudancas_ou_impactos": "A experiencia contribuiu para melhorar a qualidade das recomendacoes e reforcar a importancia de criterios de justica climatica.",
            "motivo_boa_pratica": "A experiencia combina abordagem metodologica clara, foco em vulnerabilidade e potencial de replicacao por outras EFS.",
            "elementos_replicaveis": "Matriz de risco, roteiro de entrevistas, criterios de priorizacao, indicadores de vulnerabilidade e estrutura de ficha tecnica.",
            "dificuldades": "Limitacoes de dados, baixa padronizacao de informacoes, capacidade institucional desigual e integracao limitada entre setores.",
            "licoes_aprendidas": "Auditorias climaticas ganham qualidade quando incorporam criterios territoriais, sociais e distributivos desde o planejamento.",
            "o_que_fariam_diferente": "Ampliar a etapa inicial de validacao com atores territoriais e definir indicadores de equidade antes da coleta de dados.",
            "necessidades_para_replicacao": "Dados minimos, equipe capacitada, apoio institucional, criterios de vulnerabilidade e metodologia adaptavel.",
            "ferramentas_metodologias_uteis": "Matriz de risco climatico, analise de vulnerabilidade, entrevistas estruturadas e painel de indicadores.",
            "temas_sugeridos_para_guia": "Governanca climatica, financiamento climatico, infraestrutura resiliente, adaptacao territorial e participacao social.",
            "apoio_requerido_pelas_efs": "Capacitacao, intercambio metodologico, modelos de referencia e apoio para sistematizar evidencias.",
        }

        for item in experiencias_data:
            pais = Pais.objects.get(sigla=item["pais"])
            efs = EFS.objects.get(nome=item["efs"], pais=pais)
            tipo = TipoExperiencia.objects.get(nome=item["tipo"])
            setor = Setor.objects.get(nome=item["setor"])

            experiencia, _ = Experiencia.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "efs": efs,
                    "pais": pais,
                    "tipo_experiencia": tipo,
                    "ano_execucao": item["ano"],
                    "status_iniciativa": item["status"],
                    "setor": setor,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    "descricao": item["descricao"],
                    "problema_climatico": item["problema_climatico"],
                    "objetivo": item["objetivo"],
                    "resultados": item["resultados"],
                    "recomendacoes": item["recomendacoes"],
                    "replicabilidade": item["replicabilidade"],
                    **texto_comum,
                },
            )

            experiencia.dimensoes_consideradas.set(
                DimensaoJusticaClimatica.objects.filter(nome__in=item["dimensoes"])
            )
            experiencia.grupos_vulneraveis.set(
                GrupoVulneravel.objects.filter(nome__in=item["grupos"])
            )

        banco_tecnico_data = [
            (
                "Roteiro de perguntas para auditoria com enfoque de justica climatica",
                "Perguntas orientadoras para incorporar vulnerabilidade, equidade, participacao e impactos diferenciados no planejamento de auditorias.",
                "Perguntas de auditoria",
                "https://www.olacefs.com",
                "Meio ambiente",
                ["Procedimental", "Participacao social"],
            ),
            (
                "Matriz de criterios para avaliacao de vulnerabilidade climatica",
                "Modelo de criterios para identificar exposicao, sensibilidade, capacidade adaptativa e prioridade territorial.",
                "Criterios",
                "https://www.cepal.org",
                "Gestao de riscos",
                ["Distributiva", "Acesso a servicos"],
            ),
            (
                "Modelo de ficha tecnica para boas praticas",
                "Estrutura padronizada para registrar objetivo, metodologia, resultados, licoes aprendidas e potencial de replicacao.",
                "Modelo",
                "https://www.giz.de",
                "Infraestrutura",
                ["Reconhecimento", "Intergeracional"],
            ),
            (
                "Checklist para avaliar planos de adaptacao climatica",
                "Lista de verificacao para analisar governanca, metas, indicadores, financiamento, participacao social e foco em grupos vulneraveis.",
                "Checklist",
                "https://www.olacefs.com",
                "Recursos hidricos",
                ["Procedimental", "Distributiva"],
            ),
        ]

        for titulo, descricao, tipo_recurso, url, setor_nome, dimensoes_nomes in banco_tecnico_data:
            setor = Setor.objects.get(nome=setor_nome)

            recurso, _ = BancoTecnico.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "descricao": descricao,
                    "tipo_recurso": tipo_recurso,
                    "url": url,
                    "setor": setor,
                },
            )

            recurso.dimensoes.set(
                DimensaoJusticaClimatica.objects.filter(nome__in=dimensoes_nomes)
            )

        self.stdout.write(self.style.SUCCESS("Dados ficticios realistas carregados com sucesso."))