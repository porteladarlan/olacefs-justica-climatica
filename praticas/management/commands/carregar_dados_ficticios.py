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
    help = "Carrega dados fictícios para demonstração do MVP"

    def handle(self, *args, **options):
        dim_nomes = ["Distributiva", "Reconhecimento", "Procedimental", "Intergeracional"]
        grupo_nomes = ["Comunidades indígenas", "Mulheres", "Pescadores artesanais", "População rural"]
        setor_nomes = ["Recursos hídricos", "Agricultura", "Energia", "Saúde", "Gestão de riscos"]
        tipo_nomes = ["Auditoria de conformidade", "Auditoria operacional", "Estudo técnico", "Monitoramento"]

        paises = {
            "Brasil": "BRA",
            "Chile": "CHL",
            "Colômbia": "COL",
            "México": "MEX",
            "Peru": "PER",
            "Costa Rica": "CRI",
        }

        for nome in dim_nomes:
            DimensaoJusticaClimatica.objects.get_or_create(nome=nome)
        for nome in grupo_nomes:
            GrupoVulneravel.objects.get_or_create(nome=nome)
        for nome in setor_nomes:
            Setor.objects.get_or_create(nome=nome)
        for nome in tipo_nomes:
            TipoExperiencia.objects.get_or_create(nome=nome)

        for nome, sigla in paises.items():
            Pais.objects.get_or_create(nome=nome, defaults={"sigla": sigla})

        efs_data = [
            ("Tribunal de Contas da União", "TCU", "Brasil"),
            ("Contraloría General de la República", "CGR", "Chile"),
            ("Contraloría General de la República", "CGR", "Colômbia"),
            ("Auditoría Superior de la Federación", "ASF", "México"),
            ("Contraloría General de la República", "CGR", "Peru"),
            ("Contraloría General de la República", "CGR", "Costa Rica"),
        ]

        for nome, sigla, pais_nome in efs_data:
            pais = Pais.objects.get(nome=pais_nome)
            EFS.objects.get_or_create(nome=nome, pais=pais, defaults={"sigla": sigla})

        base_texto = {
            "descricao": "Experiência focada em fortalecer políticas públicas diante dos efeitos climáticos.",
            "problema_climatico": "Eventos extremos e vulnerabilidade territorial com impactos socioeconômicos.",
            "relacao_adaptacao_mitigacao_gestao_desastres": "A iniciativa contribui para adaptação e gestão de desastres com foco preventivo.",
            "riscos_climaticos": "Secas prolongadas, enchentes e perdas produtivas.",
            "enfoque_justica_climatica": "Priorização de grupos historicamente expostos e com menor acesso a serviços públicos.",
            "impactos_diferenciados": "Comunidades vulneráveis sofrem efeitos mais severos sobre renda e acesso à água.",
            "objetivo": "Avaliar efetividade de políticas e orientar melhorias de governança climática.",
            "perguntas_chave": "As ações alcançam os territórios mais vulneráveis? Há monitoramento de resultados?",
            "criterios_utilizados": "Eficiência, efetividade, equidade territorial e participação social.",
            "metodologia": "Análise documental, entrevistas e visitas em campo.",
            "fontes_informacao": "Bases governamentais, relatórios setoriais e dados geoespaciais.",
            "resultados": "Identificação de lacunas de planejamento e recomendações para aprimorar execução.",
            "recomendacoes": "Reforçar integração interinstitucional e ampliar indicadores de vulnerabilidade.",
            "mudancas_ou_impactos": "Melhor alocação de recursos e incorporação de critérios socioambientais.",
            "motivo_boa_pratica": "Modelo replicável com método claro e foco em populações vulneráveis.",
            "elementos_replicaveis": "Matriz de risco, protocolo de participação e indicadores comparáveis.",
            "dificuldades": "Limitações de dados padronizados e de coordenação federativa.",
            "licoes_aprendidas": "Participação social melhora a qualidade das recomendações.",
            "o_que_fariam_diferente": "Incluir etapa inicial de harmonização de bases territoriais.",
            "replicabilidade": "Alta, desde que haja dados mínimos e equipe técnica multidisciplinar.",
            "necessidades_para_replicacao": "Capacitação, integração de bases e apoio institucional.",
            "ferramentas_metodologias_uteis": "Painéis de indicadores e roteiros de auditoria temática.",
            "temas_sugeridos_para_guia": "Financiamento climático e governança multinível.",
            "apoio_requerido_pelas_efs": "Troca regional de metodologia e capacitação em dados climáticos.",
        }

        experiencias = [
            ("Auditoria de resiliência hídrica em semiárido", "Brasil", "Tribunal de Contas da União", "Auditoria operacional", "Recursos hídricos", 2024),
            ("Monitoramento de adaptação costeira", "Chile", "Contraloría General de la República", "Monitoramento", "Gestão de riscos", 2023),
            ("Auditoria de proteção a comunidades ribeirinhas", "Colômbia", "Contraloría General de la República", "Auditoria de conformidade", "Saúde", 2022),
            ("Estudo técnico sobre transição energética justa", "México", "Auditoría Superior de la Federación", "Estudo técnico", "Energia", 2024),
            ("Avaliação de resposta a enchentes urbanas", "Peru", "Contraloría General de la República", "Auditoria operacional", "Gestão de riscos", 2021),
            ("Auditoria de agricultura resiliente", "Costa Rica", "Contraloría General de la República", "Auditoria de conformidade", "Agricultura", 2025),
        ]

        dims = list(DimensaoJusticaClimatica.objects.all()[:2])
        grupos = list(GrupoVulneravel.objects.all()[:2])
        tipo_status = [
            Experiencia.StatusIniciativa.CONCLUIDA,
            Experiencia.StatusIniciativa.EM_EXECUCAO,
            Experiencia.StatusIniciativa.CONCLUIDA,
            Experiencia.StatusIniciativa.EM_EXECUCAO,
            Experiencia.StatusIniciativa.CONCLUIDA,
            Experiencia.StatusIniciativa.EM_PLANEJAMENTO,
        ]

        for idx, (titulo, pais_nome, efs_nome, tipo_nome, setor_nome, ano) in enumerate(experiencias):
            pais = Pais.objects.get(nome=pais_nome)
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
                    "status_iniciativa": tipo_status[idx],
                    "setor": setor,
                    "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
                    **base_texto,
                },
            )
            experiencia.dimensoes_consideradas.set(dims)
            experiencia.grupos_vulneraveis.set(grupos)

        recursos = [
            ("Guia de auditoria climática", "Documento metodológico para planejamento de auditorias.", "Guia", "https://www.olacefs.com"),
            ("Base regional de indicadores", "Coleção de indicadores de risco e vulnerabilidade.", "Base de dados", "https://www.cepal.org"),
            ("Curso introdutório de justiça climática", "Material de capacitação para equipes técnicas.", "Curso", "https://www.iadb.org"),
        ]
        setor_energia = Setor.objects.get(nome="Energia")
        dimensao_reconhecimento = DimensaoJusticaClimatica.objects.get(nome="Reconhecimento")

        for titulo, descricao, tipo_recurso, url in recursos:
            recurso, _ = BancoTecnico.objects.get_or_create(
                titulo=titulo,
                defaults={
                    "descricao": descricao,
                    "tipo_recurso": tipo_recurso,
                    "url": url,
                    "setor": setor_energia,
                },
            )
            recurso.dimensoes.add(dimensao_reconhecimento)

        self.stdout.write(self.style.SUCCESS("Dados fictícios carregados com sucesso."))
