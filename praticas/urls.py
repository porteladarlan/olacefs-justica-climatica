from django.urls import path

from . import views

urlpatterns = [
    path("", views.pagina_inicial, name="pagina_inicial"),
    path("catalogo/", views.catalogo_experiencias, name="catalogo_experiencias"),
    path("experiencias/<int:pk>/", views.detalhe_experiencia, name="detalhe_experiencia"),
    path("normas-internacionais/", views.normas_internacionais, name="normas_internacionais"),
    path("adicionar-boa-pratica/", views.adicionar_boa_pratica, name="adicionar_boa_pratica"),
    path("envio-confirmado/", views.confirmacao_envio, name="confirmacao_envio"),
    path("banco-tecnico/", views.banco_tecnico, name="banco_tecnico"),
    path("sobre/", views.sobre_plataforma, name="sobre_plataforma"),
]
