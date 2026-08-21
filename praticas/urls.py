from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import RecuperarSenhaForm, RedefinirSenhaForm

urlpatterns = [
    path("", views.pagina_inicial, name="pagina_inicial"),
    path(
        "exemplos-injustica-climatica/",
        views.exemplos_injustica_climatica,
        name="exemplos_injustica_climatica",
    ),
    path("cadastro/", views.registrar_usuario, name="registrar_usuario"),
    path(
        "cadastro/confirmacao-enviada/",
        views.confirmacao_email_enviada,
        name="confirmacao_email_enviada",
    ),
    path(
        "confirmar-email/<uidb64>/<token>/",
        views.confirmar_email,
        name="confirmar_email",
    ),
    path(
        "confirmar-email/reenviar/",
        views.reenviar_confirmacao_email,
        name="reenviar_confirmacao_email",
    ),
    path("entrar/", views.login_usuario, name="login_usuario"),
    path(
        "senha/esqueci/",
        auth_views.PasswordResetView.as_view(
            template_name="praticas/password_reset_form.html",
            form_class=RecuperarSenhaForm,
            email_template_name="praticas/emails/password_reset_email.txt",
            html_email_template_name="praticas/emails/password_reset_email.html",
            subject_template_name="praticas/emails/password_reset_assunto.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "senha/email-enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="praticas/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "senha/redefinir/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="praticas/password_reset_confirm.html",
            form_class=RedefinirSenhaForm,
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "senha/redefinida/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="praticas/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("sair/", views.logout_usuario, name="logout_usuario"),
    path("meus-envios/", views.meus_envios, name="meus_envios"),
    path("catalogo/", views.catalogo_experiencias, name="catalogo_experiencias"),
    path("comparar/", views.comparar_experiencias, name="comparar_experiencias"),
    path("favoritos/", views.favoritos_experiencias, name="favoritos_experiencias"),
    path("favoritos/alternar/<int:pk>/", views.alternar_favorito, name="alternar_favorito"),
    path("experiencias/<int:pk>/", views.detalhe_experiencia, name="detalhe_experiencia"),
    path("excluir-boa-pratica/<int:pk>/", views.excluir_boa_pratica, name="excluir_boa_pratica"),
    path("normas-internacionais/", views.normas_internacionais, name="normas_internacionais"),
    path("adicionar-boa-pratica/", views.adicionar_boa_pratica, name="adicionar_boa_pratica"),
    path("editar-ferramenta/<int:pk>/", views.editar_ferramenta, name="editar_ferramenta"),
    path("editar-boa-pratica/<int:pk>/", views.editar_boa_pratica, name="editar_boa_pratica"),
    path("solicitar-edicao-publicada/<int:pk>/", views.solicitar_edicao_publicada, name="solicitar_edicao_publicada"),
    path("envio-confirmado/", views.confirmacao_envio, name="confirmacao_envio"),
    path("status-envio/", views.status_envio, name="status_envio"),
    path("painel-revisao/", views.painel_revisao, name="painel_revisao"),
    path("painel-revisao/<int:pk>/", views.revisar_experiencia, name="revisar_experiencia"),
    path("painel-revisao-edicoes/", views.painel_revisao_edicoes, name="painel_revisao_edicoes"),
    path("painel-revisao-edicoes/<int:pk>/", views.revisar_edicao_publicada, name="revisar_edicao_publicada"),
    path("banco-tecnico/", views.banco_tecnico, name="banco_tecnico"),
    path("ferramentas/", views.ferramentas, name="ferramentas"),
    path("sobre/", views.sobre_plataforma, name="sobre_plataforma"),
    path("guia/", views.guia_inicio, name="guia_inicio"),
    path("guia/eixos/", views.guia_eixos, name="guia_eixos"),
    path(
        "guia/eixos/<slug:eixo_codigo>/",
        views.guia_eixo,
        name="guia_eixo",
    ),
    path(
        "guia/eixos/<slug:eixo_codigo>/subeixos/<slug:subeixo_codigo>/",
        views.guia_subeixo,
        name="guia_subeixo",
    ),
    path("guia/setores/", views.guia_setores, name="guia_setores"),
    path(
        "guia/setores/<slug:setor_codigo>/",
        views.guia_setor,
        name="guia_setor",
    ),
    path(
        "guia/setores/<slug:setor_codigo>/subareas/<slug:subarea_codigo>/",
        views.guia_subarea,
        name="guia_subarea",
    ),
    path("guia/preview/", views.guia_preview_inicio, name="guia_preview_inicio"),
    path("guia/preview/eixos/", views.guia_preview_eixos, name="guia_preview_eixos"),
    path(
        "guia/preview/eixos/<slug:eixo_codigo>/",
        views.guia_preview_eixo,
        name="guia_preview_eixo",
    ),
    path(
        "guia/preview/eixos/<slug:eixo_codigo>/subeixos/<slug:subeixo_codigo>/",
        views.guia_preview_subeixo,
        name="guia_preview_subeixo",
    ),
    path("guia/preview/setores/", views.guia_preview_setores, name="guia_preview_setores"),
    path(
        "guia/preview/setores/<slug:setor_codigo>/",
        views.guia_preview_setor,
        name="guia_preview_setor",
    ),
    path(
        "guia/preview/setores/<slug:setor_codigo>/subareas/<slug:subarea_codigo>/",
        views.guia_preview_subarea,
        name="guia_preview_subarea",
    ),
]
