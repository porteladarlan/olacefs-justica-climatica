from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import translation

from .admin import AnexoInline
from .forms import (
    AnexoAdminForm,
    AnexoSubmissaoForm,
    NormaInternacionalAdminForm,
)
from .models import Anexo, NormaInternacional
from .uploads import validar_anexo_upload


def arquivo_upload(nome, conteudo, content_type):
    return SimpleUploadedFile(nome, conteudo, content_type=content_type)


class ValidacaoUploadTests(TestCase):
    def test_formatos_atuais_validos_permanecem_aceitos(self):
        casos = (
            ("relatorio.pdf", b"%PDF-1.4\n", "application/pdf"),
            ("evidencia.jpg", b"\xff\xd8\xff\xe0", "image/jpeg"),
            ("grafico.jpeg", b"\xff\xd8\xff\xe0", "image/jpeg"),
            ("mapa.png", b"\x89PNG\r\n\x1a\n", "image/png"),
        )

        for nome, conteudo, content_type in casos:
            with self.subTest(nome=nome):
                form = AnexoSubmissaoForm(
                    data={"titulo": "Arquivo válido", "url_externa": ""},
                    files={"arquivo": arquivo_upload(nome, conteudo, content_type)},
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_extensao_e_normalizada_sem_diferenciar_maiusculas(self):
        casos = (
            ("RELATORIO.PDF", b"%PDF-1.4\n", "application/pdf"),
            ("Foto.JpG", b"\xff\xd8\xff\xe0", "image/jpeg"),
        )

        for nome, conteudo, content_type in casos:
            with self.subTest(nome=nome):
                validar_anexo_upload(
                    arquivo_upload(nome, conteudo, content_type)
                )

    def test_extensao_nao_permitida_retorna_erro_e_nao_persiste(self):
        form = AnexoSubmissaoForm(
            data={"titulo": "Executável", "url_externa": ""},
            files={
                "arquivo": arquivo_upload(
                    "programa.exe", b"MZ", "application/octet-stream"
                )
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("tipo de arquivo não permitido", form.errors["arquivo"][0])
        self.assertEqual(Anexo.objects.count(), 0)

    @override_settings(MAX_UPLOAD_SIZE_MB=1, MAX_UPLOAD_SIZE_BYTES=8)
    def test_arquivo_acima_do_limite_retorna_erro_amigavel(self):
        form = AnexoSubmissaoForm(
            data={"titulo": "Arquivo grande", "url_externa": ""},
            files={
                "arquivo": arquivo_upload(
                    "grande.pdf", b"%PDF-123456", "application/pdf"
                )
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("arquivo maior que 1 MB", form.errors["arquivo"][0])
        self.assertEqual(Anexo.objects.count(), 0)

    def test_mime_e_assinatura_sao_camadas_complementares(self):
        casos = (
            arquivo_upload("imagem.png", b"\x89PNG\r\n\x1a\n", "image/jpeg"),
            arquivo_upload("documento.pdf", b"conteudo falso", "application/pdf"),
        )

        for arquivo in casos:
            with self.subTest(nome=arquivo.name):
                with self.assertRaises(ValidationError):
                    validar_anexo_upload(arquivo)

    def test_nomes_com_path_traversal_permanecem_no_diretorio_de_upload(self):
        casos = (
            ("../../relatorio.pdf", "relatorio.pdf"),
            ("..\\..\\relatorio.pdf", "relatorio.pdf"),
            ("relatorio-final.pdf", "relatorio-final.pdf"),
        )

        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root
        ):
            raiz_media = Path(media_root).resolve()
            diretorio_anexos = (raiz_media / "anexos").resolve()

            for nome_recebido, nome_esperado in casos:
                with self.subTest(nome=nome_recebido):
                    arquivo = arquivo_upload(
                        "temporario.pdf", b"%PDF-1.4\n", "application/pdf"
                    )
                    # Simula o nome bruto recebido, sem depender do basename
                    # aplicado pelo sistema operacional no UploadedFile.
                    arquivo._name = nome_recebido
                    validar_anexo_upload(arquivo)
                    self.assertEqual(arquivo.name, nome_esperado)

                    anexo = Anexo(titulo="Traversal bloqueado")
                    anexo.arquivo.save(arquivo.name, arquivo, save=False)
                    caminho_armazenado = Path(anexo.arquivo.path).resolve()

                    self.assertTrue(caminho_armazenado.is_relative_to(raiz_media))
                    self.assertEqual(caminho_armazenado.parent, diretorio_anexos)
                    self.assertNotIn("..", caminho_armazenado.parts)
                    self.assertEqual(caminho_armazenado.name, nome_esperado)
                    anexo.arquivo.delete(save=False)

    def test_ficha_tecnica_do_admin_aceita_somente_pdf(self):
        form_valido = NormaInternacionalAdminForm(
            data={"nome": "Norma com ficha PDF"},
            files={
                "ficha_tecnica": arquivo_upload(
                    "ficha.PDF", b"%PDF-1.4\n", "application/pdf"
                )
            },
        )
        form_invalido = NormaInternacionalAdminForm(
            data={"nome": "Norma com imagem"},
            files={
                "ficha_tecnica": arquivo_upload(
                    "ficha.png", b"\x89PNG\r\n\x1a\n", "image/png"
                )
            },
        )

        self.assertTrue(form_valido.is_valid(), form_valido.errors)
        self.assertFalse(form_invalido.is_valid())
        self.assertIn(
            "tipo de arquivo não permitido",
            form_invalido.errors["ficha_tecnica"][0],
        )
        self.assertEqual(NormaInternacional.objects.count(), 0)

    def test_mensagens_de_erro_respeitam_pt_es_en(self):
        esperados = {
            "pt-br": "tipo de arquivo não permitido",
            "es": "tipo de archivo no permitido",
            "en": "file type not allowed",
        }

        for idioma, esperado in esperados.items():
            with self.subTest(idioma=idioma), translation.override(idioma):
                with self.assertRaisesMessage(ValidationError, esperado):
                    validar_anexo_upload(
                        arquivo_upload("arquivo.exe", b"MZ", "application/octet-stream")
                    )

    def test_admin_e_inline_usam_formularios_com_validacao_central(self):
        self.assertIs(admin.site._registry[Anexo].form, AnexoAdminForm)
        self.assertIs(
            admin.site._registry[NormaInternacional].form,
            NormaInternacionalAdminForm,
        )
        inline = next(
            item
            for item in admin.site._registry[
                Anexo._meta.get_field("experiencia").remote_field.model
            ].inlines
            if item is AnexoInline
        )
        self.assertIs(inline.form, AnexoAdminForm)
