from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Quando executado a partir da raiz do projeto, __file__ fica em scripts/.
# Quando copiado para outro contexto, usamos o diretório atual como fallback.
if not (Path.cwd() / "manage.py").exists():
    raise SystemExit("Execute este script a partir da raiz do projeto Django, onde está o manage.py.")
ROOT = Path.cwd()


def replace_once(path, old, new, label):
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"OK  {label} já aplicado")
        return
    if old not in text:
        raise SystemExit(f"ERRO  Padrão não encontrado em {path}: {label}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"OK  {label}")


def append_if_missing(path, marker, block, label):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"OK  {label} já aplicado")
        return
    path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")
    print(f"OK  {label}")


urls = ROOT / "praticas" / "urls.py"
views = ROOT / "praticas" / "views.py"
catalogo = ROOT / "templates" / "praticas" / "catalogo_experiencias.html"
detalhe = ROOT / "templates" / "praticas" / "detalhe_experiencia.html"
painel = ROOT / "templates" / "praticas" / "painel_revisao.html"

# urls.py
replace_once(
    urls,
    '    path("experiencias/<int:pk>/", views.detalhe_experiencia, name="detalhe_experiencia"),',
    '    path("experiencias/<int:pk>/", views.detalhe_experiencia, name="detalhe_experiencia"),\n    path("excluir-boa-pratica/<int:pk>/", views.excluir_boa_pratica, name="excluir_boa_pratica"),',
    "rota excluir_boa_pratica",
)

# views.py import seguro
text = views.read_text(encoding="utf-8")
if "from django.utils.http import url_has_allowed_host_and_scheme" not in text:
    text = text.replace(
        "from django.shortcuts import get_object_or_404, redirect, render\n",
        "from django.shortcuts import get_object_or_404, redirect, render\nfrom django.utils.http import url_has_allowed_host_and_scheme\n",
        1,
    )
    views.write_text(text, encoding="utf-8")
    print("OK  import url_has_allowed_host_and_scheme")
else:
    print("OK  import url_has_allowed_host_and_scheme já aplicado")

view_block = r'''
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
        },
    )
'''
# inserir antes de banco_tecnico para manter área administrativa agrupada
text = views.read_text(encoding="utf-8")
if "def excluir_boa_pratica(request, pk):" not in text:
    marker = "\ndef banco_tecnico(request):\n"
    if marker not in text:
        append_if_missing(views, "def excluir_boa_pratica(request, pk):", view_block, "view excluir_boa_pratica")
    else:
        views.write_text(text.replace(marker, "\n" + view_block.strip() + "\n\n" + marker.lstrip(), 1), encoding="utf-8")
        print("OK  view excluir_boa_pratica")
else:
    print("OK  view excluir_boa_pratica já aplicada")

# catalogo button
catalog_insert = '''{% if request.user.is_staff %}
                    <a href="{% url 'excluir_boa_pratica' experiencia.pk %}?next={{ request.get_full_path|urlencode }}" class="btn btn-sm btn-outline-danger">
                        {% if LANGUAGE_CODE == 'en' %}Delete{% elif LANGUAGE_CODE == 'es' %}Eliminar{% else %}Excluir{% endif %}
                    </a>
                    {% endif %}
                    <a href="{% url 'detalhe_experiencia' experiencia.pk %}" class="btn btn-primary">{% if LANGUAGE_CODE == 'en' %}Open profile{% elif LANGUAGE_CODE == 'es' %}Abrir ficha{% else %}Abrir ficha{% endif %}</a>'''
replace_once(
    catalogo,
    '''<a href="{% url 'detalhe_experiencia' experiencia.pk %}" class="btn btn-primary">{% if LANGUAGE_CODE == 'en' %}Open profile{% elif LANGUAGE_CODE == 'es' %}Abrir ficha{% else %}Abrir ficha{% endif %}</a>''',
    catalog_insert,
    "botão de exclusão no catálogo para staff",
)

# detalhe button
text = detalhe.read_text(encoding="utf-8")
if "excluir_boa_pratica" not in text:
    old = "</section>\n\n<section class=\"row g-3 mb-4\">"
    new = '''{% if request.user.is_staff %}
    <div class="mt-3">
        <a href="{% url 'excluir_boa_pratica' experiencia.pk %}?next={{ request.get_full_path|urlencode }}" class="btn btn-outline-danger">
            {% if LANGUAGE_CODE == 'en' %}Delete good practice{% elif LANGUAGE_CODE == 'es' %}Eliminar buena práctica{% else %}Excluir boa prática{% endif %}
        </a>
    </div>
    {% endif %}
</section>

<section class="row g-3 mb-4">'''
    if old not in text:
        print("AVISO  Não inseri botão no detalhe: padrão não encontrado")
    else:
        detalhe.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("OK  botão de exclusão no detalhe para staff")
else:
    print("OK  botão de exclusão no detalhe já aplicado")

# painel button
painel_insert = '''<div class="d-flex flex-wrap gap-2">
                <a href="{% url 'revisar_experiencia' experiencia.pk %}" class="btn btn-primary">Abrir revisão</a>
                <a href="{% url 'excluir_boa_pratica' experiencia.pk %}?next={{ request.get_full_path|urlencode }}" class="btn btn-outline-danger">Excluir</a>
            </div>'''
replace_once(
    painel,
    '''<a href="{% url 'revisar_experiencia' experiencia.pk %}" class="btn btn-primary">Abrir revisão</a>''',
    painel_insert,
    "botão de exclusão no painel de revisão",
)

print("\nFase 16I aplicada. Rode: python manage.py test praticas.tests_fase16i && python manage.py test")
