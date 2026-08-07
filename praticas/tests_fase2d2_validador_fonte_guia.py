import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from praticas.management.commands.validar_fonte_guia_fase2d2 import (
    Command as ValidadorGuiaCommand,
)


class ValidadorFonteGuiaFase2D2Tests(SimpleTestCase):
    SHA_ARQUIVO = (
        "cd78b9beca799aa9c6976af825c314e57e4a1903bfa832ecec2fbc3d86b61c67"
    )
    SHA_GUIA = (
        "8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d"
    )

    def _distribuir(self, total, quantidade):
        base, resto = divmod(total, quantidade)
        return [
            base + (1 if indice < resto else 0)
            for indice in range(quantidade)
        ]

    def _perguntas(self, prefixo, tipo, quantidade):
        return [
            {
                "codigo": f"{prefixo}-{tipo}-{indice:03d}",
                "texto_es": (
                    f"Pregunta institucional de prueba "
                    f"{prefixo} {tipo} {indice}"
                ),
                "ordem": indice,
            }
            for indice in range(1, quantidade + 1)
        ]

    def _documento_valido(self):
        cumprimento_subeixos = self._distribuir(27, 8)
        gestao_subeixos = self._distribuir(27, 8)

        distribuicao_subeixos = [3, 3, 2]

        eixos = []
        indice_subeixo_global = 0

        for indice_eixo, qtd_subeixos in enumerate(
            distribuicao_subeixos,
            start=1,
        ):
            subeixos = []

            for ordem_subeixo in range(
                1,
                qtd_subeixos + 1,
            ):
                indice_distribuicao = indice_subeixo_global
                indice_subeixo_global += 1

                prefixo = (
                    f"subeixo-{indice_subeixo_global:02d}"
                )

                subeixos.append(
                    {
                        "codigo": prefixo,
                        "nome_es": (
                            f"Subeje de prueba "
                            f"{indice_subeixo_global}"
                        ),
                        "ordem": ordem_subeixo,
                        "perguntas": {
                            "cumplimiento": self._perguntas(
                                prefixo,
                                "cumplimiento",
                                cumprimento_subeixos[
                                    indice_distribuicao
                                ],
                            ),
                            "gestion": self._perguntas(
                                prefixo,
                                "gestion",
                                gestao_subeixos[
                                    indice_distribuicao
                                ],
                            ),
                        },
                    }
                )

            prefixo_eixo = f"eixo-{indice_eixo:02d}"

            eixos.append(
                {
                    "codigo": prefixo_eixo,
                    "nome_es": f"Eje de prueba {indice_eixo}",
                    "ordem": indice_eixo,
                    "perguntas": {
                        "cumplimiento": self._perguntas(
                            prefixo_eixo,
                            "cumplimiento",
                            1,
                        ),
                        "gestion": self._perguntas(
                            prefixo_eixo,
                            "gestion",
                            1,
                        ),
                    },
                    "subeixos": subeixos,
                }
            )

        subareas_por_setor = [
            6,
            6,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
        ]

        cumprimento_subareas = self._distribuir(194, 47)
        gestao_subareas = self._distribuir(153, 47)
        referencias_subareas = self._distribuir(224, 47)

        setores = []
        indice_subarea_global = 0
        indice_referencia_global = 0

        for indice_setor, qtd_subareas in enumerate(
            subareas_por_setor,
            start=1,
        ):
            subareas = []

            for ordem_subarea in range(
                1,
                qtd_subareas + 1,
            ):
                distribuicao = indice_subarea_global
                indice_subarea_global += 1

                prefixo = (
                    f"subarea-{indice_subarea_global:02d}"
                )

                referencias = []

                for ordem_referencia in range(
                    1,
                    referencias_subareas[distribuicao] + 1,
                ):
                    indice_referencia_global += 1

                    if indice_referencia_global == 224:
                        codigo_ref = "ref-0001"
                        citacao_ref = (
                            "Referencia institucional de prueba 1"
                        )
                    else:
                        codigo_ref = (
                            f"ref-{indice_referencia_global:04d}"
                        )
                        citacao_ref = (
                            "Referencia institucional de prueba "
                            f"{indice_referencia_global}"
                        )

                    referencias.append(
                        {
                            "codigo": codigo_ref,
                            "citacao_es": citacao_ref,
                            "ordem": ordem_referencia,
                        }
                    )

                subareas.append(
                    {
                        "codigo": prefixo,
                        "nome_es": (
                            f"Subarea de prueba "
                            f"{indice_subarea_global}"
                        ),
                        "ordem": ordem_subarea,
                        "perguntas": {
                            "cumplimiento": self._perguntas(
                                prefixo,
                                "cumplimiento",
                                cumprimento_subareas[
                                    distribuicao
                                ],
                            ),
                            "gestion": self._perguntas(
                                prefixo,
                                "gestion",
                                gestao_subareas[
                                    distribuicao
                                ],
                            ),
                        },
                        "referencias": referencias,
                    }
                )

            setores.append(
                {
                    "codigo": f"setor-{indice_setor:02d}",
                    "nome_es": (
                        f"Sector de prueba {indice_setor}"
                    ),
                    "ordem": indice_setor,
                    "subareas": subareas,
                }
            )

        return {
            "formato": (
                "guia-justica-climatica-fase2d2-v1"
            ),
            "idioma_canonico": "es",
            "fonte_origem": {
                "arquivo": (
                    "plataforma-justicia-climatica/index.html"
                ),
                "sha256_arquivo": self.SHA_ARQUIVO,
                "sha256_guia": self.SHA_GUIA,
            },
            "versao": {
                "codigo": "guia-institucional-v1",
                "fonte": "Fonte institucional de teste",
            },
            "eixos": eixos,
            "setores": setores,
        }

    def _preparar_hash_sintetico(self, documento):
        validador = ValidadorGuiaCommand()

        hash_sintetico = (
            validador._calcular_sha256_guia_canonico(
                documento
            )
        )

        documento["fonte_origem"]["sha256_guia"] = (
            hash_sintetico
        )

        return hash_sintetico

    def _executar(
        self,
        documento,
        *,
        sha_guia_esperado=None,
    ):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "guia.json"

            caminho.write_text(
                json.dumps(
                    documento,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            saida = io.StringIO()

            def executar():
                call_command(
                    "validar_fonte_guia_fase2d2",
                    "--arquivo",
                    str(caminho),
                    stdout=saida,
                )

            if sha_guia_esperado is None:
                executar()
            else:
                with patch.object(
                    ValidadorGuiaCommand,
                    "SHA256_GUIA_ORIGEM",
                    sha_guia_esperado,
                ):
                    executar()

            return saida.getvalue()

    def test_fonte_codificada_valida_eh_aceita(self):
        documento = self._documento_valido()

        hash_sintetico = (
            self._preparar_hash_sintetico(
                documento
            )
        )

        saida = self._executar(
            documento,
            sha_guia_esperado=hash_sintetico,
        )

        self.assertIn(
            "FONTE 2D.2 VÁLIDA",
            saida,
        )
        self.assertIn(
            "407 perguntas",
            saida,
        )
        self.assertIn(
            "224 ocorrências de referências",
            saida,
        )
        self.assertIn(
            "Equivalência canônica confirmada",
            saida,
        )
        self.assertIn(
            hash_sintetico,
            saida,
        )

    def test_fonte_sem_codigo_institucional_eh_bloqueada(self):
        documento = self._documento_valido()
        del documento["eixos"][0]["codigo"]

        with self.assertRaisesRegex(
            CommandError,
            "campos obrigatórios: codigo",
        ):
            self._executar(documento)

    def test_hash_de_origem_divergente_eh_bloqueado(self):
        documento = self._documento_valido()

        documento["fonte_origem"]["sha256_arquivo"] = (
            "0" * 64
        )

        with self.assertRaisesRegex(
            CommandError,
            "não corresponde",
        ):
            self._executar(documento)

    def test_contagem_de_perguntas_divergente_eh_bloqueada(self):
        documento = self._documento_valido()

        documento["eixos"][0]["perguntas"][
            "cumplimiento"
        ].pop()

        with self.assertRaisesRegex(
            CommandError,
            "Contagem inválida",
        ):
            self._executar(documento)

    def test_mesmo_codigo_de_referencia_nao_pode_mudar_citacao(self):
        documento = self._documento_valido()

        ultima_referencia = (
            documento["setores"][-1]["subareas"][-1][
                "referencias"
            ][-1]
        )

        self.assertEqual(
            ultima_referencia["codigo"],
            "ref-0001",
        )

        ultima_referencia["citacao_es"] = (
            "Citação incompatível"
        )

        with self.assertRaisesRegex(
            CommandError,
            "com citação diferente",
        ):
            self._executar(documento)

    def test_serializacao_canonica_preserva_ordem_e_utf8(self):
        guia = {
            "transversales": [
                {
                    "nombre": "Água",
                    "pregCumpl": [],
                    "pregGest": [],
                    "subejes": [],
                }
            ],
            "sectores": [],
        }

        serializado = (
            ValidadorGuiaCommand()
            ._serializar_guia_canonico(guia)
        )

        self.assertEqual(
            serializado,
            (
                '{"transversales":[{"nombre":"Água",'
                '"pregCumpl":[],"pregGest":[],'
                '"subejes":[]}],"sectores":[]}'
            ),
        )

    def test_mesmas_contagens_sem_equivalencia_sao_bloqueadas(self):
        documento = self._documento_valido()

        with self.assertRaisesRegex(
            CommandError,
            "canonicamente equivalente",
        ):
            self._executar(documento)

    def test_texto_alterado_com_mesmas_contagens_eh_bloqueado(self):
        documento = self._documento_valido()

        hash_original = (
            self._preparar_hash_sintetico(
                documento
            )
        )

        pergunta = documento[
            "eixos"
        ][0]["subeixos"][0][
            "perguntas"
        ]["cumplimiento"][0]

        pergunta["texto_es"] += " alterada"

        with self.assertRaisesRegex(
            CommandError,
            "canonicamente equivalente",
        ):
            self._executar(
                documento,
                sha_guia_esperado=hash_original,
            )

    def test_ordem_semantica_alterada_eh_bloqueada(self):
        documento = self._documento_valido()

        hash_original = (
            self._preparar_hash_sintetico(
                documento
            )
        )

        perguntas = documento[
            "eixos"
        ][0]["subeixos"][0][
            "perguntas"
        ]["cumplimiento"]

        self.assertGreaterEqual(
            len(perguntas),
            2,
        )

        perguntas[0]["ordem"], perguntas[1]["ordem"] = (
            perguntas[1]["ordem"],
            perguntas[0]["ordem"],
        )

        with self.assertRaisesRegex(
            CommandError,
            "canonicamente equivalente",
        ):
            self._executar(
                documento,
                sha_guia_esperado=hash_original,
            )

    def test_troca_de_tipo_com_mesmas_contagens_eh_bloqueada(self):
        documento = self._documento_valido()

        hash_original = (
            self._preparar_hash_sintetico(
                documento
            )
        )

        bloco = documento[
            "eixos"
        ][0]["subeixos"][0]["perguntas"]

        cumprimento = bloco["cumplimiento"][0]
        gestao = bloco["gestion"][0]

        (
            cumprimento["texto_es"],
            gestao["texto_es"],
        ) = (
            gestao["texto_es"],
            cumprimento["texto_es"],
        )

        with self.assertRaisesRegex(
            CommandError,
            "canonicamente equivalente",
        ):
            self._executar(
                documento,
                sha_guia_esperado=hash_original,
            )

    def test_referencia_alterada_com_mesmas_contagens_eh_bloqueada(self):
        documento = self._documento_valido()

        hash_original = (
            self._preparar_hash_sintetico(
                documento
            )
        )

        referencias = documento[
            "setores"
        ][0]["subareas"][0][
            "referencias"
        ]

        self.assertGreaterEqual(
            len(referencias),
            2,
        )

        referencias[1]["citacao_es"] += (
            " alterada"
        )

        with self.assertRaisesRegex(
            CommandError,
            "canonicamente equivalente",
        ):
            self._executar(
                documento,
                sha_guia_esperado=hash_original,
            )

    def test_html_legado_nao_eh_aceito_como_fonte_codificada(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "index.html"

            caminho.write_text(
                "<html><script>guia: {}</script></html>",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                CommandError,
                "JSON UTF-8 válido",
            ):
                call_command(
                    "validar_fonte_guia_fase2d2",
                    "--arquivo",
                    str(caminho),
                )
