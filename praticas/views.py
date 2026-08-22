import json
from smtplib import SMTPException
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, validate_email

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Max, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from .emails import (
    agendar_notificacao_decisao_edicao,
    agendar_notificacao_status_experiencia,
    agendar_notificacoes_nova_submissao,
    agendar_notificacoes_solicitacao_edicao,
    enviar_confirmacao_email,
    primeiro_email_valido,
)
from .forms import (
    CadastroUsuarioForm,
    EXPERIENCIA_LABELS,
    ExperienciaSubmissaoForm,
    FerramentaSubmissaoForm,
    PropostaEdicaoPublicadaForm,
    ReenviarConfirmacaoForm,
    RevisaoExperienciaForm,
    RevisaoPropostaEdicaoForm,
    texto_idioma,
)
from .tokens import confirmacao_email_token
from .models import (
    Anexo,
    BancoTecnico,
    ConfirmacaoEmailPendente,
    DimensaoJusticaClimatica,
    EFS,
    Experiencia,
    Ferramenta,
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    PerguntaAuditoria,
    PropostaEdicaoExperiencia,
    SETORES_OFICIAIS_CODIGOS,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)
from .seletores_guia_preview import (
    listar_eixos,
    listar_setores,
    obter_versao_publicada_vigente,
    queryset_eixo_detalhado,
    queryset_setor_detalhado,
    queryset_subarea_detalhada,
    queryset_subeixo_detalhado,
    separar_perguntas_por_tipo,
)
from .uploads import validar_anexo_upload

# Configurações padrão para anexos.
# Mantém compatibilidade com as três posições disponíveis nos formulários.
ANEXO_LIMITE_POR_EXPERIENCIA = 3

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

    efs_participantes_mapa = (
        EFS.objects.select_related("pais")
        .only(
            "id",
            "nome",
            "nome_es",
            "nome_en",
            "sigla",
            "pais_id",
            "pais__id",
            "pais__nome",
            "pais__nome_es",
            "pais__nome_en",
            "pais__sigla",
        )
        .order_by("nome")
    )
    experiencias_coordenadas = (
        Experiencia.objects.filter(
            status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
        )
        .filter(
            Q(efs_participantes__isnull=False)
            | Q(
                tipo_experiencia__codigo="auditoria_coordenada",
                paises_participantes__isnull=False,
            )
        )
        .select_related("efs__pais", "pais", "tipo_experiencia")
        .prefetch_related(
            Prefetch(
                "efs_participantes",
                queryset=efs_participantes_mapa,
                to_attr="efs_participantes_mapa",
            ),
            Prefetch(
                "paises_participantes",
                queryset=Pais.objects.only(
                    "id", "nome", "nome_es", "nome_en", "sigla"
                ).order_by("nome"),
                to_attr="paises_participantes_mapa",
            ),
        )
        .distinct()
        .order_by("titulo", "pk")
    )

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

    auditorias_coordenadas = []
    for experiencia in experiencias_coordenadas:
        efs_adicionais = [
            efs
            for efs in experiencia.efs_participantes_mapa
            if efs.pk != experiencia.efs_id
        ]
        paises_adicionais = []
        if experiencia.tipo_experiencia.codigo == "auditoria_coordenada":
            paises_adicionais = [
                pais
                for pais in experiencia.paises_participantes_mapa
                if pais.pk != experiencia.pais_id
            ]
        if not efs_adicionais and not paises_adicionais:
            continue

        paises_da_auditoria = {
            experiencia.pais_id: experiencia.pais,
        }
        for efs_participante in efs_adicionais:
            paises_da_auditoria[efs_participante.pais_id] = efs_participante.pais
        for pais_participante in paises_adicionais:
            paises_da_auditoria[pais_participante.pk] = pais_participante

        paises_ordenados = sorted(
            paises_da_auditoria.values(),
            key=lambda pais: (pais.nome_exibicao.casefold(), pais.pk),
        )
        auditorias_coordenadas.append(
            {
                "id": experiencia.pk,
                "titulo": experiencia.titulo_exibicao,
                "efs_lider": {
                    "id": experiencia.efs_id,
                    "nome": experiencia.efs.nome_exibicao,
                    "sigla": experiencia.efs.sigla,
                },
                "paises": [
                    {
                        "id": pais.pk,
                        "nome": pais.nome_exibicao,
                        "geo_id": MAPA_REGIONAL_ISO3_PARA_GEO_ID.get(pais.sigla),
                    }
                    for pais in paises_ordenados
                ],
            }
        )

    return {
        "paises": paises_publicos,
        "geo_ids_regiao": MAPA_REGIONAL_GEO_IDS,
        "auditorias_coordenadas": auditorias_coordenadas,
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


def _url_ficha_tecnica_segura(norma):
    url_externa = _url_http_segura(norma.ficha_tecnica_url)
    if url_externa:
        return url_externa
    if (
        norma.ficha_tecnica
        and norma.ficha_tecnica.storage.exists(norma.ficha_tecnica.name)
    ):
        return norma.ficha_tecnica.url
    return ""


def ferramentas_catalogadas():
    return Ferramenta.objects.filter(situacao=Ferramenta.Situacao.PUBLICADA)


def _contexto_perguntas(perguntas):
    cumplimiento, gestion = separar_perguntas_por_tipo(perguntas)
    return {
        "perguntas_cumplimiento": cumplimiento,
        "perguntas_gestion": gestion,
    }


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
            texto_idioma(
                f"É permitido informar no máximo {ANEXO_LIMITE_POR_EXPERIENCIA} anexos por experiência.",
                f"Se permite informar como máximo {ANEXO_LIMITE_POR_EXPERIENCIA} archivos adjuntos por experiencia.",
                f"A maximum of {ANEXO_LIMITE_POR_EXPERIENCIA} attachments may be provided per experience.",
            )
        )

    quantidade_final = quantidade_existente - len(ids_remover) + len(anexos)
    if quantidade_final > ANEXO_LIMITE_POR_EXPERIENCIA:
        erros.append(
            texto_idioma(
                f"É permitido manter no máximo {ANEXO_LIMITE_POR_EXPERIENCIA} anexos por experiência.",
                f"Se permite mantener como máximo {ANEXO_LIMITE_POR_EXPERIENCIA} archivos adjuntos por experiencia.",
                f"A maximum of {ANEXO_LIMITE_POR_EXPERIENCIA} attachments may be kept per experience.",
            )
        )

    for anexo in anexos:
        indice = anexo["indice"]
        arquivo = anexo["arquivo"]
        url = anexo["url"]

        if arquivo:
            try:
                validar_anexo_upload(arquivo)
            except ValidationError as exc:
                erros.extend(
                    texto_idioma(
                        f"Anexo {indice}: {mensagem}",
                        f"Archivo adjunto {indice}: {mensagem}",
                        f"Attachment {indice}: {mensagem}",
                    )
                    for mensagem in exc.messages
                )

        if url:
            try:
                validador_url(url)
            except ValidationError:
                erros.append(
                    texto_idioma(
                        f"Anexo {indice}: informe uma URL válida iniciada por http:// ou https://.",
                        f"Archivo adjunto {indice}: informe una URL válida que comience por http:// o https://.",
                        f"Attachment {indice}: provide a valid URL starting with http:// or https://.",
                    )
                )

        if not arquivo and not url:
            erros.append(
                texto_idioma(
                    f"Anexo {indice}: informe um arquivo ou um link externo.",
                    f"Archivo adjunto {indice}: informe un archivo o un enlace externo.",
                    f"Attachment {indice}: provide a file or an external link.",
                )
            )

    return anexos, erros


def adicionar_erros_anexos_ao_formulario(form, erros):
    for erro in erros:
        form.add_error(None, erro)





def estilizar_formulario_autenticacao(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault("class", "form-control")
    return form


@require_http_methods(["GET", "POST"])
def registrar_usuario(request):
    if request.user.is_authenticated:
        return redirect(obter_destino_seguro(request))

    destino_apos_login = obter_destino_seguro(request, padrao="")
    if request.method == "POST":
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                usuario = form.save()
                ConfirmacaoEmailPendente.objects.create(
                    usuario=usuario,
                    destino_apos_login=destino_apos_login,
                )
            try:
                enviar_confirmacao_email(request, usuario)
            except (OSError, SMTPException):
                messages.warning(
                    request,
                    texto_idioma(
                        "Não foi possível enviar a mensagem agora. Sua conta permanece "
                        "pendente e você pode solicitar um novo envio.",
                        "No fue posible enviar el mensaje ahora. Su cuenta permanece "
                        "pendiente y puede solicitar un nuevo envío.",
                        "The message could not be sent now. Your account remains "
                        "pending and you can request another message.",
                    ),
                )
                return redirect(f"{reverse('confirmacao_email_enviada')}?envio=pendente")
            return redirect("confirmacao_email_enviada")
    else:
        form = CadastroUsuarioForm()

    return render(
        request,
        "praticas/registrar_usuario.html",
        {"form": form, "next": destino_apos_login},
    )


@require_safe
def confirmacao_email_enviada(request):
    return render(
        request,
        "praticas/confirmacao_email_enviada.html",
        {"envio_pendente": request.GET.get("envio") == "pendente"},
    )


@require_safe
def confirmar_email(request, uidb64, token):
    User = get_user_model()
    try:
        usuario_id = force_str(urlsafe_base64_decode(uidb64))
        usuario_id = int(usuario_id)
    except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
        usuario_id = None

    destino_apos_login = ""
    confirmado = False
    if usuario_id is not None:
        with transaction.atomic():
            usuario = User.objects.select_for_update().filter(pk=usuario_id).first()
            pendencia = (
                ConfirmacaoEmailPendente.objects.select_for_update()
                .filter(usuario_id=usuario_id)
                .first()
            )
            if (
                usuario is not None
                and not usuario.is_active
                and pendencia is not None
                and confirmacao_email_token.check_token(usuario, token)
            ):
                destino_apos_login = pendencia.destino_apos_login
                usuario.is_active = True
                usuario.save(update_fields=["is_active"])
                pendencia.delete()
                confirmado = True

    if confirmado:
        messages.success(
            request,
            texto_idioma(
                "E-mail confirmado. Entre com suas credenciais para acessar sua conta.",
                "Correo confirmado. Ingrese sus credenciales para acceder a su cuenta.",
                "E-mail confirmed. Sign in with your credentials to access your account.",
            ),
        )
        if destino_apos_login:
            consulta = urlencode({"next": destino_apos_login})
            return redirect(f"{reverse('login_usuario')}?{consulta}")
        return redirect("login_usuario")

    return render(request, "praticas/confirmacao_email_invalida.html", status=400)


@require_http_methods(["GET", "POST"])
def reenviar_confirmacao_email(request):
    form = ReenviarConfirmacaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pendencia = (
            ConfirmacaoEmailPendente.objects.select_related("usuario")
            .filter(
                usuario__email__iexact=form.cleaned_data["email"],
                usuario__is_active=False,
            )
            .order_by("pk")
            .first()
        )
        if pendencia is not None:
            try:
                enviar_confirmacao_email(request, pendencia.usuario)
            except (OSError, SMTPException):
                pass
        return redirect(f"{reverse('reenviar_confirmacao_email')}?enviado=1")

    return render(
        request,
        "praticas/reenviar_confirmacao_email.html",
        {"form": form, "enviado": request.GET.get("enviado") == "1"},
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
    messages.success(
        request,
        texto_idioma(
            "Sessão encerrada com sucesso.",
            "Sesión cerrada correctamente.",
            "Session closed successfully.",
        ),
    )
    return redirect("pagina_inicial")


@login_required(login_url="login_usuario")
def meus_envios(request):
    experiencias = queryset_meus_envios(request.user)
    ferramentas = Ferramenta.objects.all() if request.user.is_staff else Ferramenta.objects.filter(autor=request.user)
    ferramentas = ferramentas.select_related("setor").order_by("-atualizado_em")
    propostas = PropostaEdicaoExperiencia.objects.select_related("experiencia")
    if not request.user.is_staff:
        propostas = propostas.filter(experiencia__autor=request.user)
    propostas = propostas.order_by("-atualizado_em")
    return render(
        request,
        "praticas/meus_envios.html",
        {
            "experiencias": experiencias,
            "ferramentas_enviadas": ferramentas,
            "propostas": propostas,
        },
    )

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
        messages.success(
            request,
            texto_idioma(
                "Experiência removida dos favoritos.",
                "Experiencia eliminada de los favoritos.",
                "Experience removed from favorites.",
            ),
        )
    else:
        ids.append(experiencia.pk)
        messages.success(
            request,
            texto_idioma(
                "Experiência adicionada aos favoritos.",
                "Experiencia añadida a los favoritos.",
                "Experience added to favorites.",
            ),
        )

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


@require_safe
def exemplos_injustica_climatica(request):
    return render(request, "praticas/exemplos_injustica_climatica.html")


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
        Q(experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO)
        | Q(
            experiencias_como_pais_participante__status_publicacao=
            Experiencia.StatusPublicacao.PUBLICADO
        )
    ).distinct()
    efs_lista = EFS.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    ).select_related("pais").distinct()
    tipos = TipoExperiencia.objects.filter(
        experiencias__status_publicacao=Experiencia.StatusPublicacao.PUBLICADO
    )
    if TipoExperiencia.objects.filter(codigo__isnull=False).exists():
        tipos = tipos.filter(codigo__isnull=False)
    tipos = tipos.distinct()
    setores = Setor.objects.filter(codigo__in=SETORES_OFICIAIS_CODIGOS)
    setores_para_filtro = Setor.objects.filter(
        Q(codigo__in=SETORES_OFICIAIS_CODIGOS)
        | Q(pk__in=[valor for valor in request.GET.getlist("setor") if str(valor).isdigit()])
    )
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
    selecoes = {
        "pais": _objetos_selecionados(request, "pais", Pais.objects.all()),
        "efs": _objetos_selecionados(request, "efs", efs_lista),
        "tipo": _objetos_selecionados(request, "tipo", tipos),
        "setor": _objetos_selecionados(request, "setor", setores_para_filtro),
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
        "efs": "efs_id__in",
        "tipo": "tipo_experiencia_id__in",
        "setor": "setor_id__in",
        "tema": "temas_transversais__id__in",
        "norma": "normas_internacionais__id__in",
        "dimensao": "dimensoes_consideradas__id__in",
        "grupo": "grupos_vulneraveis__id__in",
    }
    if selecoes["pais"]:
        paises_ids = [objeto.pk for objeto in selecoes["pais"]]
        experiencias = experiencias.filter(
            Q(pais_id__in=paises_ids)
            | Q(paises_participantes__id__in=paises_ids)
        )
    for chave, campo in campos_filtro.items():
        if selecoes[chave]:
            experiencias = experiencias.filter(
                **{campo: [objeto.pk for objeto in selecoes[chave]]}
            )
    if anos_selecionados:
        experiencias = experiencias.filter(ano_execucao__in=anos_selecionados)
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
    contato_nome = (
        (experiencia.contato_referencia or "").strip()
        or (experiencia.pessoa_responsavel or "").strip()
    )
    contato_email = (experiencia.email_contato or "").strip()
    contato_email_mailto = ""
    if contato_email:
        try:
            validate_email(contato_email)
        except ValidationError:
            pass
        else:
            contato_email_mailto = contato_email

    return render(
        request,
        "praticas/detalhe_experiencia.html",
        {
            "experiencia": experiencia,
            "favoritos_ids": favoritos_ids(request),
            "contato_nome": contato_nome,
            "contato_email": contato_email,
            "contato_email_mailto": contato_email_mailto,
        },
    )


def normas_internacionais(request):
    termo = (request.GET.get("q") or "").strip()[:200]
    paises = Pais.objects.filter(
        normas_internacionais_status__isnull=False
    ).distinct()
    setores = sorted(
        {
            setor.strip()
            for valor in NormaInternacional.objects.exclude(
                setores_aplicaveis=""
            ).values_list("setores_aplicaveis", flat=True)
            for setor in valor.split(",")
            if setor.strip()
        },
        key=str.casefold,
    )
    naturezas_juridicas = list(
        NormaInternacional.objects.exclude(natureza_juridica="")
        .values_list("natureza_juridica", flat=True)
        .distinct()
        .order_by("natureza_juridica")
    )
    paises_selecionados = _objetos_selecionados(
        request, "pais", Pais.objects.all()
    )
    setor_selecionado = (request.GET.get("setor") or "").strip()[:160]
    if setor_selecionado not in setores:
        setor_selecionado = ""
    natureza_selecionada = (request.GET.get("natureza") or "").strip()[:80]
    if natureza_selecionada not in naturezas_juridicas:
        natureza_selecionada = ""

    normas = NormaInternacional.objects.prefetch_related(
        "paises_status__pais"
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

    if paises_selecionados:
        normas = normas.filter(
            paises_status__pais_id__in=[pais.pk for pais in paises_selecionados]
        )
    if setor_selecionado:
        normas = normas.filter(setores_aplicaveis__icontains=setor_selecionado)
    if natureza_selecionada:
        normas = normas.filter(natureza_juridica=natureza_selecionada)

    normas = list(normas.distinct())
    for norma in normas:
        norma.url_publica = _url_http_segura(norma.url_referencia)
        norma.ficha_publica = _url_ficha_tecnica_segura(norma)
        norma.paises_publicos = list(norma.paises_status.all())
        norma.setores_publicos = [
            setor.strip()
            for setor in norma.setores_aplicaveis.split(",")
            if setor.strip()
        ]

    chips = []
    if termo:
        chips.append(
            {
                "rotulo": termo,
                "url_remover": _url_sem_valor_filtro(request, "q"),
            }
        )
    for objeto in paises_selecionados:
        chips.append(
            {
                "rotulo": objeto.nome_exibicao,
                "url_remover": _url_sem_valor_filtro(request, "pais", objeto.pk),
            }
        )
    for chave, valor in (
        ("setor", setor_selecionado),
        ("natureza", natureza_selecionada),
    ):
        if valor:
            chips.append(
                {
                    "rotulo": valor,
                    "url_remover": _url_sem_valor_filtro(request, chave),
                }
            )

    return render(
        request,
        "praticas/normas_internacionais.html",
        {
            "normas": normas,
            "paises": paises,
            "setores": setores,
            "naturezas_juridicas": naturezas_juridicas,
            "paises_selecionados": [item.pk for item in paises_selecionados],
            "setor_selecionado": setor_selecionado,
            "natureza_selecionada": natureza_selecionada,
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


def salvar_perguntas_auditoria(experiencia, perguntas):
    experiencia.perguntas_auditoria.all().delete()
    PerguntaAuditoria.objects.bulk_create(
        [
            PerguntaAuditoria(experiencia=experiencia, texto=texto, ordem=ordem)
            for ordem, texto in enumerate(perguntas, start=1)
        ]
    )


def idioma_submissao_ferramenta(codigo_idioma):
    codigo = (codigo_idioma or "").lower()
    if codigo.startswith("en"):
        return Ferramenta.IdiomaSubmissao.INGLES
    if codigo.startswith("es"):
        return Ferramenta.IdiomaSubmissao.ESPANHOL
    return Ferramenta.IdiomaSubmissao.PORTUGUES


def dados_iniciais_ferramenta(ferramenta):
    campos_idioma = {
        Ferramenta.IdiomaSubmissao.PORTUGUES: ("titulo", "descricao"),
        Ferramenta.IdiomaSubmissao.ESPANHOL: ("titulo_es", "descricao_es"),
        Ferramenta.IdiomaSubmissao.INGLES: ("titulo_en", "descricao_en"),
    }
    campo_titulo, campo_descricao = campos_idioma.get(
        ferramenta.idioma_submissao,
        ("titulo_es", "descricao_es"),
    )
    return {
        "nome": getattr(ferramenta, campo_titulo),
        "ano": ferramenta.ano,
        "descricao": getattr(ferramenta, campo_descricao),
        "setor": ferramenta.setor_id,
        "link_acesso": ferramenta.url,
        "pais_ou_instancia": ferramenta.pais_ou_instancia,
    }


def salvar_ferramenta_submetida(form, usuario, situacao, ferramenta=None):
    dados = form.cleaned_data
    if ferramenta is None:
        base_codigo = slugify(dados.get("nome") or "ferramenta")[:140] or "ferramenta"
        codigo = base_codigo
        sufixo = 2
        while Ferramenta.objects.filter(codigo=codigo).exists():
            codigo = f"{base_codigo}-{sufixo}"
            sufixo += 1
        proxima_ordem = (Ferramenta.objects.aggregate(maior=Max("ordem"))["maior"] or 0) + 1
        ferramenta = Ferramenta(
            autor=usuario,
            codigo=codigo,
            ordem=proxima_ordem,
        )
        ferramenta.idioma_submissao = idioma_submissao_ferramenta(
            getattr(form, "language_code", None)
        )

    nome = dados.get("nome", "")
    descricao = dados.get("descricao", "")
    if ferramenta.idioma_submissao == Ferramenta.IdiomaSubmissao.INGLES:
        ferramenta.titulo_en = nome
        ferramenta.descricao_en = descricao
    elif ferramenta.idioma_submissao == Ferramenta.IdiomaSubmissao.PORTUGUES:
        ferramenta.titulo = nome
        ferramenta.descricao = descricao
    else:
        ferramenta.titulo_es = nome
        ferramenta.descricao_es = descricao
    ferramenta.ano = dados.get("ano")
    ferramenta.periodo = str(dados.get("ano") or "")
    ferramenta.pais_ou_instancia = dados.get("pais_ou_instancia", "")
    ferramenta.responsavel = dados.get("pais_ou_instancia", "")
    ferramenta.setor = dados.get("setor")
    ferramenta.url = dados.get("link_acesso", "")
    ferramenta.situacao = situacao
    ferramenta.save()
    return ferramenta


@login_required(login_url="login_usuario")
def adicionar_boa_pratica(request):
    tipo_compartilhamento = (
        request.POST.get("tipo_compartilhamento")
        or request.GET.get("tipo")
        or ""
    )
    if (
        request.method == "POST"
        and not tipo_compartilhamento
        and any(
            campo in request.POST
            for campo in ("titulo", "tipo_experiencia", "descricao", "acao_envio")
        )
    ):
        # Compatibilidade com formulários abertos antes da introdução da etapa
        # de escolha. Um tipo explicitamente inválido continua sendo rejeitado.
        tipo_compartilhamento = "boa_pratica"
    tipos_validos = {"boa_pratica", "ferramenta"}
    if request.method == "POST" and tipo_compartilhamento not in tipos_validos:
        return render(
            request,
            "praticas/escolher_compartilhamento.html",
            {"escolha_invalida": True},
            status=400,
        )
    if not tipo_compartilhamento:
        return render(request, "praticas/escolher_compartilhamento.html")

    acao = request.POST.get("acao_envio", "enviar")
    obrigatorio_para_envio = acao != "rascunho"

    if tipo_compartilhamento == "ferramenta":
        if request.method == "POST":
            form = FerramentaSubmissaoForm(
                request.POST,
                obrigatorio_para_envio=obrigatorio_para_envio,
            )
            form.language_code = getattr(request, "LANGUAGE_CODE", "pt-br")
            if form.is_valid():
                with transaction.atomic():
                    salvar_ferramenta_submetida(
                        form,
                        request.user,
                        Ferramenta.Situacao.RASCUNHO
                        if acao == "rascunho"
                        else Ferramenta.Situacao.ENVIADA,
                    )
                messages.success(
                    request,
                    texto_idioma(
                        "Ferramenta salva como rascunho."
                        if acao == "rascunho"
                        else "Ferramenta enviada para revisão.",
                        "Herramienta guardada como borrador."
                        if acao == "rascunho"
                        else "Herramienta enviada para revisión.",
                        "Tool saved as a draft."
                        if acao == "rascunho"
                        else "Tool submitted for review.",
                    ),
                )
                if acao == "rascunho":
                    return redirect("meus_envios")
                return redirect(f"{reverse('confirmacao_envio')}?tipo=ferramenta")
        else:
            form = FerramentaSubmissaoForm()
        return render(
            request,
            "praticas/submeter_ferramenta.html",
            {"form": form, "tipo_compartilhamento": "ferramenta"},
        )

    if request.method == "POST":
        form = ExperienciaSubmissaoForm(
            request.POST,
            request.FILES,
            obrigatorio_para_envio=obrigatorio_para_envio,
        )
        anexos, erros_anexos = validar_anexos_request(request)

        if form.is_valid() and not erros_anexos:
            with transaction.atomic():
                experiencia = form.save(commit=False)
                experiencia.autor = request.user
                experiencia.status_iniciativa = Experiencia.StatusIniciativa.CONCLUIDA
                if request.user.is_authenticated and not experiencia.email_contato:
                    experiencia.email_contato = request.user.email
                if request.user.is_authenticated and not experiencia.pessoa_responsavel:
                    experiencia.pessoa_responsavel = request.user.get_full_name() or request.user.username
                if acao == "rascunho":
                    experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                    mensagem = texto_idioma(
                        "Rascunho salvo com sucesso. Ele ainda não foi enviado para revisão.",
                        "Borrador guardado correctamente. Todavía no se ha enviado para revisión.",
                        "Draft saved successfully. It has not yet been submitted for review.",
                    )
                else:
                    experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
                    mensagem = texto_idioma(
                        "Boa prática enviada com sucesso. Ela ficará pendente até a revisão.",
                        "Buena práctica enviada correctamente. Permanecerá pendiente hasta la revisión.",
                        "Good practice submitted successfully. It will remain pending until review.",
                    )
                experiencia.save()
                form.save_m2m()
                salvar_perguntas_auditoria(
                    experiencia, form.perguntas_auditoria_limpas
                )
                salvar_anexos_submissao(experiencia, anexos)
                if experiencia.status_publicacao == Experiencia.StatusPublicacao.ENVIADO:
                    agendar_notificacoes_nova_submissao(request, experiencia)

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

    return render(
        request,
        "praticas/adicionar_boa_pratica.html",
        {
            "form": form,
            "tipo_compartilhamento": "boa_pratica",
            "perguntas_auditoria": form.perguntas_auditoria_valores,
        },
    )


@login_required(login_url="login_usuario")
def editar_ferramenta(request, pk):
    ferramenta = get_object_or_404(Ferramenta.objects.select_related("setor"), pk=pk)
    pertence_ao_usuario = ferramenta.autor_id == request.user.id
    if not request.user.is_staff and not pertence_ao_usuario:
        messages.error(
            request,
            texto_idioma(
                "Você não tem permissão para editar esta ferramenta.",
                "No tiene permiso para editar esta herramienta.",
                "You do not have permission to edit this tool.",
            ),
        )
        return redirect("meus_envios")
    if ferramenta.situacao == Ferramenta.Situacao.PUBLICADA:
        messages.error(
            request,
            texto_idioma(
                "Ferramentas publicadas não podem ser alteradas por este fluxo.",
                "Las herramientas publicadas no pueden modificarse mediante este flujo.",
                "Published tools cannot be changed through this workflow.",
            ),
        )
        return redirect("meus_envios")
    if not request.user.is_staff and ferramenta.situacao != Ferramenta.Situacao.RASCUNHO:
        messages.error(
            request,
            texto_idioma(
                "Somente rascunhos podem ser retomados para edição.",
                "Solo los borradores pueden retomarse para su edición.",
                "Only drafts can be resumed for editing.",
            ),
        )
        return redirect("meus_envios")

    acao = request.POST.get("acao_envio", "rascunho")
    obrigatorio_para_envio = acao != "rascunho"
    if request.method == "POST":
        form = FerramentaSubmissaoForm(
            request.POST,
            obrigatorio_para_envio=obrigatorio_para_envio,
        )
        form.language_code = ferramenta.idioma_submissao
        if form.is_valid():
            with transaction.atomic():
                salvar_ferramenta_submetida(
                    form,
                    ferramenta.autor or request.user,
                    Ferramenta.Situacao.RASCUNHO
                    if acao == "rascunho"
                    else Ferramenta.Situacao.ENVIADA,
                    ferramenta=ferramenta,
                )
            messages.success(
                request,
                texto_idioma(
                    "Rascunho da ferramenta atualizado."
                    if acao == "rascunho"
                    else "Ferramenta enviada para revisão.",
                    "Borrador de la herramienta actualizado."
                    if acao == "rascunho"
                    else "Herramienta enviada para revisión.",
                    "Tool draft updated."
                    if acao == "rascunho"
                    else "Tool submitted for review.",
                ),
            )
            return redirect("meus_envios")
    else:
        form = FerramentaSubmissaoForm(
            initial=dados_iniciais_ferramenta(ferramenta),
            obrigatorio_para_envio=False,
        )

    return render(
        request,
        "praticas/submeter_ferramenta.html",
        {
            "form": form,
            "ferramenta": ferramenta,
            "edicao": True,
            "tipo_compartilhamento": "ferramenta",
        },
    )


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
            texto_idioma(
                "Não foi possível validar sua permissão para edição deste envio.",
                "No fue posible validar su permiso para editar este envío.",
                "Your permission to edit this submission could not be validated.",
            ),
        )
        return redirect("meus_envios")

    if experiencia.status_publicacao == Experiencia.StatusPublicacao.PUBLICADO:
        return redirect("solicitar_edicao_publicada", pk=experiencia.pk)

    status_anterior = experiencia.status_publicacao
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
            with transaction.atomic():
                Anexo.objects.filter(experiencia=experiencia, id__in=ids_remover).delete()
                experiencia = form.save(commit=False)
                if request.user.is_authenticated and not experiencia.autor_id:
                    experiencia.autor = request.user
                if acao == "rascunho":
                    experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                    mensagem = texto_idioma(
                        "Alterações salvas como rascunho.",
                        "Cambios guardados como borrador.",
                        "Changes saved as draft.",
                    )
                else:
                    experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
                    mensagem = texto_idioma(
                        "Boa prática reenviada para revisão.",
                        "Buena práctica reenviada para revisión.",
                        "Good practice resubmitted for review.",
                    )
                experiencia.save()
                form.save_m2m()
                salvar_perguntas_auditoria(
                    experiencia, form.perguntas_auditoria_limpas
                )
                salvar_anexos_submissao(experiencia, anexos)
                if (
                    status_anterior != Experiencia.StatusPublicacao.ENVIADO
                    and experiencia.status_publicacao == Experiencia.StatusPublicacao.ENVIADO
                ):
                    agendar_notificacoes_nova_submissao(request, experiencia)

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
            "perguntas_auditoria": form.perguntas_auditoria_valores,
        },
    )


def dados_proposta_from_form(form):
    dados = {}
    campos_many_to_many = {
        "paises_participantes",
        "temas_transversais",
        "normas_internacionais",
    }
    campos_fk = {"efs", "pais", "tipo_experiencia", "setor"}

    for campo in ExperienciaSubmissaoForm.Meta.fields:
        valor = form.cleaned_data.get(campo)

        if campo in campos_many_to_many:
            dados[campo] = [item.pk for item in valor]
        elif campo in campos_fk:
            dados[campo] = valor.pk if valor else None
        else:
            dados[campo] = valor

    dados["perguntas_auditoria"] = form.perguntas_auditoria_limpas
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
        messages.error(
            request,
            texto_idioma(
                "Não foi possível validar sua permissão para solicitar edição.",
                "No fue posible validar su permiso para solicitar la edición.",
                "Your permission to request an edit could not be validated.",
            ),
        )
        return redirect("meus_envios")

    if request.method == "POST":
        form = PropostaEdicaoPublicadaForm(
            request.POST,
            instance=experiencia,
            obrigatorio_para_envio=True,
        )
        if form.is_valid():
            email_solicitante = primeiro_email_valido(
                request.user.email,
                experiencia.email_contato,
            )
            with transaction.atomic():
                proposta = PropostaEdicaoExperiencia.objects.create(
                    experiencia=experiencia,
                    email_contato=email_solicitante,
                    comentario_autor=form.cleaned_data.get("comentario_autor", ""),
                    dados_json=dados_proposta_from_form(form),
                    status=PropostaEdicaoExperiencia.Status.PENDENTE,
                )
                agendar_notificacoes_solicitacao_edicao(
                    request, proposta, proposta.email_contato
                )
            messages.success(
                request,
                texto_idioma(
                    "Proposta de edição enviada para revisão. A versão publicada permanecerá ativa até aprovação.",
                    "Propuesta de edición enviada para revisión. La versión publicada permanecerá activa hasta su aprobación.",
                    "Edit proposal submitted for review. The published version will remain active until approval.",
                ),
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
            "perguntas_auditoria": form.perguntas_auditoria_valores,
        },
    )



CAMPOS_COMPARACAO_EDICAO = [
    ("titulo", EXPERIENCIA_LABELS["titulo"]),
    ("efs", EXPERIENCIA_LABELS["efs"]),
    ("pais", EXPERIENCIA_LABELS["pais"]),
    ("paises_participantes", EXPERIENCIA_LABELS["paises_participantes"]),
    ("tipo_experiencia", EXPERIENCIA_LABELS["tipo_experiencia"]),
    ("tipo_auditoria", EXPERIENCIA_LABELS["tipo_auditoria"]),
    ("outras_efs_envolvidas", EXPERIENCIA_LABELS["outras_efs_envolvidas"]),
    ("setor", EXPERIENCIA_LABELS["setor"]),
    ("temas_transversais", EXPERIENCIA_LABELS["temas_transversais"]),
    ("normas_internacionais", EXPERIENCIA_LABELS["normas_internacionais"]),
    ("email_contato", EXPERIENCIA_LABELS["email_contato"]),
    ("pessoa_responsavel", EXPERIENCIA_LABELS["pessoa_responsavel"]),
    ("descricao", EXPERIENCIA_LABELS["descricao"]),
    (
        "enfoque_justica_climatica",
        EXPERIENCIA_LABELS["enfoque_justica_climatica"],
    ),
    ("objetivo", EXPERIENCIA_LABELS["objetivo"]),
    (
        "perguntas_auditoria",
        {
            "pt": "Perguntas de auditoria",
            "es": "Preguntas de auditoría",
            "en": "Audit questions",
        },
    ),
    ("criterios_utilizados", EXPERIENCIA_LABELS["criterios_utilizados"]),
    ("metodologia", EXPERIENCIA_LABELS["metodologia"]),
    ("ferramentas_utilizadas", EXPERIENCIA_LABELS["ferramentas_utilizadas"]),
    ("resultados", EXPERIENCIA_LABELS["resultados"]),
    ("recomendacoes", EXPERIENCIA_LABELS["recomendacoes"]),
    ("replicabilidade", EXPERIENCIA_LABELS["replicabilidade"]),
    ("informacoes_adicionais", EXPERIENCIA_LABELS["informacoes_adicionais"]),
    ("ano_execucao", EXPERIENCIA_LABELS["ano_execucao"]),
    (
        "contribui_para_guia",
        {
            "pt": "Contribui para a Guia",
            "es": "Contribuye a la Guía",
            "en": "Contribution to the Guide",
        },
    ),
]


def texto_booleano(valor):
    if valor:
        return texto_idioma("Sim", "Sí", "Yes")
    return texto_idioma("Não", "No", "No")


def texto_lista_objetos(objetos):
    nomes = [getattr(item, "nome_exibicao", str(item)) for item in objetos]
    return ", ".join(nomes) if nomes else "-"


def valor_atual_para_comparacao(experiencia, campo):
    if campo in {"efs", "pais", "tipo_experiencia", "setor"}:
        objeto = getattr(experiencia, campo, None)
        return getattr(objeto, "nome_exibicao", str(objeto)) if objeto else "-"

    if campo in {"paises_participantes", "temas_transversais", "normas_internacionais"}:
        return texto_lista_objetos(getattr(experiencia, campo).all())

    if campo == "perguntas_auditoria":
        return "\n".join(
            experiencia.perguntas_auditoria.order_by("ordem").values_list(
                "texto", flat=True
            )
        ) or "-"

    if campo == "tipo_auditoria":
        return experiencia.tipo_auditoria_exibicao or "-"

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

    if campo == "paises_participantes":
        return texto_lista_objetos(Pais.objects.filter(pk__in=valor or []))

    if campo == "perguntas_auditoria":
        return "\n".join(valor or []) or "-"

    if campo == "tipo_auditoria":
        traducoes = {
            Experiencia.TipoAuditoria.DESEMPENHO: ("Desempenho", "Desempeño", "Performance"),
            Experiencia.TipoAuditoria.CUMPRIMENTO: ("Cumprimento", "Cumplimiento", "Compliance"),
            Experiencia.TipoAuditoria.FINANCEIRA: ("Financeira", "Financiera", "Financial"),
        }
        return texto_idioma(*traducoes[valor]) if valor in traducoes else "-"

    if campo == "contribui_para_guia":
        return texto_booleano(bool(valor))

    if valor is None or valor == "":
        return "-"

    return str(valor)


def montar_comparativo_proposta_edicao(proposta):
    experiencia = proposta.experiencia
    linhas = []

    for campo, traducoes_rotulo in CAMPOS_COMPARACAO_EDICAO:
        valor_atual = valor_atual_para_comparacao(experiencia, campo)
        valor_proposto = valor_proposto_para_comparacao(proposta, campo)
        alterado = valor_atual.strip() != valor_proposto.strip()
        rotulo = texto_idioma(
            traducoes_rotulo["pt"],
            traducoes_rotulo["es"],
            traducoes_rotulo["en"],
        )

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
        "paises_participantes": Pais,
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
    if "perguntas_auditoria" in dados:
        salvar_perguntas_auditoria(
            experiencia,
            [texto for texto in dados.get("perguntas_auditoria", []) if texto],
        )


def confirmacao_envio(request):
    return render(
        request,
        "praticas/confirmacao_envio.html",
        {"ferramenta_enviada": request.GET.get("tipo") == "ferramenta"},
    )


@login_required(login_url="login_usuario")
def status_envio(request):
    experiencias = queryset_meus_envios(request.user)
    ferramentas = Ferramenta.objects.all() if request.user.is_staff else Ferramenta.objects.filter(autor=request.user)
    ferramentas = ferramentas.select_related("setor").order_by("-atualizado_em")
    propostas = PropostaEdicaoExperiencia.objects.select_related("experiencia")
    if not request.user.is_staff:
        propostas = propostas.filter(experiencia__autor=request.user)
    propostas = propostas.order_by("-atualizado_em")

    return render(
        request,
        "praticas/status_envio.html",
        {
            "experiencias": experiencias,
            "ferramentas_enviadas": ferramentas,
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
            status_anterior = experiencia.status_publicacao
            experiencia.comentario_revisor = form.cleaned_data["comentario_revisor"]

            if acao == "em_revisao":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.EM_REVISAO
                mensagem = texto_idioma(
                    "Experiência marcada como em revisão.",
                    "Experiencia marcada como en revisión.",
                    "Experience marked as under review.",
                )
            elif acao == "aprovar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = texto_idioma(
                    "Experiência aprovada e publicada no catálogo público.",
                    "Experiencia aprobada y publicada en el catálogo público.",
                    "Experience approved and published in the public catalog.",
                )
            elif acao == "publicar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = texto_idioma(
                    "Experiência publicada no catálogo público.",
                    "Experiencia publicada en el catálogo público.",
                    "Experience published in the public catalog.",
                )
            elif acao == "devolver":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                mensagem = texto_idioma(
                    "Experiência devolvida para ajustes.",
                    "Experiencia devuelta para ajustes.",
                    "Experience returned for adjustments.",
                )
            elif acao == "rejeitar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.REJEITADO
                mensagem = texto_idioma(
                    "Experiência rejeitada.",
                    "Experiencia rechazada.",
                    "Experience rejected.",
                )
            else:
                mensagem = texto_idioma(
                    "Revisão registrada.",
                    "Revisión registrada.",
                    "Review recorded.",
                )

            with transaction.atomic():
                experiencia.save(update_fields=["status_publicacao", "comentario_revisor", "atualizado_em"])
                if (
                    experiencia.status_publicacao != status_anterior
                    and acao in {"aprovar", "publicar", "devolver", "rejeitar"}
                ):
                    agendar_notificacao_status_experiencia(
                        request, experiencia, acao
                    )
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
            status_anterior = proposta.status
            proposta.comentario_revisor = form.cleaned_data["comentario_revisor"]

            with transaction.atomic():
                if acao == "em_revisao":
                    proposta.status = PropostaEdicaoExperiencia.Status.EM_REVISAO
                    mensagem = texto_idioma(
                        "Proposta marcada como em revisão.",
                        "Propuesta marcada como en revisión.",
                        "Proposal marked as under review.",
                    )
                elif acao == "aprovar":
                    aplicar_proposta_edicao(proposta)
                    proposta.status = PropostaEdicaoExperiencia.Status.APROVADA
                    mensagem = texto_idioma(
                        "Proposta aprovada e aplicada à experiência publicada.",
                        "Propuesta aprobada y aplicada a la experiencia publicada.",
                        "Proposal approved and applied to the published experience.",
                    )
                elif acao == "rejeitar":
                    proposta.status = PropostaEdicaoExperiencia.Status.REJEITADA
                    mensagem = texto_idioma(
                        "Proposta de edição rejeitada.",
                        "Propuesta de edición rechazada.",
                        "Edit proposal rejected.",
                    )
                else:
                    mensagem = texto_idioma(
                        "Revisão registrada.",
                        "Revisión registrada.",
                        "Review recorded.",
                    )

                proposta.save(update_fields=["status", "comentario_revisor", "atualizado_em"])
                if (
                    proposta.status != status_anterior
                    and acao in {"aprovar", "rejeitar"}
                ):
                    agendar_notificacao_decisao_edicao(request, proposta, acao)
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
@require_http_methods(["GET", "POST"])
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
            messages.error(
                request,
                texto_idioma(
                    "Confirmação de exclusão inválida.",
                    "Confirmación de eliminación no válida.",
                    "Invalid deletion confirmation.",
                ),
            )
            return redirect("excluir_boa_pratica", pk=experiencia.pk)

        titulo = experiencia.titulo_exibicao
        for anexo in experiencia.anexos.all():
            if anexo.arquivo:
                anexo.arquivo.delete(save=False)
        experiencia.delete()
        messages.success(
            request,
            texto_idioma(
                f"Boa prática excluída com sucesso: {titulo}",
                f"Buena práctica eliminada correctamente: {titulo}",
                f"Good practice deleted successfully: {titulo}",
            ),
        )
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
    )
    if Setor.objects.filter(codigo__isnull=False).exists():
        setores = setores.filter(codigo__isnull=False)
    setores = setores.distinct().order_by("nome_es", "nome")
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


GUIA_ROTAS_PUBLICAS = {
    "guia_rota_inicio": "guia_inicio",
    "guia_rota_eixos": "guia_eixos",
    "guia_rota_eixo": "guia_eixo",
    "guia_rota_subeixo": "guia_subeixo",
    "guia_rota_setores": "guia_setores",
    "guia_rota_setor": "guia_setor",
    "guia_rota_subarea": "guia_subarea",
}

GUIA_ROTAS_PREVIEW = {
    "guia_rota_inicio": "guia_preview_inicio",
    "guia_rota_eixos": "guia_preview_eixos",
    "guia_rota_eixo": "guia_preview_eixo",
    "guia_rota_subeixo": "guia_preview_subeixo",
    "guia_rota_setores": "guia_preview_setores",
    "guia_rota_setor": "guia_preview_setor",
    "guia_rota_subarea": "guia_preview_subarea",
}


def _exigir_guia_publico_habilitado():
    if not settings.GUIA_PUBLICO_HABILITADO:
        raise Http404


def _contexto_navegacao_guia(*, preview_interna):
    rotas = GUIA_ROTAS_PREVIEW if preview_interna else GUIA_ROTAS_PUBLICAS
    return {"guia_preview_interna": preview_interna, **rotas}


def _render_guia_inicio(request, *, preview_interna):
    versao = obter_versao_publicada_vigente()
    contexto = {
        "versao": versao,
        "eixos": listar_eixos(versao) if versao else (),
        "setores": listar_setores(versao) if versao else (),
    }
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(
        request,
        "praticas/guia_preview/inicio.html",
        contexto,
    )


def _render_guia_eixos(request, *, preview_interna):
    versao = obter_versao_publicada_vigente()
    contexto = {
        "versao": versao,
        "eixos": listar_eixos(versao) if versao else (),
    }
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(
        request,
        "praticas/guia_preview/eixos.html",
        contexto,
    )


def _render_guia_eixo(request, eixo_codigo, *, preview_interna):
    versao = obter_versao_publicada_vigente()
    eixo = get_object_or_404(
        queryset_eixo_detalhado(versao),
        codigo=eixo_codigo,
    )
    contexto = {
        "versao": versao,
        "eixo": eixo,
        "subeixos": eixo.subeixos_preview,
    }
    contexto.update(_contexto_perguntas(eixo.perguntas_preview))
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(request, "praticas/guia_preview/eixo_detalhe.html", contexto)


def _render_guia_subeixo(
    request, eixo_codigo, subeixo_codigo, *, preview_interna
):
    versao = obter_versao_publicada_vigente()
    subeixo = get_object_or_404(
        queryset_subeixo_detalhado(versao, eixo_codigo),
        codigo=subeixo_codigo,
    )
    contexto = {
        "versao": versao,
        "eixo": subeixo.eixo,
        "subeixo": subeixo,
    }
    contexto.update(_contexto_perguntas(subeixo.perguntas_preview))
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(request, "praticas/guia_preview/subeixo_detalhe.html", contexto)


def _render_guia_setores(request, *, preview_interna):
    versao = obter_versao_publicada_vigente()
    contexto = {
        "versao": versao,
        "setores": listar_setores(versao) if versao else (),
    }
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(
        request,
        "praticas/guia_preview/setores.html",
        contexto,
    )


def _render_guia_setor(request, setor_codigo, *, preview_interna):
    versao = obter_versao_publicada_vigente()
    setor = get_object_or_404(
        queryset_setor_detalhado(versao),
        codigo=setor_codigo,
    )
    contexto = {
        "versao": versao,
        "setor": setor,
        "subareas": setor.subareas_preview,
    }
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(
        request,
        "praticas/guia_preview/setor_detalhe.html",
        contexto,
    )


def _render_guia_subarea(
    request, setor_codigo, subarea_codigo, *, preview_interna
):
    versao = obter_versao_publicada_vigente()
    subarea = get_object_or_404(
        queryset_subarea_detalhada(versao, setor_codigo),
        codigo=subarea_codigo,
    )
    contexto = {
        "versao": versao,
        "setor": subarea.setor,
        "subarea": subarea,
        "ocorrencias_referencias": subarea.ocorrencias_referencias_preview,
    }
    contexto.update(_contexto_perguntas(subarea.perguntas_preview))
    contexto.update(_contexto_navegacao_guia(preview_interna=preview_interna))
    return render(request, "praticas/guia_preview/subarea_detalhe.html", contexto)


@require_safe
def guia_inicio(request):
    _exigir_guia_publico_habilitado()
    return _render_guia_inicio(request, preview_interna=False)


@require_safe
def guia_eixos(request):
    _exigir_guia_publico_habilitado()
    return _render_guia_eixos(request, preview_interna=False)


@require_safe
def guia_eixo(request, eixo_codigo):
    _exigir_guia_publico_habilitado()
    return _render_guia_eixo(request, eixo_codigo, preview_interna=False)


@require_safe
def guia_subeixo(request, eixo_codigo, subeixo_codigo):
    _exigir_guia_publico_habilitado()
    return _render_guia_subeixo(
        request,
        eixo_codigo,
        subeixo_codigo,
        preview_interna=False,
    )


@require_safe
def guia_setores(request):
    _exigir_guia_publico_habilitado()
    return _render_guia_setores(request, preview_interna=False)


@require_safe
def guia_setor(request, setor_codigo):
    _exigir_guia_publico_habilitado()
    return _render_guia_setor(request, setor_codigo, preview_interna=False)


@require_safe
def guia_subarea(request, setor_codigo, subarea_codigo):
    _exigir_guia_publico_habilitado()
    return _render_guia_subarea(
        request,
        setor_codigo,
        subarea_codigo,
        preview_interna=False,
    )


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_inicio(request):
    return _render_guia_inicio(request, preview_interna=True)


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_eixos(request):
    return _render_guia_eixos(request, preview_interna=True)


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_eixo(request, eixo_codigo):
    return _render_guia_eixo(request, eixo_codigo, preview_interna=True)


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_subeixo(request, eixo_codigo, subeixo_codigo):
    return _render_guia_subeixo(
        request,
        eixo_codigo,
        subeixo_codigo,
        preview_interna=True,
    )


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_setores(request):
    return _render_guia_setores(request, preview_interna=True)


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_setor(request, setor_codigo):
    return _render_guia_setor(request, setor_codigo, preview_interna=True)


@staff_member_required(login_url="login_usuario")
@require_safe
def guia_preview_subarea(request, setor_codigo, subarea_codigo):
    return _render_guia_subarea(
        request,
        setor_codigo,
        subarea_codigo,
        preview_interna=True,
    )
