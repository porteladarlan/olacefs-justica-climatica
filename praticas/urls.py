from django.urls import path

from . import views

urlpatterns = [
    path("", views.pagina_inicial, name="pagina_inicial"),
    path("cadastro/", views.registrar_usuario, name="registrar_usuario"),
    path("entrar/", views.login_usuario, name="login_usuario"),
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
]
