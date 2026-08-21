import hashlib
import re
from pathlib import Path

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class HomePrimeiraEvolucaoTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate_all()

    def test_home_responde_e_usa_asset_institucional_local(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<section class="jc-hero home-block"', html=False)
        self.assertContains(response, f'src="{static("praticas/img/icone-jc.svg")}"')
        self.assertContains(response, "pessoas colaborando ao redor de uma balan&ccedil;a")

    def test_cabecalho_corresponde_ao_prototipo_sem_busca_legada(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertContains(response, "Plataforma de Justi&ccedil;a Clim&aacute;tica", html=False)
        self.assertContains(response, "CGID + COMTEMA", html=False)
        self.assertNotContains(response, "Plataforma Regional &middot; CGID + COMTEMA", html=False)
        self.assertNotContains(response, "Guia Viva", html=False)
        self.assertContains(response, f'href="{reverse("catalogo_experiencias")}"')
        self.assertContains(response, f'href="{reverse("normas_internacionais")}"')
        self.assertContains(response, "Boas Pr&aacute;ticas", html=False)
        self.assertContains(response, "Marcos Normativos")
        self.assertContains(response, "Ferramentas")
        self.assertContains(response, f'href="{reverse("ferramentas")}"')
        self.assertIsNone(re.search(r'class="[^"]*\bnav-link-pending\b', html))
        self.assertContains(response, f'href="{reverse("login_usuario")}"')
        self.assertContains(response, f'href="{reverse("registrar_usuario")}"')
        self.assertContains(response, f'href="{reverse("status_envio")}"')
        self.assertContains(response, 'id="languageSwitcher"')
        self.assertContains(response, 'id="highContrastToggle"')
        self.assertNotIn('id="buscaGlobal"', html)
        self.assertNotIn("nav-search-form", html)
        self.assertNotIn("data-home-tab-target", html)

    def test_hero_preserva_proposito_e_ctas_corretos_nos_tres_idiomas(self):
        casos = [
            ("/", "pr&aacute;tica do controle externo", "Explorar marcos normativos", "Ver mapa da regi&atilde;o"),
            ("/es/", "pr&aacute;ctica del control externo", "Explorar marcos normativos", "Ver mapa de la regi&oacute;n"),
            ("/en/", "external-control practice", "Explore normative frameworks", "View the regional map"),
        ]

        for caminho, proposito, cta_marcos, cta_mapa in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)

                html = response.content.decode("utf-8")
                hero = html.split(
                    '<section class="jc-hero home-block"',
                    1,
                )[1].split("</section>", 1)[0]

                self.assertContains(response, proposito, html=False)
                self.assertContains(response, "COMTEMA")
                self.assertContains(response, "CGID")
                self.assertNotIn("GIZ", hero)
                self.assertContains(response, cta_marcos, html=False)
                self.assertContains(response, cta_mapa, html=False)
                self.assertContains(response, f'href="{reverse("normas_internacionais")}"')
                self.assertContains(response, 'href="#mapSection"')

    def test_home_remove_grade_antiga_e_preserva_ordem_aprovada(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertNotIn("home-primary-access", html)
        self.assertNotIn("Banco T&eacute;cnico", html)
        self.assertNotIn("Dimens&otilde;es de Justi&ccedil;a Clim&aacute;tica", html)
        hero = html.index('class="jc-hero home-block"')
        mensagens = html.index('id="testimonialsSection"')
        fundamentos = html.index('id="pillarsSection"')
        mapa = html.index('id="mapSection"')
        video = html.index('id="videoSection"')
        self.assertLess(hero, mensagens)
        self.assertLess(mensagens, fundamentos)
        self.assertLess(fundamentos, mapa)
        self.assertLess(mapa, video)

    def test_mensagens_institucionais_usam_assets_locais(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")

        self.assertContains(response, "Palavras das Presid&ecirc;ncias da CGID e da COMTEMA")
        self.assertContains(response, "Dr. Camilo Ben&iacute;tez", html=False)
        self.assertContains(response, "Dra. Pamela Calletti")
        self.assertContains(response, f'src="{static("praticas/img/camilo-benitez.jpg")}"')
        self.assertContains(response, f'src="{static("praticas/img/pamela-calletti.jpg")}"')
        self.assertIsNone(re.search(r'<img[^>]+src=["\']https?://', html, re.IGNORECASE))
        self.assertLess(
            html.index("Dra. Pamela Calletti"),
            html.index("Dr. Camilo Ben&iacute;tez"),
        )

    def test_fundamentos_tem_exatamente_tres_abas_acessiveis(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(response, '<button class="home-foundation-tab', count=3, html=False)
        self.assertContains(response, 'id="concepto-tab"')
        self.assertContains(response, 'id="controle-tab"')
        self.assertContains(response, 'id="genero-tab"')
        self.assertNotContains(response, 'id="normas-tab"')
        self.assertContains(response, 'id="concepto-pane" role="tabpanel" aria-labelledby="concepto-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'id="controle-pane" role="tabpanel" aria-labelledby="controle-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'id="genero-pane" role="tabpanel" aria-labelledby="genero-tab" tabindex="-1"', html=False)
        self.assertContains(response, f'src="{static("praticas/img/fundamentos-justica-climatica.svg")}"')
        self.assertContains(response, f'src="{static("praticas/img/fundamentos-controle-externo.svg")}"')
        self.assertContains(response, f'src="{static("praticas/img/fundamentos-estrategia-genero.svg")}"')
        self.assertNotContains(response, "praticas/img/pilar-justicia.jpg")
        self.assertNotContains(response, "praticas/img/pilar-control.jpg")
        self.assertNotContains(response, "praticas/img/pilar-genero.jpg")

    def test_svgs_oficiais_foram_copiados_sem_alteracao(self):
        hashes_esperados = {
            "praticas/img/fundamentos-justica-climatica.svg": "6F38114C6D053EDCD8C418857CF839CA9BC1FDBA7BA86D28321223842581649F",
            "praticas/img/fundamentos-controle-externo.svg": "DA9BDC3C512DF64A079DF5D7EA4D671D12738420083F0D3B0FC00D55B8DB8464",
            "praticas/img/fundamentos-estrategia-genero.svg": "4AEAE96D7AEC91D4A22F20B6541C39C09AF7E0C443610D0D99F0F784B9D7C07C",
        }
        for caminho, hash_esperado in hashes_esperados.items():
            with self.subTest(caminho=caminho):
                arquivo = Path(finders.find(caminho))
                self.assertEqual(
                    hashlib.sha256(arquivo.read_bytes()).hexdigest().upper(),
                    hash_esperado,
                )

    def test_fundamentos_preservam_hierarquia_de_titulos(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split('<section class="home-foundations', 1)[1].split("</section>", 1)[0]

        self.assertEqual(len(re.findall(r"<h2\b", fundamentos)), 1)
        self.assertEqual(len(re.findall(r"<h3\b", fundamentos)), 3)
        self.assertEqual(len(re.findall(r"<h4\b", fundamentos)), 5)
        self.assertEqual(len(re.findall(r"<h5\b", fundamentos)), 2)
        self.assertIsNone(re.search(r"<h(?:1|6)\b", fundamentos))
        self.assertIsNone(re.search(r"<h[2-5][^>]*>\s*</h[2-5]>", fundamentos))

    def test_home_carrega_estilo_proprio_e_preserva_foco_das_abas(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertContains(response, f'href="{static("praticas/css/home.css")}"')
        self.assertContains(response, 'role="tablist"')
        self.assertContains(response, 'aria-selected="true"')
        self.assertContains(response, 'id="concepto-pane" role="tabpanel" aria-labelledby="concepto-tab" tabindex="-1"', html=False)
        self.assertContains(response, 'tab.addEventListener("shown.bs.tab", handleShown, { once: true });', count=1)
        self.assertContains(response, "bootstrap.Tab.getOrCreateInstance(tab).show();", count=1)
        self.assertContains(response, 'event.key === "Enter" || event.key === " "')

    def test_home_usa_estados_roxos_sem_foco_amarelo(self):
        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )

        self.assertRegex(
            css,
            r"\.home-foundation-tab\s*\{[^}]*background: var\(--lilac-pale\)",
        )
        self.assertRegex(
            css,
            r"\.home-foundation-tab\.active,[^{]+\{[^}]*background: var\(--purple\)",
        )
        self.assertRegex(
            css,
            r"\.home-map-country\.is-member\s*\{[^}]*fill: var\(--purple-soft\)",
        )
        self.assertRegex(
            css,
            r"\.home-map-country\.is-selected\s*\{[^}]*fill: var\(--purple\)",
        )
        self.assertIn(".home-map-country.is-coordinated", css)
        self.assertIn("outline: 3px solid var(--purple-mid);", css)
        self.assertNotIn("#f4b400", css.lower())
        self.assertNotIn("#ffd800", css.lower())
        self.assertNotIn("fill: #698D8B", css)

    def test_ctas_usam_position_paper_e_pagina_de_exemplos(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split(
            '<section class="home-foundations', 1
        )[1].split("</section>", 1)[0]
        position_paper = (
            "https://olacefs.com/giz/wp-content/uploads/sites/14/2025/11/"
            "Position_Paper_Miolo_ESP.pdf"
        )

        self.assertEqual(
            fundamentos.count(f'href="{position_paper}"'),
            1,
        )
        self.assertEqual(
            fundamentos.count('target="_blank" rel="noopener noreferrer"'),
            4,
        )
        self.assertEqual(
            fundamentos.count(
                f'href="{reverse("exemplos_injustica_climatica")}"'
            ),
            1,
        )
        self.assertNotIn(f'href="{reverse("sobre_plataforma")}"', fundamentos)
        self.assertNotIn("#ejemplosModal", fundamentos)

    def test_caixas_conceituais_aparecem_antes_dos_ctas_em_todas_as_abas(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        fundamentos = html.split(
            '<section class="home-foundations', 1
        )[1].split("</section>", 1)[0]

        conceito = fundamentos.split('id="concepto-pane"', 1)[1].split('id="controle-pane"', 1)[0]
        controle = fundamentos.split('id="controle-pane"', 1)[1].split('id="genero-pane"', 1)[0]
        genero = fundamentos.split('id="genero-pane"', 1)[1]
        self.assertLess(conceito.index('class="home-foundation-introduction"'), conceito.index('class="home-foundation-concept-layout"'))
        self.assertLess(conceito.index('class="home-foundation-concept-layout"'), conceito.index('class="home-foundation-actions"'))
        self.assertNotIn('class="home-foundation-actions"', controle)
        self.assertLess(genero.index('class="home-foundation-top"'), genero.index('class="home-foundation-actions"'))

    def test_primeira_aba_tem_layout_e_ordem_equivalentes_nos_tres_idiomas(self):
        casos = (
            (
                "/",
                "Equidade e Inclusão",
                "Responsabilidades comuns, porém diferenciadas",
                "Participação Social",
            ),
            (
                "/es/",
                "Equidad e Inclusión",
                "Responsabilidades comunes, pero diferenciadas",
                "Participación Social",
            ),
            (
                "/en/",
                "Equity and Inclusion",
                "Common but differentiated responsibilities",
                "Social Participation",
            ),
        )

        for caminho, primeiro, segundo, terceiro in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode("utf-8")
                painel = html.split('id="concepto-pane"', 1)[1].split(
                    'id="controle-pane"', 1
                )[0]

                self.assertEqual(
                    painel.count('class="home-foundation-strategy"'),
                    3,
                )
                self.assertIn('class="home-foundation-introduction"', painel)
                self.assertIn('class="home-foundation-concept-layout"', painel)
                self.assertEqual(
                    painel.count(static("praticas/img/fundamentos-justica-climatica.svg")),
                    1,
                )
                self.assertLess(painel.index(primeiro), painel.index(segundo))
                self.assertLess(painel.index(segundo), painel.index(terceiro))
                self.assertLess(
                    painel.index('class="home-foundation-strategies"'),
                    painel.index(
                        'class="home-foundation-photo home-foundation-concept-photo"'
                    ),
                )

        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            css,
            r"\.home-foundation-concept-layout\s*\{[^}]*"
            r"grid-template-columns:\s*minmax\(0, 1fr\)\s+minmax\(0, 1\.02fr\)",
        )
        responsivo = css.split("@media (max-width: 820px)", 1)[1]
        self.assertIn(".home-design .home-foundation-concept-layout,", responsivo)
        self.assertRegex(
            responsivo,
            r"\.home-foundation-concept-photo img\s*\{[^}]*height:\s*auto",
        )

    def test_texto_negocial_portugues_e_integralmente_renderizado(self):
        response = self.client.get(reverse("pagina_inicial"))

        trechos = (
            "Justiça climática é uma abordagem que integra os Direitos Humanos, "
            "a justiça social e a proteção ambiental",
            "Equidade e Inclusão",
            "Não se trata apenas de minimizar os impactos negativos das mudanças climáticas",
            "Participação Social",
            "Incorporar a consulta, envolvimento e participação efetiva",
            "Responsabilidades comuns, porém diferenciadas",
            "a responsabilidade pelo enfrentamento da mudança do clima é comum, "
            "porém diferenciada",
        )
        for trecho in trechos:
            with self.subTest(trecho=trecho):
                self.assertContains(response, trecho)

    def test_home_nao_renderiza_modal_legado_de_exemplos(self):
        response = self.client.get(reverse("pagina_inicial"))

        self.assertNotContains(response, 'id="ejemplosModal"')
        self.assertNotContains(response, 'data-bs-target="#ejemplosModal"')

    def test_fundamentos_preservam_conteudo_nos_tres_idiomas(self):
        casos = [
            ("/", "Fundamentos e estratégias", "Equidade e Inclusão", "Estratégia de gênero da OLACEFS"),
            ("/es/", "Fundamentos y estrategias", "Equidad e Inclusión", "Estrategia de género de la OLACEFS"),
            ("/en/", "Foundations and strategies", "Equity and Inclusion", "OLACEFS Gender Strategy"),
        ]

        for caminho, titulo, beneficio, genero in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo, html=False)
                self.assertContains(response, beneficio, html=False)
                self.assertContains(response, genero, html=False)

    def test_home_preserva_textos_institucionais_existentes_em_es_e_en(self):
        casos = (
            (
                "/es/",
                "La justicia climática es un enfoque que integra los Derechos "
                "Humanos, la justicia social y la protección ambiental",
            ),
            (
                "/en/",
                "Climate justice is an approach that integrates Human Rights, "
                "social justice and environmental protection",
            ),
        )

        for caminho, trecho in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, trecho)

    def test_controle_externo_tem_seis_caixas_fechadas_e_trilingues(self):
        casos = (
            (
                "/",
                (
                    "Incorporação da perspectiva de justiça climática nas auditorias",
                    "Institucionalização nas Entidades Fiscalizadoras",
                    "Planejamento e escopo das auditorias e avaliações",
                    "Avaliação de capacidades e recursos institucionais",
                    "Inclusão e participação cidadã",
                    "Acompanhamento e recomendações",
                ),
            ),
            (
                "/es/",
                (
                    "Incorporación de la perspectiva de justicia climática en auditorias",
                    "Institucionalización en de las Entidades Fiscalizadoras",
                    "Planificación y alcance de las auditorías y evaluaciones",
                    "Evaluación de capacidades y recursos institucionales",
                    "Inclusión y participación ciudadana",
                    "Seguimiento y recomendaciones",
                ),
            ),
            (
                "/en/",
                (
                    "Incorporating a climate justice perspective into audits",
                    "Institutionalization within Supreme Audit Institutions",
                    "Planning and scope of audits and evaluations",
                    "Assessment of institutional capacities and resources",
                    "Inclusion and citizen participation",
                    "Follow-up and recommendations",
                ),
            ),
        )

        for caminho, titulos_esperados in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                html = response.content.decode("utf-8")
                painel = html.split('id="controle-pane"', 1)[1].split(
                    'id="genero-pane"', 1
                )[0]
                caixas = re.findall(
                    r'<details class="home-foundation-audit-item"([^>]*)>(.*?)</details>',
                    painel,
                    flags=re.DOTALL,
                )
                titulos = []
                for atributos, caixa in caixas:
                    self.assertNotRegex(atributos, r"\bopen\b")
                    summary = re.search(r"<summary>(.*?)</summary>", caixa, re.DOTALL)
                    self.assertIsNotNone(summary)
                    titulo = re.sub(r"<[^>]+>", "", summary.group(1))
                    titulos.append(" ".join(titulo.split()))

                self.assertEqual(len(caixas), 6)
                self.assertEqual(tuple(titulos), titulos_esperados)
                self.assertEqual(
                    [caixa.count("<li>") for _, caixa in caixas],
                    [0, 5, 3, 2, 2, 2],
                )
                self.assertNotIn("home-foundation-audit-number", painel)
                self.assertIn("home-foundation-top", painel)
                self.assertEqual(
                    painel.count(static("praticas/img/fundamentos-controle-externo.svg")),
                    1,
                )

    def test_conteudo_negocial_portugues_das_seis_caixas_e_integral(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        painel = html.split('id="controle-pane"', 1)[1].split(
            'id="genero-pane"', 1
        )[0]
        caixas = re.findall(
            r'<details class="home-foundation-audit-item"[^>]*>(.*?)</details>',
            painel,
            flags=re.DOTALL,
        )
        paragrafos_primeira_caixa = [
            " ".join(re.sub(r"<[^>]+>", "", item).split())
            for item in re.findall(r"<p>(.*?)</p>", caixas[0], re.DOTALL)
        ]
        self.assertEqual(
            paragrafos_primeira_caixa,
            [
                "Não basta que existam normas que protejam as comunidades vulneráveis; é necessário verificar se essas normas são efetivamente aplicadas na prática. As perguntas de uma auditoria de conformidade buscam verificar a existência de diagnósticos diferenciados por gênero e etnia, mecanismos de consulta, medidas de proteção de direitos, espaços de participação e programas de compensação.",
                "O desempenho não é medido apenas em termos técnicos, mas também em termos de impacto equitativo: os resultados chegam a quem mais necessita deles? As perguntas orientadoras avaliam se essas medidas tiveram impacto real: se as lacunas de acesso foram reduzidas, se a participação foi genuína e se os mecanismos de reparação funcionaram.",
            ],
        )
        textos_esperados = (
            "Incorporar diretrizes de justiça climática em regulamentos, políticas internas e códigos de ética, garantindo coerência entre o discurso e a prática institucional.",
            "Promover a capacitação contínua das equipes em mudança climática, direitos humanos, equidade de gênero, raça e diversidade.",
            "Estabelecer metas e indicadores internos de sustentabilidade, equidade e inclusão, vinculados ao planejamento estratégico e ao acompanhamento institucional.",
            "Garantir a diversidade nas equipes de auditoria, valorizando a participação de mulheres, indígenas, afrodescendentes e outros grupos historicamente sub-representados.",
            "Fomentar o intercâmbio de experiências e boas práticas entre as EFS da região.",
            "Incluir nos planos anuais de auditoria programas e políticas públicas relacionados à justiça climática, avaliando governança, transparência, prestação de contas e participação cidadã.",
            "Identificar critérios de equidade e inclusão na fiscalização.",
            "Fiscalizar a integração da justiça climática no planejamento, na implementação, no acompanhamento e na avaliação das políticas de mitigação, adaptação e gestão ambiental, verificando a eficácia da execução, o cumprimento de metas e indicadores e a correta aplicação dos investimentos previstos.",
            "Garantir que os recursos financeiros, institucionais e humanos destinados às políticas climáticas e de infraestrutura sustentável sejam suficientes para cumprir os objetivos estabelecidos.",
            "Garantir que o Estado disponha de estruturas sólidas, com mecanismos de transparência, prestação de contas e participação social, para gerir as políticas públicas de maneira sustentável, inclusiva e equitativa.",
            "Avaliar como as políticas e os projetos afetam de maneira diferenciada as comunidades vulneráveis, prestando especial atenção à equidade intergeracional, gênero, raça, etnia, território e não discriminação.",
            "Verificar se as estruturas de governança estão alinhadas com os princípios de justiça climática e se existem mecanismos funcionais de participação significativa da cidadania, especialmente das comunidades mais afetadas ou em maior risco.",
            "Garantir que, durante todo o ciclo de políticas e projetos, os organismos auditados possam reformular estratégias e corrigir falhas para assegurar maior eficácia e alinhamento com os objetivos de justiça climática.",
            "Emitir relatórios e recomendações aos organismos auditados para promover uma gestão pública orientada à justiça climática, contribuindo para prevenir e reduzir riscos sociais e ambientais.",
        )
        textos_renderizados = []
        for caixa in caixas:
            for item in re.findall(r"<li>(.*?)</li>", caixa, re.DOTALL):
                textos_renderizados.append(" ".join(re.sub(r"<[^>]+>", "", item).split()))

        self.assertEqual(tuple(textos_renderizados), textos_esperados)

    def test_conteudo_espanhol_reproduz_integralmente_a_fonte_negocial(self):
        response = self.client.get("/es/")
        textos_aprovados = (
            "Las Entidades Fiscalizadoras EFS pueden actuar como garantes de que las políticas climáticas y las inversiones en infraestructura sean justas, transparentes y eficaces, convirtiendo la auditoría en una herramienta para proteger a las comunidades más vulnerables y promover la justicia climática.",
            "Una auditoría con perspectiva de justicia climática tiene por objetivo evaluar si las políticas climáticas llegaron a quienes más las necesitan, si respetaron los derechos de las comunidades afectadas y si generaron cambios reales en las condiciones de vida de las poblaciones más vulnerables.",
            "Estrategias clave para la promoción de la justicia climática por parte de las Entidades Fiscalizadoras",
            "No basta con que existan normas que protejan a las comunidades vulnerables; es necesario verificar que esas normas se aplican efectivamente en la práctica. Las preguntas de una auditoría de cumplimiento buscan verificar la existencia de diagnósticos diferenciados por género y etnia, mecanismos de consulta, medidas de protección de derechos, espacios de participación y programas de compensación.",
            "El desempeño no solo se mide en términos técnicos, sino en términos de impacto equitativo: ¿los resultados llegan a quienes más los necesitan? Las preguntas orientadoras evalúan si estas medidas tuvieron impacto real: si las brechas de acceso se redujeron, si la participación fue genuina y si los mecanismos de reparación funcionaron.",
            "Incorporar directrices de justicia climática en reglamentos, políticas internas y códigos de ética, garantizando coherencia entre el discurso y la práctica institucional.",
            "Promover la capacitación continua de los equipos en cambio climático, derechos humanos, equidad de género, raza y diversidad.",
            "Establecer metas e indicadores internos de sostenibilidad, equidad e inclusión, vinculados a la planificación estratégica y al seguimiento institucional.",
            "Garantizar la diversidad en los equipos de auditoría, valorando la participación de mujeres, indígenas, afrodescendientes y otros grupos históricamente subrepresentados.",
            "Fomentar el intercambio de experiencias y buenas prácticas entre las EFS de la región.",
            "Incluir en los planes anuales de auditoría programas y políticas públicas relacionadas con justicia climática, evaluando gobernanza, transparencia, rendición de cuentas y participación ciudadana.",
            "Identificar criterios de equidad e inclusión en la fiscalización.",
            "Fiscalizar la integración de la justicia climática en la planificación, implementación, seguimiento y evaluación de las políticas de mitigación, adaptación y gestión ambiental, verificando la eficacia de la ejecución, el cumplimiento de metas e indicadores y la correcta aplicación de las inversiones previstas.",
            "Garantizar que los recursos financieros, institucionales y humanos destinados a políticas climáticas y de infraestructura sostenible sean suficientes para cumplir con los objetivos establecidos.",
            "Garantizar que el Estado disponga de estructuras sólidas, con mecanismos de transparencia, rendición de cuentas y participación social, para gestionar las políticas públicas de manera sostenible, inclusiva y equitativa.",
            "Evaluar cómo las políticas y los proyectos afectan de manera diferenciada a las comunidades vulnerables, prestando especial atención a la equidad intergeneracional, género, raza, etnia, territorio y no discriminación.",
            "Verificar que las estructuras de gobernanza estén alineadas con los principios de justicia climática y que existan mecanismos funcionales de participación significativa de la ciudadanía, especialmente de las comunidades más afectadas o en mayor riesgo.",
            "Garantizar que, durante todo el ciclo de políticas y proyectos, los organismos auditados puedan reformular estrategias y corregir fallos para asegurar mayor eficacia y alineación con los objetivos de justicia climática.",
            "Emitir informes y recomendaciones a los organismos auditados para promover una gestión pública orientada a la justicia climática, contribuyendo a prevenir y reducir riesgos sociales y ambientales",
        )
        for texto in textos_aprovados:
            self.assertContains(response, texto)
        self.assertNotContains(response, "(6) Seguimiento y recomendaciones")

    def test_estrategia_genero_tem_conteudo_integral_trilingue_e_tres_links(self):
        casos = (
            (
                "/",
                "A mudança climática não é um problema que afeta todas as pessoas da mesma forma.",
                "Assim, esta plataforma se relaciona com a Estratégia de Gênero da OLACEFS: compartilha seu marco de direitos humanos, equidade e inclusão e busca traduzi-lo em critérios concretos e verificáveis para as auditorias com perspectiva de justiça climática.",
            ),
            (
                "/es/",
                "El cambio climático no es un problema que afecta a todas las personas por igual.",
                "Así, esta plataforma se relaciona con la Estrategia de Género de la OLACEFS: comparte su marco de derechos humanos, equidad e inclusión, y busca traducirlo en criterios concretos y verificables para las auditorías con perspectiva de justicia climática.",
            ),
            (
                "/en/",
                "Climate change is not a problem that affects everyone equally.",
                "Thus, this platform relates to the OLACEFS Gender Strategy: it shares its human rights, equity and inclusion framework and seeks to translate it into concrete and verifiable criteria for audits with a climate justice perspective.",
            ),
        )
        for caminho, primeiro_paragrafo, paragrafo_final in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                html = response.content.decode("utf-8")
                painel = html.split('id="genero-pane"', 1)[1].split("</section>", 1)[0]
                self.assertIn(primeiro_paragrafo, painel)
                self.assertIn(paragrafo_final, painel)
                self.assertEqual(painel.count("<li>"), 6)
                self.assertIn(static("praticas/img/fundamentos-estrategia-genero.svg"), painel)
                self.assertIn("https://olacefs.com/cgid", painel)
                self.assertIn("https://olacefs.com/cgid/politica-de-genero/", painel)
                self.assertIn("https://olacefs.com/ogid/", painel)

    def test_grade_das_nove_caixas_e_responsiva(self):
        css = Path(finders.find("praticas/css/home.css")).read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            css,
            r"\.home-foundation-audit-grid\s*\{[^}]*"
            r"grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)",
        )
        tablet = css.split("@media (max-width: 820px)", 1)[1].split(
            "@media (max-width: 480px)", 1
        )[0]
        self.assertRegex(
            tablet,
            r"\.home-foundation-audit-grid\s*\{[^}]*"
            r"grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        )
        mobile = css.split("@media (max-width: 480px)", 1)[1].split(
            "@media (prefers-reduced-motion", 1
        )[0]
        self.assertRegex(
            mobile,
            r"\.home-foundation-audit-grid\s*\{[^}]*"
            r"grid-template-columns:\s*1fr",
        )

    def test_pagina_de_exemplos_e_publica_trilingue_e_usa_acervo_oficial(self):
        casos = (
            ("/exemplos-injustica-climatica/", "Exemplos de injustiça climática"),
            ("/es/exemplos-injustica-climatica/", "Ejemplos de injusticia climática"),
            ("/en/exemplos-injustica-climatica/", "Examples of climate injustice"),
        )

        for caminho, titulo in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, titulo)
                self.assertContains(response, "OLACEFS + GIZ")
                self.assertContains(response, "Gustavo Mansur / Agência Senado")
                self.assertContains(response, "FAO (2019)")
                self.assertContains(response, "Denisa Starbova")
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-rs2024.jpg"',
                )
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-corredor-seco.jpg"',
                )
                self.assertContains(
                    response,
                    'src="/static/praticas/img/ejemplo-huni-kui.jpg"',
                )

    def test_pagina_de_exemplos_tem_breadcrumb_e_hierarquia_semantica(self):
        response = self.client.get(reverse("exemplos_injustica_climatica"))
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Navegação estrutural"')
        self.assertContains(response, f'href="{reverse("pagina_inicial")}"')
        self.assertContains(
            response,
            f'href="{reverse("pagina_inicial")}#pillarsSection"',
        )
        self.assertEqual(len(re.findall(r"<h1\b", html)), 1)
        self.assertGreaterEqual(len(re.findall(r"<h2\b", html)), 4)

    def test_mapa_funcional_e_video_oficial_trilingue(self):
        casos = [
            ("/", "EFS da Am&eacute;rica Latina e Caribe", "Mapa interativo", "Teaser da Plataforma de Justi&ccedil;a Clim&aacute;tica"),
            ("/es/", "EFS de Am&eacute;rica Latina y el Caribe", "Mapa interactivo", "Teaser de la Plataforma de Justicia Clim&aacute;tica"),
            ("/en/", "SAIs of Latin America and the Caribbean", "Interactive map", "Climate Justice Platform Teaser"),
        ]

        for caminho, mapa, estado_funcional, video in casos:
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, mapa, html=False)
                self.assertContains(response, estado_funcional)
                self.assertContains(response, video, html=False)
                self.assertNotContains(response, "Etapa futura")
                self.assertNotContains(response, "Future stage")
                self.assertContains(response, f'formaction="{reverse("catalogo_experiencias")}"')
                self.assertContains(response, f'formaction="{reverse("normas_internacionais")}"')

    def test_video_home_usa_player_html5_via_media_sem_autoplay(self):
        response = self.client.get(reverse("pagina_inicial"))
        html = response.content.decode("utf-8")
        bloco = html.split('<section class="home-video', 1)[1].split(
            "</section>", 1
        )[0]

        self.assertIn("<video", bloco)
        self.assertIn("controls", bloco)
        self.assertIn('preload="metadata"', bloco)
        self.assertIn("playsinline", bloco)
        self.assertIn(
            '<source src="/media/videos/teaser-plataforma-jc.mp4" type="video/mp4">',
            bloco,
        )
        self.assertNotIn("autoplay", bloco)
        self.assertNotIn("Conte&uacute;do audiovisual em prepara&ccedil;&atilde;o", bloco)
        self.assertNotIn("static/praticas", bloco)
        self.assertIn(
            'class="home-video-fallback" id="home-video-error" role="status" hidden',
            bloco,
        )

        pagina = response.content.decode("utf-8")
        self.assertIn('player.addEventListener("error"', pagina)
        self.assertIn("errorMessage.hidden = false;", pagina)
