from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import confirmacao_email_token


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
