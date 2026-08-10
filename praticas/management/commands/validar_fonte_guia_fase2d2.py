import hashlib
import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_slug


HASH_CANONICO_GUIA = "8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d"
HASH_FONTE_OFICIAL = "cd78b9beca799aa9c6976af825c314e57e4a1903bfa832ecec2fbc3d86b61c67"
CONTAGENS_OFICIAIS = {
    "eixos": 3,
    "subeixos": 8,
    "setores": 9,
    "subareas": 47,
    "perguntas": 407,
    "ocorrencias_referencias": 224,
    "referencias": 223,
}
CONTRATO = "guia-fase2d2-v1"


class ErroFonteGuia(ValueError):
    pass


def _objeto(objeto, obrigatorias, permitidas, contexto):
    if not isinstance(objeto, dict):
        raise ErroFonteGuia(f"{contexto}: deve ser um objeto.")
    chaves = set(objeto)
    ausentes = sorted(set(obrigatorias) - chaves)
    if ausentes:
        raise ErroFonteGuia(
            f"{contexto}: campos obrigatorios ausentes: {', '.join(ausentes)}."
        )
    desconhecidas = sorted(chaves - set(permitidas))
    if desconhecidas:
        raise ErroFonteGuia(
            f"{contexto}: campos desconhecidos: {', '.join(desconhecidas)}."
        )


def _texto(objeto, campo, contexto, limite=None):
    valor = objeto.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ErroFonteGuia(f"{contexto}: campo {campo} ausente ou invalido.")
    if limite is not None and len(valor) > limite:
        raise ErroFonteGuia(f"{contexto}: campo {campo} excede {limite} caracteres.")
    return valor


def _codigo(objeto, contexto, limite=160):
    codigo = _texto(objeto, "codigo", contexto)
    try:
        validate_slug(codigo)
    except ValidationError:
        raise ErroFonteGuia(f"{contexto}: codigo institucional invalido.") from None
    if len(codigo) > limite:
        raise ErroFonteGuia(f"{contexto}: codigo institucional invalido.")
    return codigo


def _lista(objeto, campo, contexto):
    valor = objeto.get(campo)
    if not isinstance(valor, list):
        raise ErroFonteGuia(f"{contexto}: campo {campo} deve ser uma lista.")
    return valor


def _validar_ordem(itens, contexto):
    if any(not isinstance(item, dict) for item in itens):
        raise ErroFonteGuia(f"{contexto}: todos os itens devem ser objetos.")
    ordens = [item.get("ordem") for item in itens]
    if any(
        isinstance(ordem, bool)
        or not isinstance(ordem, int)
        or not 1 <= ordem <= 32767
        for ordem in ordens
    ) or sorted(ordens) != list(range(1, len(itens) + 1)):
        raise ErroFonteGuia(
            f"{contexto}: ordens devem ser inteiros contiguos de 1 a {len(itens)}."
        )


def validar_estrutura_2d2a(documento):
    campos_raiz = {
        "contrato",
        "idioma_canonico",
        "versao",
        "guia",
        "sha256_guia",
        "contagens",
    }
    _objeto(documento, campos_raiz, campos_raiz, "raiz")
    if documento["contrato"] != CONTRATO:
        raise ErroFonteGuia(f"Contrato invalido; esperado {CONTRATO}.")
    if documento["idioma_canonico"] != "es":
        raise ErroFonteGuia("raiz: idioma_canonico deve permanecer es.")
    versao = documento["versao"]
    campos_versao = {"codigo", "fonte", "sha256_fonte"}
    _objeto(versao, campos_versao, campos_versao, "versao")
    _codigo(versao, "versao", limite=100)
    # O prefixo operacional usado no lote tambem deve caber em fonte (500).
    _texto(versao, "fonte", "versao", limite=500 - len("guia-fase2d2/"))
    sha_fonte = _texto(versao, "sha256_fonte", "versao").lower()
    if len(sha_fonte) != 64 or any(c not in "0123456789abcdef" for c in sha_fonte):
        raise ErroFonteGuia("versao: sha256_fonte invalido.")
    if sha_fonte != HASH_FONTE_OFICIAL:
        raise ErroFonteGuia("Hash de proveniencia da fonte divergente.")
    guia = documento["guia"]
    campos_guia = {"eixos", "setores", "referencias"}
    _objeto(guia, campos_guia, campos_guia, "guia")
    hash_calculado = hashlib.sha256(
        json.dumps(guia, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if documento.get("sha256_guia") != hash_calculado:
        raise ErroFonteGuia("Hash canonico declarado do Guia divergente.")

    codigos = {nome: set() for nome in ("eixos", "subeixos", "setores", "subareas", "perguntas", "referencias")}
    totais = {nome: 0 for nome in (*codigos, "ocorrencias_referencias")}
    referencias_usadas = []

    def registrar(tipo, item, contexto):
        codigo = _codigo(item, contexto)
        if codigo in codigos[tipo]:
            raise ErroFonteGuia(f"{contexto}: codigo duplicado {codigo}.")
        codigos[tipo].add(codigo)
        totais[tipo] += 1

    def perguntas(itens, contexto):
        for item in itens:
            campos = {"codigo", "texto_es", "tipo_auditoria", "ordem"}
            _objeto(item, campos, campos, contexto)
            registrar("perguntas", item, contexto)
            _texto(item, "texto_es", contexto)
            if item.get("tipo_auditoria") not in ("cumplimiento", "gestion"):
                raise ErroFonteGuia(f"{contexto}: tipo_auditoria invalido.")
        for tipo in ("cumplimiento", "gestion"):
            _validar_ordem(
                [item for item in itens if item["tipo_auditoria"] == tipo],
                f"{contexto} ({tipo})",
            )

    eixos = _lista(guia, "eixos", "guia")
    _validar_ordem(eixos, "eixos")
    for eixo in eixos:
        campos = {"codigo", "nome_es", "ordem", "perguntas", "subeixos"}
        _objeto(eixo, campos, campos, "eixo")
        registrar("eixos", eixo, "eixo")
        _texto(eixo, "nome_es", "eixo", limite=220)
        perguntas(_lista(eixo, "perguntas", "eixo"), "perguntas de eixo")
        subeixos = _lista(eixo, "subeixos", "eixo")
        _validar_ordem(subeixos, "subeixos")
        for subeixo in subeixos:
            campos = {"codigo", "nome_es", "ordem", "perguntas"}
            _objeto(subeixo, campos, campos, "subeixo")
            registrar("subeixos", subeixo, "subeixo")
            _texto(subeixo, "nome_es", "subeixo", limite=220)
            perguntas(_lista(subeixo, "perguntas", "subeixo"), "perguntas de subeixo")

    setores = _lista(guia, "setores", "guia")
    _validar_ordem(setores, "setores")
    for setor in setores:
        campos = {"codigo", "nome_es", "ordem", "subareas"}
        _objeto(setor, campos, campos, "setor")
        registrar("setores", setor, "setor")
        _texto(setor, "nome_es", "setor", limite=220)
        subareas = _lista(setor, "subareas", "setor")
        _validar_ordem(subareas, "subareas")
        for subarea in subareas:
            campos = {"codigo", "nome_es", "ordem", "perguntas", "referencias"}
            _objeto(subarea, campos, campos, "subarea")
            registrar("subareas", subarea, "subarea")
            _texto(subarea, "nome_es", "subarea", limite=220)
            perguntas(_lista(subarea, "perguntas", "subarea"), "perguntas de subarea")
            ocorrencias = _lista(subarea, "referencias", "subarea")
            _validar_ordem(ocorrencias, "referencias da subarea")
            for ocorrencia in ocorrencias:
                campos = {"codigo_referencia", "ordem"}
                _objeto(ocorrencia, campos, campos, "ocorrencia")
                referencias_usadas.append(_texto(ocorrencia, "codigo_referencia", "ocorrencia"))
                totais["ocorrencias_referencias"] += 1

    referencias = _lista(guia, "referencias", "guia")
    for referencia in referencias:
        campos = {"codigo", "citacao_es"}
        _objeto(referencia, campos, campos, "referencia")
        registrar("referencias", referencia, "referencia")
        _texto(referencia, "citacao_es", "referencia")
    inexistentes = sorted(set(referencias_usadas) - codigos["referencias"])
    if inexistentes:
        raise ErroFonteGuia(f"Ocorrencia referencia codigo inexistente: {inexistentes[0]}.")
    contagens = documento["contagens"]
    _objeto(contagens, totais, totais, "contagens")
    if any(
        isinstance(valor, bool) or not isinstance(valor, int) or valor < 0
        for valor in contagens.values()
    ):
        raise ErroFonteGuia("Contagens devem ser inteiros nao negativos.")
    if contagens != totais:
        raise ErroFonteGuia("Contagens declaradas ou realizadas divergentes.")
    return {"documento": documento, "guia": guia, "versao": versao, "contagens": totais, "sha256_guia": hash_calculado}


def _ordenar_por_ordem(itens):
    return sorted(itens, key=lambda item: item["ordem"])


def _textos_por_tipo(perguntas, tipo):
    return [
        pergunta["texto_es"]
        for pergunta in _ordenar_por_ordem(
            [item for item in perguntas if item["tipo_auditoria"] == tipo]
        )
    ]


def _reconstruir_guia_canonico(guia):
    referencias = {
        referencia["codigo"]: referencia["citacao_es"]
        for referencia in guia["referencias"]
    }
    transversales = []
    for eixo in _ordenar_por_ordem(guia["eixos"]):
        subejes = []
        for subeixo in _ordenar_por_ordem(eixo["subeixos"]):
            subejes.append(
                {
                    "nombre": subeixo["nome_es"],
                    "cumplimiento": _textos_por_tipo(
                        subeixo["perguntas"], "cumplimiento"
                    ),
                    "gestion": _textos_por_tipo(subeixo["perguntas"], "gestion"),
                }
            )
        transversales.append(
            {
                "nombre": eixo["nome_es"],
                "pregCumpl": _textos_por_tipo(
                    eixo["perguntas"], "cumplimiento"
                ),
                "pregGest": _textos_por_tipo(eixo["perguntas"], "gestion"),
                "subejes": subejes,
            }
        )

    sectores = []
    for setor in _ordenar_por_ordem(guia["setores"]):
        subareas = []
        for subarea in _ordenar_por_ordem(setor["subareas"]):
            subareas.append(
                {
                    "nombre": subarea["nome_es"],
                    "cumplimiento": _textos_por_tipo(
                        subarea["perguntas"], "cumplimiento"
                    ),
                    "gestion": _textos_por_tipo(
                        subarea["perguntas"], "gestion"
                    ),
                    "referencias": [
                        referencias[ocorrencia["codigo_referencia"]]
                        for ocorrencia in _ordenar_por_ordem(
                            subarea["referencias"]
                        )
                    ],
                }
            )
        sectores.append({"sector": setor["nome_es"], "subareas": subareas})
    return {"transversales": transversales, "sectores": sectores}


def _calcular_sha256_guia_canonico(guia):
    serializado = json.dumps(
        _reconstruir_guia_canonico(guia),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def validar_equivalencia_2d2b(resultado):
    """Reconstrói e confirma o conteúdo espanhol institucional auditado."""
    hash_canonico = _calcular_sha256_guia_canonico(resultado["guia"])
    if hash_canonico != HASH_CANONICO_GUIA:
        raise ErroFonteGuia("Hash canonico do Guia divergente.")
    if resultado["contagens"] != CONTAGENS_OFICIAIS:
        raise ErroFonteGuia("Contagens declaradas ou realizadas divergentes.")
    return {**resultado, "sha256_guia_canonico": hash_canonico}


def validar_documento(documento):
    """Executa, em ordem, o contrato 2D.2A e a equivalência canônica 2D.2B."""
    return validar_equivalencia_2d2b(validar_estrutura_2d2a(documento))


def ler_e_validar(caminho):
    caminho = Path(caminho).expanduser().resolve()
    if not caminho.is_file():
        raise ErroFonteGuia("Arquivo de fonte inexistente ou nao regular.")
    if caminho.stat().st_size > 20 * 1024 * 1024:
        raise ErroFonteGuia("Arquivo de fonte excede o limite operacional de 20 MiB.")
    try:
        documento = json.loads(caminho.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErroFonteGuia("Arquivo deve conter JSON UTF-8 valido.") from exc
    return validar_documento(documento)


class Command(BaseCommand):
    help = "Valida a fonte institucional codificada da Fase 2D.2 sem escrever no banco."

    def add_arguments(self, parser):
        parser.add_argument("--arquivo", required=True)

    def handle(self, *args, **options):
        try:
            resultado = ler_e_validar(options["arquivo"])
        except ErroFonteGuia as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"FONTE VALIDA: {resultado['contagens']['perguntas']} perguntas; SHA-256 {resultado['sha256_guia']}."))
