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
    help = "Carrega dados ficticios para demonstracao do MVP"

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

        texto_padrao = {
            "descricao": "Experiencia ficticia criada para demonstracao do MVP da plataforma regional.",
            "problema_climatico": "A experiencia aborda riscos climaticos com impactos diferenciados em grupos vulneraveis.",
            "relacao_adaptacao_mitigacao_gestao_desastres": "A iniciativa contribui para adaptacao climatica, gestao de riscos e melhoria da governanca publica.",
            "riscos_climaticos": "Secas prolongadas, enchentes, eventos extremos e perda de acesso a servicos essenciais.",
            "enfoque_justica_climatica": "A experiencia considera desigualdades territoriais, sociais e economicas na exposicao aos impactos climaticos.",
            "impactos_diferenciados": "Grupos vulneraveis apresentam maior exposicao aos riscos e menor capacidade de resposta institucional.",
            "objetivo": "Avaliar a resposta publica e identificar oportunidades de melhoria na incorporacao da justica climatica.",
            "perguntas_chave": "As politicas alcancam os grupos mais vulneraveis? Existem criterios de equidade na alocacao de recursos?",
            "criterios_utilizados": "Efetividade, equidade, transparencia, participacao social e capacidade de resposta institucional.",
            "metodologia": "Analise documental, entrevistas, revisao de bases publicas e sistematizacao de evidencias.",
            "fontes_informacao": "Relatorios publicos, dados governamentais, informacoes territoriais e documentos institucionais.",
            "resultados": "Foram identificadas lacunas de coordenacao, dados insuficientes e oportunidades de melhoria na gestao climatica.",
            "recomendacoes": "Fortalecer mecanismos de monitoramento, aprimorar indicadores e ampliar a participacao dos grupos afetados.",
            "mudancas_ou_impactos": "A experiencia contribuiu para orientar melhorias na governanca e na priorizacao de politicas publicas.",
            "motivo_boa_pratica": "A experiencia apresenta abordagem replicavel, estrutura metodologica clara e foco em populacoes vulneraveis.",
            "elementos_replicaveis": "Matriz de risco, criterios de priorizacao, roteiro de entrevistas e estrutura de analise de vulnerabilidade.",
            "dificuldades": "Limitacoes na padronizacao de dados, baixa integracao institucional e restricoes de informacao territorial.",
            "licoes_aprendidas": "A inclusao de criterios de justica climatica melhora a qualidade das analises e das recomendacoes.",
            "o_que_fariam_diferente": "Incluir uma etapa inicial de alinhamento metodologico e validacao dos dados com atores territoriais.",
            "replicabilidade": "A experiencia pode ser replicada por outras EFS com adaptacoes ao contexto institucional e territorial.",
            "necessidades_para_replicacao": "Dados minimos, equipe tecnica capacitada, apoio institucional e metodologia adaptavel.",
            "ferramentas_metodologias_uteis": "Matriz de risco climatico, analise de vulnerabilidade, entrevistas estruturadas e paineis de indicadores.",
            "temas_sugeridos_para_guia": "Governanca climatica, financiamento climatico, participacao social e avaliacao de impactos diferenciados.",
            "apoio_requerido_pelas_efs": "Capacitacao, intercambio metodologico, modelos de referencia e apoio para sistematizacao de evidencias.",
        }

        experiencias_data = [
            ("Auditoria sobre resiliencia hidrica em comunidades vulneraveis", "BRA", "Tribunal de Contas da Uniao", "Auditoria de desempenho", "Recursos hidricos", 2024, Experiencia.StatusIniciativa.CONCLUIDA, ["Distributiva", "Acesso a servicos"], ["Populacao rural", "Pessoas em situacao de pobreza"]),
            ("Avaliacao de adaptacao costeira e comunidades expostas", "CHL", "Contraloria General de la Republica", "Avaliacao de politica publica", "Gestao de riscos", 2023, Experiencia.StatusIniciativa.CONCLUIDA, ["Reconhecimento", "Procedimental"], ["Comunidades costeiras", "Pescadores artesanais"]),
            ("Estudo sobre infraestrutura resiliente em areas de risco", "COL", "Contraloria General de la Republica", "Estudo tecnico", "Infraestrutura", 2024, Experiencia.StatusIniciativa.EXECUCAO, ["Distributiva", "Intergeracional"], ["Comunidades indigenas", "Populacao rural"]),
            ("Auditoria de transicao energetica justa", "MEX", "Auditoria Superior de la Federacion", "Auditoria de conformidade", "Energia", 2022, Experiencia.StatusIniciativa.CONCLUIDA, ["Distributiva", "Participacao social"], ["Mulheres", "Pessoas em situacao de pobreza"]),
            ("Metodologia para avaliar resposta publica a enchentes urbanas", "PER", "Contraloria General de la Republica", "Metodologia ou guia", "Gestao de riscos", 2025, Experiencia.StatusIniciativa.EXECUCAO, ["Procedimental", "Acesso a servicos"], ["Pessoas em situacao de pobreza", "Populacao rural"]),
            ("Auditoria coordenada sobre agricultura resiliente", "CRI", "Contraloria General de la Republica", "Auditoria coordenada", "Agricultura", 2023, Experiencia.StatusIniciativa.CONCLUIDA, ["Reconhecimento", "Intergeracional"], ["Comunidades indigenas", "Mulheres"]),
        ]

        for titulo, pais_sigla, efs_nome, tipo_nome, setor_nome, ano, status, dimensoes_nomes, grupos_nomes in experiencias_data:
            pais = Pais.objects.get(sigla=pais_sigla)
            efs = EFS.objects.get(nome=efs_nome, pais=pais)
            tipo = TipoExperiencia.objects.get(nome=tipo_nome)
            setor = Setor.objects.get(nome=setor_nome)

            experiencia, _ = Experiencia.objects.get_or_create(
                titulo=titulo,
                defaults={
                    "efs": efs,
                    "pais": pais,
                    "tipo_experiencia": tipo,
                    "ano_execucao": ano,
                    "status_iniciativa": status,
                    "setor": setor,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    **texto_padrao,
                },
            )

            experiencia.dimensoes_consideradas.set(
                DimensaoJusticaClimatica.objects.filter(nome__in=dimensoes_nomes)
            )
            experiencia.grupos_vulneraveis.set(
                GrupoVulneravel.objects.filter(nome__in=grupos_nomes)
            )

        banco_tecnico_data = [
            ("Roteiro de perguntas para auditoria com enfoque de justica climatica", "Conjunto de perguntas orientadoras para apoiar equipes de auditoria na analise de impactos diferenciados.", "Perguntas de auditoria", "https://www.olacefs.com", "Meio ambiente", ["Procedimental", "Participacao social"]),
            ("Matriz de criterios para avaliacao de vulnerabilidade climatica", "Modelo de criterios para identificar exposicao, sensibilidade e capacidade adaptativa.", "Criterios", "https://www.cepal.org", "Gestao de riscos", ["Distributiva", "Acesso a servicos"]),
            ("Ferramenta de sistematizacao de evidencias climaticas", "Referencia metodologica para organizar evidencias de auditoria relacionadas a justica climatica.", "Ferramenta", "https://www.iadb.org", "Infraestrutura", ["Reconhecimento", "Intergeracional"]),
        ]

        for titulo, descricao, tipo_recurso, url, setor_nome, dimensoes_nomes in banco_tecnico_data:
            setor = Setor.objects.get(nome=setor_nome)

            recurso, _ = BancoTecnico.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS("Dados ficticios carregados com sucesso."))
