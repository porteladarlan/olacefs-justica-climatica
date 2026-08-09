import copy
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from .management.commands.validar_fonte_guia_fase2d2 import (
    ErroFonteGuia,
    _calcular_sha256_guia_canonico,
    ler_e_validar,
    validar_documento,
    validar_equivalencia_2d2b,
    validar_estrutura_2d2a,
)
from .tests_fase2d2_importador_guia import fonte_sintetica


class ValidadorFonteGuiaFase2D2Tests(SimpleTestCase):
    def test_camadas_2d2a_e_2d2b_preservam_canonicalizacao(self):
        documento, _ = fonte_sintetica()

        with (
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                "a" * 64,
            ),
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                _calcular_sha256_guia_canonico(documento["guia"]),
            ),
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
                documento["contagens"],
            ),
        ):
            estrutura = validar_estrutura_2d2a(documento)
            resultado = validar_equivalencia_2d2b(estrutura)

        canonico = json.dumps(
            documento["guia"], ensure_ascii=False, separators=(",", ":")
        )
        self.assertEqual(
            resultado["sha256_guia"],
            hashlib.sha256(canonico.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            resultado["sha256_guia_canonico"],
            _calcular_sha256_guia_canonico(documento["guia"]),
        )

    def test_2d2a_rejeita_contrato_proveniencia_e_hash_declarado(self):
        for alterar, mensagem in (
            (lambda d: d.update(contrato="contrato-desconhecido"), "Contrato invalido"),
            (
                lambda d: d["versao"].update(sha256_fonte="b" * 64),
                "Hash de proveniencia",
            ),
            (lambda d: d.update(sha256_guia="0" * 64), "Hash canonico declarado"),
        ):
            documento, _ = fonte_sintetica()
            alterar(documento)
            with self.assertRaisesRegex(ErroFonteGuia, mensagem):
                with patch(
                    "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                    "a" * 64,
                ):
                    validar_estrutura_2d2a(documento)

    def test_2d2a_rejeita_campos_idioma_tipos_e_ordens_invalidos(self):
        casos = (
            (lambda d: d.update(campo_extra=True), "campos desconhecidos"),
            (
                lambda d: d["versao"].update(campo_extra=True),
                "campos desconhecidos",
            ),
            (lambda d: d.update(idioma_canonico="pt"), "idioma_canonico"),
            (
                lambda d: d["guia"]["eixos"][0].pop("codigo"),
                "campos obrigatorios",
            ),
            (
                lambda d: d["guia"]["eixos"][0].update(ordem=True),
                "ordens devem ser inteiros contiguos",
            ),
            (
                lambda d: d["guia"]["setores"][0]["subareas"][1].update(
                    ordem=3
                ),
                "ordens devem ser inteiros contiguos",
            ),
            (
                lambda d: d["guia"]["eixos"][0].update(campo_extra=True),
                "campos desconhecidos",
            ),
            (
                lambda d: d["guia"]["eixos"][0].update(perguntas=[None]),
                "deve ser um objeto",
            ),
        )
        for alterar, mensagem in casos:
            with self.subTest(mensagem=mensagem):
                documento, _ = fonte_sintetica()
                alterar(documento)
                documento["sha256_guia"] = hashlib.sha256(
                    json.dumps(
                        documento["guia"],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                with (
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                        "a" * 64,
                    ),
                    self.assertRaisesRegex(ErroFonteGuia, mensagem),
                ):
                    validar_estrutura_2d2a(documento)

    def test_2d2b_bloqueia_texto_ordem_tipo_e_referencia_alterados(self):
        documento_original, _ = fonte_sintetica()
        hash_canonico_oficial = _calcular_sha256_guia_canonico(
            documento_original["guia"]
        )
        mutacoes = (
            lambda d: d["guia"]["eixos"][0]["perguntas"][0].update(
                texto_es="Texto alterado"
            ),
            lambda d: (
                d["guia"]["setores"][0]["subareas"][0].update(ordem=2),
                d["guia"]["setores"][0]["subareas"][1].update(ordem=1),
            ),
            lambda d: d["guia"]["eixos"][0]["perguntas"][0].update(
                tipo_auditoria="gestion"
            ),
            lambda d: d["guia"]["referencias"][0].update(
                citacao_es="Referencia alterada"
            ),
        )
        for alterar in mutacoes:
            with self.subTest(alterar=alterar):
                documento = copy.deepcopy(documento_original)
                alterar(documento)
                documento["sha256_guia"] = hashlib.sha256(
                    json.dumps(
                        documento["guia"],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                with (
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                        "a" * 64,
                    ),
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                        hash_canonico_oficial,
                    ),
                    patch(
                        "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
                        documento_original["contagens"],
                    ),
                    self.assertRaisesRegex(ErroFonteGuia, "Hash canonico"),
                ):
                    validar_documento(documento)

    def test_2d2b_ordena_listas_semanticamente_por_ordem(self):
        documento, _ = fonte_sintetica()
        hash_canonico_oficial = _calcular_sha256_guia_canonico(
            documento["guia"]
        )
        documento["guia"]["setores"][0]["subareas"].reverse()
        documento["sha256_guia"] = hashlib.sha256(
            json.dumps(
                documento["guia"], ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        with (
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                "a" * 64,
            ),
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                hash_canonico_oficial,
            ),
            patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
                documento["contagens"],
            ),
        ):
            resultado = validar_documento(documento)
        self.assertEqual(
            resultado["sha256_guia_canonico"],
            hash_canonico_oficial,
        )

    def test_2d2b_nao_flexibiliza_hash_e_contagens_de_producao(self):
        documento, _ = fonte_sintetica()
        with patch(
            "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
            "a" * 64,
        ):
            estrutura = validar_estrutura_2d2a(documento)

        with self.assertRaisesRegex(ErroFonteGuia, "Hash canonico"):
            validar_equivalencia_2d2b(estrutura)
        with self.assertRaisesRegex(ErroFonteGuia, "Contagens"):
            with patch(
                "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                _calcular_sha256_guia_canonico(documento["guia"]),
            ):
                validar_equivalencia_2d2b(estrutura)

    def test_rejeita_contagem_real_divergente_da_declarada(self):
        documento, _ = fonte_sintetica()
        documento["contagens"]["perguntas"] += 1

        with self.assertRaisesRegex(ErroFonteGuia, "Contagens"):
            with (
                patch(
                    "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_CANONICO_GUIA",
                    _calcular_sha256_guia_canonico(documento["guia"]),
                ),
                patch(
                    "praticas.management.commands.validar_fonte_guia_fase2d2.CONTAGENS_OFICIAIS",
                    documento["contagens"],
                ),
                patch(
                    "praticas.management.commands.validar_fonte_guia_fase2d2.HASH_FONTE_OFICIAL",
                    "a" * 64,
                ),
            ):
                validar_documento(documento)

    def test_leitura_rejeita_arquivo_inexistente_json_invalido_e_utf8_invalido(self):
        with tempfile.TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            with self.assertRaisesRegex(ErroFonteGuia, "inexistente"):
                ler_e_validar(raiz / "ausente.json")

            invalido = raiz / "invalido.json"
            invalido.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ErroFonteGuia, "JSON UTF-8 valido"):
                ler_e_validar(invalido)

            nao_utf8 = raiz / "nao-utf8.json"
            nao_utf8.write_bytes(b"\xff")
            with self.assertRaisesRegex(ErroFonteGuia, "JSON UTF-8 valido"):
                ler_e_validar(nao_utf8)

    def test_command_permanece_somente_validacao_sem_escrita(self):
        documento, _ = fonte_sintetica()
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "fonte.json"
            arquivo.write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(CommandError, "Hash de proveniencia"):
                call_command("validar_fonte_guia_fase2d2", arquivo=arquivo)
