"""Provider boundary for automatic translation of free-text experience fields."""

import json
import logging
import os
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def _timeout():
    try:
        return max(1, float(os.environ.get("PJC_TRANSLATION_TIMEOUT", "8")))
    except ValueError:
        return 8.0


def _traduzir_lote(campos, idioma_origem, idioma_destino):
    endpoint = os.environ.get("PJC_TRANSLATION_ENDPOINT", "").strip()
    if not endpoint or not campos:
        if not endpoint and campos:
            logger.info("Automatic translation disabled: provider endpoint is not configured")
        return {}
    payload = json.dumps({
        "source": idioma_origem,
        "target": idioma_destino,
        "fields": campos,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("PJC_TRANSLATION_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(endpoint, data=payload, headers=headers, method="POST")
    with urlopen(request, timeout=_timeout()) as response:
        data = json.loads(response.read().decode("utf-8"))
    translations = data.get("translations") if isinstance(data, dict) else None
    if not isinstance(translations, dict):
        raise ValueError("translation provider returned an invalid translations object")
    return {
        campo: valor
        for campo, valor in translations.items()
        if campo in campos and isinstance(valor, str)
    }


def traduzir_texto(texto, idioma_origem, idioma_destino):
    if not texto or idioma_origem == idioma_destino:
        return texto or ""
    return _traduzir_lote({"text": texto}, idioma_origem, idioma_destino).get("text", "")


def traduzir_campos_experiencia(experiencia, campos, idioma_origem):
    """Translate only supplied free-text fields, preserving the source fields."""
    if idioma_origem not in {"pt", "es", "en"}:
        return {}
    traducoes = {}
    fontes = {}
    for campo in campos:
        campo_origem = campo if idioma_origem == "pt" else f"{campo}_{idioma_origem}"
        original = getattr(experiencia, campo_origem, "") or ""
        if original:
            fontes[campo] = original
    for destino in ("pt", "es", "en"):
        if destino == idioma_origem:
            continue
        try:
            resultado = _traduzir_lote(fontes, idioma_origem, destino)
        except Exception as exc:
            logger.warning("Automatic translation unavailable for target %s: %s", destino, exc.__class__.__name__)
            continue
        for campo, valor in resultado.items():
            campo_destino = campo if destino == "pt" else f"{campo}_{destino}"
            traducoes[campo_destino] = valor
    return traducoes
