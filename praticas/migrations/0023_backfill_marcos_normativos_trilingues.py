import json
import hashlib
import unicodedata
from pathlib import Path

from django.db import migrations


FONTE = Path(__file__).resolve().parents[1] / "data" / "marcos_normativos_trilingues_0023.json"
HASH_FONTE = "bc4a9529928acb0f88c04ff42b202df382c145016fcad3ef2635a603cf61f392"

ALIASES_EXISTENTES = {
    "acuerdo-de-escazu-acuerdo-regional-sobre-el-acceso-a-la-informacion-la-participacion-publica-y-el-acceso-a-la-justicia-en-asuntos-ambientales-en-america-latina-y-el-caribe": "Acordo de Escazú",
    "acuerdo-de-paris": "Acordo de Paris",
    "agenda-2030-para-el-desarrollo-sostenible-objetivos-de-desarrollo-sostenible": "Agenda 2030 — ODS 13",
    "marco-de-sendai-para-la-reduccion-del-riesgo-de-desastres-2015-2030": "Marco de Sendai para Redução do Risco de Desastres",
}


def normalizar(valor):
    return unicodedata.normalize("NFKD", valor or "").encode("ascii", "ignore").decode("ascii").casefold().strip()


def carregar_fonte():
    conteudo = FONTE.read_bytes()
    if hashlib.sha256(conteudo).hexdigest() != HASH_FONTE:
        raise RuntimeError("A fonte congelada da migration 0023 foi alterada.")
    dados = json.loads(conteudo.decode("utf-8"))
    marcos = dados["marcos"]
    if dados.get("quantidade") != 34 or len(marcos) != 34:
        raise RuntimeError("A fonte 0023 deve conter exatamente 34 marcos.")
    return marcos


def setores(marco, idioma):
    valores = marco["setores_aplicaveis"]
    if isinstance(valores, list):
        return ", ".join(item[idioma] for item in valores)
    return valores


def encontrar_norma(Norma, marco, usados):
    candidatos = [marco["nome_pt"], marco["nome_es"], marco["nome_en"]]
    alias = ALIASES_EXISTENTES.get(marco["id_referencia"])
    if alias:
        candidatos.append(alias)
    normalizados = {normalizar(candidato) for candidato in candidatos}
    for norma in Norma.objects.all().order_by("pk"):
        if norma.pk in usados:
            continue
        if any(normalizar(valor) in normalizados for valor in (norma.nome, norma.nome_es, norma.nome_en)):
            return norma
    return None


def preencher_idiomas(apps, schema_editor):
    Norma = apps.get_model("praticas", "NormaInternacional")
    Vinculo = apps.get_model("praticas", "NormaInternacionalPais")
    Pais = apps.get_model("praticas", "Pais")
    marcos = carregar_fonte()
    vinculos_fonte = sum(len(marco["paises_status"]) for marco in marcos)
    ids = [marco.get("id_referencia") for marco in marcos]
    if len(ids) != 34 or len(set(ids)) != 34 or any(not identificador for identificador in ids):
        raise RuntimeError("A fonte 0023 possui id_referencia inválido ou duplicado.")
    if vinculos_fonte != 253:
        raise RuntimeError(f"A fonte 0023 possui {vinculos_fonte} vínculos; esperados 253.")
    if not Norma.objects.exists():
        return
    paises = {}
    for pais in Pais.objects.all():
        for nome in (pais.nome, pais.nome_es, pais.nome_en):
            if nome:
                paises[normalizar(nome)] = pais

    usados = set()
    for marco in marcos:
        norma = encontrar_norma(Norma, marco, usados)
        if norma is None:
            raise RuntimeError(
                "Marco não encontrado: {id_referencia}; candidatos: {candidatos}".format(
                    id_referencia=marco["id_referencia"],
                    candidatos=[marco["nome_pt"], marco["nome_es"], marco["nome_en"]],
                )
            )
        usados.add(norma.pk)
        Norma.objects.filter(pk=norma.pk).update(
            nome=marco["nome_pt"], nome_es=marco["nome_es"], nome_en=marco["nome_en"],
            resumo=marco["introducao_pt"], resumo_es=marco["introducao_es"], resumo_en=marco["introducao_en"],
            natureza_juridica=marco["natureza_juridica_pt"], natureza_juridica_es=marco["natureza_juridica_es"], natureza_juridica_en=marco["natureza_juridica_en"],
            setores_aplicaveis=setores(marco, "pt"), setores_aplicaveis_es=setores(marco, "es"), setores_aplicaveis_en=setores(marco, "en"),
            cobertura_paises=marco["cobertura_paises_pt"], cobertura_paises_es=marco["cobertura_paises_es"], cobertura_paises_en=marco["cobertura_paises_en"],
        )
        for item in marco["paises_status"]:
            pais = paises.get(normalizar(item["pais"]))
            if pais is None:
                raise RuntimeError(
                    "País não encontrado para o marco {id_referencia}: {pais}".format(
                        id_referencia=marco["id_referencia"], pais=item["pais"]
                    )
                )
            vinculo, _ = Vinculo.objects.update_or_create(
                norma_id=norma.pk, pais_id=pais.pk,
                defaults={"status": item["status_pt"], "status_es": item["status_es"], "status_en": item["status_en"]},
            )
    if len(usados) != 34:
        raise RuntimeError(f"Backfill incompleto: {len(usados)} de 34 marcos correlacionados.")


class Migration(migrations.Migration):
    dependencies = [("praticas", "0022_tema_comunidades_rurais")]
    operations = [migrations.RunPython(preencher_idiomas, migrations.RunPython.noop)]
