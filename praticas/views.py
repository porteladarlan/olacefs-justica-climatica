import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    ConsultaStatusForm,
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
    GrupoVulneravel,
    NormaInternacional,
    Pais,
    PropostaEdicaoExperiencia,
    Setor,
    TemaTransversal,
    TipoExperiencia,
)

# ConfiguraÃ§Ãµes padrÃ£o para anexos.
# MantÃ©m compatibilidade com validaÃ§Ãµes de upload em testes e ambiente local.
ANEXO_LIMITE_POR_EXPERIENCIA = 5
ANEXO_TAMANHO_MAX_MB = 10
ANEXO_TAMANHO_MAX_BYTES = ANEXO_TAMANHO_MAX_MB * 1024 * 1024
ANEXO_TAMANHO_MAXIMO_BYTES = ANEXO_TAMANHO_MAX_BYTES
ANEXO_EXTENSOES_PERMITIDAS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv",
    ".png", ".jpg", ".jpeg", ".geojson", ".zip",
}
ANEXO_CONTENT_TYPES_PERMITIDOS = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "image/png",
    "image/jpeg",
    "application/geo+json",
    "application/json",
    "application/zip",
    "application/x-zip-compressed",
}

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


STATUS_VISIVEIS_REVISAO = [
    Experiencia.StatusPublicacao.ENVIADO,
    Experiencia.StatusPublicacao.EM_REVISAO,
    Experiencia.StatusPublicacao.APROVADO,
    Experiencia.StatusPublicacao.REJEITADO,
]


def experiencia_pertence_ao_usuario(experiencia, usuario, email_informado=None):
    if usuario and usuario.is_authenticated and usuario.is_staff:
        return True

    email_experiencia = (experiencia.email_contato or "").strip().lower()
    email_informado = (email_informado or "").strip().lower()

    if email_informado and email_experiencia and email_informado == email_experiencia:
        return True

    if not usuario or not usuario.is_authenticated:
        return False

    if getattr(experiencia, "autor_id", None) and experiencia.autor_id == usuario.id:
        return True

    email_usuario = (getattr(usuario, "email", "") or "").strip().lower()
    return bool(email_usuario and email_experiencia and email_usuario == email_experiencia)

def queryset_meus_envios(usuario):
    if not usuario or not usuario.is_authenticated:
        return Experiencia.objects.none()

    filtros = Q()
    if getattr(usuario, "email", ""):
        filtros |= Q(email_contato__iexact=usuario.email)
    filtros |= Q(autor=usuario)

    return (
        Experiencia.objects.filter(filtros)
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .distinct()
        .order_by("-atualizado_em")
    )

def obter_anexos_do_request(request):
    anexos = []
    for indice in range(1, ANEXO_LIMITE_POR_EXPERIENCIA + 1):
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

    quantidade_final = quantidade_existente - len(ids_remover) + len(anexos)
    if quantidade_final > ANEXO_LIMITE_POR_EXPERIENCIA:
        erros.append(
            f"Ã‰ permitido manter no mÃ¡ximo {ANEXO_LIMITE_POR_EXPERIENCIA} anexos por experiÃªncia."
        )

    for anexo in anexos:
        indice = anexo["indice"]
        arquivo = anexo["arquivo"]
        url = anexo["url"]

        if arquivo:
            extensao = Path(arquivo.name).suffix.lower()
            if extensao not in ANEXO_EXTENSOES_PERMITIDAS:
                erros.append(
                    f"Anexo {indice}: tipo de arquivo nÃ£o permitido. Use PDF, Word ou Excel."
                )
            if arquivo.size > ANEXO_TAMANHO_MAXIMO_BYTES:
                erros.append(
                    f"Anexo {indice}: arquivo maior que {ANEXO_TAMANHO_MAXIMO_MB} MB."
                )

        if url:
            try:
                validador_url(url)
            except ValidationError:
                erros.append(
                    f"Anexo {indice}: informe uma URL vÃ¡lida iniciada por http:// ou https://."
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
    messages.success(request, "SessÃ£o encerrada com sucesso.")
    return redirect("pagina_inicial")


@login_required(login_url="login_usuario")
def meus_envios(request):
    experiencias = queryset_meus_envios(request.user)
    propostas = (
        PropostaEdicaoExperiencia.objects.filter(email_contato__iexact=request.user.email)
        .select_related("experiencia")
        .order_by("-atualizado_em")
    )
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
        messages.success(request, "ExperiÃªncia removida dos favoritos.")
    else:
        ids.append(experiencia.pk)
        messages.success(request, "ExperiÃªncia adicionada aos favoritos.")

    salvar_favoritos_ids(request, ids)
    destino = request.POST.get("next") or request.GET.get("next") or "catalogo_experiencias"
    return redirect(destino)


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
        "experiencias_destacadas": experiencias.filter(Q(destacado=True) | Q(relevante=True))[:3],
    }
    return render(request, "praticas/pagina_inicial.html", contexto)


def catalogo_experiencias(request):
    experiencias = (
        experiencias_publicas()
        .select_related("efs", "pais", "tipo_experiencia", "setor")
        .prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "dimensoes_consideradas",
            "grupos_vulneraveis",
        )
        .distinct()
    )

    pais_id = request.GET.get("pais")
    efs_id = request.GET.get("efs")
    tipo_id = request.GET.get("tipo")
    setor_id = request.GET.get("setor")
    tema_id = request.GET.get("tema")
    norma_id = request.GET.get("norma")
    dimensao_id = request.GET.get("dimensao")
    grupo_id = request.GET.get("grupo")
    ano = request.GET.get("ano")
    termo = request.GET.get("q")

    if pais_id:
        experiencias = experiencias.filter(pais_id=pais_id)
    if efs_id:
        experiencias = experiencias.filter(efs_id=efs_id)
    if tipo_id:
        experiencias = experiencias.filter(tipo_experiencia_id=tipo_id)
    if setor_id:
        experiencias = experiencias.filter(setor_id=setor_id)
    if tema_id:
        experiencias = experiencias.filter(temas_transversais__id=tema_id)
    if norma_id:
        experiencias = experiencias.filter(normas_internacionais__id=norma_id)
    if dimensao_id:
        experiencias = experiencias.filter(dimensoes_consideradas__id=dimensao_id)
    if grupo_id:
        experiencias = experiencias.filter(grupos_vulneraveis__id=grupo_id)
    if ano:
        experiencias = experiencias.filter(ano_execucao=ano)

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
        ).distinct()

    contexto = {
        "experiencias": experiencias,
        "paises": Pais.objects.all(),
        "efs_lista": EFS.objects.select_related("pais").all(),
        "tipos": TipoExperiencia.objects.all(),
        "setores": Setor.objects.all(),
        "temas": TemaTransversal.objects.all(),
        "normas": NormaInternacional.objects.all(),
        "dimensoes": DimensaoJusticaClimatica.objects.all(),
        "grupos": GrupoVulneravel.objects.all(),
        "anos": (
            Experiencia.objects.values_list("ano_execucao", flat=True)
            .distinct()
            .order_by("-ano_execucao")
        ),
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
    normas = NormaInternacional.objects.all()
    return render(request, "praticas/normas_internacionais.html", {"normas": normas})


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
                mensagem = "Rascunho salvo com sucesso. Ele ainda nÃ£o foi enviado para revisÃ£o."
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


def editar_boa_pratica(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related(
            "temas_transversais",
            "normas_internacionais",
            "anexos",
        ),
        pk=pk,
    )

    email = request.GET.get("email") or request.POST.get("email_contato_original")
    if not experiencia_pertence_ao_usuario(experiencia, request.user, email):
        messages.error(
            request,
            "NÃ£o foi possÃ­vel validar sua permissÃ£o para ediÃ§Ã£o deste envio.",
        )
        return redirect("meus_envios" if request.user.is_authenticated else "status_envio")

    email = email or experiencia.email_contato or request.user.email

    if experiencia.status_publicacao == Experiencia.StatusPublicacao.PUBLICADO:
        return redirect(f"/solicitar-edicao-publicada/{experiencia.pk}/?email={email}")

    acao = request.POST.get("acao_envio", "enviar")
    obrigatorio_para_envio = acao != "rascunho"

    if request.method == "POST":
        form = ExperienciaSubmissaoForm(
            request.POST,
            request.FILES,
            instance=experiencia,
            obrigatorio_para_envio=obrigatorio_para_envio,
        )
        ids_remover = [
            int(valor)
            for valor in request.POST.getlist("remover_anexo")
            if valor.isdigit()
        ]
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
                mensagem = "AlteraÃ§Ãµes salvas como rascunho."
            else:
                experiencia.status_publicacao = Experiencia.StatusPublicacao.ENVIADO
                mensagem = "Boa prÃ¡tica reenviada para revisÃ£o."
            experiencia.save()
            form.save_m2m()
            salvar_anexos_submissao(experiencia, anexos)

            messages.success(request, mensagem)
            return redirect("painel_revisao") if request.user.is_authenticated and request.user.is_staff else redirect(f"/status-envio/?email_contato={experiencia.email_contato}")
        adicionar_erros_anexos_ao_formulario(form, erros_anexos)
    else:
        form = ExperienciaSubmissaoForm(instance=experiencia)

    return render(
        request,
        "praticas/editar_boa_pratica.html",
        {
            "form": form,
            "experiencia": experiencia,
            "email_validado": email,
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


def solicitar_edicao_publicada(request, pk):
    experiencia = get_object_or_404(
        Experiencia.objects.select_related("efs", "pais", "tipo_experiencia", "setor").prefetch_related(
            "temas_transversais",
            "normas_internacionais",
        ),
        pk=pk,
        status_publicacao=Experiencia.StatusPublicacao.PUBLICADO,
    )

    email = request.GET.get("email") or request.POST.get("email_contato_original")
    if not email or email.lower() != (experiencia.email_contato or "").lower():
        messages.error(request, "NÃ£o foi possÃ­vel validar o e-mail informado para solicitar ediÃ§Ã£o.")
        return redirect("status_envio")

    if request.method == "POST":
        form = PropostaEdicaoPublicadaForm(
            request.POST,
            instance=experiencia,
            obrigatorio_para_envio=True,
        )
        if form.is_valid():
            PropostaEdicaoExperiencia.objects.create(
                experiencia=experiencia,
                email_contato=email,
                comentario_autor=form.cleaned_data.get("comentario_autor", ""),
                dados_json=dados_proposta_from_form(form),
                status=PropostaEdicaoExperiencia.Status.PENDENTE,
            )
            messages.success(
                request,
                "Proposta de ediÃ§Ã£o enviada para revisÃ£o. A versÃ£o publicada permanecerÃ¡ ativa atÃ© aprovaÃ§Ã£o.",
            )
            return redirect(f"/status-envio/?email_contato={email}")
    else:
        form = PropostaEdicaoPublicadaForm(instance=experiencia)

    return render(
        request,
        "praticas/solicitar_edicao_publicada.html",
        {
            "form": form,
            "experiencia": experiencia,
            "email_validado": email,
        },
    )



CAMPOS_COMPARACAO_EDICAO = [
    ("titulo", "Nome da boa prÃ¡tica / iniciativa"),
    ("efs", "EFS"),
    ("pais", "PaÃ­s"),
    ("tipo_experiencia", "Tipo de boa prÃ¡tica"),
    ("setor", "Setor"),
    ("temas_transversais", "Temas transversais"),
    ("normas_internacionais", "Normas internacionais"),
    ("email_contato", "E-mail institucional"),
    ("pessoa_responsavel", "Pessoa responsÃ¡vel"),
    ("descricao", "Breve descriÃ§Ã£o da boa prÃ¡tica"),
    ("enfoque_justica_climatica", "VÃ­nculo com justiÃ§a climÃ¡tica"),
    ("objetivo", "Objetivo"),
    ("perguntas_chave", "Perguntas de auditoria"),
    ("criterios_utilizados", "CritÃ©rios utilizados"),
    ("metodologia", "Metodologia"),
    ("ferramentas_utilizadas", "Metodologias e instrumentos utilizados"),
    ("resultados", "Resultados"),
    ("recomendacoes", "RecomendaÃ§Ãµes"),
    ("replicabilidade", "Replicabilidade"),
    ("informacoes_adicionais", "InformaÃ§Ãµes adicionais"),
    ("ano_execucao", "Ano"),
    ("contribui_para_guia", "Contribui para a Guia"),
]


def texto_booleano(valor):
    return "Sim" if valor else "NÃ£o"


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

        # Propostas criadas antes da inclusÃ£o de novos campos podem nÃ£o trazer
        # todas as chaves no JSON. Nesses casos, preserva-se o valor atual para
        # evitar sobrescrever campos novos com None e violar restriÃ§Ãµes NOT NULL.
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


def status_envio(request):
    form = ConsultaStatusForm(request.GET or None)
    experiencias = Experiencia.objects.none()
    propostas = PropostaEdicaoExperiencia.objects.none()

    if form.is_valid():
        email = form.cleaned_data["email_contato"]
        experiencias = (
            Experiencia.objects.filter(email_contato__iexact=email)
            .select_related("efs", "pais", "tipo_experiencia", "setor")
            .order_by("-atualizado_em")
        )
        propostas = (
            PropostaEdicaoExperiencia.objects.filter(email_contato__iexact=email)
            .select_related("experiencia")
            .order_by("-atualizado_em")
        )

    return render(
        request,
        "praticas/status_envio.html",
        {
            "form": form,
            "experiencias": experiencias,
            "propostas": propostas,
            "consulta_realizada": form.is_valid(),
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
                mensagem = "ExperiÃªncia marcada como em revisÃ£o."
            elif acao == "aprovar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = "ExperiÃªncia aprovada e publicada no catÃ¡logo pÃºblico."
            elif acao == "publicar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO
                mensagem = "ExperiÃªncia publicada no catÃ¡logo pÃºblico."
            elif acao == "devolver":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.RASCUNHO
                mensagem = "ExperiÃªncia devolvida para ajustes."
            elif acao == "rejeitar":
                experiencia.status_publicacao = Experiencia.StatusPublicacao.REJEITADO
                mensagem = "ExperiÃªncia rejeitada."
            else:
                mensagem = "RevisÃ£o registrada."

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
                mensagem = "Proposta marcada como em revisÃ£o."
            elif acao == "aprovar":
                aplicar_proposta_edicao(proposta)
                proposta.status = PropostaEdicaoExperiencia.Status.APROVADA
                mensagem = "Proposta aprovada e aplicada Ã  experiÃªncia publicada."
            elif acao == "rejeitar":
                proposta.status = PropostaEdicaoExperiencia.Status.REJEITADA
                mensagem = "Proposta de ediÃ§Ã£o rejeitada."
            else:
                mensagem = "RevisÃ£o registrada."

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
            messages.error(request, "ConfirmaÃ§Ã£o de exclusÃ£o invÃ¡lida.")
            return redirect("excluir_boa_pratica", pk=experiencia.pk)

        titulo = experiencia.titulo_exibicao
        for anexo in experiencia.anexos.all():
            if anexo.arquivo:
                anexo.arquivo.delete(save=False)
        experiencia.delete()
        messages.success(request, f"Boa prÃ¡tica excluÃ­da com sucesso: {titulo}")
        if proximo:
            return redirect(proximo)
        return redirect("catalogo_experiencias")

    return render(
        request,
        "praticas/excluir_boa_pratica.html",
        {
            "experiencia": experiencia,
        },
    )

def banco_tecnico(request):
    recursos = (
        BancoTecnico.objects.select_related("setor")
        .prefetch_related("dimensoes")
        .all()
    )
    return render(request, "praticas/banco_tecnico.html", {"recursos": recursos})


def sobre_plataforma(request):
    return render(request, "praticas/sobre_plataforma.html")


