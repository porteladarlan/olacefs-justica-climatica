from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    Anexo,
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class RotasPublicasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autor_pendente = get_user_model().objects.create_user(
            username="autor_pendente",
            email="autor@example.org",
            password="teste123",
        )
        pais = Pais.objects.create(
            nome="Brasil",
            nome_es="Brasil",
            nome_en="Brazil",
            sigla="BRA",
        )
        efs = EFS.objects.create(
            nome="Tribunal de Contas da Uniao",
            nome_es="Tribunal de Cuentas de la Union",
            nome_en="Federal Court of Accounts",
            sigla="TCU",
            pais=pais,
        )
        tipo = TipoExperiencia.objects.create(
            nome="Auditoria",
            nome_es="Auditoria",
            nome_en="Audit",
        )
        setor = Setor.objects.create(
            nome="Agua",
            nome_es="Agua",
            nome_en="Water",
        )
        tema = TemaTransversal.objects.create(
            nome="Direitos humanos",
            nome_es="Derechos humanos",
            nome_en="Human rights",
        )
        norma = NormaInternacional.objects.create(
            nome="Acordo de Paris",
            nome_es="Acuerdo de Paris",
            nome_en="Paris Agreement",
        )
        dimensao = DimensaoJusticaClimatica.objects.create(
            nome="Distributiva",
            nome_es="Distributiva",
            nome_en="Distributive",
        )
        grupo = GrupoVulneravel.objects.create(
            nome="Populacao rural",
            nome_es="Poblacion rural",
            nome_en="Rural population",
        )

        experiencia = Experiencia.objects.create(
            titulo="Avaliacao da equidade no acesso a agua",
            titulo_es="Evaluacion de la equidad en el acceso al agua",
            titulo_en="Assessment of equity in access to water",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2025,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            contato_referencia="Contato TCU",
            email_contato="contato@example.org",
            descricao="Experiencia de demonstracao sobre agua e justica climatica.",
            descricao_es="Experiencia de demostracion sobre agua y justicia climatica.",
            descricao_en="Demonstration experience on water and climate justice.",
            enfoque_justica_climatica="Direitos humanos e equidade.",
            enfoque_justica_climatica_es="Derechos humanos y equidad.",
            enfoque_justica_climatica_en="Human rights and equity.",
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        experiencia.temas_transversais.add(tema)
        experiencia.normas_internacionais.add(norma)
        experiencia.dimensoes_consideradas.add(dimensao)
        experiencia.grupos_vulneraveis.add(grupo)

        pendente = Experiencia.objects.create(
            autor=cls.autor_pendente,
            titulo="Boa pratica pendente",
            titulo_es="Buena practica pendiente",
            titulo_en="Pending good practice",
            efs=efs,
            pais=pais,
            tipo_experiencia=tipo,
            ano_execucao=2026,
            status_iniciativa=Experiencia.StatusIniciativa.CONCLUIDA,
            setor=setor,
            contato_referencia="Contato Pendente",
            email_contato="autor@example.org",
            descricao="Experiencia aguardando revisao.",
            descricao_es="Experiencia esperando revision.",
            descricao_en="Experience awaiting review.",
            enfoque_justica_climatica="Equidade.",
            enfoque_justica_climatica_es="Equidad.",
            enfoque_justica_climatica_en="Equity.",
            status_publicacao=Experiencia.StatusPublicacao.ENVIADO,
        )
        pendente.temas_transversais.add(tema)
        pendente.normas_internacionais.add(norma)

        recurso = BancoTecnico.objects.create(
            titulo="Checklist para avaliar planos de adaptacao",
            titulo_es="Checklist para evaluar planes de adaptacion",
            titulo_en="Checklist for assessing adaptation plans",
            descricao="Recurso tecnico de demonstracao.",
            descricao_es="Recurso tecnico de demostracion.",
            descricao_en="Demonstration technical resource.",
            tipo_recurso="Checklist",
            tipo_recurso_es="Checklist",
            tipo_recurso_en="Checklist",
            setor=setor,
        )
        recurso.dimensoes.add(dimensao)

    def test_pagina_inicial_retorna_200(self):
        self.assertEqual(self.client.get(reverse("pagina_inicial")).status_code, 200)

    def test_catalogo_retorna_200(self):
        self.assertEqual(self.client.get(reverse("catalogo_experiencias")).status_code, 200)

    def test_comparar_experiencias_retorna_200(self):
        self.assertEqual(self.client.get(reverse("comparar_experiencias")).status_code, 200)

    def test_comparar_experiencias_com_item(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        response = self.client.get(reverse("comparar_experiencias"), {"experiencias": [experiencia.pk]})
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "TCU" in conteudo or "Federal Court of Accounts" in conteudo,
            conteudo,
        )

    def test_normas_retorna_200(self):
        self.assertEqual(self.client.get(reverse("normas_internacionais")).status_code, 200)

    def test_adicionar_boa_pratica_exige_login(self):
        response = self.client.get(reverse("adicionar_boa_pratica"))
        self.assertEqual(response.status_code, 302)

    def test_adicionar_boa_pratica_logado_retorna_200(self):
        usuario = get_user_model().objects.create_user(
            username="autor",
            email="autor.org",
            password="teste123",
        )
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse("adicionar_boa_pratica")).status_code, 200)

    def test_status_envio_exige_login(self):
        self.assertEqual(self.client.get(reverse("status_envio")).status_code, 302)

    def test_banco_tecnico_retorna_200(self):
        self.assertEqual(self.client.get(reverse("banco_tecnico")).status_code, 200)

    def test_sobre_retorna_200(self):
        self.assertEqual(self.client.get(reverse("sobre_plataforma")).status_code, 200)

    def test_rota_es_retorna_200(self):
        self.assertEqual(self.client.get("/es/").status_code, 200)

    def test_rota_en_retorna_200(self):
        self.assertEqual(self.client.get("/en/").status_code, 200)

    def test_busca_em_ingles_retorna_resultado(self):
        response = self.client.get("/en/catalogo/", {"q": "water"})
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "TCU" in conteudo or "Federal Court of Accounts" in conteudo,
            conteudo,
        )

    def test_filtro_por_norma_retorna_resultado(self):
        norma = NormaInternacional.objects.get(nome="Acordo de Paris")
        response = self.client.get(reverse("catalogo_experiencias"), {"norma": norma.id})
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "TCU" in conteudo or "Federal Court of Accounts" in conteudo,
            conteudo,
        )

    def test_painel_revisao_exige_login_staff(self):
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.status_code, 302)

    def test_painel_revisao_staff_retorna_200(self):
        usuario = get_user_model().objects.create_user(
            username="revisor",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        response = self.client.get(reverse("painel_revisao"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "Boa pratica pendente" in conteudo
            or "Pending good practice" in conteudo
            or "Buena práctica pendiente" in conteudo
        )
        self.assertIn("autor@example.org", conteudo)
        self.assertIn("2026", conteudo)

    def test_revisor_publica_experiencia(self):
        usuario = get_user_model().objects.create_user(
            username="revisor2",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {
                "acao": "publicar",
                "comentario_revisor": "Aprovada para publicação.",
            },
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(
            experiencia.status_publicacao,
            Experiencia.StatusPublicacao.PUBLICADO,
        )

    def test_status_envio_exibe_registro_do_autor_autenticado(self):
        self.client.force_login(self.autor_pendente)
        response = self.client.get(reverse("status_envio"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "Boa pratica pendente" in conteudo
            or "Buena practica pendiente" in conteudo
            or "Pending good practice" in conteudo,
            conteudo,
        )
        self.assertNotContains(response, "autor@example.org")
        self.assertContains(response, "2026")

    def test_edicao_exige_login(self):
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        response = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(response.status_code, 302)

    def test_autor_edita_e_reenvia(self):
        experiencia = Experiencia.objects.get(titulo="Boa pratica pendente")
        self.client.force_login(self.autor_pendente)
        response = self.client.post(
            reverse("editar_boa_pratica", args=[experiencia.pk]),
            {
                "efs": experiencia.efs_id,
                "pais": experiencia.pais_id,
                "titulo": "Boa pratica ajustada",
                "tipo_experiencia": experiencia.tipo_experiencia_id,
                "setor": experiencia.setor_id,
                "temas_transversais": [str(item.id) for item in experiencia.temas_transversais.all()],
                "normas_internacionais": [str(item.id) for item in experiencia.normas_internacionais.all()],
                "contato_referencia": "Contato Ajustado",
                "email_contato": "autor@example.org",
                "pessoa_responsavel": "Pessoa Ajustada",
                "descricao": "Descricao ajustada.",
                "enfoque_justica_climatica": "Enfoque ajustado.",
                "objetivo": "Objetivo ajustado.",
                "perguntas_chave": "Pergunta ajustada.",
                "criterios_utilizados": "Criterio ajustado.",
                "metodologia": "Metodologia ajustada.",
                "ferramentas_utilizadas": "Ferramenta ajustada.",
                "resultados": "Resultado ajustado.",
                "recomendacoes": "Recomendacao ajustada.",
                "replicabilidade": "Replicabilidade ajustada.",
                "ano_execucao": 2026,
                "contribui_para_guia": "on",
                "acao_envio": "enviar",
            },
        )
        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.titulo, "Boa pratica ajustada")
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)

    def test_catalogo_preserva_apenas_acoes_previstas_no_prototipo(self):
        response = self.client.get(reverse("catalogo_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "modalBoaPratica")
        self.assertNotContains(response, "What is a good practice")
        self.assertNotContains(response, ">Favoritar<")
        self.assertNotContains(response, "catalog-compare-checkbox")
        self.assertNotContains(response, "catalogoCompararSelecionadas")
        self.assertNotContains(response, "Open comparison page")

    def test_login_com_next_redireciona_para_formulario(self):
        usuario = get_user_model().objects.create_user(
            username="autor_next",
            email="autor_next@example.org",
            password="teste123",
        )
        response = self.client.post(
            f"{reverse('login_usuario')}?next={reverse('adicionar_boa_pratica')}",
            {
                "username": "autor_next",
                "password": "teste123",
                "next": reverse("adicionar_boa_pratica"),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("adicionar_boa_pratica"))


    def test_favoritos_retorna_200(self):
        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)

    def test_alternar_favorito_adiciona_na_sessao(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        response = self.client.post(
            reverse("alternar_favorito", args=[experiencia.pk]),
            {"next": reverse("favoritos_experiencias")},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(experiencia.pk, self.client.session.get("favoritos_experiencias", []))

    def test_favoritos_exibe_experiencia_salva(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        session = self.client.session
        session["favoritos_experiencias"] = [experiencia.pk]
        session.save()

        response = self.client.get(reverse("favoritos_experiencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Assessment of equity in access to water")


    def test_cadastro_usuario_retorna_200(self):
        response = self.client.get(reverse("registrar_usuario"))
        self.assertEqual(response.status_code, 200)

    def test_login_usuario_retorna_200(self):
        response = self.client.get(reverse("login_usuario"))
        self.assertEqual(response.status_code, 200)

    def test_meus_envios_exige_login(self):
        response = self.client.get(reverse("meus_envios"))
        self.assertEqual(response.status_code, 302)

    def test_meus_envios_nao_vincula_registro_apenas_por_email(self):
        usuario = get_user_model().objects.create_user(
            username="autor_envios",
            email="autor@example.org",
            password="teste123",
        )
        self.client.force_login(usuario)
        response = self.client.get(reverse("meus_envios"))
        self.assertEqual(response.status_code, 200)
        conteudo = response.content.decode("utf-8")
        self.assertNotIn("Boa pratica pendente", conteudo)
        self.assertNotIn("Buena practica pendiente", conteudo)
        self.assertNotIn("Pending good practice", conteudo)

    def dados_validos_submissao(self):
        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        tema = experiencia.temas_transversais.first()
        norma = experiencia.normas_internacionais.first()
        return {
            "efs": experiencia.efs_id,
            "pais": experiencia.pais_id,
            "titulo": "Boa pratica com anexo validado",
            "tipo_experiencia": experiencia.tipo_experiencia_id,
            "setor": experiencia.setor_id,
            "temas_transversais": [str(tema.id)],
            "normas_internacionais": [str(norma.id)],
            "contato_referencia": "Contato Anexo",
            "email_contato": "anexo@example.org",
            "pessoa_responsavel": "Pessoa Anexo",
            "descricao": "Descricao com anexo.",
            "enfoque_justica_climatica": "Enfoque com anexo.",
            "objetivo": "Objetivo com anexo.",
            "perguntas_chave": "Pergunta com anexo.",
            "criterios_utilizados": "Criterio com anexo.",
            "metodologia": "Metodologia com anexo.",
            "ferramentas_utilizadas": "Ferramenta com anexo.",
            "resultados": "Resultado com anexo.",
            "recomendacoes": "Recomendacao com anexo.",
            "replicabilidade": "Replicabilidade com anexo.",
            "ano_execucao": 2026,
            "contribui_para_guia": "on",
            "acao_envio": "enviar",
        }

    def test_anexo_invalido_nao_e_aceito_no_envio(self):
        usuario = get_user_model().objects.create_user(
            username="autor_anexo",
            email="anexo@example.org",
            password="teste123",
        )
        self.client.force_login(usuario)

        dados = self.dados_validos_submissao()
        dados["anexo_titulo_1"] = "Arquivo executavel"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "risco.exe",
            b"conteudo",
            content_type="application/octet-stream",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tipo de arquivo")
        self.assertFalse(Anexo.objects.filter(titulo="Arquivo executavel").exists())

    def test_anexo_pdf_valido_e_salvo_no_envio(self):
        usuario = get_user_model().objects.create_user(
            username="autor_anexo_pdf",
            email="anexo_pdf@example.org",
            password="teste123",
        )
        self.client.force_login(usuario)

        dados = self.dados_validos_submissao()
        dados["email_contato"] = "anexo_pdf@example.org"
        dados["anexo_titulo_1"] = "Relatorio PDF"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "relatorio.pdf",
            b"%PDF-1.4 conteudo",
            content_type="application/pdf",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Anexo.objects.filter(titulo="Relatorio PDF").exists())

    def test_revisao_edicao_publicada_exibe_comparativo_visual(self):
        usuario = get_user_model().objects.create_user(
            username="revisor_comparativo",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)

        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        tema = experiencia.temas_transversais.first()
        norma = experiencia.normas_internacionais.first()

        proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=experiencia,
            email_contato=experiencia.email_contato,
            comentario_autor="Atualização do título e dos resultados.",
            dados_json={
                "efs": experiencia.efs_id,
                "pais": experiencia.pais_id,
                "titulo": "Titulo atualizado para comparativo",
                "tipo_experiencia": experiencia.tipo_experiencia_id,
                "setor": experiencia.setor_id,
                "temas_transversais": [tema.id],
                "normas_internacionais": [norma.id],
                "contato_referencia": experiencia.contato_referencia,
                "email_contato": experiencia.email_contato,
                "pessoa_responsavel": experiencia.pessoa_responsavel,
                "descricao": experiencia.descricao,
                "enfoque_justica_climatica": experiencia.enfoque_justica_climatica,
                "objetivo": experiencia.objetivo,
                "perguntas_chave": experiencia.perguntas_chave,
                "criterios_utilizados": experiencia.criterios_utilizados,
                "metodologia": experiencia.metodologia,
                "ferramentas_utilizadas": experiencia.ferramentas_utilizadas,
                "resultados": "Resultados atualizados para revisão visual.",
                "recomendacoes": experiencia.recomendacoes,
                "replicabilidade": experiencia.replicabilidade,
                "ano_execucao": experiencia.ano_execucao,
                "contribui_para_guia": experiencia.contribui_para_guia,
            },
        )

        response = self.client.get(reverse("revisar_edicao_publicada", args=[proposta.pk]))
        self.assertEqual(response.status_code, 200)

        conteudo = response.content.decode("utf-8")
        self.assertTrue(
            "Valor atual" in conteudo
            or "Valor actual" in conteudo
            or "Current value" in conteudo
        )
        self.assertTrue(
            "Valor proposto" in conteudo
            or "Valor propuesto" in conteudo
            or "Proposed value" in conteudo
        )
        self.assertIn("Titulo atualizado para comparativo", conteudo)
        self.assertIn("Resultados atualizados para revisão visual.", conteudo)

    def test_aprovar_proposta_edicao_aplica_valor_proposto(self):
        usuario = get_user_model().objects.create_user(
            username="revisor_aprovacao_comparativo",
            password="teste123",
            is_staff=True,
        )
        self.client.force_login(usuario)

        experiencia = Experiencia.objects.get(titulo="Avaliacao da equidade no acesso a agua")
        tema = experiencia.temas_transversais.first()
        norma = experiencia.normas_internacionais.first()

        proposta = PropostaEdicaoExperiencia.objects.create(
            experiencia=experiencia,
            email_contato=experiencia.email_contato,
            comentario_autor="Atualização aprovada.",
            dados_json={
                "efs": experiencia.efs_id,
                "pais": experiencia.pais_id,
                "titulo": "Titulo aprovado no fluxo visual",
                "tipo_experiencia": experiencia.tipo_experiencia_id,
                "setor": experiencia.setor_id,
                "temas_transversais": [tema.id],
                "normas_internacionais": [norma.id],
                "contato_referencia": experiencia.contato_referencia,
                "email_contato": experiencia.email_contato,
                "pessoa_responsavel": experiencia.pessoa_responsavel,
                "descricao": experiencia.descricao,
                "enfoque_justica_climatica": experiencia.enfoque_justica_climatica,
                "objetivo": experiencia.objetivo,
                "perguntas_chave": experiencia.perguntas_chave,
                "criterios_utilizados": experiencia.criterios_utilizados,
                "metodologia": experiencia.metodologia,
                "ferramentas_utilizadas": experiencia.ferramentas_utilizadas,
                "resultados": experiencia.resultados,
                "recomendacoes": experiencia.recomendacoes,
                "replicabilidade": experiencia.replicabilidade,
                "ano_execucao": experiencia.ano_execucao,
                "contribui_para_guia": experiencia.contribui_para_guia,
            },
        )

        response = self.client.post(
            reverse("revisar_edicao_publicada", args=[proposta.pk]),
            {
                "acao": "aprovar",
                "comentario_revisor": "Aprovado com base no comparativo.",
            },
        )

        self.assertEqual(response.status_code, 302)
        experiencia.refresh_from_db()
        proposta.refresh_from_db()
        self.assertEqual(experiencia.titulo, "Titulo aprovado no fluxo visual")
        self.assertEqual(proposta.status, PropostaEdicaoExperiencia.Status.APROVADA)
