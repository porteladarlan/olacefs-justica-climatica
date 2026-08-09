from dataclasses import dataclass
import hashlib

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from .models import (
    EixoGuia, ItemLoteImportacaoConteudo, LoteImportacaoConteudo, PerguntaGuia,
    ReferenciaGuia, SetorGuia, SubareaGuia, SubareaReferenciaGuia,
    SubeixoGuia, VersaoGuia,
)


class DivergenciaGuia(ValueError):
    pass


@dataclass
class PlanoImportacao:
    criar_versao: bool
    novos: int
    identicos: int
    divergencias: tuple


MODELOS_LEDGER = {
    ItemLoteImportacaoConteudo.Entidade.VERSAO_GUIA: VersaoGuia,
    ItemLoteImportacaoConteudo.Entidade.EIXO: EixoGuia,
    ItemLoteImportacaoConteudo.Entidade.SUBEIXO: SubeixoGuia,
    ItemLoteImportacaoConteudo.Entidade.SETOR_GUIA: SetorGuia,
    ItemLoteImportacaoConteudo.Entidade.SUBAREA: SubareaGuia,
    ItemLoteImportacaoConteudo.Entidade.PERGUNTA: PerguntaGuia,
    ItemLoteImportacaoConteudo.Entidade.REFERENCIA: ReferenciaGuia,
    ItemLoteImportacaoConteudo.Entidade.SUBAREA_REFERENCIA_GUIA: SubareaReferenciaGuia,
}


def validar_executor(usuario):
    if usuario is None:
        raise ValidationError("Executor inexistente.")
    if not usuario.is_active:
        raise ValidationError("Executor deve estar ativo.")
    if not usuario.is_staff:
        raise ValidationError("Executor deve ser staff.")


def _campos(objeto, nomes):
    return {nome: getattr(objeto, nome) for nome in nomes}


def _registrar_divergencias(divergencias, entidade, codigo, atual, esperado):
    for campo, valor in esperado.items():
        if atual.get(campo) != valor:
            divergencias.append({"entidade": entidade, "codigo": codigo, "campo": campo})


def _iterar_fonte(resultado):
    guia = resultado["guia"]
    for eixo in guia["eixos"]:
        yield "eixo", eixo, None
        for pergunta in eixo["perguntas"]:
            yield "pergunta", pergunta, ("eixo", eixo["codigo"])
        for subeixo in eixo["subeixos"]:
            yield "subeixo", subeixo, eixo["codigo"]
            for pergunta in subeixo["perguntas"]:
                yield "pergunta", pergunta, ("subeixo", subeixo["codigo"])
    for setor in guia["setores"]:
        yield "setor_guia", setor, None
        for subarea in setor["subareas"]:
            yield "subarea", subarea, setor["codigo"]
            for pergunta in subarea["perguntas"]:
                yield "pergunta", pergunta, ("subarea", subarea["codigo"])
            for ocorrencia in subarea["referencias"]:
                yield "subarea_referencia_guia", ocorrencia, subarea["codigo"]
    for referencia in guia["referencias"]:
        yield "referencia", referencia, None


def planejar_importacao(resultado):
    codigo_versao = resultado["versao"]["codigo"]
    versao = VersaoGuia.objects.filter(codigo=codigo_versao).first()
    if not versao:
        return PlanoImportacao(True, 1 + sum(1 for _ in _iterar_fonte(resultado)), 0, ())
    divergencias = []
    _registrar_divergencias(
        divergencias, "versao_guia", codigo_versao,
        _campos(versao, ("fonte", "sha256_fonte")),
        {"fonte": resultado["versao"]["fonte"], "sha256_fonte": resultado["versao"]["sha256_fonte"].lower()},
    )
    mapas = {
        "eixo": {o.codigo: o for o in versao.eixos.all()},
        "subeixo": {o.codigo: o for o in versao.subeixos.all()},
        "setor_guia": {o.codigo: o for o in versao.setores.all()},
        "subarea": {o.codigo: o for o in versao.subareas.all()},
        "pergunta": {o.codigo: o for o in versao.perguntas.all()},
        "referencia": {o.codigo: o for o in versao.referencias.all()},
    }
    novos = identicos = 0
    for entidade, item, pai in _iterar_fonte(resultado):
        if entidade == "subarea_referencia_guia":
            subarea = mapas["subarea"].get(pai)
            atual = SubareaReferenciaGuia.objects.filter(subarea=subarea, ordem=item["ordem"]).select_related("referencia").first() if subarea else None
            esperado = {"ordem": item["ordem"], "referencia_codigo": item["codigo_referencia"]}
            if not atual:
                novos += 1
            else:
                identicos += 1
                _registrar_divergencias(divergencias, entidade, f"{pai}:{item['ordem']}", {"ordem": atual.ordem, "referencia_codigo": atual.referencia.codigo}, esperado)
            continue
        atual = mapas[entidade].get(item["codigo"])
        if not atual:
            novos += 1
            continue
        identicos += 1
        if entidade in ("eixo", "setor_guia"):
            campos = {"nome_es": item["nome_es"], "ordem": item["ordem"]}
        elif entidade == "subeixo":
            campos = {"nome_es": item["nome_es"], "ordem": item["ordem"], "eixo_codigo": pai}
            atual.eixo_codigo = atual.eixo.codigo
        elif entidade == "subarea":
            campos = {"nome_es": item["nome_es"], "ordem": item["ordem"], "setor_codigo": pai}
            atual.setor_codigo = atual.setor.codigo
        elif entidade == "pergunta":
            escopo, codigo_escopo = pai
            campos = {"texto_es": item["texto_es"], "tipo_auditoria": item["tipo_auditoria"], "ordem": item["ordem"], "escopo": escopo, "codigo_escopo": codigo_escopo}
            atual.escopo = next(nome for nome in ("eixo", "subeixo", "subarea") if getattr(atual, f"{nome}_id"))
            atual.codigo_escopo = getattr(atual, atual.escopo).codigo
        else:
            campos = {"citacao_es": item["citacao_es"]}
        _registrar_divergencias(divergencias, entidade, item["codigo"], _campos(atual, campos), campos)
    return PlanoImportacao(False, novos, identicos, tuple(divergencias))


def _estado(objeto, campos):
    estado = {}
    for campo in campos:
        valor = getattr(objeto, campo)
        if hasattr(valor, "isoformat"):
            valor = valor.isoformat()
        estado[campo] = valor
    estado["atualizado_em"] = objeto.atualizado_em.isoformat() if hasattr(objeto, "atualizado_em") else None
    return estado


def _item(lote, entidade, codigo, objeto, campos, operacao="criado"):
    ItemLoteImportacaoConteudo.objects.create(
        lote=lote, entidade=entidade, codigo_origem=codigo, objeto_pk=str(objeto.pk),
        operacao=operacao,
        snapshot_anterior={"estado_pos_importacao": _estado(objeto, campos)},
        status_rollback=(ItemLoteImportacaoConteudo.StatusRollback.PENDENTE if operacao == "criado" else ItemLoteImportacaoConteudo.StatusRollback.NAO_APLICAVEL),
    )


def _obter_ou_criar_bloqueado(
    modelo, *, entidade, codigo_origem, defaults, campos_existentes=None, **lookup
):
    objeto, criado = modelo.objects.select_for_update().get_or_create(
        defaults=defaults,
        **lookup,
    )
    if criado:
        return objeto, True

    esperados = defaults if campos_existentes is None else campos_existentes
    for campo, esperado in esperados.items():
        if getattr(objeto, campo) != esperado:
            raise DivergenciaGuia(
                f"Divergencia concorrente em {entidade} {codigo_origem}, campo {campo}."
            )
    return objeto, False


def importar(resultado, executor):
    validar_executor(executor)
    plano = planejar_importacao(resultado)
    if plano.divergencias:
        primeira = plano.divergencias[0]
        raise DivergenciaGuia(f"Divergencia em {primeira['entidade']} {primeira['codigo']}, campo {primeira['campo']}.")
    with transaction.atomic():
        VersaoGuia.objects.select_for_update().filter(codigo=resultado["versao"]["codigo"]).first()
        plano = planejar_importacao(resultado)
        if plano.divergencias:
            raise DivergenciaGuia("A fonte divergiu durante a aquisicao do bloqueio de importacao.")
        lote = LoteImportacaoConteudo.objects.create(
            fonte=f"guia-fase2d2/{resultado['versao']['fonte']}", sha256=resultado["sha256_guia"],
            versao_fonte=resultado["versao"]["codigo"], executado_por=executor,
            status=LoteImportacaoConteudo.Status.EM_EXECUCAO,
            contagens_esperadas=resultado["contagens"], contagens_realizadas=resultado["contagens"],
        )
        campos_versao = {
            "fonte": resultado["versao"]["fonte"],
            "sha256_fonte": resultado["versao"]["sha256_fonte"].lower(),
        }
        versao, criada = _obter_ou_criar_bloqueado(
            VersaoGuia,
            entidade="versao_guia",
            codigo_origem=resultado["versao"]["codigo"],
            codigo=resultado["versao"]["codigo"],
            defaults={**campos_versao, "lote_origem": lote},
            campos_existentes=campos_versao,
        )
        if criada:
            _item(lote, "versao_guia", versao.codigo, versao, ("codigo", "fonte", "sha256_fonte", "situacao", "vigente", "publicado_em_id" if False else "publicado_em"))
        else:
            _item(lote, "versao_guia", versao.codigo, versao, ("codigo", "fonte", "sha256_fonte", "situacao", "vigente", "publicado_em"), "ignorado")
        mapas = {"eixo": {}, "subeixo": {}, "setor_guia": {}, "subarea": {}, "referencia": {}}
        # Referencias precedem ocorrencias no banco, sem alterar a ordem hierarquica do plano institucional.
        for ref in resultado["guia"]["referencias"]:
            obj, nova = _obter_ou_criar_bloqueado(
                ReferenciaGuia,
                entidade="referencia",
                codigo_origem=ref["codigo"],
                versao=versao,
                codigo=ref["codigo"],
                defaults={"citacao_es": ref["citacao_es"]},
            )
            mapas["referencia"][obj.codigo] = obj
            _item(lote, "referencia", obj.codigo, obj, ("codigo", "citacao_es"), "criado" if nova else "ignorado")
        for entidade, dado, pai in _iterar_fonte(resultado):
            if entidade == "referencia": continue
            if entidade == "eixo":
                defaults = {"nome_es": dado["nome_es"], "ordem": dado["ordem"]}
                obj, nova = _obter_ou_criar_bloqueado(
                    EixoGuia, entidade=entidade, codigo_origem=dado["codigo"],
                    versao=versao, codigo=dado["codigo"], defaults=defaults,
                )
            elif entidade == "subeixo":
                defaults = {"eixo": mapas["eixo"][pai], "nome_es": dado["nome_es"], "ordem": dado["ordem"]}
                obj, nova = _obter_ou_criar_bloqueado(
                    SubeixoGuia, entidade=entidade, codigo_origem=dado["codigo"],
                    versao=versao, codigo=dado["codigo"], defaults=defaults,
                )
            elif entidade == "setor_guia":
                defaults = {"nome_es": dado["nome_es"], "ordem": dado["ordem"]}
                obj, nova = _obter_ou_criar_bloqueado(
                    SetorGuia, entidade=entidade, codigo_origem=dado["codigo"],
                    versao=versao, codigo=dado["codigo"], defaults=defaults,
                )
            elif entidade == "subarea":
                defaults = {"setor": mapas["setor_guia"][pai], "nome_es": dado["nome_es"], "ordem": dado["ordem"]}
                obj, nova = _obter_ou_criar_bloqueado(
                    SubareaGuia, entidade=entidade, codigo_origem=dado["codigo"],
                    versao=versao, codigo=dado["codigo"], defaults=defaults,
                )
            elif entidade == "pergunta":
                escopo, codigo_escopo = pai
                defaults = {"texto_es": dado["texto_es"], "tipo_auditoria": dado["tipo_auditoria"], "ordem": dado["ordem"], escopo: mapas[escopo][codigo_escopo]}
                obj, nova = _obter_ou_criar_bloqueado(
                    PerguntaGuia, entidade=entidade, codigo_origem=dado["codigo"],
                    versao=versao, codigo=dado["codigo"], defaults=defaults,
                )
            else:
                subarea = mapas["subarea"][pai]
                codigo_ocorrencia = f"{pai}:{dado['ordem']}"
                obj, nova = _obter_ou_criar_bloqueado(
                    SubareaReferenciaGuia,
                    entidade=entidade,
                    codigo_origem=codigo_ocorrencia,
                    subarea=subarea,
                    ordem=dado["ordem"],
                    defaults={"referencia": mapas["referencia"][dado["codigo_referencia"]]},
                )
            if entidade in mapas: mapas[entidade][getattr(obj, "codigo")] = obj
            if "codigo" in dado:
                codigo = dado["codigo"]
            else:
                identidade = f"{pai}:{dado['ordem']}".encode("utf-8")
                codigo = f"ocorrencia:{hashlib.sha256(identidade).hexdigest()}"
            _item(lote, entidade, codigo, obj, tuple(f.attname for f in obj._meta.concrete_fields if f.name not in ("id", "criado_em", "atualizado_em")), "criado" if nova else "ignorado")
        plano_final = planejar_importacao(resultado)
        if plano_final.divergencias or plano_final.novos:
            raise DivergenciaGuia(
                "O conteudo divergiu antes da conclusao atomica da importacao."
            )
        lote.status = LoteImportacaoConteudo.Status.CONCLUIDO
        lote.finalizado_em = timezone.now()
        lote.save(update_fields=("status", "finalizado_em"))
        return lote, plano


def publicar(codigo_versao, executor, vigente):
    validar_executor(executor)
    with transaction.atomic():
        versao = VersaoGuia.objects.select_for_update().filter(codigo=codigo_versao).first()
        if not versao:
            raise ValidationError("Versao inexistente.")
        if versao.situacao != VersaoGuia.Situacao.RASCUNHO or not versao.lote_origem_id:
            raise ValidationError("Somente rascunho importado com proveniencia pode ser publicado.")
        lote = versao.lote_origem
        if lote.status != LoteImportacaoConteudo.Status.CONCLUIDO or lote.relatorio_divergencias:
            raise ValidationError("Lote de origem nao esta concluido sem divergencias.")
        # Contagens, sozinhas, nao detectam uma edicao editorial feita depois da
        # importacao. A publicacao precisa confirmar tambem que cada objeto ainda
        # corresponde ao estado registrado pelo ledger de proveniencia.
        for item in lote.itens.select_for_update().filter(
            operacao=ItemLoteImportacaoConteudo.Operacao.CRIADO,
        ):
            modelo = MODELOS_LEDGER.get(item.entidade)
            objeto = (
                modelo.objects.select_for_update().filter(pk=item.objeto_pk).first()
                if modelo
                else None
            )
            esperado = item.snapshot_anterior.get("estado_pos_importacao")
            if not objeto or not esperado:
                raise ValidationError(
                    f"Integridade do lote divergente em {item.entidade} {item.codigo_origem}."
                )
            campos = tuple(campo for campo in esperado if campo != "atualizado_em")
            if _estado(objeto, campos) != esperado:
                raise ValidationError(
                    f"Integridade do lote divergente em {item.entidade} {item.codigo_origem}."
                )
        realizadas = {
            "eixos": versao.eixos.count(),
            "subeixos": versao.subeixos.count(),
            "setores": versao.setores.count(),
            "subareas": versao.subareas.count(),
            "perguntas": versao.perguntas.count(),
            "referencias": versao.referencias.count(),
            "ocorrencias_referencias": SubareaReferenciaGuia.objects.filter(subarea__versao=versao).count(),
        }
        if realizadas != lote.contagens_esperadas:
            raise ValidationError("Conteudo atual da versao nao corresponde as contagens validadas do lote.")
        if vigente:
            VersaoGuia.objects.select_for_update().filter(vigente=True).exclude(pk=versao.pk).update(vigente=False)
        versao.situacao = VersaoGuia.Situacao.PUBLICADA
        versao.publicado_em = timezone.now()
        versao.vigente = vigente
        versao.save(update_fields=("situacao", "publicado_em", "vigente", "atualizado_em"))
        return versao


def reverter(lote, executor, justificativa):
    validar_executor(executor)
    if not justificativa.strip():
        raise ValidationError("Justificativa de reversao obrigatoria.")
    with transaction.atomic():
        lote = LoteImportacaoConteudo.objects.select_for_update().get(pk=lote.pk)
        if not lote.fonte.startswith("guia-fase2d2/") or lote.status not in (LoteImportacaoConteudo.Status.CONCLUIDO, LoteImportacaoConteudo.Status.COM_DIVERGENCIAS):
            raise ValidationError("Lote nao pertence a importacao reversivel do Guia.")
        versoes_referenciadas = lote.itens.filter(
            entidade=ItemLoteImportacaoConteudo.Entidade.VERSAO_GUIA,
        ).exclude(objeto_pk="").values_list("objeto_pk", flat=True)
        list(
            VersaoGuia.objects.select_for_update()
            .filter(pk__in=versoes_referenciadas)
            .order_by("pk")
        )
        itens = list(lote.itens.select_for_update().filter(status_rollback="pendente").order_by("-pk"))
        bloqueados = 0
        for item in itens:
            modelo = MODELOS_LEDGER.get(item.entidade)
            objeto = (
                modelo.objects.select_for_update().filter(pk=item.objeto_pk).first()
                if modelo
                else None
            )
            esperado = item.snapshot_anterior.get("estado_pos_importacao", {})
            campos_estado = tuple(
                campo for campo in esperado if campo != "atualizado_em"
            )
            if not objeto:
                item.status_rollback = "revertido"
            elif (
                (objeto if isinstance(objeto, VersaoGuia) else objeto.versao_guia).situacao
                == VersaoGuia.Situacao.PUBLICADA
            ):
                item.status_rollback = "bloqueado"; bloqueados += 1
            elif not esperado or _estado(objeto, campos_estado) != esperado:
                item.status_rollback = "bloqueado"; bloqueados += 1
            else:
                try:
                    objeto.delete()
                except ProtectedError:
                    # Um descendente alterado e preservado pode proteger seu ancestral.
                    # Nesse caso a reversao deve ser parcial, nunca abortar ou forcar a exclusao.
                    item.status_rollback = "bloqueado"
                    bloqueados += 1
                else:
                    item.status_rollback = "revertido"
            item.save(update_fields=("status_rollback", "atualizado_em"))
        lote.status = LoteImportacaoConteudo.Status.REVERSAO_PARCIAL if bloqueados else LoteImportacaoConteudo.Status.REVERTIDO
        lote.revertido_em = timezone.now(); lote.revertido_por = executor; lote.justificativa_reversao = justificativa
        lote.save(update_fields=("status", "revertido_em", "revertido_por", "justificativa_reversao"))
        return bloqueados
