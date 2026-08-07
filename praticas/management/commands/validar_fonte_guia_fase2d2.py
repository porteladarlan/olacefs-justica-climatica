import hashlib
import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Valida o contrato institucional codificado do Guia da Fase 2D.2 "
        "sem escrever no banco."
    )

    FORMATO = "guia-justica-climatica-fase2d2-v1"

    SHA256_ARQUIVO_ORIGEM = (
        "cd78b9beca799aa9c6976af825c314e57e4a1903bfa832ecec2fbc3d86b61c67"
    )
    SHA256_GUIA_ORIGEM = (
        "8d56bed6eb08a32ef496f251d11cb423463544ecb43ba41ba804fc12c19ded3d"
    )

    CONTAGENS_ESPERADAS = {
        "eixos": 3,
        "subeixos": 8,
        "setores": 9,
        "subareas": 47,
        "perguntas_eixo": 6,
        "perguntas_subeixo": 54,
        "perguntas_subarea": 347,
        "perguntas": 407,
        "cumplimiento": 224,
        "gestion": 183,
        "referencias_ocorrencias": 224,
        "referencias_textuais_unicas": 223,
        "perguntas_textuais_unicas": 407,
    }

    PADRAO_CODIGO = re.compile(r"^[A-Za-z0-9_-]+$")

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            required=True,
            help="Caminho do JSON institucional codificado do Guia.",
        )

    def handle(self, *args, **options):
        caminho = Path(options["arquivo"]).expanduser().resolve()

        if not caminho.is_file():
            raise CommandError(f"Arquivo não encontrado: {caminho}")

        dados_brutos = caminho.read_bytes()
        sha256_arquivo = hashlib.sha256(dados_brutos).hexdigest()

        try:
            documento = json.loads(dados_brutos.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CommandError(
                "A fonte codificada do Guia deve ser um JSON UTF-8 válido."
            ) from exc

        resumo = self._validar_documento(documento)

        self.stdout.write(
            self.style.SUCCESS(
                "FONTE 2D.2 VÁLIDA: "
                f"{resumo['eixos']} eixos, "
                f"{resumo['subeixos']} subeixos, "
                f"{resumo['setores']} setores, "
                f"{resumo['subareas']} subáreas, "
                f"{resumo['perguntas']} perguntas, "
                f"{resumo['referencias_ocorrencias']} ocorrências de referências. "
                f"SHA-256 do JSON: {sha256_arquivo}. "
                "Validação somente estrutural; nenhuma escrita foi realizada."
            )
        )

    def _validar_documento(self, documento):
        self._validar_objeto(
            documento,
            obrigatorias={
                "formato",
                "idioma_canonico",
                "fonte_origem",
                "versao",
                "eixos",
                "setores",
            },
            permitidas={
                "formato",
                "idioma_canonico",
                "fonte_origem",
                "versao",
                "eixos",
                "setores",
            },
            contexto="raiz",
        )

        if documento["formato"] != self.FORMATO:
            raise CommandError(
                f"raiz.formato deve ser exatamente {self.FORMATO!r}."
            )

        if documento["idioma_canonico"] != "es":
            raise CommandError(
                "raiz.idioma_canonico deve permanecer exatamente 'es'."
            )

        self._validar_fonte_origem(documento["fonte_origem"])
        self._validar_versao(documento["versao"])

        eixos = documento["eixos"]
        setores = documento["setores"]

        self._validar_lista(eixos, "raiz.eixos")
        self._validar_lista(setores, "raiz.setores")

        if len(eixos) != self.CONTAGENS_ESPERADAS["eixos"]:
            raise CommandError(
                "A fonte deve conter exatamente 3 eixos."
            )

        if len(setores) != self.CONTAGENS_ESPERADAS["setores"]:
            raise CommandError(
                "A fonte deve conter exatamente 9 setores."
            )

        estado = {
            "eixos": len(eixos),
            "subeixos": 0,
            "setores": len(setores),
            "subareas": 0,
            "perguntas_eixo": 0,
            "perguntas_subeixo": 0,
            "perguntas_subarea": 0,
            "perguntas": 0,
            "cumplimiento": 0,
            "gestion": 0,
            "referencias_ocorrencias": 0,
            "codigos_eixos": set(),
            "codigos_subeixos": set(),
            "codigos_setores": set(),
            "codigos_subareas": set(),
            "codigos_perguntas": set(),
            "referencias_por_codigo": {},
            "textos_perguntas": set(),
            "textos_referencias": set(),
        }

        for indice, eixo in enumerate(eixos, start=1):
            contexto = f"raiz.eixos[{indice}]"
            self._validar_eixo(eixo, contexto, estado)

        self._validar_ordens_contiguas(
            eixos,
            "raiz.eixos",
        )

        for indice, setor in enumerate(setores, start=1):
            contexto = f"raiz.setores[{indice}]"
            self._validar_setor(setor, contexto, estado)

        self._validar_ordens_contiguas(
            setores,
            "raiz.setores",
        )

        estado["perguntas_textuais_unicas"] = len(
            estado["textos_perguntas"]
        )
        estado["referencias_textuais_unicas"] = len(
            estado["textos_referencias"]
        )

        for chave, esperado in self.CONTAGENS_ESPERADAS.items():
            realizado = estado[chave]
            if realizado != esperado:
                raise CommandError(
                    f"Contagem inválida para {chave}: "
                    f"esperado {esperado}, encontrado {realizado}."
                )

        return {
            chave: estado[chave]
            for chave in self.CONTAGENS_ESPERADAS
        }

    def _validar_fonte_origem(self, fonte):
        contexto = "raiz.fonte_origem"

        self._validar_objeto(
            fonte,
            obrigatorias={
                "arquivo",
                "sha256_arquivo",
                "sha256_guia",
            },
            permitidas={
                "arquivo",
                "sha256_arquivo",
                "sha256_guia",
            },
            contexto=contexto,
        )

        self._validar_texto(
            fonte["arquivo"],
            f"{contexto}.arquivo",
        )

        sha_arquivo = self._validar_sha256(
            fonte["sha256_arquivo"],
            f"{contexto}.sha256_arquivo",
        )
        sha_guia = self._validar_sha256(
            fonte["sha256_guia"],
            f"{contexto}.sha256_guia",
        )

        if sha_arquivo != self.SHA256_ARQUIVO_ORIGEM:
            raise CommandError(
                "O SHA-256 do arquivo de origem não corresponde "
                "à fonte auditada na Fase 2D.0."
            )

        if sha_guia != self.SHA256_GUIA_ORIGEM:
            raise CommandError(
                "O SHA-256 do objeto original PJC_DATA.guia não corresponde "
                "à fonte auditada na Fase 2D.0."
            )

    def _validar_versao(self, versao):
        contexto = "raiz.versao"

        self._validar_objeto(
            versao,
            obrigatorias={"codigo", "fonte"},
            permitidas={"codigo", "fonte"},
            contexto=contexto,
        )

        self._validar_codigo(
            versao["codigo"],
            f"{contexto}.codigo",
            tamanho_maximo=100,
        )
        self._validar_texto(
            versao["fonte"],
            f"{contexto}.fonte",
        )

    def _validar_eixo(self, eixo, contexto, estado):
        self._validar_objeto(
            eixo,
            obrigatorias={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
                "subeixos",
            },
            permitidas={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
                "subeixos",
            },
            contexto=contexto,
        )

        self._validar_codigo_unico(
            eixo["codigo"],
            f"{contexto}.codigo",
            estado["codigos_eixos"],
        )
        self._validar_texto(
            eixo["nome_es"],
            f"{contexto}.nome_es",
        )
        self._validar_ordem(
            eixo["ordem"],
            f"{contexto}.ordem",
        )

        self._validar_perguntas(
            eixo["perguntas"],
            f"{contexto}.perguntas",
            estado,
            "perguntas_eixo",
        )

        subeixos = eixo["subeixos"]
        self._validar_lista(
            subeixos,
            f"{contexto}.subeixos",
        )

        for indice, subeixo in enumerate(subeixos, start=1):
            self._validar_subeixo(
                subeixo,
                f"{contexto}.subeixos[{indice}]",
                estado,
            )

        self._validar_ordens_contiguas(
            subeixos,
            f"{contexto}.subeixos",
        )

    def _validar_subeixo(self, subeixo, contexto, estado):
        self._validar_objeto(
            subeixo,
            obrigatorias={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
            },
            permitidas={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
            },
            contexto=contexto,
        )

        self._validar_codigo_unico(
            subeixo["codigo"],
            f"{contexto}.codigo",
            estado["codigos_subeixos"],
        )
        self._validar_texto(
            subeixo["nome_es"],
            f"{contexto}.nome_es",
        )
        self._validar_ordem(
            subeixo["ordem"],
            f"{contexto}.ordem",
        )

        estado["subeixos"] += 1

        self._validar_perguntas(
            subeixo["perguntas"],
            f"{contexto}.perguntas",
            estado,
            "perguntas_subeixo",
        )

    def _validar_setor(self, setor, contexto, estado):
        self._validar_objeto(
            setor,
            obrigatorias={
                "codigo",
                "nome_es",
                "ordem",
                "subareas",
            },
            permitidas={
                "codigo",
                "nome_es",
                "ordem",
                "subareas",
            },
            contexto=contexto,
        )

        self._validar_codigo_unico(
            setor["codigo"],
            f"{contexto}.codigo",
            estado["codigos_setores"],
        )
        self._validar_texto(
            setor["nome_es"],
            f"{contexto}.nome_es",
        )
        self._validar_ordem(
            setor["ordem"],
            f"{contexto}.ordem",
        )

        subareas = setor["subareas"]
        self._validar_lista(
            subareas,
            f"{contexto}.subareas",
        )

        for indice, subarea in enumerate(subareas, start=1):
            self._validar_subarea(
                subarea,
                f"{contexto}.subareas[{indice}]",
                estado,
            )

        self._validar_ordens_contiguas(
            subareas,
            f"{contexto}.subareas",
        )

    def _validar_subarea(self, subarea, contexto, estado):
        self._validar_objeto(
            subarea,
            obrigatorias={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
                "referencias",
            },
            permitidas={
                "codigo",
                "nome_es",
                "ordem",
                "perguntas",
                "referencias",
            },
            contexto=contexto,
        )

        self._validar_codigo_unico(
            subarea["codigo"],
            f"{contexto}.codigo",
            estado["codigos_subareas"],
        )
        self._validar_texto(
            subarea["nome_es"],
            f"{contexto}.nome_es",
        )
        self._validar_ordem(
            subarea["ordem"],
            f"{contexto}.ordem",
        )

        estado["subareas"] += 1

        self._validar_perguntas(
            subarea["perguntas"],
            f"{contexto}.perguntas",
            estado,
            "perguntas_subarea",
        )

        referencias = subarea["referencias"]
        self._validar_lista(
            referencias,
            f"{contexto}.referencias",
        )

        for indice, referencia in enumerate(referencias, start=1):
            ref_contexto = f"{contexto}.referencias[{indice}]"

            self._validar_objeto(
                referencia,
                obrigatorias={
                    "codigo",
                    "citacao_es",
                    "ordem",
                },
                permitidas={
                    "codigo",
                    "citacao_es",
                    "ordem",
                },
                contexto=ref_contexto,
            )

            codigo = self._validar_codigo(
                referencia["codigo"],
                f"{ref_contexto}.codigo",
            )
            citacao = self._validar_texto(
                referencia["citacao_es"],
                f"{ref_contexto}.citacao_es",
            )
            self._validar_ordem(
                referencia["ordem"],
                f"{ref_contexto}.ordem",
            )

            citacao_anterior = estado["referencias_por_codigo"].get(
                codigo
            )
            if (
                citacao_anterior is not None
                and citacao_anterior != citacao
            ):
                raise CommandError(
                    f"{ref_contexto}.codigo reutiliza {codigo!r} "
                    "com citação diferente."
                )

            estado["referencias_por_codigo"][codigo] = citacao
            estado["textos_referencias"].add(citacao)
            estado["referencias_ocorrencias"] += 1

        self._validar_ordens_contiguas(
            referencias,
            f"{contexto}.referencias",
        )

    def _validar_perguntas(
        self,
        bloco,
        contexto,
        estado,
        contador_escopo,
    ):
        self._validar_objeto(
            bloco,
            obrigatorias={"cumplimiento", "gestion"},
            permitidas={"cumplimiento", "gestion"},
            contexto=contexto,
        )

        for tipo in ("cumplimiento", "gestion"):
            perguntas = bloco[tipo]

            self._validar_lista(
                perguntas,
                f"{contexto}.{tipo}",
            )

            for indice, pergunta in enumerate(perguntas, start=1):
                pergunta_contexto = (
                    f"{contexto}.{tipo}[{indice}]"
                )

                self._validar_objeto(
                    pergunta,
                    obrigatorias={
                        "codigo",
                        "texto_es",
                        "ordem",
                    },
                    permitidas={
                        "codigo",
                        "texto_es",
                        "ordem",
                    },
                    contexto=pergunta_contexto,
                )

                self._validar_codigo_unico(
                    pergunta["codigo"],
                    f"{pergunta_contexto}.codigo",
                    estado["codigos_perguntas"],
                )
                texto = self._validar_texto(
                    pergunta["texto_es"],
                    f"{pergunta_contexto}.texto_es",
                )
                self._validar_ordem(
                    pergunta["ordem"],
                    f"{pergunta_contexto}.ordem",
                )

                estado["textos_perguntas"].add(texto)
                estado[tipo] += 1
                estado[contador_escopo] += 1
                estado["perguntas"] += 1

            self._validar_ordens_contiguas(
                perguntas,
                f"{contexto}.{tipo}",
            )

    def _validar_objeto(
        self,
        valor,
        obrigatorias,
        permitidas,
        contexto,
    ):
        if not isinstance(valor, dict):
            raise CommandError(
                f"{contexto} deve ser um objeto JSON."
            )

        faltantes = obrigatorias - set(valor)
        if faltantes:
            raise CommandError(
                f"{contexto} não possui campos obrigatórios: "
                f"{', '.join(sorted(faltantes))}."
            )

        desconhecidas = set(valor) - permitidas
        if desconhecidas:
            raise CommandError(
                f"{contexto} possui campos não homologados: "
                f"{', '.join(sorted(desconhecidas))}."
            )

    def _validar_lista(self, valor, contexto):
        if not isinstance(valor, list):
            raise CommandError(
                f"{contexto} deve ser uma lista JSON."
            )

    def _validar_codigo_unico(
        self,
        valor,
        contexto,
        conjunto,
    ):
        codigo = self._validar_codigo(
            valor,
            contexto,
        )

        if codigo in conjunto:
            raise CommandError(
                f"{contexto} repete o código {codigo!r}."
            )

        conjunto.add(codigo)
        return codigo

    def _validar_codigo(
        self,
        valor,
        contexto,
        tamanho_maximo=160,
    ):
        if not isinstance(valor, str) or not valor:
            raise CommandError(
                f"{contexto} deve ser um código não vazio."
            )

        if valor != valor.strip():
            raise CommandError(
                f"{contexto} não pode possuir espaços externos."
            )

        if len(valor) > tamanho_maximo:
            raise CommandError(
                f"{contexto} excede {tamanho_maximo} caracteres."
            )

        if not self.PADRAO_CODIGO.fullmatch(valor):
            raise CommandError(
                f"{contexto} deve usar somente letras ASCII, "
                "números, hífen ou sublinhado."
            )

        return valor

    def _validar_texto(self, valor, contexto):
        if not isinstance(valor, str):
            raise CommandError(
                f"{contexto} deve ser texto."
            )

        if not valor.strip():
            raise CommandError(
                f"{contexto} não pode ser vazio."
            )

        if "\x00" in valor:
            raise CommandError(
                f"{contexto} contém caractere NUL inválido."
            )

        return valor

    def _validar_ordem(self, valor, contexto):
        if (
            isinstance(valor, bool)
            or not isinstance(valor, int)
            or valor < 1
        ):
            raise CommandError(
                f"{contexto} deve ser inteiro positivo."
            )

        return valor

    def _validar_ordens_contiguas(
        self,
        itens,
        contexto,
    ):
        ordens = [item["ordem"] for item in itens]

        esperado = list(
            range(
                1,
                len(itens) + 1,
            )
        )

        if sorted(ordens) != esperado:
            raise CommandError(
                f"{contexto} deve possuir ordens únicas e "
                f"contíguas de 1 a {len(itens)}."
            )

    def _validar_sha256(self, valor, contexto):
        if (
            not isinstance(valor, str)
            or not re.fullmatch(
                r"[0-9a-fA-F]{64}",
                valor,
            )
        ):
            raise CommandError(
                f"{contexto} deve ser SHA-256 hexadecimal "
                "com 64 caracteres."
            )

        return valor.lower()
