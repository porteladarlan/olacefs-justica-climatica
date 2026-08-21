import importlib
from pathlib import Path

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import translation

from .forms import ExperienciaAdminForm, ExperienciaSubmissaoForm
from .models import (
    EFS,
    BancoTecnico,
    Experiencia,
    Ferramenta,
    NormaInternacional,
    Pais,
    PerguntaAuditoria,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)
from .views import _payload_mapa_regional


class PacoteDesignNegocialTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="autora-pacote",
            email="autora@example.org",
            password="SenhaForte123!",
        )
        cls.outro_usuario = get_user_model().objects.create_user(
            username="outra-autora",
            email="outra@example.org",
            password="SenhaForte123!",
        )
        cls.brasil = Pais.objects.create(nome="Brasil", sigla="BRA")
        cls.chile = Pais.objects.create(nome="Chile", sigla="CHL")
        cls.peru = Pais.objects.create(nome="Peru", sigla="PER")
        cls.efs_brasil = EFS.objects.create(
            nome="Tribunal de Contas do Brasil",
            sigla="TCB",
            pais=cls.brasil,
        )
        cls.efs_chile = EFS.objects.create(
            nome="Controladoria do Chile",
            sigla="CCH",
            pais=cls.chile,
        )
        cls.auditoria = TipoExperiencia.objects.create(
            codigo="auditoria",
            nome="Auditoria",
            nome_es="Auditoría",
            nome_en="Audit",
        )
        cls.coordenada = TipoExperiencia.objects.create(
            codigo="auditoria_coordenada",
            nome="Auditoria coordenada",
            nome_es="Auditoría coordinada",
            nome_en="Coordinated audit",
        )
        cls.avaliacao = TipoExperiencia.objects.create(
            codigo="avaliacao_politica_publica",
            nome="Avaliação de política pública",
            nome_es="Evaluación de política pública",
            nome_en="Public policy evaluation",
        )
        cls.setor = Setor.objects.create(
            codigo="infraestrutura",
            nome="Infraestrutura",
            nome_es="Infraestructura",
            nome_en="Infrastructure",
        )
        cls.setor_historico = Setor.objects.create(nome="Taxonomia histórica")
        cls.tema = TemaTransversal.objects.create(nome="Direitos humanos")
        cls.norma = NormaInternacional.objects.create(nome="Acordo de Paris")

    def setUp(self):
        translation.activate("pt-br")
        self.client.force_login(self.usuario)

    def tearDown(self):
        translation.deactivate_all()

    def dados_pratica(self, **alteracoes):
        dados = {
            "tipo_compartilhamento": "boa_pratica",
            "acao_envio": "enviar",
            "efs": str(self.efs_brasil.pk),
            "pais": str(self.brasil.pk),
            "titulo": "Auditoria climática regional",
            "tipo_experiencia": str(self.auditoria.pk),
            "tipo_auditoria": Experiencia.TipoAuditoria.DESEMPENHO,
            "setor": str(self.setor.pk),
            "temas_transversais": [str(self.tema.pk)],
            "normas_internacionais": [str(self.norma.pk)],
            "email_contato": "autora@example.org",
            "pessoa_responsavel": "Autora",
            "descricao": "Descrição suficiente para revisão.",
            "enfoque_justica_climatica": "Equidade e direitos humanos.",
            "objetivo": "Avaliar a política.",
            "criterios_utilizados": "Critérios técnicos.",
            "metodologia": "Análise documental.",
            "ferramentas_utilizadas": "Base documental preservada.",
            "resultados": "Resultados.",
            "recomendacoes": "Recomendações.",
            "replicabilidade": "Replicável.",
            "informacoes_adicionais": "Informação adicional.",
            "ano_execucao": "2026",
            "perguntas_auditoria": ["Pergunta um?", "Pergunta dois?"],
        }
        dados.update(alteracoes)
        return dados

    def test_primeira_decisao_e_tooltip_sao_trilingues_e_acessiveis(self):
        casos = (
            ("/adicionar-boa-pratica/", "Você deseja compartilhar:", "Uma boa prática é"),
            ("/es/adicionar-boa-pratica/", "¿Qué desea compartir?", "Una buena práctica es"),
            ("/en/adicionar-boa-pratica/", "What would you like to share?", "A good practice is"),
        )
        for caminho, pergunta, explicacao in casos:
            with self.subTest(caminho=caminho):
                resposta = self.client.get(caminho)
                self.assertContains(resposta, pergunta)
                self.assertContains(resposta, explicacao)
                self.assertContains(resposta, '<details class="accessible-info">', html=False)
                self.assertContains(resposta, "Boa prática" if caminho.startswith("/adicionar") else ("Buena práctica" if "/es/" in caminho else "Good practice"))

    def test_escolha_determina_formulario_e_tipo_explicito_invalido_e_rejeitado(self):
        boa_pratica = self.client.get(f"{reverse('adicionar_boa_pratica')}?tipo=boa_pratica")
        ferramenta = self.client.get(f"{reverse('adicionar_boa_pratica')}?tipo=ferramenta")
        invalido = self.client.post(
            reverse("adicionar_boa_pratica"),
            {"tipo_compartilhamento": "forjado"},
        )
        self.assertContains(boa_pratica, 'value="boa_pratica"')
        self.assertContains(boa_pratica, "Tipo de boa prática")
        self.assertContains(ferramenta, 'value="ferramenta"')
        self.assertContains(ferramenta, "País ou Instância")
        self.assertNotContains(ferramenta, "Tipo de ferramenta")
        self.assertEqual(invalido.status_code, 400)

    def test_ferramenta_e_criada_no_modelo_correto_e_nao_publicada(self):
        resposta = self.client.post(
            reverse("adicionar_boa_pratica"),
            {
                "tipo_compartilhamento": "ferramenta",
                "acao_envio": "enviar",
                "nome": "Matriz de auditoria",
                "ano": "2026",
                "descricao": "Instrumento de apoio às EFS.",
                "setor": str(self.setor.pk),
                "link_acesso": "https://example.org/matriz",
                "pais_ou_instancia": "Comissão da OLACEFS",
            },
        )
        self.assertRedirects(
            resposta,
            f"{reverse('confirmacao_envio')}?tipo=ferramenta",
            fetch_redirect_response=False,
        )
        self.assertEqual(Experiencia.objects.count(), 0)
        ferramenta = Ferramenta.objects.get()
        self.assertEqual(ferramenta.autor, self.usuario)
        self.assertEqual(ferramenta.situacao, Ferramenta.Situacao.ENVIADA)
        self.assertEqual(ferramenta.idioma_submissao, Ferramenta.IdiomaSubmissao.PORTUGUES)
        self.assertEqual(ferramenta.titulo, "Matriz de auditoria")
        self.assertEqual(ferramenta.titulo_es, "")
        self.assertEqual(ferramenta.pais_ou_instancia, "Comissão da OLACEFS")
        self.assertNotEqual(ferramenta.situacao, Ferramenta.Situacao.PUBLICADA)

        rascunho_parcial = self.client.post(
            reverse("adicionar_boa_pratica"),
            {
                "tipo_compartilhamento": "ferramenta",
                "acao_envio": "rascunho",
                "nome": "Rascunho parcial",
            },
        )
        self.assertRedirects(
            rascunho_parcial,
            reverse("meus_envios"),
            fetch_redirect_response=False,
        )
        rascunho = Ferramenta.objects.get(titulo="Rascunho parcial")
        self.assertEqual(rascunho.situacao, Ferramenta.Situacao.RASCUNHO)
        self.assertIsNone(rascunho.setor)
        self.assertEqual(rascunho.url, "")
        meus_envios = self.client.get(reverse("meus_envios"))
        self.assertContains(meus_envios, reverse("editar_ferramenta", args=[rascunho.pk]))

        retomada = self.client.post(
            reverse("editar_ferramenta", args=[rascunho.pk]),
            {
                "acao_envio": "enviar",
                "nome": "Rascunho concluído",
                "ano": "2026",
                "descricao": "Descrição completa.",
                "setor": str(self.setor.pk),
                "link_acesso": "https://example.org/rascunho",
                "pais_ou_instancia": "CGID",
            },
        )
        self.assertRedirects(retomada, reverse("meus_envios"), fetch_redirect_response=False)
        rascunho.refresh_from_db()
        self.assertEqual(rascunho.situacao, Ferramenta.Situacao.ENVIADA)
        self.assertEqual(rascunho.titulo, "Rascunho concluído")

    def test_ferramenta_preserva_idioma_real_sem_falsas_traducoes(self):
        casos = (
            ("/adicionar-boa-pratica/", "PT", "pt", "titulo"),
            ("/es/adicionar-boa-pratica/", "ES", "es", "titulo_es"),
            ("/en/adicionar-boa-pratica/", "EN", "en", "titulo_en"),
        )
        for caminho, sufixo, idioma, campo_titulo in casos:
            with self.subTest(idioma=idioma):
                resposta = self.client.post(
                    caminho,
                    {
                        "tipo_compartilhamento": "ferramenta",
                        "acao_envio": "enviar",
                        "nome": f"Ferramenta {sufixo}",
                        "ano": "2026",
                        "descricao": f"Descrição {sufixo}",
                        "setor": str(self.setor.pk),
                        "link_acesso": f"https://example.org/{idioma}",
                        "pais_ou_instancia": "OLACEFS",
                    },
                )
                self.assertEqual(resposta.status_code, 302)
                ferramenta = Ferramenta.objects.get(url=f"https://example.org/{idioma}")
                self.assertEqual(ferramenta.idioma_submissao, idioma)
                for campo in ("titulo", "titulo_es", "titulo_en"):
                    esperado = f"Ferramenta {sufixo}" if campo == campo_titulo else ""
                    self.assertEqual(getattr(ferramenta, campo), esperado)

    def test_migration_remove_copia_falsa_sem_alterar_conteudo_importado(self):
        enviada = Ferramenta.objects.create(
            autor=self.usuario,
            codigo="ferramenta-pt-duplicada",
            titulo="Título em português",
            titulo_es="Título em português",
            descricao="Descrição em português",
            descricao_es="Descrição em português",
            ordem=1,
        )
        importada = Ferramenta.objects.create(
            codigo="ferramenta-importada",
            titulo="Conteúdo histórico",
            titulo_es="Conteúdo histórico",
            descricao="Descrição histórica",
            descricao_es="Descrição histórica",
            ordem=2,
        )
        migration = importlib.import_module(
            "praticas.migrations.0018_corrigir_rascunho_ferramenta"
        )
        migration.corrigir_idioma_ferramentas(apps, None)
        enviada.refresh_from_db()
        importada.refresh_from_db()
        self.assertEqual(enviada.idioma_submissao, Ferramenta.IdiomaSubmissao.PORTUGUES)
        self.assertEqual(enviada.titulo_es, "")
        self.assertEqual(enviada.descricao_es, "")
        self.assertEqual(importada.titulo_es, "Conteúdo histórico")
        self.assertEqual(importada.descricao_es, "Descrição histórica")

    def test_auditoria_coordenada_preserva_lideres_paises_e_efs_abertas(self):
        dados = self.dados_pratica(
            tipo_experiencia=str(self.coordenada.pk),
            paises_participantes=[str(self.chile.pk), str(self.peru.pk)],
            outras_efs_envolvidas="EFS do Chile; EFS do Peru",
            perguntas_auditoria=[f"Pergunta {indice}?" for indice in range(1, 31)],
        )
        resposta = self.client.post(reverse("adicionar_boa_pratica"), dados)
        self.assertRedirects(resposta, reverse("confirmacao_envio"), fetch_redirect_response=False)
        experiencia = Experiencia.objects.get()
        self.assertEqual(experiencia.pais, self.brasil)
        self.assertEqual(experiencia.efs, self.efs_brasil)
        self.assertQuerySetEqual(
            experiencia.paises_participantes.order_by("pk"),
            [self.chile, self.peru],
        )
        self.assertEqual(experiencia.outras_efs_envolvidas, "EFS do Chile; EFS do Peru")
        self.assertEqual(experiencia.perguntas_auditoria.count(), 30)
        self.assertEqual(
            list(experiencia.perguntas_auditoria.values_list("ordem", flat=True)),
            list(range(1, 31)),
        )

    def test_pais_lider_duplicado_e_campos_condicionais_adulterados_sao_rejeitados(self):
        duplicado = self.dados_pratica(
            tipo_experiencia=str(self.coordenada.pk),
            paises_participantes=[str(self.brasil.pk)],
        )
        resposta = self.client.post(reverse("adicionar_boa_pratica"), duplicado)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "O país líder não pode ser repetido")

        adulterado = self.dados_pratica(
            tipo_experiencia=str(self.avaliacao.pk),
            tipo_auditoria=Experiencia.TipoAuditoria.FINANCEIRA,
            outras_efs_envolvidas="Campo escondido adulterado",
            perguntas_auditoria=["Pergunta adulterada"],
        )
        resposta = self.client.post(reverse("adicionar_boa_pratica"), adulterado)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "não se aplica a esta categoria")
        self.assertContains(resposta, "Perguntas de auditoria só podem ser informadas")
        self.assertEqual(Experiencia.objects.count(), 0)

    def test_efs_lider_de_outro_pais_e_valor_de_auditoria_invalido_falham(self):
        efs_errada = self.dados_pratica(efs=str(self.efs_chile.pk))
        resposta = self.client.post(reverse("adicionar_boa_pratica"), efs_errada)
        self.assertContains(resposta, "A EFS líder deve pertencer ao país líder")

        tipo_invalido = self.dados_pratica(tipo_auditoria="inventado")
        resposta = self.client.post(reverse("adicionar_boa_pratica"), tipo_invalido)
        self.assertContains(resposta, "Faça uma escolha válida")
        self.assertEqual(Experiencia.objects.count(), 0)

    def test_perguntas_sobrevivem_a_erro_draft_edicao_e_legado(self):
        com_erro = self.dados_pratica(email_contato="inválido")
        resposta = self.client.post(reverse("adicionar_boa_pratica"), com_erro)
        self.assertContains(resposta, "Pergunta um?")
        self.assertContains(resposta, "Pergunta dois?")

        rascunho = self.dados_pratica(
            acao_envio="rascunho",
            perguntas_auditoria=["Primeira", "Segunda", "Terceira"],
        )
        self.client.post(reverse("adicionar_boa_pratica"), rascunho)
        experiencia = Experiencia.objects.get()
        experiencia.perguntas_chave = "Texto legado indivisível. Não migrar por heurística."
        experiencia.save(update_fields=["perguntas_chave"])
        editados = self.dados_pratica(
            titulo=experiencia.titulo,
            perguntas_auditoria=["Terceira revisada", "Primeira revisada"],
            perguntas_chave="Tentativa de sobrescrever o legado.",
        )
        resposta = self.client.post(
            reverse("editar_boa_pratica", args=[experiencia.pk]), editados
        )
        self.assertEqual(resposta.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.ENVIADO)
        self.assertEqual(
            list(experiencia.perguntas_auditoria.values_list("texto", flat=True)),
            ["Terceira revisada", "Primeira revisada"],
        )
        self.assertEqual(
            experiencia.perguntas_chave,
            "Texto legado indivisível. Não migrar por heurística.",
        )

    def test_taxonomia_nova_na_interface_preserva_setor_historico(self):
        formulario = ExperienciaSubmissaoForm()
        self.assertIn(self.setor, formulario.fields["setor"].queryset)
        self.assertNotIn(self.setor_historico, formulario.fields["setor"].queryset)
        self.assertTrue(Setor.objects.filter(pk=self.setor_historico.pk).exists())

    def test_filtros_publicos_mantem_quatro_campos_e_encontram_pais_participante(self):
        experiencia = Experiencia.objects.create(
            autor=self.usuario,
            titulo="Coordenada localizável pelo Chile",
            efs=self.efs_brasil,
            pais=self.brasil,
            tipo_experiencia=self.coordenada,
            tipo_auditoria=Experiencia.TipoAuditoria.CUMPRIMENTO,
            ano_execucao=2026,
            setor=self.setor,
            descricao="Descrição",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        experiencia.paises_participantes.add(self.chile)
        resposta = self.client.get(
            reverse("catalogo_experiencias"), {"pais": self.chile.pk}
        )
        self.assertContains(resposta, experiencia.titulo)
        for identificador in (
            'for="filter-efs-search"',
            'for="filter-country-search"',
            'for="filter-type-search"',
            'for="filter-sector-search"',
        ):
            self.assertContains(resposta, identificador)
        self.assertContains(resposta, 'class="catalog-filter-group"', count=4)
        html = resposta.content.decode("utf-8")
        self.assertLess(html.index("filter-efs-search"), html.index("filter-country-search"))
        self.assertLess(html.index("filter-country-search"), html.index("filter-type-search"))
        self.assertLess(html.index("filter-type-search"), html.index("filter-sector-search"))
        self.assertNotContains(resposta, "FONTES DE INFORMAÇÃO OU EVIDÊNCIAS")
        experiencia.fontes_informacao = "Evidência histórica preservada"
        experiencia.save(update_fields=["fontes_informacao"])
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.fontes_informacao, "Evidência histórica preservada")

    def test_design_home_mapa_guia_rodape_e_links_institucionais(self):
        resposta = self.client.get(reverse("pagina_inicial"))
        html = resposta.content.decode("utf-8")
        conceito = html.split('id="concepto-pane"', 1)[1].split('id="controle-pane"', 1)[0]
        controle = html.split('id="controle-pane"', 1)[1].split('id="genero-pane"', 1)[0]
        genero = html.split('id="genero-pane"', 1)[1].split('</section>', 1)[0]
        self.assertIn("Enviar boa pr&aacute;tica", html)
        self.assertLess(html.index("Explorar marcos normativos"), html.index("Ver mapa da regi&atilde;o"))
        self.assertLess(html.index("Ver mapa da regi&atilde;o"), html.index("Enviar boa pr&aacute;tica"))
        self.assertIn("Palavras das Presid&ecirc;ncias da CGID e da COMTEMA", html)
        self.assertIn("Equidade e Inclusão", conceito)
        self.assertIn("Saiba mais", conceito)
        self.assertNotIn("Saiba mais", controle)
        self.assertNotIn("Ver exemplos", controle)
        self.assertIn("https://olacefs.com/cgid", genero)
        self.assertIn("https://olacefs.com/ogid/", genero)
        self.assertNotIn("Guia Viva", html)
        self.assertNotIn("Cooperação Alemã (GIZ) · BMZ", html)
        self.assertIn('id="regionalMap"', html)

        mapa_js = Path(finders.find("praticas/js/mapa-regional.js")).read_text(
            encoding="utf-8"
        )
        self.assertIn("tooltip.textContent = country.nome;", mapa_js)
        self.assertNotIn("EFS de América Latina", mapa_js)
        self.assertIn('"ABW": "533"', Path("praticas/views.py").read_text(encoding="utf-8"))
        self.assertIn('"CUW": "531"', Path("praticas/views.py").read_text(encoding="utf-8"))

    def test_ferramentas_e_boas_praticas_respeitam_ownership_no_meu_espaco(self):
        Ferramenta.objects.create(
            autor=self.outro_usuario,
            codigo="privada-outra",
            titulo_es="Ferramenta de outra autora",
            descricao_es="Privada",
            setor=self.setor,
            url="https://example.org/outra",
            ordem=1,
        )
        Ferramenta.objects.create(
            autor=self.usuario,
            codigo="privada-propria",
            titulo_es="Minha ferramenta",
            descricao_es="Própria",
            setor=self.setor,
            url="https://example.org/propria",
            ordem=2,
        )
        resposta = self.client.get(reverse("meus_envios"))
        self.assertContains(resposta, "Minha ferramenta")
        self.assertNotContains(resposta, "Ferramenta de outra autora")

        outra = Ferramenta.objects.get(codigo="privada-outra")
        bloqueada = self.client.get(reverse("editar_ferramenta", args=[outra.pk]))
        self.assertRedirects(bloqueada, reverse("meus_envios"), fetch_redirect_response=False)

        staff = get_user_model().objects.create_user(
            username="staff-ferramentas",
            password="SenhaForte123!",
            is_staff=True,
        )
        self.client.force_login(staff)
        self.assertEqual(
            self.client.get(reverse("editar_ferramenta", args=[outra.pk])).status_code,
            200,
        )
        outra.situacao = Ferramenta.Situacao.PUBLICADA
        outra.save(update_fields=["situacao"])
        publicada = self.client.get(reverse("editar_ferramenta", args=[outra.pk]))
        self.assertRedirects(publicada, reverse("meus_envios"), fetch_redirect_response=False)

    def test_aliases_inequivocos_de_setor_migram_relacoes_sem_apagar_ambiguos(self):
        alias = Setor.objects.create(
            nome="Alimentación y agricultura",
            nome_es="Alimentación y agricultura",
        )
        ambiguo = Setor.objects.create(nome="Tecnologia", nome_es="Tecnología")
        recurso = BancoTecnico.objects.create(
            titulo="Recurso histórico",
            tipo_recurso="Guia",
            setor=alias,
        )
        migration = importlib.import_module(
            "praticas.migrations.0018_corrigir_rascunho_ferramenta"
        )
        migration.normalizar_setores(apps, None)
        recurso.refresh_from_db()
        self.assertEqual(recurso.setor.codigo, "alimentacao_agricultura")
        self.assertTrue(Setor.objects.filter(pk=alias.pk).exists())
        ambiguo.refresh_from_db()
        self.assertIsNone(ambiguo.codigo)

    def test_condicionais_usam_codigo_estavel_nos_tres_idiomas(self):
        for caminho in (
            "/adicionar-boa-pratica/?tipo=boa_pratica",
            "/es/adicionar-boa-pratica/?tipo=boa_pratica",
            "/en/adicionar-boa-pratica/?tipo=boa_pratica",
        ):
            with self.subTest(caminho=caminho):
                resposta = self.client.get(caminho)
                self.assertContains(resposta, 'data-tipo-codigo="auditoria"')
                self.assertContains(resposta, 'data-tipo-codigo="auditoria_coordenada"')
                self.assertContains(resposta, "data-audit-only")
                self.assertContains(resposta, "data-evaluation-only")
        javascript = Path(
            finders.find("praticas/js/submissao-conteudo.js")
        ).read_text(encoding="utf-8")
        self.assertIn("dataset.tipoCodigo", javascript)
        self.assertIn('typeCode === "avaliacao_politica_publica"', javascript)
        self.assertNotIn('label.includes("audit")', javascript)

    def test_avaliacao_edita_legado_sem_criar_perguntas_estruturadas(self):
        dados = self.dados_pratica(
            tipo_experiencia=str(self.avaliacao.pk),
            tipo_auditoria="",
            perguntas_auditoria=[],
            perguntas_chave="Como a política pública foi avaliada?",
        )
        resposta = self.client.post(reverse("adicionar_boa_pratica"), dados)
        self.assertRedirects(
            resposta,
            reverse("confirmacao_envio"),
            fetch_redirect_response=False,
        )
        experiencia = Experiencia.objects.get()
        self.assertEqual(
            experiencia.perguntas_chave,
            "Como a política pública foi avaliada?",
        )
        self.assertFalse(experiencia.perguntas_auditoria.exists())

    def test_ferramenta_de_usuario_incompleta_nao_pode_ser_publicada_no_admin(self):
        ferramenta_admin = admin.site._registry[Ferramenta]
        request = RequestFactory().get("/admin/praticas/ferramenta/add/")
        request.user = self.usuario
        formulario = ferramenta_admin.get_form(request)(
            data={
                "autor": str(self.usuario.pk),
                "codigo": "ferramenta-incompleta-admin",
                "idioma_submissao": Ferramenta.IdiomaSubmissao.PORTUGUES,
                "situacao": Ferramenta.Situacao.PUBLICADA,
                "ordem": "99",
            }
        )
        self.assertFalse(formulario.is_valid())
        for campo in ("titulo", "ano", "descricao", "setor", "url", "pais_ou_instancia"):
            self.assertIn(campo, formulario.errors)

        historica = Ferramenta(
            codigo="ferramenta-historica-incompleta",
            idioma_submissao=Ferramenta.IdiomaSubmissao.PORTUGUES,
            situacao=Ferramenta.Situacao.PUBLICADA,
            ordem=100,
        )
        historica.full_clean()

    def test_admin_protege_paises_da_auditoria_coordenada(self):
        base = {
            "titulo": "Experiência administrada",
            "efs": str(self.efs_brasil.pk),
            "pais": str(self.brasil.pk),
            "ano_execucao": "2026",
            "status_iniciativa": Experiencia.StatusIniciativa.CONCLUIDA,
            "setor": str(self.setor.pk),
            "descricao": "Descrição",
            "status_publicacao": Experiencia.StatusPublicacao.PUBLICADO,
        }
        fora_da_coordenada = ExperienciaAdminForm(
            data={
                **base,
                "tipo_experiencia": str(self.avaliacao.pk),
                "paises_participantes": [str(self.chile.pk)],
            }
        )
        self.assertFalse(fora_da_coordenada.is_valid())
        self.assertIn("paises_participantes", fora_da_coordenada.errors)

        lider_repetido = ExperienciaAdminForm(
            data={
                **base,
                "tipo_experiencia": str(self.coordenada.pk),
                "tipo_auditoria": Experiencia.TipoAuditoria.DESEMPENHO,
                "paises_participantes": [str(self.brasil.pk)],
            }
        )
        self.assertFalse(lider_repetido.is_valid())
        self.assertIn("paises_participantes", lider_repetido.errors)

    def test_mapa_separa_novo_m2m_sem_regredir_efs_legadas(self):
        avaliacao_adulterada = Experiencia.objects.create(
            titulo="Avaliação adulterada",
            efs=self.efs_brasil,
            pais=self.brasil,
            tipo_experiencia=self.avaliacao,
            ano_execucao=2026,
            setor=self.setor,
            descricao="Descrição",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        avaliacao_adulterada.paises_participantes.add(self.chile)

        coordenada = Experiencia.objects.create(
            titulo="Coordenada válida",
            efs=self.efs_brasil,
            pais=self.brasil,
            tipo_experiencia=self.coordenada,
            tipo_auditoria=Experiencia.TipoAuditoria.DESEMPENHO,
            ano_execucao=2026,
            setor=self.setor,
            descricao="Descrição",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        coordenada.paises_participantes.add(self.chile)

        auditoria_legada = Experiencia.objects.create(
            titulo="Auditoria legada",
            efs=self.efs_brasil,
            pais=self.brasil,
            tipo_experiencia=self.auditoria,
            tipo_auditoria=Experiencia.TipoAuditoria.CUMPRIMENTO,
            ano_execucao=2026,
            setor=self.setor,
            descricao="Descrição",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        auditoria_legada.efs_participantes.add(self.efs_chile)

        ids = {
            item["id"] for item in _payload_mapa_regional()["auditorias_coordenadas"]
        }
        self.assertNotIn(avaliacao_adulterada.pk, ids)
        self.assertIn(coordenada.pk, ids)
        self.assertIn(auditoria_legada.pk, ids)

    def test_home_tem_dois_ctas_aprovados_sem_bloco_editorial_inventado(self):
        home = self.client.get(reverse("pagina_inicial"))
        html = home.content.decode("utf-8")
        hero = html.split('<section class="jc-hero home-block"', 1)[1].split(
            "</section>", 1
        )[0]
        self.assertIn("CGID + COMTEMA", html)
        self.assertNotIn("Plataforma Regional &middot; CGID + COMTEMA", html)
        self.assertIn('class="btn btn-success jc-hero-submit"', hero)
        self.assertNotIn("home-submit-cta", html)
        self.assertNotIn("Compartilhe conhecimento regional", html)

        catalogo = self.client.get(reverse("catalogo_experiencias"))
        self.assertContains(catalogo, 'class="catalog-submit"', html=False)
        self.assertContains(catalogo, "Enviar boa pr&aacute;tica", html=False)

    def test_modelo_de_pergunta_exige_ordem_positiva_e_unica(self):
        experiencia = Experiencia.objects.create(
            titulo="Base",
            efs=self.efs_brasil,
            pais=self.brasil,
            tipo_experiencia=self.avaliacao,
            ano_execucao=2026,
            setor=self.setor,
            descricao="Descrição",
        )
        pergunta = PerguntaAuditoria(experiencia=experiencia, texto="Pergunta", ordem=0)
        with self.assertRaises(Exception):
            pergunta.full_clean()
