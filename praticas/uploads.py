from pathlib import PurePosixPath

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import get_language


TIPOS_ANEXO_PERMITIDOS = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
TIPOS_FICHA_TECNICA_PERMITIDOS = {
    ".pdf": "application/pdf",
}


def _texto_idioma(pt, es, en):
    idioma = (get_language() or "pt-br").lower()
    if idioma.startswith("en"):
        return en
    if idioma.startswith("es"):
        return es
    return pt


def _mime_pelo_conteudo(arquivo):
    posicao_original = arquivo.tell()
    try:
        arquivo.seek(0)
        cabecalho = arquivo.read(16)
    finally:
        arquivo.seek(posicao_original)

    if cabecalho.startswith(b"%PDF-"):
        return "application/pdf"
    if cabecalho.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if cabecalho.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None


def _normalizar_nome_arquivo(arquivo):
    nome_original = str(getattr(arquivo, "name", "") or "")
    nome_normalizado = nome_original.replace("\\", "/")
    nome_seguro = PurePosixPath(nome_normalizado).name

    if not nome_seguro or nome_seguro in {".", ".."}:
        raise ValidationError(
            _texto_idioma(
                "nome de arquivo inválido.",
                "nombre de archivo no válido.",
                "invalid file name.",
            )
        )

    arquivo.name = nome_seguro
    return nome_seguro


def _validar_upload(arquivo, tipos_permitidos, formatos_exibicao):
    if not arquivo or getattr(arquivo, "_committed", False):
        return

    erros = []
    nome_seguro = _normalizar_nome_arquivo(arquivo)
    extensao = PurePosixPath(nome_seguro).suffix.lower()
    mime_esperado = tipos_permitidos.get(extensao)
    formatos_pt, formatos_es, formatos_en = formatos_exibicao

    if not mime_esperado:
        erros.append(
            _texto_idioma(
                f"tipo de arquivo não permitido. Use {formatos_pt}.",
                f"tipo de archivo no permitido. Use {formatos_es}.",
                f"file type not allowed. Use {formatos_en}.",
            )
        )
    else:
        mime_declarado = (
            (getattr(arquivo, "content_type", "") or "")
            .split(";", 1)[0]
            .strip()
            .lower()
        )
        if mime_declarado != mime_esperado:
            erros.append(
                _texto_idioma(
                    "o tipo MIME informado não corresponde à extensão do arquivo.",
                    "el tipo MIME informado no corresponde a la extensión del archivo.",
                    "the reported MIME type does not match the file extension.",
                )
            )
        if _mime_pelo_conteudo(arquivo) != mime_esperado:
            erros.append(
                _texto_idioma(
                    f"o conteúdo do arquivo não corresponde a um {formatos_pt} válido.",
                    f"el contenido del archivo no corresponde a un {formatos_es} válido.",
                    f"the file content is not a valid {formatos_en} file.",
                )
            )

    if arquivo.size > settings.MAX_UPLOAD_SIZE_BYTES:
        erros.append(
            _texto_idioma(
                f"arquivo maior que {settings.MAX_UPLOAD_SIZE_MB} MB.",
                f"archivo mayor que {settings.MAX_UPLOAD_SIZE_MB} MB.",
                f"file larger than {settings.MAX_UPLOAD_SIZE_MB} MB.",
            )
        )

    if erros:
        raise ValidationError(erros)


def validar_anexo_upload(arquivo):
    _validar_upload(
        arquivo,
        TIPOS_ANEXO_PERMITIDOS,
        ("PDF, JPG ou PNG", "PDF, JPG o PNG", "PDF, JPG or PNG"),
    )


def validar_ficha_tecnica_upload(arquivo):
    _validar_upload(
        arquivo,
        TIPOS_FICHA_TECNICA_PERMITIDOS,
        ("PDF", "PDF", "PDF"),
    )
