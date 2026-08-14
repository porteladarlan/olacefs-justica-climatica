import logging
from functools import partial
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import get_language

from .tokens import confirmacao_email_token


logger = logging.getLogger(__name__)


TEXTOS = {
    "pt": {
        "saudacao": "Olá,",
        "titulo": "Boa prática",
        "status": "Status atual",
        "efs": "Instituição/EFS",
        "pais": "País",
        "autor": "Autor",
        "solicitante": "Solicitante",
        "observacao": "Observação da revisão",
        "meus_envios": "Acompanhar em Meus envios",
        "revisar_pratica": "Abrir revisão da boa prática",
        "ver_publicacao": "Ver boa prática publicada",
        "revisar_edicao": "Abrir revisão da solicitação de edição",
        "submissao_assunto": "Recebemos sua boa prática",
        "submissao_mensagem": "A submissão foi recebida e seguirá para análise.",
        "revisor_submissao_assunto": "Nova boa prática aguardando revisão",
        "revisor_submissao_mensagem": "Uma nova boa prática foi enviada para análise.",
        "edicao_solicitante_assunto": "Recebemos sua solicitação de edição",
        "edicao_solicitante_mensagem": (
            "A solicitação foi recebida e seguirá para análise. A versão publicada "
            "permanece disponível até a decisão."
        ),
        "edicao_revisor_assunto": "Nova solicitação de edição aguardando revisão",
        "edicao_revisor_mensagem": "Uma edição de boa prática publicada foi solicitada.",
        "aprovar_assunto": "Sua boa prática foi aprovada e publicada",
        "aprovar_mensagem": (
            "A boa prática foi aprovada e está disponível no catálogo público."
        ),
        "publicar_assunto": "Sua boa prática foi publicada",
        "publicar_mensagem": "A boa prática está disponível no catálogo público.",
        "devolver_assunto": "Sua boa prática foi devolvida para ajustes",
        "devolver_mensagem": "Revise as orientações e ajuste o envio antes de reenviar.",
        "rejeitar_assunto": "Sua boa prática foi rejeitada",
        "rejeitar_mensagem": "A decisão da revisão foi registrada.",
        "edicao_aprovar_assunto": "Sua solicitação de edição foi aprovada",
        "edicao_aprovar_mensagem": "A edição aprovada foi aplicada à boa prática publicada.",
        "edicao_rejeitar_assunto": "Sua solicitação de edição foi rejeitada",
        "edicao_rejeitar_mensagem": "A decisão da revisão foi registrada.",
    },
    "es": {
        "saudacao": "Hola,",
        "titulo": "Buena práctica",
        "status": "Estado actual",
        "efs": "Institución/EFS",
        "pais": "País",
        "autor": "Autor",
        "solicitante": "Solicitante",
        "observacao": "Observación de la revisión",
        "meus_envios": "Acompañar en Mis envíos",
        "revisar_pratica": "Abrir revisión de la buena práctica",
        "ver_publicacao": "Ver buena práctica publicada",
        "revisar_edicao": "Abrir revisión de la solicitud de edición",
        "submissao_assunto": "Hemos recibido su buena práctica",
        "submissao_mensagem": "La presentación fue recibida y seguirá para análisis.",
        "revisor_submissao_assunto": "Nueva buena práctica pendiente de revisión",
        "revisor_submissao_mensagem": "Se envió una nueva buena práctica para análisis.",
        "edicao_solicitante_assunto": "Hemos recibido su solicitud de edición",
        "edicao_solicitante_mensagem": (
            "La solicitud fue recibida y seguirá para análisis. La versión publicada "
            "permanece disponible hasta la decisión."
        ),
        "edicao_revisor_assunto": "Nueva solicitud de edición pendiente de revisión",
        "edicao_revisor_mensagem": "Se solicitó editar una buena práctica publicada.",
        "aprovar_assunto": "Su buena práctica fue aprobada y publicada",
        "aprovar_mensagem": (
            "La buena práctica fue aprobada y está disponible en el catálogo público."
        ),
        "publicar_assunto": "Su buena práctica fue publicada",
        "publicar_mensagem": "La buena práctica está disponible en el catálogo público.",
        "devolver_assunto": "Su buena práctica fue devuelta para ajustes",
        "devolver_mensagem": "Revise las orientaciones y ajuste el envío antes de reenviarlo.",
        "rejeitar_assunto": "Su buena práctica fue rechazada",
        "rejeitar_mensagem": "La decisión de la revisión fue registrada.",
        "edicao_aprovar_assunto": "Su solicitud de edición fue aprobada",
        "edicao_aprovar_mensagem": "La edición aprobada fue aplicada a la buena práctica publicada.",
        "edicao_rejeitar_assunto": "Su solicitud de edición fue rechazada",
        "edicao_rejeitar_mensagem": "La decisión de la revisión fue registrada.",
    },
    "en": {
        "saudacao": "Hello,",
        "titulo": "Good practice",
        "status": "Current status",
        "efs": "Institution/SAI",
        "pais": "Country",
        "autor": "Author",
        "solicitante": "Requester",
        "observacao": "Review comment",
        "meus_envios": "Track in My submissions",
        "revisar_pratica": "Open good practice review",
        "ver_publicacao": "View published good practice",
        "revisar_edicao": "Open edit request review",
        "submissao_assunto": "We received your good practice",
        "submissao_mensagem": "The submission was received and will proceed to review.",
        "revisor_submissao_assunto": "New good practice awaiting review",
        "revisor_submissao_mensagem": "A new good practice was submitted for review.",
        "edicao_solicitante_assunto": "We received your edit request",
        "edicao_solicitante_mensagem": (
            "The request was received and will proceed to review. The published "
            "version remains available until a decision is made."
        ),
        "edicao_revisor_assunto": "New edit request awaiting review",
        "edicao_revisor_mensagem": "An edit to a published good practice was requested.",
        "aprovar_assunto": "Your good practice was approved and published",
        "aprovar_mensagem": (
            "The good practice was approved and is available in the public catalog."
        ),
        "publicar_assunto": "Your good practice was published",
        "publicar_mensagem": "The good practice is available in the public catalog.",
        "devolver_assunto": "Your good practice was returned for adjustments",
        "devolver_mensagem": "Review the guidance and update the submission before resubmitting.",
        "rejeitar_assunto": "Your good practice was rejected",
        "rejeitar_mensagem": "The review decision was recorded.",
        "edicao_aprovar_assunto": "Your edit request was approved",
        "edicao_aprovar_mensagem": "The approved edit was applied to the published good practice.",
        "edicao_rejeitar_assunto": "Your edit request was rejected",
        "edicao_rejeitar_mensagem": "The review decision was recorded.",
    },
}

STATUS_EXPERIENCIA = {
    "pt": {
        "rascunho": "Rascunho",
        "enviado": "Enviado",
        "em_revisao": "Em revisão",
        "aprovado": "Aprovado",
        "publicado": "Publicado",
        "rejeitado": "Rejeitado",
    },
    "es": {
        "rascunho": "Borrador",
        "enviado": "Enviado",
        "em_revisao": "En revisión",
        "aprovado": "Aprobado",
        "publicado": "Publicado",
        "rejeitado": "Rechazado",
    },
    "en": {
        "rascunho": "Draft",
        "enviado": "Submitted",
        "em_revisao": "Under review",
        "aprovado": "Approved",
        "publicado": "Published",
        "rejeitado": "Rejected",
    },
}

STATUS_EDICAO = {
    "pt": {"pendente": "Pendente", "aprovada": "Aprovada", "rejeitada": "Rejeitada"},
    "es": {"pendente": "Pendiente", "aprovada": "Aprobada", "rejeitada": "Rechazada"},
    "en": {"pendente": "Pending", "aprovada": "Approved", "rejeitada": "Rejected"},
}


def _idioma_email():
    idioma = (get_language() or settings.LANGUAGE_CODE).lower()
    if idioma.startswith("en"):
        return "en", "en"
    if idioma.startswith("es"):
        return "es", "es"
    return "pt", "pt-br"


def _email_valido(email):
    email = (email or "").strip()
    if not email:
        return ""
    try:
        validate_email(email)
    except ValidationError:
        return ""
    return email


def primeiro_email_valido(*candidatos):
    for candidato in candidatos:
        email = _email_valido(candidato)
        if email:
            return email
    return ""


def _enviar_notificacao(destinatario, contexto):
    destinatario = _email_valido(destinatario)
    if not destinatario:
        return
    try:
        assunto = render_to_string(
            "praticas/emails/notificacao_editorial_assunto.txt", contexto
        ).strip()
        texto = render_to_string("praticas/emails/notificacao_editorial.txt", contexto)
        html = render_to_string("praticas/emails/notificacao_editorial.html", contexto)
        mensagem = EmailMultiAlternatives(
            subject=assunto,
            body=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        mensagem.attach_alternative(html, "text/html")
        mensagem.send(fail_silently=False)
    except (OSError, SMTPException):
        logger.error("Falha técnica no envio de notificação editorial.")


def _emails_revisores():
    emails = (
        get_user_model()
        .objects.filter(is_staff=True, is_active=True)
        .exclude(email="")
        .order_by("pk")
        .values_list("email", flat=True)
    )
    unicos = {}
    for email in emails:
        email_valido = _email_valido(email)
        if email_valido:
            unicos.setdefault(email_valido.casefold(), email_valido)
    return tuple(unicos.values())


def _nome_usuario(usuario):
    return usuario.get_full_name().strip() or usuario.get_username()


def _url(request, idioma_codigo, nome_rota, *args):
    with translation.override(idioma_codigo):
        caminho = reverse(nome_rota, args=args)
    return request.build_absolute_uri(caminho)


def _contexto(textos, idioma, assunto, mensagem, detalhes, acoes):
    return {
        "idioma_html": {"pt": "pt-BR", "es": "es", "en": "en"}[idioma],
        "assunto": assunto,
        "saudacao": textos["saudacao"],
        "mensagem": mensagem,
        "detalhes": detalhes,
        "acoes": acoes,
    }


def _notificar_nova_submissao(request, experiencia_id, idioma, idioma_codigo):
    from .models import Experiencia

    experiencia = (
        Experiencia.objects.select_related("autor", "efs", "pais")
        .filter(pk=experiencia_id)
        .first()
    )
    if experiencia is None:
        return

    with translation.override(idioma_codigo):
        textos = TEXTOS[idioma]
        detalhes = [
            {"rotulo": textos["titulo"], "valor": experiencia.titulo_exibicao},
            {
                "rotulo": textos["status"],
                "valor": STATUS_EXPERIENCIA[idioma][experiencia.status_publicacao],
            },
        ]
        if experiencia.autor and experiencia.autor.is_active:
            contexto_autor = _contexto(
                textos,
                idioma,
                textos["submissao_assunto"],
                textos["submissao_mensagem"],
                detalhes,
                [
                    {
                        "rotulo": textos["meus_envios"],
                        "url": _url(request, idioma_codigo, "meus_envios"),
                    }
                ],
            )
            _enviar_notificacao(experiencia.autor.email, contexto_autor)

        contexto_revisor = _contexto(
            textos,
            idioma,
            textos["revisor_submissao_assunto"],
            textos["revisor_submissao_mensagem"],
            [
                {"rotulo": textos["titulo"], "valor": experiencia.titulo_exibicao},
                {"rotulo": textos["efs"], "valor": experiencia.efs.nome_exibicao},
                {"rotulo": textos["pais"], "valor": experiencia.pais.nome_exibicao},
                {
                    "rotulo": textos["autor"],
                    "valor": _nome_usuario(experiencia.autor) if experiencia.autor else "-",
                },
            ],
            [
                {
                    "rotulo": textos["revisar_pratica"],
                    "url": _url(
                        request,
                        idioma_codigo,
                        "revisar_experiencia",
                        experiencia.pk,
                    ),
                }
            ],
        )
        for email in _emails_revisores():
            _enviar_notificacao(email, contexto_revisor)


def agendar_notificacoes_nova_submissao(request, experiencia):
    idioma, idioma_codigo = _idioma_email()
    transaction.on_commit(
        partial(
            _notificar_nova_submissao,
            request,
            experiencia.pk,
            idioma,
            idioma_codigo,
        )
    )


def _notificar_status_experiencia(
    request, experiencia_id, acao, idioma, idioma_codigo
):
    from .models import Experiencia

    experiencia = (
        Experiencia.objects.select_related("autor").filter(pk=experiencia_id).first()
    )
    if (
        experiencia is None
        or experiencia.autor is None
        or not experiencia.autor.is_active
    ):
        return

    with translation.override(idioma_codigo):
        textos = TEXTOS[idioma]
        detalhes = [
            {"rotulo": textos["titulo"], "valor": experiencia.titulo_exibicao},
            {
                "rotulo": textos["status"],
                "valor": STATUS_EXPERIENCIA[idioma][experiencia.status_publicacao],
            },
        ]
        if acao in {"devolver", "rejeitar"} and experiencia.comentario_revisor.strip():
            detalhes.append(
                {
                    "rotulo": textos["observacao"],
                    "valor": experiencia.comentario_revisor,
                }
            )

        acoes = [
            {
                "rotulo": textos["meus_envios"],
                "url": _url(request, idioma_codigo, "meus_envios"),
            }
        ]
        if acao in {"aprovar", "publicar"}:
            acoes.append(
                {
                    "rotulo": textos["ver_publicacao"],
                    "url": _url(
                        request,
                        idioma_codigo,
                        "detalhe_experiencia",
                        experiencia.pk,
                    ),
                }
            )
        contexto = _contexto(
            textos,
            idioma,
            textos[f"{acao}_assunto"],
            textos[f"{acao}_mensagem"],
            detalhes,
            acoes,
        )
        _enviar_notificacao(experiencia.autor.email, contexto)


def agendar_notificacao_status_experiencia(request, experiencia, acao):
    idioma, idioma_codigo = _idioma_email()
    transaction.on_commit(
        partial(
            _notificar_status_experiencia,
            request,
            experiencia.pk,
            acao,
            idioma,
            idioma_codigo,
        )
    )


def _notificar_solicitacao_edicao(
    request, proposta_id, solicitante_email, idioma, idioma_codigo
):
    from .models import PropostaEdicaoExperiencia

    proposta = (
        PropostaEdicaoExperiencia.objects.select_related(
            "experiencia", "experiencia__efs", "experiencia__pais"
        )
        .filter(pk=proposta_id)
        .first()
    )
    if proposta is None:
        return

    with translation.override(idioma_codigo):
        textos = TEXTOS[idioma]
        experiencia = proposta.experiencia
        contexto_solicitante = _contexto(
            textos,
            idioma,
            textos["edicao_solicitante_assunto"],
            textos["edicao_solicitante_mensagem"],
            [
                {"rotulo": textos["titulo"], "valor": experiencia.titulo_exibicao},
                {
                    "rotulo": textos["status"],
                    "valor": STATUS_EDICAO[idioma][proposta.status],
                },
            ],
            [
                {
                    "rotulo": textos["meus_envios"],
                    "url": _url(request, idioma_codigo, "status_envio"),
                }
            ],
        )
        _enviar_notificacao(solicitante_email, contexto_solicitante)

        contexto_revisor = _contexto(
            textos,
            idioma,
            textos["edicao_revisor_assunto"],
            textos["edicao_revisor_mensagem"],
            [
                {"rotulo": textos["titulo"], "valor": experiencia.titulo_exibicao},
                {"rotulo": textos["efs"], "valor": experiencia.efs.nome_exibicao},
                {"rotulo": textos["pais"], "valor": experiencia.pais.nome_exibicao},
                {"rotulo": textos["solicitante"], "valor": solicitante_email},
            ],
            [
                {
                    "rotulo": textos["revisar_edicao"],
                    "url": _url(
                        request,
                        idioma_codigo,
                        "revisar_edicao_publicada",
                        proposta.pk,
                    ),
                }
            ],
        )
        for email in _emails_revisores():
            _enviar_notificacao(email, contexto_revisor)


def agendar_notificacoes_solicitacao_edicao(
    request, proposta, solicitante_email
):
    idioma, idioma_codigo = _idioma_email()
    transaction.on_commit(
        partial(
            _notificar_solicitacao_edicao,
            request,
            proposta.pk,
            solicitante_email,
            idioma,
            idioma_codigo,
        )
    )


def _notificar_decisao_edicao(request, proposta_id, acao, idioma, idioma_codigo):
    from .models import PropostaEdicaoExperiencia

    proposta = (
        PropostaEdicaoExperiencia.objects.select_related(
            "experiencia", "experiencia__autor"
        )
        .filter(pk=proposta_id)
        .first()
    )
    if proposta is None:
        return

    with translation.override(idioma_codigo):
        textos = TEXTOS[idioma]
        detalhes = [
            {
                "rotulo": textos["titulo"],
                "valor": proposta.experiencia.titulo_exibicao,
            },
            {
                "rotulo": textos["status"],
                "valor": STATUS_EDICAO[idioma][proposta.status],
            },
        ]
        if proposta.comentario_revisor.strip():
            detalhes.append(
                {
                    "rotulo": textos["observacao"],
                    "valor": proposta.comentario_revisor,
                }
            )
        contexto = _contexto(
            textos,
            idioma,
            textos[f"edicao_{acao}_assunto"],
            textos[f"edicao_{acao}_mensagem"],
            detalhes,
            [
                {
                    "rotulo": textos["meus_envios"],
                    "url": _url(request, idioma_codigo, "status_envio"),
                }
            ],
        )
        autor = proposta.experiencia.autor
        destinatario = primeiro_email_valido(
            proposta.email_contato,
            autor.email if autor is not None and autor.is_active else "",
        )
        _enviar_notificacao(destinatario, contexto)


def agendar_notificacao_decisao_edicao(request, proposta, acao):
    idioma, idioma_codigo = _idioma_email()
    transaction.on_commit(
        partial(
            _notificar_decisao_edicao,
            request,
            proposta.pk,
            acao,
            idioma,
            idioma_codigo,
        )
    )


def enviar_confirmacao_email(request, usuario):
    uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = confirmacao_email_token.make_token(usuario)
    caminho = reverse(
        "confirmar_email",
        kwargs={"uidb64": uidb64, "token": token},
    )
    contexto = {
        "usuario": usuario,
        "confirmacao_url": request.build_absolute_uri(caminho),
    }
    assunto = render_to_string(
        "praticas/emails/confirmacao_email_assunto.txt", contexto, request=request
    ).strip()
    texto = render_to_string(
        "praticas/emails/confirmacao_email.txt", contexto, request=request
    )
    html = render_to_string(
        "praticas/emails/confirmacao_email.html", contexto, request=request
    )
    mensagem = EmailMultiAlternatives(
        subject=assunto,
        body=texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email],
    )
    mensagem.attach_alternative(html, "text/html")
    mensagem.send(fail_silently=False)
