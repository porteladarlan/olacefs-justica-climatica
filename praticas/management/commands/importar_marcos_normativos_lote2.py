import json
import re
import unicodedata
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db import transaction

from praticas.models import NormaInternacional, NormaInternacionalPais, Pais


FONTE_PADRAO = Path(__file__).resolve().parents[2] / "data" / "marcos_normativos_lote2.json"
URL_MARKDOWN = re.compile(r"^\[[^\]]+\]\([^)]+\)$")
VALIDAR_URL_HTTP = URLValidator(schemes=["http", "https"])


def normalizar(texto):
    return (
        unicodedata.normalize("NFKD", texto or "")
        .encode("ascii", "ignore")
        .decode("ascii")
        .casefold()
        .strip()
    )


def validar_url_http_pura(valor, campo, indice):
    if valor == "":
        return
    if not isinstance(valor, str):
        raise CommandError(f"{campo} inválida no marco {indice}.")
    if valor != valor.strip() or URL_MARKDOWN.fullmatch(valor):
        raise CommandError(
            f"{campo} deve conter somente uma URL HTTP/HTTPS pura no marco {indice}."
        )
    if not valor.startswith(("http://", "https://")):
        raise CommandError(
            f"{campo} deve usar o esquema HTTP ou HTTPS no marco {indice}."
        )
    try:
        VALIDAR_URL_HTTP(valor)
    except ValidationError as exc:
        raise CommandError(f"{campo} inválida no marco {indice}.") from exc


ALIASES_EXISTENTES = {
    "acuerdo de escazu acuerdo regional sobre el acceso a la informacion, la participacion publica y el acceso a la justicia en asuntos ambientales en america latina y el caribe": "Acordo de Escazú",
    "acuerdo de paris": "Acordo de Paris",
    "agenda 2030 para el desarrollo sostenible objetivos de desarrollo sostenible": "Agenda 2030 — ODS 13",
    "marco de sendai para la reduccion del riesgo de desastres 2015-2030": "Marco de Sendai para Redução do Risco de Desastres",
}


class Command(BaseCommand):
    help = "Importa de forma idempotente os 34 marcos normativos do Lote 2."

    def add_arguments(self, parser):
        parser.add_argument("--fonte", type=Path, default=FONTE_PADRAO)
        parser.add_argument("--validar", action="store_true")

    def handle(self, *args, **options):
        fonte = options["fonte"].resolve()
        try:
            dados = json.loads(fonte.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Fonte inválida: {exc}") from exc

        marcos = dados.get("marcos")
        if not isinstance(marcos, list) or dados.get("quantidade") != 34 or len(marcos) != 34:
            raise CommandError("A fonte deve conter exatamente 34 marcos.")

        self._validar(marcos)
        if options["validar"]:
            self.stdout.write(self.style.SUCCESS("Fonte válida: 34 marcos."))
            return

        with transaction.atomic():
            resultado = self._importar(marcos)

        self.stdout.write(
            self.style.SUCCESS(
                "Carga concluída: {criados} criados, {atualizados} atualizados, "
                "{vinculos} vínculos de países/status.".format(**resultado)
            )
        )

    def _validar(self, marcos):
        obrigatorios = {
            "nome_es",
            "ano",
            "ano_texto",
            "natureza_juridica",
            "setores_aplicaveis",
            "cobertura_paises_es",
            "introducao_es",
            "paises_status",
        }
        nomes = set()
        for indice, marco in enumerate(marcos, start=1):
            ausentes = obrigatorios - marco.keys()
            if ausentes:
                raise CommandError(
                    f"Marco {indice} sem campos obrigatórios: {sorted(ausentes)}"
                )
            nome = normalizar(marco["nome_es"])
            if not nome or nome in nomes:
                raise CommandError(f"Nome ausente ou duplicado no marco {indice}.")
            nomes.add(nome)
            validar_url_http_pura(
                marco.get("fonte_oficial_url", ""), "fonte_oficial_url", indice
            )
            validar_url_http_pura(
                marco.get("ficha_tecnica_url", ""), "ficha_tecnica_url", indice
            )
            if marco["natureza_juridica"] not in {"Vinculante", "No vinculante"}:
                raise CommandError(
                    f"Natureza jurídica não reconhecida na fonte: {marco['natureza_juridica']}"
                )
            if not isinstance(marco["setores_aplicaveis"], list):
                raise CommandError(f"Setores inválidos no marco {indice}.")
            for vinculo in marco["paises_status"]:
                if not vinculo.get("pais") or not vinculo.get("status"):
                    raise CommandError(f"País/status incompleto no marco {indice}.")

        nomes_paises = {
            normalizar(nome)
            for nomes in Pais.objects.values_list("nome", "nome_es", "nome_en")
            for nome in nomes
            if nome
        }
        informados = {
            normalizar(vinculo["pais"])
            for marco in marcos
            for vinculo in marco["paises_status"]
        }
        desconhecidos = sorted(informados - nomes_paises)
        if desconhecidos:
            raise CommandError(f"Países da fonte não cadastrados: {desconhecidos}")

    def _importar(self, marcos):
        paises = {}
        for pais in Pais.objects.all():
            for nome in (pais.nome, pais.nome_es, pais.nome_en):
                if nome:
                    paises[normalizar(nome)] = pais
        existentes = {
            normalizar(norma.nome): norma
            for norma in NormaInternacional.objects.all()
        }
        criados = atualizados = vinculos = 0

        for marco in marcos:
            nome_es = marco["nome_es"]
            alias = ALIASES_EXISTENTES.get(normalizar(nome_es))
            norma = existentes.get(normalizar(alias or nome_es))
            if norma is None:
                norma = NormaInternacional(nome=nome_es)
                criados += 1
            else:
                atualizados += 1

            norma.nome_es = nome_es
            norma.ano = marco["ano"]
            norma.ano_texto = marco["ano_texto"]
            norma.natureza_juridica = marco["natureza_juridica"]
            norma.setores_aplicaveis = ", ".join(marco["setores_aplicaveis"])
            norma.cobertura_paises_es = marco["cobertura_paises_es"]
            norma.resumo_es = marco["introducao_es"]
            norma.url_referencia = marco.get("fonte_oficial_url", "")
            norma.ficha_tecnica_url = marco.get("ficha_tecnica_url", "")
            norma.save()
            existentes[normalizar(norma.nome)] = norma

            ids_presentes = []
            for item in marco["paises_status"]:
                pais = paises[normalizar(item["pais"])]
                relacao, _ = NormaInternacionalPais.objects.update_or_create(
                    norma=norma,
                    pais=pais,
                    defaults={"status": item["status"]},
                )
                ids_presentes.append(relacao.pk)
                vinculos += 1
            norma.paises_status.exclude(pk__in=ids_presentes).delete()

        return {
            "criados": criados,
            "atualizados": atualizados,
            "vinculos": vinculos,
        }
