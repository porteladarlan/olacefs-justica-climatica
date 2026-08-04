import json
from pathlib import Path
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    ExperienciaSubmissaoForm,
    PropostaEdicaoPublicadaForm,
    RevisaoExperienciaForm,
    RevisaoPropostaEdicaoForm,
)
from .models import (
    Anexo,
    BancoTecnico,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    Ferramenta,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)

# Configurações padrão para anexos.
# Mantém compatibilidade com as três posições disponíveis nos formulários.
ANEXO_LIMITE_POR_EXPERIENCIA = 3
ANEXO_TAMANHO_MAX_MB = 10
ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB * 1024 * 1024
ANEXO_MIME_POR_EXTENSAO = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
ANEXO_CONTENT_TYPES_PERMITIDOS = set(ANEXO_MIME_POR_EXTENSAO.values())

# ISO 3166-1 alfa-3 usado no cadastro -> identificador numérico do world-atlas.
# A lista regional segue a referência visual oficial e permite desenhar também
# territórios sem correspondência institucional no banco.
MAPA_REGIONAL_ISO3_PARA_GEO_ID = {
    "ABW": "533",
    "ARG": "032",
    "BHS": "044",
    "BLZ": "084",
    "BOL": "068",
    "BRA": "076",
    "CHL": "152",
    "COL": "170",
    "CRI": "188",
    "CUB": "192",
    "CUW": "531",
    "DOM": "214",
    "ECU": "218",
    "FLK": "238",
    "GLP": "312",
    "GTM": "320",
    "GUY": "328",
    "HTI": "332",
    "HND": "340",
    "JAM": "388",
    "MEX": "484",
    "NIC": "558",
    "PAN": "591",
    "PRY": "600",
    "PER": "604",
    "PRI": "630",
    "SLV": "222",
    "SUR": "740",
    "TTO": "780",
    "URY": "858",
    "VEN": "862",
}
MAPA_REGIONAL_GEO_IDS = tuple(MAPA_REGIONAL_ISO3_PARA_GEO_ID.values())


def obter_destino_seguro(request, padrao="meus_envios"):
    destino = request.POST.get("next") or request.GET.get("next")
    if destino and url_has_allowed_host_and_scheme(
        url=destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return padrao


def experiencias_publicas():
    return Experiencia.objects.filter(
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    )


def _url_com_paises(nome_rota, paises_ids):
    base = reverse(nome_rota)
    consulta = urlencode([("pais", pais_id) for pais_id in paises_ids])
    return f"{base}?{consulta}" if consulta else base


def _payload_mapa_regional():
    efs_mapa = EFS.objects.only(
        "id",
        "nome",
        "nome_es",
        "nome_en",
        "sigla",
        "pais_id",
    ).order_by("nome")
    paises = (
        Pais.objects.filter(
            sigla__in=MAPA_REGIONAL_ISO3_PARA_GEO_ID,
            efs__isnull=False,
        )
        .annotate(
            experiencias_publicadas=Count(
                "experiencias",
                filter=Q(
                    experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
                ),
                distinct=True,
            ),
            criterios_normativos=Count(
                "experiencias__normas_internacionais",
                filter=Q(
                    experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
                ),
                distinct=True,
            ),
        )
        .prefetch_related(Prefetch("efs", queryset=efs_mapa, to_attr="efs_mapa"))
        .distinct()
        .order_by("nome")
    )

    paises = list(paises)
    criterios_ids_por_pais = {pais.pk: [] for pais in paises}
    pares_criterios = (
        Experiencia.objects.filter(
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
            pais_id__in=criterios_ids_por_pais.keys(),
            normas_internacionais__isnull=False,
        )
        .values_list("pais_id", "normas_internacionais__id")
        .distinct()
        .order_by("pais_id", "normas_internacionais__id")
    )
    for pais_id, norma_id in pares_criterios:
        criterios_ids_por_pais[pais_id].append(norma_id)

    paises_publicos = []
    for pais in paises:
        paises_publicos.append(
            {
                "id": pais.pk,
                "sigla": pais.sigla,
                "nome": pais.nome_exibicao,
                "geo_id": MAPA_REGIONAL_ISO3_PARA_GEO_ID[pais.sigla],
                "efs": [
                    {"nome": efs.nome_exibicao, "sigla": efs.sigla}
                    for efs in pais.efs_mapa
                ],
                "experiencias_publicadas": pais.experiencias_publicadas,
                "criterios_normativos": pais.criterios_normativos,
                "criterios_normativos_ids": criterios_ids_por_pais[pais.pk],
                "url_boas_praticas": _url_com_paises(
                    "catalogo_experiencias", [pais.pk]
                ),
                "url_marcos_normativos": _url_com_paises(
                    "normas_internacionais", [pais.pk]
                ),
            }
        )

    return {
        "paises": paises_publicos,
        "geo_ids_regiao": MAPA_REGIONAL_GEO_IDS,
    }


def _objetos_selecionados(request, parametro, queryset):
    """Retorna objetos existentes, preservando a ordem dos valores GET válidos."""
    identificadores = []
    vistos = set()
    for valor in request.GET.getlist(parametro):
        try:
            identificador = int(valor)
        except (TypeError, ValueError):
            continue
        if identificador > 0 and identificador not in vistos:
            vistos.add(identificador)
            identificadores.append(identificador)

    objetos_por_id = {
        objeto.pk: objeto for objeto in queryset.filter(pk__in=identificadores)
    }
    return [
        objetos_por_id[identificador]
        for identificador in identificadores
        if identificador in objetos_por_id
    ]


def _url_sem_valor_filtro(request, parametro, valor=None):
    parametros = request.GET.copy()
    if valor is None:
        parametros.pop(parametro, None)
    else:
        valores = [
            item for item in parametros.getlist(parametro) if item != str(valor)
        ]
        if valores:
            parametros.setlist(parametro, valores)
        else:
            parametros.pop(parametro, None)
    consulta = parametros.urlencode()
    return f"{request.path}?{consulta}" if consulta else request.path


def _url_http_segura(valor):
    if not valor:
        return ""
    try:
        URLValidator(schemes=["http", "https"])(valor)
    except ValidationError:
        return ""
    return valor


def ferramentas_catalogadas():
    return Ferramenta.objects.filter(situacao=Ferramenta.Situacao.PUBLICADA)


STATUS_VISIVEIS_REVISAO = [
    Experiencia.StatusPublicacao.ENVIADO,
    Experiencia.StatusPublicacao.EM_REVISAO,
    Experiencia.StatusPublicacao.APROVADO,
    Experiencia.StatusPublicacao.REJEITADO,
]


def experiencia_pertence_ao_usuario(experiencia, usuario):
    if not usuario or not usuario.is_authenticated:
        return False

    if usuario.is_staff:
        return True

    return bool(
        getattr(experiencia, "autor_id", None)
        and experiencia.autor_id == usuario.id
    )

def queryset_meus_envios(usuario):
    if not usuario or not usuario.is_authenticated:
        return Experiencia.objects.none()

    queryset = Experiencia.objects.all() if usuario.is_staff else Experiencia.objects.filter(autor=usuario)

    return (
        queryset
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .order_by("-atualizado_em")
    )


def detectar_mime_real(arquivo):
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


def obter_indices_anexos_informados(request):
    prefixos = ("anexo_titulo_", "anexo_arquivo_", "anexo_url_")
    indices = set()
    for campo in set(request.POST.keys()) | set(request.FILES.keys()):
        for prefixo in prefixos:
            if campo.startswith(prefixo):
                sufixo = campo[len(prefixo):]
                if sufixo.isdigit():
                    indices.add(int(sufixo))
                break
    return indices

def obter_anexos_do_request(request):
    anexos = []
    indices = obter_indices_anexos_informados(request)
    for indice in sorted(item for item in indices if 1 <= item <= ANEXO_LIMITE_POR_EXPERIENCIA):
        titulo = request.POST.get(f"anexo_titulo_{indice}", "").strip()
        arquivo = request.FILES.get(f"anexo_arquivo_{indice}")
        url = request.POST.get(f"anexo_url_{indice}", "").strip()

        if titulo or arquivo or url:
            anexos.append(
                {
                    "indice": indice,
                    "titulo": titulo,
                    "arquivo": arquivo,
                    "url": url,
                }
            )
    return anexos


def validar_anexos_request(request, quantidade_existente=0, ids_remover=None):
    ids_remover = ids_remover or []
    anexos = obter_anexos_do_request(request)
    erros = []
    validador_url = URLValidator(schemes=["http", "https"])

    indices_excedentes = [
        indice
        for indice in obter_indices_anexos_informados(request)
        if indice < 1 or indice > ANEXO_LIMITE_POR_EXPERIENCIA
    ]
    if indices_excedentes:
        erros.append(
            f"É permitido informar no máximo {ANEXO_LIMITE_POR_EXPERIENCIA} anexos por experiência."
        )

    quantidade_final = quantidade_existente - len(ids_remover) + len(anexos)
    if quantidade_final > ANEXO_LIMITE_POR_EXPERIENCIA:
        erros.append(
            f"É permitido manter no máximo {ANEXO_LIMITE_POR_EXPERIENCIA} anexos por experiência."
        )

    for anexo in anexos:
        indice = anexo["indice"]
        arquivo = anexo["arquivo"]
        url = anexo["url"]

        if arquivo:
            extensao = Path(arquivo.name).suffix.lower()
            mime_esperado = ANEXO_MIME_POR_EXTENSAO.get(extensao)
            if not mime_esperado:
                erros.append(
                    f"Anexo {indice}: tipo de arquivo não permitido. Use PDF, JPG ou PNG."
                )
            else:
                mime_declarado = (getattr(arquivo, "content_type", "") or "").split(";", 1)[0].strip().lower()
                mime_real = detectar_mime_real(arquivo)
                if mime_declarado not in ANEXO_CONTENT_TYPES_PERMITIDOS or mime_declarado != mime_esperado:
                    erros.append(
                        f"Anexo {indice}: o tipo MIME informado não corresponde à extensão do arquivo."
                    )
                if mime_real != mime_esperado:
                    erros.append(
                        f"Anexo {indice}: o conteúdo do arquivo não corresponde a um PDF, JPG ou PNG válido."
                    )
            if arquivo.size > ANEXO_TAMANHO_MAX_BYTES:
                erros.append(
                    f"Anexo {indice}: arquivo maior que {ANEXO_TAMANHO_MAX_MB} MB."
                )

        if url:
            try:
                validador_url(url)
            except ValidationError:
                erros.append(
                    f"Anexo {indice}: informe uma URL válida iniciada por http:// ou https://."
                )

        if not arquivo and not url:
            erros.append(
                f"Anexo {indice}: informe um arquivo ou um link externo."
            )

    return anexos, erros


def adicionar_erros_anexos_ao_formulario(form, erros):
    for erro in erros:
        form.add_error(None, erro)





def estilizar_formulario_autenticacao(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault("class", "form-control")
    return form


def registrar_usuario(request):
    if request.user.is_authenticated:
        return redirect(obter_destino_seguro(request))

    if request.method == "POST":
        form = estilizar_formulario_autenticacao(UserCreationForm(request.POST))
        email = request.POST.get("email", "").strip().lower()
        nome = request.POST.get("first_name", "").strip()
        sobrenome = request.POST.get("last_name", "").strip()

        if not email:
            form.add_error(None, "Informe um e-mail institucional.")
        elif form.is_valid():
            user = form.save(commit=False)
            user.email = email
            user.first_name = nome
            user.last_name = sobrenome
            user.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect(obter_destino_seguro(request))
    else:
        form = estilizar_formulario_autenticacao(UserCreationForm())

    return render(
        request,
        "praticas/registrar_usuario.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect("meus_envios")

    if request.method == "POST":
        form = estilizar_formulario_autenticacao(AuthenticationForm(request, data=request.POST))
        if form.is_valid():
            login(request, form.get_user())
            return redirect(obter_destino_seguro(request))
    else:
        form = estilizar_formulario_autenticacao(AuthenticationForm(request))

    return render(request, "praticas/login_usuario.html", {"form": form, "next": request.GET.get("next", "")})


def logout_usuario(request):
    logout(request)
    messages.success(request, "Sessão encerrada com sucesso.")
    return redirect("pagina_inicial")


@login_required(login_url="login_usuario")
def meus_envios(request):
    experiencias = queryset_meus_envios(request.user)
    propostas = PropostaEdicaoExperiencia.objects.select_related("experiencia")
    if not request.user.is_staff:
        propostas = propostas.filter(experiencia__autor=request.user)
    propostas = propostas.order_by("-atualizado_em")
    return render(request, "praticas/meus_envios.html", {"experiencias": experiencias, "propostas": propostas})

def favoritos_ids(request):
    return [int(item) for item in request.session.get("favoritos_experiencias", []) if str(item).isdigit()]


def salvar_favoritos_ids(request, ids):
    request.session["favoritos_experiencias"] = [int(item) for item in ids]
    request.session.modified = True


@require_POST
def alternar_favorito(request, pk):
    experiencia = get_object_or_404(experiencias_publicas(), pk=pk)
    ids = favoritos_ids(request)

    if experiencia.pk in ids:
        ids = [item for item in ids if item != experiencia.pk]
        messages.success(request, "Experiência removida dos favoritos.")
    else:
        ids.append(experiencia.pk)
        messages.success(request, "Experiência adicionada aos favoritos.")

    salvar_favoritos_ids(request, ids)
    return redirect(obter_destino_seguro(request, padrao="catalogo_experiencias"))


def favoritos_experiencias(request):
    ids = favoritos_ids(request)
    experiencias = (
        experiencias_publicas()
        .filter(id__in=ids)
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
        )
        .order_by("-ano_execucao", "titulo")
    )

    contexto = {
        "experiencias": experiencias,
        "favoritos_ids": ids,
    }
    return render(request, "praticas/favoritos_experiencias.html", contexto)


def pagina_inicial(request):
    experiencias = experiencias_publicas().select_related(
        "efs",
        "pais",
        "tipo_experiencia",
        "setor",
    ).prefetch_related(
        "temas_transversais",
        "normas_internacionais",
    )

    contexto = {
        "total_experiencias": experiencias.count(),
        "total_efs": EFS.objects.count(),
        "total_paises": Pais.objects.count(),
        "total_normas": NormaInternacional.objects.count(),
        "ultimas_experiencias": experiencias[:3],
        "experiencias_destacadas": experiencias.filter(
            Q(destacado=True) | Q(relevante=True)
        )[:3],
        "mapa_regional": _payload_mapa_regional(),
    }
    return render(request, "praticas/pagina_inicial.html", contexto)


def catalogo_experiencias(request):
    experiencias_base = experiencias_publicas()
    experiencias = (
        experiencias_base
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
        )
        .distinct()
    )

    paises = Pais.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    efs_lista = EFS.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).select_related("pais").distinct()
    tipos = TipoExperiencia.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    setores = Setor.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    temas = TemaTransversal.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    normas = NormaInternacional.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    dimensoes = DimensaoJusticaClimatica.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    grupos = GrupoVulneravel.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).distinct()
    anos = list(
        experiencias_base.values_list("ano_execucao", flat=True)
        .distinct()
        .order_by("-ano_execucao")
    )
    idioma = getattr(request, "LANGUAGE_CODE", "pt-br")
    ferramentas_opcoes = []
    ferramentas_por_valor = {}
    for valor_pt, valor_es, valor_en in experiencias_base.values_list(
        "ferramentas_utilizadas",
        "ferramentas_utilizadas_es",
        "ferramentas_utilizadas_en",
    ):
        valor = (valor_pt or valor_es or valor_en or "").strip()
        if not valor or len(valor) > 200 or valor in ferramentas_por_valor:
            continue
        if idioma == "en":
            rotulo = (valor_en or valor_pt or valor_es or valor).strip()
        elif idioma == "es":
            rotulo = (valor_es or valor_pt or valor_en or valor).strip()
        else:
            rotulo = (valor_pt or valor_es or valor_en or valor).strip()
        opcao = {"valor": valor, "rotulo": rotulo}
        ferramentas_por_valor[valor] = opcao
        ferramentas_opcoes.append(opcao)
    ferramentas_opcoes.sort(key=lambda opcao: opcao["rotulo"].casefold())
    ferramentas_selecionadas = []
    for valor in request.GET.getlist("ferramenta"):
        if valor in ferramentas_por_valor and valor not in ferramentas_selecionadas:
            ferramentas_selecionadas.append(valor)

    selecoes = {
        "pais": _objetos_selecionados(request, "pais", Pais.objects.all()),
        "efs": _objetos_selecionados(request, "efs", efs_lista),
        "tipo": _objetos_selecionados(request, "tipo", tipos),
        "setor": _objetos_selecionados(request, "setor", setores),
        "tema": _objetos_selecionados(request, "tema", temas),
        "norma": _objetos_selecionados(request, "norma", normas),
        "dimensao": _objetos_selecionados(request, "dimensao", dimensoes),
        "grupo": _objetos_selecionados(request, "grupo", grupos),
    }
    anos_selecionados = []
    for valor in request.GET.getlist("ano"):
        try:
            ano = int(valor)
        except (TypeError, ValueError):
            continue
        if ano in anos and ano not in anos_selecionados:
            anos_selecionados.append(ano)

    campos_filtro = {
        "pais": "pais_id__in",
        "efs": "efs_id__in",
        "tipo": "tipo_experiencia_id__in",
        "setor": "setor_id__in",
        "tema": "temas_transversais__id__in",
        "norma": "normas_internacionais__id__in",
        "dimensao": "dimensoes_consideradas__id__in",
        "grupo": "grupos_vulneraveis__id__in",
    }
    for chave, campo in campos_filtro.items():
        if selecoes[chave]:
            experiencias = experiencias.filter(
                **{campo: [objeto.pk for objeto in selecoes[chave]]}
            )
    if anos_selecionados:
        experiencias = experiencias.filter(ano_execucao__in=anos_selecionados)
    if ferramentas_selecionadas:
        experiencias = experiencias.filter(
            Q(ferramentas_utilizadas__in=ferramentas_selecionadas)
            | Q(ferramentas_utilizadas_es__in=ferramentas_selecionadas)
            | Q(ferramentas_utilizadas_en__in=ferramentas_selecionadas)
        )

    termo = (request.GET.get("q") or "").strip()[:200]
    if termo:
        experiencias = experiencias.filter(
            Q(titulo__icontains=termo)
            | Q(titulo_es__icontains=termo)
            | Q(titulo_en__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(descricao_es__icontains=termo)
            | Q(descricao_en__icontains=termo)
            | Q(perguntas_chave__icontains=termo)
            | Q(perguntas_chave_es__icontains=termo)
            | Q(perguntas_chave_en__icontains=termo)
            | Q(criterios_utilizados__icontains=termo)
            | Q(criterios_utilizados_es__icontains=termo)
            | Q(criterios_utilizados_en__icontains=termo)
            | Q(ferramentas_utilizadas__icontains=termo)
            | Q(ferramentas_utilizadas_es__icontains=termo)
            | Q(ferramentas_utilizadas_en__icontains=termo)
            | Q(setor__nome__icontains=termo)
            | Q(setor__nome_es__icontains=termo)
            | Q(setor__nome_en__icontains=termo)
            | Q(tipo_experiencia__nome__icontains=termo)
            | Q(tipo_experiencia__nome_es__icontains=termo)
            | Q(tipo_experiencia__nome_en__icontains=termo)
            | Q(temas_transversais__nome__icontains=termo)
            | Q(temas_transversais__nome_es__icontains=termo)
            | Q(temas_transversais__nome_en__icontains=termo)
            | Q(normas_internacionais__nome__icontains=termo)
            | Q(normas_internacionais__nome_es__icontains=termo)
            | Q(normas_internacionais__nome_en__icontains=termo)
            | Q(pais__nome__icontains=termo)
            | Q(pais__nome_es__icontains=termo)
            | Q(pais__nome_en__icontains=termo)
            | Q(efs__nome__icontains=termo)
            | Q(efs__nome_es__icontains=termo)
            | Q(efs__nome_en__icontains=termo)
            | Q(efs__sigla__icontains=termo)
        )

    experiencias = experiencias.distinct()
    chips = []
    if termo:
        chips.append(
            {
                "chave": "q",
                "rotulo": termo,
                "url_remover": _url_sem_valor_filtro(request, "q"),
            }
        )
    for chave, objetos in selecoes.items():
        for objeto in objetos:
            chips.append(
                {
                    "chave": chave,
                    "rotulo": objeto.nome_exibicao,
                    "url_remover": _url_sem_valor_filtro(
                        request, chave, objeto.pk
                    ),
                }
            )
    for ano in anos_selecionados:
        chips.append(
            {
                "chave": "ano",
                "rotulo": str(ano),
                "url_remover": _url_sem_valor_filtro(request, "ano", ano),
            }
        )
    for valor in ferramentas_selecionadas:
        chips.append(
            {
                "chave": "ferramenta",
                "rotulo": ferramentas_por_valor[valor]["rotulo"],
                "url_remover": _url_sem_valor_filtro(
                    request, "ferramenta", valor
                ),
            }
        )

    contexto = {
        "experiencias": experiencias,
        "paises": paises,
        "efs_lista": efs_lista,
        "tipos": tipos,
        "setores": setores,
        "temas": temas,
        "normas": normas,
        "dimensoes": dimensoes,
        "grupos": grupos,
        "anos": anos,
        "filtros_ids": {
            chave: [objeto.pk for objeto in objetos]
            for chave, objetos in selecoes.items()
        },
        "anos_selecionados": anos_selecionados,
        "ferramentas_opcoes": ferramentas_opcoes,
        "ferramentas_selecionadas": ferramentas_selecionadas,
        "termo_busca": termo,
        "chips_filtros": chips,
        "total_resultados": experiencias.count(),
        "favoritos_ids": favoritos_ids(request),
    }
    return render(request, "praticas/catalogo_experiencias.html", contexto)


def comparar_experiencias(request):
    ids = request.GET.getlist("experiencias")
    experiencias_selecionadas = (
        experiencias_publicas()
        .filter(id__in=ids)
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
            "anexos",
        )
        .order_by("-ano_execucao", "titulo")
    )

    experiencias_disponiveis = (
        experiencias_publicas()
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .order_by("-ano_execucao", "titulo")
    )

    contexto = {
        "experiencias_disponiveis": experiencias_disponiveis,
        "experiencias_selecionadas": experiencias_selecionadas,
        "ids_selecionados": [str(item) for item in ids],
        "limite_comparacao": 3,
        "favoritos_ids": favoritos_ids(request),
    }
    return render(request, "praticas/comparar_experiencias.html", contexto)


def detalhe_experiencia(request, pk):
    experiencia = get_object_or_404(
        experiencias_publicas()
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
            "anexos",
        ),
        pk=pk,
    )
    return render(
        request,
        "praticas/detalhe_experiencia.html",
        {"experiencia": experiencia, "favoritos_ids": favoritos_ids(request)},
    )


def normas_internacionais(request):
    termo = (request.GET.get("q") or "").strip()[:200]
    experiencias_relacionadas = experiencias_publicas().select_related(
        "pais", "setor"
    )
    paises = Pais.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        experiencias__normas_internacionais__isnull=False,
    ).distinct()
    setores = Setor.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        experiencias__normas_internacionais__isnull=False,
    ).distinct()
    paises_selecionados = _objetos_selecionados(
        request, "pais", Pais.objects.all()
    )
    setores_selecionados = _objetos_selecionados(request, "setor", setores)

    normas = NormaInternacional.objects.annotate(
        total_experiencias_publicas=Count(
            "experiencias",
            filter=Q(
                experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
            ),
            distinct=True,
        )
    ).prefetch_related(
        Prefetch(
            "experiencias",
            queryset=experiencias_relacionadas,
            to_attr="experiencias_publicas_catalogo",
        )
    )
    if termo:
        normas = normas.filter(
            Q(nome__icontains=termo)
            | Q(nome_es__icontains=termo)
            | Q(nome_en__icontains=termo)
            | Q(resumo__icontains=termo)
            | Q(resumo_es__icontains=termo)
            | Q(resumo_en__icontains=termo)
        )

    filtros_relacionados = Q()
    if paises_selecionados:
        filtros_relacionados &= Q(
            experiencias__pais_id__in=[pais.pk for pais in paises_selecionados]
        )
    if setores_selecionados:
        filtros_relacionados &= Q(
            experiencias__setor_id__in=[setor.pk for setor in setores_selecionados]
        )
    if filtros_relacionados:
        normas = normas.filter(
            filtros_relacionados,
            experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )

    normas = list(normas.distinct())
    for norma in normas:
        norma.url_publica = _url_http_segura(norma.url_referencia)
        norma.paises_publicos = sorted(
            {
                experiencia.pais.nome_exibicao
                for experiencia in norma.experiencias_publicas_catalogo
            },
            key=str.casefold,
        )
        norma.setores_publicos = sorted(
            {
                experiencia.setor.nome_exibicao
                for experiencia in norma.experiencias_publicas_catalogo
            },
            key=str.casefold,
        )

    chips = []
    if termo:
        chips.append(
            {
                "rotulo": termo,
                "url_remover": _url_sem_valor_filtro(request, "q"),
            }
        )
    for chave, objetos in (
        ("pais", paises_selecionados),
        ("setor", setores_selecionados),
    ):
        for objeto in objetos:
            chips.append(
                {
                    "rotulo": objeto.nome_exibicao,
                    "url_remover": _url_sem_valor_filtro(
                        request, chave, objeto.pk
                    ),
                }
            )

    return render(
        request,
        "praticas/normas_internacionais.html",
        {
            "normas": normas,
            "paises": paises,
            "setores": setores,
            "paises_selecionados": [item.pk for item in paises_selecionados],
            "setores_selecionados": [item.pk for item in setores_selecionados],
            "chips_filtros": chips,
            "termo_busca": termo,
            "total_resultados": len(normas),
        },
    )


def salvar_anexos_submissao(experiencia, anexos):
    for anexo in anexos:
        Anexo.objects.create(
            experiencia=experiencia,
            titulo=anexo["titulo"] or f"Anexo {anexo['indice']}",
            arquivo=anexo["arquivo"],
            url_externa=anexo["url"],
        )


@login_required(login_url="login_usuario")
def adicionar_boa_pratica(request):
    acao = request.POST.get("acao_envio", "enviar")
    obrigatorio_para_envio = acao != "rascunho"

    if request.method == "POST":
        form = ExperienciaSubmissaoForm(
            request.POST,
            request.FILES,
            obrigatorio_para_envio=obrigatorio_para_envio,
        )
        anexos, erros_anexos = validar_anexos_request(request)

        if form.is_valid() and not erros_anexos:
            experiencia = form.save(commit=False)
            experiencia.autor = request.user
            experiencia.status_iniciativa = Experiencia.StatusIniciativa.CONCLUIDA
            if request.user.is_authenticated and not experiencia.email_contato:
                experiencia.email_contato = request.user.email
            if request.user.is_authenticated and not experiencia.pessoa_responsavel:
                experiencia.pessoa_responsavel = request.user.get_full_name() or request.user.username
            if acao == "rascunho":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                mensagem = "Rascunho salvo com sucesso. Ele ainda não foi enviado para revisão."
            else:
                experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
                mensagem = "Boa prática enviada com sucesso. Ela ficará pendente até a revisão."
            experiencia.save()
            form.save_m2m()
            salvar_anexos_submissao(experiencia, anexos)

            messages.success(request, mensagem)
            if acao == "rascunho":
                return redirect("meus_envios")
            return redirect("confirmacao_envio")

        adicionar_erros_anexos_ao_formulario(form, erros_anexos)
    else:
        form = ExperienciaSubmissaoForm(
            initial={
                "email_contato": request.user.email,
                "pessoa_responsavel": request.user.get_full_name() or request.user.username,
            }
        )

    return render(request, "praticas/adicionar_boa_pratica.html", {"form": form})


@login_required(login_url="login_usuario")
def editar_boa_pratica(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "anexos",
        ),
        pk=pk,
    )

    if not experiencia_pertence_ao_usuario(experiencia, request.user):
        messages.error(
            request,
            "Não foi possível validar sua permissão para edição deste envio.",
        )
        return redirect("meus_envios")

    if experiencia.status_publicacao == Experiencia.StatusPublicacao.PUBLICADO:
        return redirect("solicitar_edicao_publicada", pk=experiencia.pk)

    acao = request.POST.get("acao_envio", "enviar")
    obrigatorio_para_envio = acao != "rascunho"

    if request.method == "POST":
        form = ExperienciaSubmissaoForm(
            request.POST,
            request.FILES,
            instance=experiencia,
            obrigatorio_para_envio=obrigatorio_para_envio,
        )
        ids_remover_solicitados = {
            int(valor)
            for valor in request.POST.getlist("remover_anexo")
            if valor.isdigit()
        }
        ids_remover = list(
            experiencia.anexos.filter(id__in=ids_remover_solicitados).values_list("id", flat=True)
        )
        quantidade_existente = experiencia.anexos.count()
        anexos, erros_anexos = validar_anexos_request(
            request,
            quantidade_existente=quantidade_existente,
            ids_remover=ids_remover,
        )

        if form.is_valid() and not erros_anexos:
            Anexo.objects.filter(experiencia=experiencia, id__in=ids_remover).delete()
            experiencia = form.save(commit=False)
            if request.user.is_authenticated and not experiencia.autor_id:
                experiencia.autor = request.user
            if acao == "rascunho":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                mensagem = "Alterações salvas como rascunho."
            else:
                experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
                mensagem = "Boa prática reenviada para revisão."
            experiencia.save()
            form.save_m2m()
            salvar_anexos_submissao(experiencia, anexos)

            messages.success(request, mensagem)
            return redirect("painel_revisao") if request.user.is_staff else redirect("status_envio")
        adicionar_erros_anexos_ao_formulario(form, erros_anexos)
    else:
        form = ExperienciaSubmissaoForm(instance=experiencia)

    return render(
        request,
        "praticas/editar_boa_pratica.html",
        {
            "form": form,
            "experiencia": experiencia,
        },
    )


def dados_proposta_from_form(form):
    dados = {}
    campos_many_to_many = {"temas_transversais", "normas_internacionais"}
    campos_fk = {"efs", "pais", "tipo_experiencia", "setor"}

    for campo in ExperienciaSubmissaoForm.Meta.fields:
        valor = form.cleaned_data.get(campo)

        if campo in campos_many_to_many:
            dados[campo] = [item.pk for item in valor]
        elif campo in campos_fk:
            dados[campo] = valor.pk if valor else None
        else:
            dados[campo] = valor

    return dados


@login_required(login_url="login_usuario")
def solicitar_edicao_publicada(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related(
            "temas_transversais",
            "normas_internacionais",
        ),
        pk=pk,
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
    )

    if not experiencia_pertence_ao_usuario(experiencia, request.user):
        messages.error(request, "Não foi possível validar sua permissão para solicitar edição.")
        return redirect("meus_envios")

    if request.method == "POST":
        form = PropostaEdicaoPublicadaForm(
            request.POST,
            instance=experiencia,
            obrigatorio_para_envio=True,
        )
        if form.is_valid():
            PropostaEdicaoExperiencia.objects.create(
                experiencia=experiencia,
                email_contato=experiencia.email_contato or request.user.email,
                comentario_autor=form.cleaned_data.get("comentario_autor", ""),
                dados_json=dados_proposta_from_form(form),
                status=PropostaEdicaoExperiencia.Status.PENDENTE,
            )
            messages.success(
                request,
                "Proposta de edição enviada para revisão. A versão publicada permanecerá ativa até aprovação.",
            )
            return redirect("status_envio")
    else:
        form = PropostaEdicaoPublicadaForm(instance=experiencia)

    return render(
        request,
        "praticas/solicitar_edicao_publicada.html",
        {
            "form": form,
            "experiencia": experiencia,
        },
    )



CAMPOS_COMPARACAO_EDICAO = [
    ("titulo", "Nome da boa prática / iniciativa"),
    ("efs", "EFS"),
    ("pais", "País"),
    ("tipo_experiencia", "Tipo de boa prática"),
    ("setor", "Setor"),
    ("temas_transversais", "Temas transversais"),
    ("normas_internacionais", "Normas internacionais"),
    ("email_contato", "E-mail institucional"),
    ("pessoa_responsavel", "Pessoa responsável"),
    ("descricao", "Breve descrição da boa prática"),
    ("enfoque_justica_climatica", "Vínculo com justiça climática"),
    ("objetivo", "Objetivo"),
    ("perguntas_chave", "Perguntas de auditoria"),
    ("criterios_utilizados", "Critérios utilizados"),
    ("metodologia", "Metodologia"),
    ("ferramentas_utilizadas", "Metodologias e instrumentos utilizados"),
    ("resultados", "Resultados"),
    ("recomendacoes", "Recomendações"),
    ("replicabilidade", "Replicabilidade"),
    ("informacoes_adicionais", "Informações adicionais"),
    ("ano_execucao", "Ano"),
    ("contribui_para_guia", "Contribui para a Guia"),
]


def texto_booleano(valor):
    return "Sim" if valor else "Não"


def texto_lista_objetos(objetos):
    nomes = [getattr(item, "nome_exibicao", str(item)) for item in objetos]
    return ", ".join(nomes) if nomes else "-"


def valor_atual_para_comparacao(experiencia, campo):
    if campo in {"efs", "pais", "tipo_experiencia", "setor"}:
        objeto = getattr(experiencia, campo, None)
        return getattr(objeto, "nome_exibicao", str(objeto)) if objeto else "-"

    if campo in {"temas_transversais", "normas_internacionais"}:
        return texto_lista_objetos(getattr(experiencia, campo).all())

    valor = getattr(experiencia, campo, "")

    if campo == "contribui_para_guia":
        return texto_booleano(bool(valor))

    if valor is None or valor == "":
        return "-"

    return str(valor)


def valor_proposto_para_comparacao(proposta, campo):
    dados = proposta.dados_json or {}
    valor = dados.get(campo)

    if campo == "efs":
        objeto = EFS.objects.filter(pk=valor).first()
        return getattr(objeto, "nome_exibicao", "-") if objeto else "-"

    if campo == "pais":
        objeto = Pais.objects.filter(pk=valor).first()
        return getattr(objeto, "nome_exibicao", "-") if objeto else "-"

    if campo == "tipo_experiencia":
        objeto = TipoExperiencia.objects.filter(pk=valor).first()
        return getattr(objeto, "nome_exibicao", "-") if objeto else "-"

    if campo == "setor":
        objeto = Setor.objects.filter(pk=valor).first()
        return getattr(objeto, "nome_exibicao", "-") if objeto else "-"

    if campo == "temas_transversais":
        return texto_lista_objetos(TemaTransversal.objects.filter(pk__in=valor or []))

    if campo == "normas_internacionais":
        return texto_lista_objetos(NormaInternacional.objects.filter(pk__in=valor or []))

    if campo == "contribui_para_guia":
        return texto_booleano(bool(valor))

    if valor is None or valor == "":
        return "-"

    return str(valor)


def montar_comparativo_proposta_edicao(proposta):
    experiencia = proposta.experiencia
    linhas = []

    for campo, rotulo in CAMPOS_COMPARACAO_EDICAO:
        valor_atual = valor_atual_para_comparacao(experiencia, campo)
        valor_proposto = valor_proposto_para_comparacao(proposta, campo)
        alterado = valor_atual.strip() != valor_proposto.strip()

        linhas.append(
            {
                "campo": campo,
                "rotulo": rotulo,
                "valor_atual": valor_atual,
                "valor_proposto": valor_proposto,
                "alterado": alterado,
            }
        )

    return linhas


def aplicar_proposta_edicao(proposta):
    experiencia = proposta.experiencia
    dados = proposta.dados_json

    campos_fk = {
        "efs": EFS,
        "pais": Pais,
        "tipo_experiencia": TipoExperiencia,
        "setor": Setor,
    }
    campos_many_to_many = {
        "temas_transversais": TemaTransversal,
        "normas_internacionais": NormaInternacional,
    }

    for campo, modelo in campos_fk.items():
        valor_id = dados.get(campo)
        if valor_id:
            setattr(experiencia, campo, modelo.objects.get(pk=valor_id))

    for campo in ExperienciaSubmissaoForm.Meta.fields:
        if campo in campos_fk or campo in campos_many_to_many:
            continue

        # Propostas criadas antes da inclusão de novos campos podem não trazer
        # todas as chaves no JSON. Nesses casos, preserva-se o valor atual para
        # evitar sobrescrever campos novos com None e violar restrições NOT NULL.
        if campo not in dados:
            continue

        valor = dados.get(campo)
        try:
            campo_modelo = Experiencia._meta.get_field(campo)
        except Exception:
            campo_modelo = None

        if valor is None and campo_modelo is not None and not getattr(campo_modelo, "null", False):
            valor = ""

        setattr(experiencia, campo, valor)

    experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
    experiencia.save()

    for campo, modelo in campos_many_to_many.items():
        ids = dados.get(campo, [])
        getattr(experiencia, campo).set(modelo.objects.filter(pk__in=ids))


def confirmacao_envio(request):
    return render(request, "praticas/confirmacao_envio.html")


@login_required(login_url="login_usuario")
def status_envio(request):
    experiencias = queryset_meus_envios(request.user)
    propostas = PropostaEdicaoExperiencia.objects.select_related("experiencia")
    if not request.user.is_staff:
        propostas = propostas.filter(experiencia__autor=request.user)
    propostas = propostas.order_by("-atualizado_em")

    return render(
        request,
        "praticas/status_envio.html",
        {
            "experiencias": experiencias,
            "propostas": propostas,
        },
    )


@staff_member_required
def painel_revisao(request):
    status = request.GET.get("status", "")
    status_choices_revisao = [
        item for item in Experiencia.StatusPublicacao.choices
        if item[0] in STATUS_VISIVEIS_REVISAO
    ]
    experiencias = (
        Experiencia.objects.filter(status_publicacao__in=STATUS_VISIVEIS_REVISAO)
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .order_by("-atualizado_em")
    )

    if status in STATUS_VISIVEIS_REVISAO:
        experiencias = experiencias.filter(status_publicacao=status)
    else:
        status = ""

    contadores = {
        "enviado": Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.ENVIADO).count(),
        "em_revisao": Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.EM_REVISAO).count(),
        "aprovado": Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.APROVADO).count(),
        "rejeitado": Experiencia.objects.filter(status_publicacao=Experiencia.StatusPublicacao.REJEITADO).count(),
        "edicoes_pendentes": PropostaEdicaoExperiencia.objects.filter(status=PropostaEdicaoExperiencia.Status.PENDENTE).count(),
    }

    return render(
        request,
        "praticas/painel_revisao.html",
        {
            "experiencias": experiencias,
            "status_atual": status,
            "status_choices": status_choices_revisao,
            "contadores": contadores,
        },
    )


@staff_member_required
def revisar_experiencia(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
            "anexos",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = RevisaoExperienciaForm(request.POST, instance=experiencia)
        if form.is_valid():
            acao = form.cleaned_data["acao"]
            experiencia.comentario_revisor = form.cleaned_data["comentario_revisor"]

            if acao == "em_revisao":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.EM_REVISAO
                mensagem = "Experiência marcada como em revisão."
            elif acao == "aprovar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = "Experiência aprovada e publicada no catálogo público."
            elif acao == "publicar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = "Experiência publicada no catálogo público."
            elif acao == "devolver":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                mensagem = "Experiência devolvida para ajustes."
            elif acao == "rejeitar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.REJEITADO
                mensagem = "Experiência rejeitada."
            else:
                mensagem = "Revisão registrada."

            experiencia.save(update_fields=["status_publicacao", "comentario_revisor", "atualizado_em"])
            messages.success(request, mensagem)
            return redirect("painel_revisao")
    else:
        form = RevisaoExperienciaForm(instance=experiencia)

    return render(
        request,
        "praticas/revisar_experiencia.html",
        {
            "experiencia": experiencia,
            "form": form,
        },
    )


@staff_member_required
def painel_revisao_edicoes(request):
    status = request.GET.get("status", "")
    propostas = (
        PropostaEdicaoExperiencia.objects.select_related("experiencia", "experiencia__efs", "experiencia__pais")
        .order_by("-atualizado_em")
    )
    if status:
        propostas = propostas.filter(status=status)

    return render(
        request,
        "praticas/painel_revisao_edicoes.html",
        {
            "propostas": propostas,
            "status_atual": status,
            "status_choices": PropostaEdicaoExperiencia.Status.choices,
        },
    )


@staff_member_required
def revisar_edicao_publicada(request, pk):
    proposta = get_object_or_404(
        PropostaEdicaoExperiencia.objects.select_related("experiencia", "experiencia__efs", "experiencia__pais"),
        pk=pk,
    )

    if request.method == "POST":
        form = RevisaoPropostaEdicaoForm(request.POST, instance=proposta)
        if form.is_valid():
            acao = form.cleaned_data["acao"]
            proposta.comentario_revisor = form.cleaned_data["comentario_revisor"]

            if acao == "em_revisao":
                proposta.status = PropostaEdicaoExperiencia.Status.EM_REVISAO
                mensagem = "Proposta marcada como em revisão."
            elif acao == "aprovar":
                aplicar_proposta_edicao(proposta)
                proposta.status = PropostaEdicaoExperiencia.Status.APROVADA
                mensagem = "Proposta aprovada e aplicada à experiência publicada."
            elif acao == "rejeitar":
                proposta.status = PropostaEdicaoExperiencia.Status.REJEITADA
                mensagem = "Proposta de edição rejeitada."
            else:
                mensagem = "Revisão registrada."

            proposta.save(update_fields=["status", "comentario_revisor", "atualizado_em"])
            messages.success(request, mensagem)
            return redirect("painel_revisao_edicoes")
    else:
        form = RevisaoPropostaEdicaoForm(instance=proposta)

    return render(
        request,
        "praticas/revisar_edicao_publicada.html",
        {
            "proposta": proposta,
            "form": form,
            "comparativo": montar_comparativo_proposta_edicao(proposta),
        },
    )


@staff_member_required
def excluir_boa_pratica(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related("anexos"),
        pk=pk,
    )

    proximo = request.POST.get("next") or request.GET.get("next")
    if proximo and not url_has_allowed_host_and_scheme(
        proximo,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        proximo = None

    if request.method == "POST":
        if request.POST.get("confirmar_exclusao") != "sim":
            messages.error(request, "Confirmação de exclusão inválida.")
            return redirect("excluir_boa_pratica", pk=experiencia.pk)

        titulo = experiencia.titulo_exibicao
        for anexo in experiencia.anexos.all():
            if anexo.arquivo:
                anexo.arquivo.delete(save=False)
        experiencia.delete()
        messages.success(request, f"Boa prática excluída com sucesso: {titulo}")
        if proximo:
            return redirect(proximo)
        return redirect("catalogo_experiencias")

    return render(
        request,
        "praticas/excluir_boa_pratica.html",
        {
            "experiencia": experiencia,
            "destino_cancelamento": proximo,
        },
    )

def banco_tecnico(request):
    termo = (request.GET.get("q") or "").strip()[:200]
    recursos = (
        BancoTecnico.objects.none().select_related("setor")
        .prefetch_related("dimensoes")
        .all()
    )
    if termo:
        recursos = recursos.filter(
            Q(titulo__icontains=termo)
            | Q(titulo_es__icontains=termo)
            | Q(titulo_en__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(descricao_es__icontains=termo)
            | Q(descricao_en__icontains=termo)
            | Q(tipo_recurso__icontains=termo)
            | Q(tipo_recurso_es__icontains=termo)
            | Q(tipo_recurso_en__icontains=termo)
            | Q(setor__nome__icontains=termo)
            | Q(setor__nome_es__icontains=termo)
            | Q(setor__nome_en__icontains=termo)
        )
    recursos = list(recursos.distinct())
    for recurso in recursos:
        recurso.url_publica = _url_http_segura(recurso.url)
    return render(
        request,
        "praticas/banco_tecnico.html",
        {
            "recursos": recursos,
            "termo_busca": termo,
            "total_resultados": len(recursos),
        },
    )


def ferramentas(request):
    termo = (request.GET.get("q") or "").strip()[:200]
    recursos_base = ferramentas_catalogadas()
    total_publicadas = recursos_base.count()
    setores = Setor.objects.filter(
        ferramentas__situacao=Ferramenta.Situacao.PUBLICADA
    ).distinct().order_by("nome_es", "nome")
    setor_selecionado = _objetos_selecionados(
        request, "setor", setores
    )
    setor_selecionado = setor_selecionado[0] if setor_selecionado else None

    recursos = recursos_base.select_related("setor")
    if setor_selecionado:
        recursos = recursos.filter(setor=setor_selecionado)
    if termo:
        recursos = recursos.filter(
            Q(titulo__icontains=termo)
            | Q(titulo_es__icontains=termo)
            | Q(titulo_en__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(descricao_es__icontains=termo)
            | Q(descricao_en__icontains=termo)
            | Q(responsavel__icontains=termo)
            | Q(periodo__icontains=termo)
            | Q(setor__nome__icontains=termo)
            | Q(setor__nome_es__icontains=termo)
            | Q(setor__nome_en__icontains=termo)
        )

    recursos = list(recursos.distinct())
    for recurso in recursos:
        recurso.url_publica = _url_http_segura(recurso.url)

    return render(
        request,
        "praticas/ferramentas.html",
        {
            "recursos": recursos,
            "setores": setores,
            "setor_selecionado": setor_selecionado,
            "termo_busca": termo,
            "total_resultados": len(recursos),
            "total_publicadas": total_publicadas,
        },
    )


def sobre_plataforma(request):
    return render(request, "praticas/sobre_plataforma.html")
