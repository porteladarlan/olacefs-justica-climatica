import json
import hashlib
import tempfile
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.apps import apps as django_apps
from django.test import TransactionTestCase
from django.db import transaction

from .management.commands.importar_marcos_normativos_lote2 import Command
from .models import NormaInternacional, NormaInternacionalPais, Pais


FONTE = Path(__file__).resolve().parent / "data" / "marcos_normativos_trilingues_0023.json"


class Migration0023Tests(TransactionTestCase):
    reset_sequences = True

    def test_migration_em_banco_limpo_sem_normas_eh_noop(self):
        migration = import_module("praticas.migrations.0023_backfill_marcos_normativos_trilingues")
        migration.preencher_idiomas(django_apps, None)
        self.assertEqual(NormaInternacional.objects.count(), 0)
        self.assertEqual(NormaInternacionalPais.objects.count(), 0)

    def test_migration_falha_com_banco_parcial(self):
        migration = import_module("praticas.migrations.0023_backfill_marcos_normativos_trilingues")
        fonte = json.loads(FONTE.read_text(encoding="utf-8"))["marcos"]
        NormaInternacional.objects.create(nome=fonte[0]["nome_es"])
        for indice, item in enumerate(fonte[0]["paises_status"], 1):
            Pais.objects.create(nome=item["pais"], nome_es=item["pais"], sigla=f"P{indice:02d}")
        with self.assertRaisesRegex(RuntimeError, "Marco não encontrado"):
            migration.preencher_idiomas(django_apps, None)

    def test_backfill_real_trilingue_preserva_registros_e_eh_equivalente_ao_importador(self):
        executor = MigrationExecutor(connection)
        executor.migrate([("praticas", "0022_tema_comunidades_rurais")])
        apps_0022 = executor.loader.project_state([("praticas", "0022_tema_comunidades_rurais")]).apps
        Pais = apps_0022.get_model("praticas", "Pais")
        Norma = apps_0022.get_model("praticas", "NormaInternacional")
        Vinculo = apps_0022.get_model("praticas", "NormaInternacionalPais")
        fonte = json.loads(FONTE.read_text(encoding="utf-8"))["marcos"]
        paises = {}
        for indice, nome in enumerate(sorted({item["pais"] for marco in fonte for item in marco["paises_status"]}), 1):
            paises[nome] = Pais.objects.create(nome=nome, nome_es=nome, sigla=f"T{indice:02d}")
        normas = [Norma.objects.create(nome=marco["nome_es"]) for marco in fonte]
        ids_normas = [norma.pk for norma in normas]
        primeiro_antes = normas[0]
        primeiro_antes.ano = 1901
        primeiro_antes.ano_texto = "ano legado personalizado"
        primeiro_antes.url_referencia = "https://legacy.example/source"
        primeiro_antes.ficha_tecnica_url = "https://legacy.example/ficha"
        primeiro_antes.ficha_tecnica = "marcos_normativos/fichas/legado.pdf"
        primeiro_antes.save()
        pais_extra = Pais.objects.create(nome="País administrativo extra", nome_es="País administrativo extra", sigla="EXT")
        for norma, marco in zip(normas, fonte):
            for item in marco["paises_status"]:
                Vinculo.objects.create(norma_id=norma.pk, pais_id=paises[item["pais"]].pk, status=item["status_es"])
        Vinculo.objects.create(norma_id=normas[0].pk, pais_id=pais_extra.pk, status="Vínculo adicional")
        self.assertEqual(Vinculo.objects.count(), 254)

        executor = MigrationExecutor(connection)
        executor.migrate([("praticas", "0023_backfill_marcos_normativos_trilingues")])
        self.assertEqual(NormaInternacional.objects.count(), 34)
        expected_pairs = {
            (norma.pk, paises[item["pais"]].pk)
            for norma, marco in zip(normas, fonte)
            for item in marco["paises_status"]
        }
        actual_pairs = set(NormaInternacionalPais.objects.values_list("norma_id", "pais_id"))
        self.assertEqual(len(expected_pairs), 253)
        self.assertNotIn((normas[0].pk, pais_extra.pk), expected_pairs)
        self.assertTrue(expected_pairs <= actual_pairs)
        self.assertEqual(NormaInternacionalPais.objects.count(), 254)
        self.assertEqual(list(NormaInternacional.objects.values_list("pk", flat=True).order_by("pk")), ids_normas)

        primeiro = NormaInternacional.objects.get(pk=ids_normas[0])
        self.assertEqual(primeiro.nome, fonte[0]["nome_pt"])
        self.assertEqual(primeiro.nome_es, fonte[0]["nome_es"])
        self.assertEqual(primeiro.nome_en, fonte[0]["nome_en"])
        self.assertNotEqual(primeiro.nome, primeiro.nome_es)
        self.assertNotEqual(primeiro.nome_es, primeiro.nome_en)
        self.assertEqual(primeiro.resumo, fonte[0]["introducao_pt"])
        self.assertEqual(primeiro.resumo_es, fonte[0]["introducao_es"])
        self.assertEqual(primeiro.resumo_en, fonte[0]["introducao_en"])
        self.assertEqual(primeiro.ano, 1901)
        self.assertEqual(primeiro.ano_texto, "ano legado personalizado")
        self.assertEqual(primeiro.url_referencia, "https://legacy.example/source")
        self.assertEqual(primeiro.ficha_tecnica_url, "https://legacy.example/ficha")
        self.assertEqual(primeiro.ficha_tecnica, "marcos_normativos/fichas/legado.pdf")
        status = NormaInternacionalPais.objects.filter(norma_id=ids_normas[0]).order_by("pais_id").first()
        esperado = fonte[0]["paises_status"][0]
        self.assertEqual(status.status, esperado["status_pt"])
        self.assertEqual(status.status_es, esperado["status_es"])
        self.assertEqual(status.status_en, esperado["status_en"])
        self.assertTrue(NormaInternacionalPais.objects.filter(norma_id=ids_normas[0], pais__sigla="EXT").exists())

        Command()._importar([Command()._normalizar_marco(marco) for marco in fonte])
        self.assertEqual(NormaInternacional.objects.count(), 34)
        self.assertEqual(NormaInternacionalPais.objects.count(), 253)
        for marco, pk in zip(fonte, ids_normas):
            norma = NormaInternacional.objects.get(pk=pk)
            self.assertEqual((norma.nome, norma.nome_es, norma.nome_en), (marco["nome_pt"], marco["nome_es"], marco["nome_en"]))
            self.assertEqual((norma.resumo, norma.resumo_es, norma.resumo_en), (marco["introducao_pt"], marco["introducao_es"], marco["introducao_en"]))
            self.assertEqual((norma.natureza_juridica, norma.natureza_juridica_es, norma.natureza_juridica_en), (marco["natureza_juridica_pt"], marco["natureza_juridica_es"], marco["natureza_juridica_en"]))
            self.assertEqual(norma.setores_aplicaveis, ", ".join(item["pt"] for item in marco["setores_aplicaveis"]))
            self.assertEqual(norma.setores_aplicaveis_es, ", ".join(item["es"] for item in marco["setores_aplicaveis"]))
            self.assertEqual(norma.setores_aplicaveis_en, ", ".join(item["en"] for item in marco["setores_aplicaveis"]))

    def test_fontes_operacional_e_congelada_sao_equivalentes(self):
        congelada = json.loads(FONTE.read_text(encoding="utf-8"))
        operacional = json.loads((FONTE.parent / "marcos_normativos_lote2.json").read_text(encoding="utf-8"))
        self.assertEqual(operacional["marcos"], congelada["marcos"])

    def test_migration_falha_se_marco_pais_ou_hash_nao_bater(self):
        migration = import_module("praticas.migrations.0023_backfill_marcos_normativos_trilingues")
        fonte = json.loads(FONTE.read_text(encoding="utf-8"))
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json", delete=False) as arquivo:
            alterada = json.loads(json.dumps(fonte))
            alterada["marcos"][0]["id_referencia"] = "marco-inexistente"
            json.dump(alterada, arquivo, ensure_ascii=False)
            arquivo.flush()
            arquivo.close()
            with patch.object(migration, "FONTE", Path(arquivo.name)), patch.object(migration, "HASH_FONTE", "0" * 64):
                with self.assertRaises(RuntimeError):
                    migration.carregar_fonte()

        for marco in fonte["marcos"][1:]:
            NormaInternacional.objects.create(nome=marco["nome_es"])
        alterada = json.loads(json.dumps(fonte))
        alterada["marcos"][0]["nome_pt"] = "Marco ausente"
        alterada["marcos"][0]["nome_es"] = "Marco ausente ES"
        alterada["marcos"][0]["nome_en"] = "Missing framework"
        conteudo = json.dumps(alterada, ensure_ascii=False).encode("utf-8")
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as arquivo:
            arquivo.write(conteudo)
            arquivo.flush()
            arquivo.close()
            with patch.object(migration, "FONTE", Path(arquivo.name)), patch.object(migration, "HASH_FONTE", hashlib.sha256(conteudo).hexdigest()):
                with self.assertRaisesRegex(RuntimeError, "Marco não encontrado"):
                    migration.preencher_idiomas(django_apps, None)

        NormaInternacional.objects.all().delete()
        for marco in fonte["marcos"]:
            NormaInternacional.objects.create(nome=marco["nome_es"])
        nomes_paises = sorted({item["pais"] for marco in fonte["marcos"] for item in marco["paises_status"]})
        for indice, nome in enumerate(nomes_paises[1:], 1):
            Pais.objects.create(nome=nome, nome_es=nome, sigla=f"Q{indice:02d}")
        alterada = json.loads(json.dumps(fonte))
        alterada["marcos"][0]["paises_status"][0]["pais"] = "País inexistente"
        conteudo = json.dumps(alterada, ensure_ascii=False).encode("utf-8")
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as arquivo:
            arquivo.write(conteudo)
            arquivo.flush()
            arquivo.close()
            with patch.object(migration, "FONTE", Path(arquivo.name)), patch.object(migration, "HASH_FONTE", hashlib.sha256(conteudo).hexdigest()):
                with self.assertRaisesRegex(RuntimeError, "País não encontrado"):
                    with transaction.atomic():
                        migration.preencher_idiomas(django_apps, None)
