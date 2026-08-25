from html import unescape
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .management.commands.auditar_traducoes_trilingues import (
    Command as AuditoriaTrilingueCommand,
)
from .models import (
    Anexo,
    EFS,
    Experiencia,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)


class SegurancaFaseTests(TestCase):
    def setUp(self):
        translation.activate("pt-br")

    def tearDown(self):
        translation.deactivate()

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.autor = User.objects.create_user(
            username="autor_seguranca",
            email="contato.compartilhado@example.org",
            password="SenhaForte123!",
        )
        cls.outro = User.objects.create_user(
            username="outro_seguranca",
            email="contato.compartilhado@example.org",
            password="SenhaForte123!",
        )
        cls.staff = User.objects.create_user(
            username="staff_seguranca",
            email="staff@example.org",
            password="SenhaForte123!",
            is_staff=True,
        )
        cls.pais = Pais.objects.create(
            nome="Brasil Segurança",
            nome_es="Brasil Seguridad",
            nome_en="Brazil Security",
            sigla="BRS",
        )
        cls.efs = EFS.objects.create(
            nome="EFS Segurança",
            nome_es="EFS Seguridad",
            nome_en="Security SAI",
            sigla="EFSS",
            pais=cls.pais,
        )
        cls.tipo = TipoExperiencia.objects.create(
            nome="Auditoria Segurança",
            nome_es="Auditoría Seguridad",
            nome_en="Security Audit",
        )
        cls.setor = Setor.objects.create(
            nome="Setor Segurança",
            nome_es="Sector Seguridad",
            nome_en="Security Sector",
        )
        cls.tema = TemaTransversal.objects.create(
            nome="Tema Segurança",
            nome_es="Tema Seguridad",
            nome_en="Security Theme",
        )
        cls.norma = NormaInternacional.objects.create(
            nome="Norma Segurança",
            nome_es="Norma Seguridad",
            nome_en="Security Standard",
        )
        cls.rascunho = cls.criar_experiencia(
            autor=cls.autor,
            titulo="Envio protegido do autor",
            status=Experiencia.StatusPublicacao.RASCUNHO,
        )
        cls.publicada = cls.criar_experiencia(
            autor=cls.autor,
            titulo="Experiência publicada do autor",
            status=Experiencia.StatusPublicacao.PUBLICADO,
        )
        cls.envio_outro = cls.criar_experiencia(
            autor=cls.outro,
            titulo="Envio exclusivo do outro usuário",
            status=Experiencia.StatusPublicacao.ENVIADO,
        )
        cls.proposta_autor = PropostaEdicaoExperiencia.objects.create(
            experiencia=cls.publicada,
            email_contato=cls.publicada.email_contato,
            comentario_autor="Ajuste protegido do autor.",
            comentario_revisor="Comentário protegido do revisor.",
            dados_json={},
        )

    @classmethod
    def criar_experiencia(cls, autor, titulo, status):
        experiencia = Experiencia.objects.create(
            autor=autor,
            titulo=titulo,
            efs=cls.efs,
            pais=cls.pais,
            tipo_experiencia=cls.tipo,
            setor=cls.setor,
            ano_execucao=2026,
            email_contato="contato.compartilhado@example.org",
            pessoa_responsavel="Pessoa responsável",
            descricao="Descrição suficiente para o teste de segurança.",
            enfoque_justica_climatica="Equidade e proteção de grupos vulneráveis.",
            status_publicacao=status,
        )
        experiencia.temas_transversais.add(cls.tema)
        experiencia.normas_internacionais.add(cls.norma)
        return experiencia

    def dados_validos(self, experiencia=None):
        experiencia = experiencia or self.rascunho
        return {
            "efs": experiencia.efs_id,
            "pais": experiencia.pais_id,
            "titulo": experiencia.titulo,
            "tipo_experiencia": experiencia.tipo_experiencia_id,
            "setor": experiencia.setor_id,
            "temas_transversais": [self.tema.pk],
            "normas_internacionais": [self.norma.pk],
            "email_contato": experiencia.email_contato,
            "pessoa_responsavel": experiencia.pessoa_responsavel,
            "descricao": experiencia.descricao,
            "enfoque_justica_climatica": experiencia.enfoque_justica_climatica,
            "objetivo": "Objetivo de segurança.",
            "perguntas_chave": "Pergunta de segurança.",
            "criterios_utilizados": "Critério de segurança.",
            "metodologia": "Metodologia de segurança.",
            "ferramentas_utilizadas": "Ferramenta de segurança.",
            "resultados": "Resultado de segurança.",
            "recomendacoes": "Recomendação de segurança.",
            "replicabilidade": "Replicabilidade de segurança.",
            "ano_execucao": experiencia.ano_execucao,
            "contribui_para_guia": "on",
            "acao_envio": "rascunho",
        }

    def test_edicao_anonima_com_email_conhecido_redireciona_para_login(self):
        url = reverse("editar_boa_pratica", args=[self.rascunho.pk])
        response = self.client.get(url, {"email": self.rascunho.email_contato})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_usuario"), response.url)

    def test_usuario_com_mesmo_email_nao_edita_objeto_de_outro_autor(self):
        self.client.force_login(self.outro)
        url = reverse("editar_boa_pratica", args=[self.rascunho.pk])
        response = self.client.get(url, {"email": self.rascunho.email_contato})

        self.assertRedirects(response, reverse("meus_envios"))

    def test_autor_real_e_staff_acessam_edicao(self):
        url = reverse("editar_boa_pratica", args=[self.rascunho.pk])
        for usuario in (self.autor, self.staff):
            with self.subTest(usuario=usuario.username):
                self.client.force_login(usuario)
                self.assertEqual(self.client.get(url).status_code, 200)
                self.client.logout()

    def test_solicitacao_publicada_anonima_com_email_exige_login(self):
        url = reverse("solicitar_edicao_publicada", args=[self.publicada.pk])
        response = self.client.get(url, {"email": self.publicada.email_contato})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_usuario"), response.url)

    def test_usuario_com_mesmo_email_nao_solicita_edicao_de_outro_autor(self):
        self.client.force_login(self.outro)
        url = reverse("solicitar_edicao_publicada", args=[self.publicada.pk])
        response = self.client.get(url, {"email": self.publicada.email_contato})

        self.assertRedirects(response, reverse("meus_envios"))

    def test_autor_real_acessa_solicitacao_de_edicao_publicada(self):
        self.client.force_login(self.autor)
        response = self.client.get(
            reverse("solicitar_edicao_publicada", args=[self.publicada.pk])
        )

        self.assertRedirects(response, reverse("editar_boa_pratica", args=[self.publicada.pk]))

    def test_status_anonimo_com_email_conhecido_exige_login(self):
        response = self.client.get(
            reverse("status_envio"),
            {"email_contato": self.rascunho.email_contato},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login_usuario"), response.url)

    def test_status_ignora_email_e_exibe_somente_objetos_do_usuario(self):
        self.client.force_login(self.outro)
        response = self.client.get(
            reverse("status_envio"),
            {"email_contato": self.rascunho.email_contato},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.envio_outro.titulo)
        self.assertNotContains(response, self.rascunho.titulo)
        self.assertNotContains(response, self.publicada.titulo)
        self.assertNotContains(response, "Ajuste protegido do autor.")

    def test_status_do_autor_e_staff_respeita_permissoes(self):
        self.client.force_login(self.autor)
        response_autor = self.client.get(reverse("status_envio"))
        self.assertContains(response_autor, self.rascunho.titulo)
        self.assertContains(response_autor, self.publicada.titulo)
        self.assertNotContains(response_autor, self.envio_outro.titulo)

        self.client.force_login(self.staff)
        response_staff = self.client.get(reverse("status_envio"))
        self.assertContains(response_staff, self.rascunho.titulo)
        self.assertContains(response_staff, self.envio_outro.titulo)

    def test_paginas_autenticadas_exibem_textos_e_acoes_trilingues(self):
        self.client.force_login(self.autor)
        cenarios = (
            (
                "/en",
                "linked to your authenticated account",
                "Edit",
                "Edit",
                "Review:",
            ),
            (
                "/es",
                "vinculados a su cuenta autenticada",
                "Editar",
                "Editar",
                "Revisión:",
            ),
            (
                "",
                "vinculados à sua conta autenticada",
                "Editar",
                "Editar",
                "Revisão:",
            ),
        )

        for prefixo, texto_conta, solicitar, editar, revisao in cenarios:
            idioma = "pt" if not prefixo else prefixo.removeprefix("/")
            caminho_meus_envios = f"{prefixo}/meus-envios/" if prefixo else "/meus-envios/"
            caminho_status = f"{prefixo}/status-envio/" if prefixo else "/status-envio/"
            for caminho in (caminho_meus_envios, caminho_status):
                with self.subTest(idioma=idioma, caminho=caminho):
                    response = self.client.get(caminho)
                    self.assertEqual(response.status_code, 200)
                    conteudo_visivel = unescape(response.content.decode())
                    self.assertIn(texto_conta, conteudo_visivel)
                    self.assertIn(editar, conteudo_visivel)
                    if "status-envio" not in caminho:
                        self.assertIn(revisao, conteudo_visivel)

    def test_paginas_autenticadas_nao_indicam_vinculo_por_email(self):
        self.client.force_login(self.autor)
        textos_antigos = (
            "linked to your institutional e-mail",
            "vinculadas a su correo institucional",
            "vinculadas ao seu e-mail institucional",
            "No submission found for this e-mail",
            "No se encontraron envíos para este correo",
            "Nenhum envio encontrado para este e-mail",
        )

        for caminho in (
            "/meus-envios/",
            "/status-envio/",
            "/es/meus-envios/",
            "/es/status-envio/",
            "/en/meus-envios/",
            "/en/status-envio/",
        ):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                conteudo_visivel = unescape(response.content.decode())
                for texto in textos_antigos:
                    self.assertNotIn(texto, conteudo_visivel)

    def test_estados_vazios_autenticados_sao_trilingues(self):
        usuario_sem_envios = get_user_model().objects.create_user(
            username="sem_envios_seguranca",
            password="SenhaForte123!",
        )
        self.client.force_login(usuario_sem_envios)
        cenarios = (
            ("", "Ainda não há envios vinculados à sua conta autenticada."),
            ("/es", "Aún no hay envíos vinculados a su cuenta autenticada."),
            ("/en", "No submissions are linked to your authenticated account yet."),
        )

        for prefixo, texto in cenarios:
            for rota in ("meus-envios", "status-envio"):
                caminho = f"{prefixo}/{rota}/" if prefixo else f"/{rota}/"
                with self.subTest(caminho=caminho):
                    response = self.client.get(caminho)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, texto)

    def test_meus_envios_e_status_mantem_isolamento_entre_autores(self):
        self.client.force_login(self.outro)

        for caminho in ("/meus-envios/", "/status-envio/"):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.envio_outro.titulo)
                self.assertNotContains(response, self.rascunho.titulo)
                self.assertNotContains(response, self.publicada.titulo)
                self.assertNotContains(response, self.proposta_autor.comentario_revisor)

    def test_auditoria_trilingue_autentica_paginas_restritas(self):
        saida = StringIO()
        prefixo_usuario_temporario = "auditoria_trilingue_"
        usuarios_antes = get_user_model().objects.filter(
            username__startswith=prefixo_usuario_temporario
        ).count()

        call_command("auditar_traducoes_trilingues", stdout=saida)

        conteudo = saida.getvalue()
        for caminho in (
            "/en/cadastro/",
            "/es/cadastro/",
            "/en/adicionar-boa-pratica/",
            "/en/meus-envios/",
            "/en/status-envio/",
            "/es/adicionar-boa-pratica/",
            "/es/meus-envios/",
            "/es/status-envio/",
        ):
            with self.subTest(caminho=caminho):
                self.assertIn(f"{caminho} -> ", conteudo)
                for status_ignorado in (301, 302, 403, 404):
                    self.assertNotIn(
                        f"{caminho} -> {status_ignorado} (ignorado)",
                        conteudo,
                    )

        usuarios_depois = get_user_model().objects.filter(
            username__startswith=prefixo_usuario_temporario
        ).count()
        self.assertEqual(usuarios_depois, usuarios_antes)

    def test_auditoria_trilingue_trata_url_declarada_com_404_como_alerta(self):
        saida = StringIO()

        with patch.object(
            AuditoriaTrilingueCommand,
            "URLS",
            ["/rota-inexistente-na-auditoria/"],
        ):
            call_command("auditar_traducoes_trilingues", stdout=saida)

        conteudo = saida.getvalue()
        self.assertIn(
            "/en/rota-inexistente-na-auditoria/ -> 404 (URL declarada não encontrada)",
            conteudo,
        )
        self.assertIn(
            "/es/rota-inexistente-na-auditoria/ -> 404 (URL declarada não encontrada)",
            conteudo,
        )
        self.assertIn("Auditoria concluída com 2 alerta(s).", conteudo)

    def test_favorito_rejeita_redirecionamento_externo(self):
        url = reverse("alternar_favorito", args=[self.publicada.pk])
        for destino in ("https://example.invalid/roubo", "//example.invalid/roubo"):
            with self.subTest(destino=destino):
                response = self.client.post(url, {"next": destino})
                self.assertRedirects(response, reverse("catalogo_experiencias"))

    def test_favorito_preserva_redirecionamento_interno_e_mensagem_utf8(self):
        response = self.client.post(
            reverse("alternar_favorito", args=[self.publicada.pk]),
            {"next": reverse("favoritos_experiencias")},
            follow=True,
        )

        self.assertEqual(response.redirect_chain[-1][0], reverse("favoritos_experiencias"))
        self.assertContains(response, "Experiência adicionada aos favoritos.")

    def test_upload_com_extensao_pdf_e_conteudo_falso_e_rejeitado(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos()
        dados["anexo_titulo_1"] = "PDF falso"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "falso.pdf",
            b"arquivo executavel disfarcado",
            content_type="application/pdf",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "conteúdo do arquivo")
        self.assertFalse(Anexo.objects.filter(titulo="PDF falso").exists())

    def test_upload_com_mime_declarado_incoerente_e_rejeitado(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos()
        dados["anexo_titulo_1"] = "PNG com MIME falso"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "imagem.png",
            b"\x89PNG\r\n\x1a\nconteudo",
            content_type="image/jpeg",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tipo MIME informado")
        self.assertFalse(Anexo.objects.filter(titulo="PNG com MIME falso").exists())

    def test_upload_acima_de_10_mb_retorna_erro_controlado(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos()
        dados["anexo_titulo_1"] = "PDF grande"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "grande.pdf",
            b"%PDF-" + b"x" * settings.MAX_UPLOAD_SIZE_BYTES,
            content_type="application/pdf",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "arquivo maior que 10 MB")
        self.assertFalse(Anexo.objects.filter(titulo="PDF grande").exists())

    def test_upload_com_traversal_e_normalizado_sem_erro_500(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos()
        dados["anexo_titulo_1"] = "PDF com nome normalizado"
        arquivo = SimpleUploadedFile(
            "temporario.pdf",
            b"%PDF-1.4 conteudo",
            content_type="application/pdf",
        )
        arquivo._name = "..\\..\\relatorio.pdf"
        dados["anexo_arquivo_1"] = arquivo

        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse("adicionar_boa_pratica"), dados)
            anexo = Anexo.objects.get(titulo="PDF com nome normalizado")
            caminho_armazenado = Path(anexo.arquivo.path).resolve()

            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                caminho_armazenado.is_relative_to(Path(media_root).resolve())
            )
            self.assertEqual(caminho_armazenado.parent.name, "anexos")
            self.assertEqual(caminho_armazenado.name, "relatorio.pdf")

    def test_quarta_posicao_de_anexo_e_rejeitada(self):
        self.client.force_login(self.autor)
        dados = self.dados_validos()
        dados["anexo_titulo_4"] = "Quarto anexo"
        dados["anexo_arquivo_4"] = SimpleUploadedFile(
            "quarto.pdf",
            b"%PDF-1.4 conteudo",
            content_type="application/pdf",
        )

        response = self.client.post(reverse("adicionar_boa_pratica"), dados)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no máximo 3 anexos")
        self.assertFalse(Anexo.objects.filter(titulo="Quarto anexo").exists())

    def test_id_de_anexo_alheio_nao_contorna_limite_da_edicao(self):
        for indice in range(3):
            Anexo.objects.create(
                experiencia=self.rascunho,
                titulo=f"Anexo existente {indice}",
                url_externa=f"https://example.org/anexo-{indice}",
            )
        anexo_alheio = Anexo.objects.create(
            experiencia=self.envio_outro,
            titulo="Anexo alheio",
            url_externa="https://example.org/alheio",
        )
        self.client.force_login(self.autor)
        dados = self.dados_validos(self.rascunho)
        dados["remover_anexo"] = str(anexo_alheio.pk)
        dados["anexo_titulo_1"] = "Tentativa de quarto anexo"
        dados["anexo_arquivo_1"] = SimpleUploadedFile(
            "novo.pdf",
            b"%PDF-1.4 conteudo",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("editar_boa_pratica", args=[self.rascunho.pk]),
            dados,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "manter no máximo 3 anexos")
        self.assertEqual(self.rascunho.anexos.count(), 3)
        self.assertTrue(Anexo.objects.filter(pk=anexo_alheio.pk).exists())

    def test_codigo_executavel_nao_contem_sequencias_de_mojibake(self):
        base_dir = Path(settings.BASE_DIR)
        arquivos = [base_dir / "praticas" / "views.py", base_dir / "praticas" / "forms.py"]
        arquivos.extend((base_dir / "praticas" / "management" / "commands").glob("*.py"))
        arquivos.extend((base_dir / "praticas").glob("tests*.py"))
        arquivos.extend((base_dir / "templates" / "praticas").rglob("*.html"))
        sequencias = [
            "".join(chr(codigo) for codigo in codigos)
            for codigos in (
                (0xC3, 0xA7),
                (0xC3, 0xA3),
                (0xC3, 0xB5),
                (0xC3, 0xAA),
                (0xC3, 0xA1),
                (0xC3, 0xA9),
                (0xC3, 0xAD),
                (0xC3, 0xB3),
                (0xC3, 0xBA),
                (0xC3, 0x89),
                (0xC3, 0xA0),
                (0xE2, 0x20AC),
                (0xF0, 0x178),
            )
        ]
        sequencias.extend((chr(0xC2), chr(0xFFFD)))

        achados = []
        for arquivo in arquivos:
            conteudo = arquivo.read_text(encoding="utf-8")
            for sequencia in sequencias:
                if sequencia in conteudo:
                    achados.append(f"{arquivo.relative_to(base_dir)}: {sequencia!r}")

        self.assertEqual(achados, [])
