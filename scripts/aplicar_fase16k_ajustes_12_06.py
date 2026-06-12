from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]
MODELS = BASE / "praticas" / "models.py"
FORMS = BASE / "praticas" / "forms.py"
VIEWS = BASE / "praticas" / "views.py"
MIGRATIONS = BASE / "praticas" / "migrations"
TEMPLATES = BASE / "templates" / "praticas"

def read(path):
    if not path.exists():
        print(f"ERRO: arquivo não encontrado: {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.write_text(text, encoding="utf-8")

def ensure_settings_import(text):
    if "from django.conf import settings" in text:
        return text
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("from django.db import models"):
            lines.insert(idx, "from django.conf import settings")
            return "\n".join(lines) + "\n"
    return "from django.conf import settings\n" + text

def ensure_experiencia_autor():
    text = ensure_settings_import(read(MODELS))
    start = text.find("class Experiencia(models.Model):")
    if start == -1:
        print("ERRO: classe Experiencia não encontrada.")
        sys.exit(1)
    next_class = text.find("\nclass ", start + 1)
    if next_class == -1:
        next_class = len(text)

    before, block, after = text[:start], text[start:next_class], text[next_class:]

    if not re.search(r"\n    autor\s*=\s*models\.ForeignKey\(", block):
        field = """    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boas_praticas_enviadas",
    )
"""
        marker = "    criado_em ="
        pos = block.find(marker)
        if pos == -1:
            pos = block.find("\n") + 1
            block = block[:pos] + field + block[pos:]
        else:
            block = block[:pos] + field + block[pos:]
        print("OK: Experiencia.autor adicionado ao model.")
    else:
        print("INFO: Experiencia.autor já existe.")

    text = before + block + after
    banco = text.find("class BancoTecnico(models.Model):")
    if banco != -1:
        nxt = text.find("\nclass ", banco + 1)
        if nxt == -1:
            nxt = len(text)
        bbefore, bblock, bafter = text[:banco], text[banco:nxt], text[nxt:]
        bblock_new = re.sub(
            r'\n    autor = models\.ForeignKey\(\n'
            r'        settings\.AUTH_USER_MODEL,\n'
            r'        on_delete=models\.SET_NULL,\n'
            r'        null=True,\n'
            r'        blank=True,\n'
            r'        related_name="experiencias_enviadas",\n'
            r'    \)\n',
            "\n",
            bblock,
            count=1,
        )
        if bblock_new != bblock:
            print("OK: BancoTecnico.autor indevido removido.")
        text = bbefore + bblock_new + bafter

    write(MODELS, text)

def ensure_autor_migration():
    MIGRATIONS.mkdir(exist_ok=True)
    for p in MIGRATIONS.glob("*.py"):
        if p.name == "__init__.py":
            continue
        content = p.read_text(encoding="utf-8", errors="ignore")
        if "boas_praticas_enviadas" in content and "model_name='experiencia'" in content:
            print(f"INFO: migration de autor já existe: {p.name}")
            return

    nums = []
    for p in MIGRATIONS.glob("[0-9][0-9][0-9][0-9]_*.py"):
        try:
            nums.append(int(p.name[:4]))
        except ValueError:
            pass

    next_num = max(nums) + 1 if nums else 1
    prev_num = max(nums) if nums else 0
    prev_name = None
    if prev_num:
        for p in MIGRATIONS.glob(f"{prev_num:04d}_*.py"):
            prev_name = p.stem
            break

    dep = f"        ('praticas', '{prev_name}'),\n" if prev_name else ""
    migration = f"""# Generated manually for Fase 16K

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
{dep}        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='experiencia',
            name='autor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='boas_praticas_enviadas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
"""
    path = MIGRATIONS / f"{next_num:04d}_autor_experiencia.py"
    write(path, migration)
    print(f"OK: migration criada: {path.name}")

def patch_forms():
    text = read(FORMS)

    text = re.sub(r'\n\s*"contato_referencia",', '', text)
    text = re.sub(r'\n\s*"contato_referencia": forms\.TextInput\(attrs=\{"class": "form-control"\}\),', '', text)

    text = text.replace('"contato_referencia": {\n        "pt": "Contato de referência da EFS",\n        "es": "Contacto de referencia de la EFS",\n        "en": "SAI reference contact",\n    },\n', '')

    text = re.sub(
        r'\n    "contato_referencia": \{\n        "pt": "Informe a pessoa ou área de referência para eventuais contatos institucionais\.",\n        "es": "Indique la persona o área de referencia para eventuales contactos institucionales\.",\n        "en": "Provide the reference person or unit for possible institutional contact\.",\n    \},',
        '',
        text,
    )

    text = text.replace(
        '"pt": "E-mail institucional de referência",\n        "es": "Correo institucional de referencia",\n        "en": "Reference institutional e-mail",',
        '"pt": "E-mail",\n        "es": "Correo electrónico",\n        "en": "E-mail",',
    )
    text = text.replace(
        '"pt": "Use preferencialmente um e-mail institucional vinculado à EFS.",\n        "es": "Use preferentemente un correo institucional vinculado a la EFS.",\n        "en": "Preferably use an institutional e-mail linked to the SAI.",',
        '"pt": "Informe o e-mail institucional para acompanhar o envio e receber orientações de revisão.",\n        "es": "Informe el correo institucional para acompañar el envío y recibir orientaciones de revisión.",\n        "en": "Provide the institutional e-mail to track the submission and receive review guidance.",',
    )

    write(FORMS, text)
    print("OK: forms.py ajustado para manter apenas e-mail no formulário.")

def replace_function(text, name, new_func):
    start = text.find(f"def {name}(")
    if start == -1:
        return text, False
    candidates = []
    for pattern in ["\ndef ", "\n@login_required", "\n@staff_member_required", "\n@require_POST"]:
        pos = text.find(pattern, start + 1)
        if pos != -1:
            candidates.append(pos)
    end = min(candidates) if candidates else len(text)
    return text[:start] + new_func.rstrip() + "\n\n" + text[end:].lstrip("\n"), True

def patch_views():
    text = read(VIEWS)

    helper_perm = """def experiencia_pertence_ao_usuario(experiencia, usuario, email_informado=None):
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
"""

    helper_qs = """def queryset_meus_envios(usuario):
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
"""

    if "def experiencia_pertence_ao_usuario(" in text:
        text, _ = replace_function(text, "experiencia_pertence_ao_usuario", helper_perm)
    else:
        pos = text.find("def estilizar_formulario_autenticacao")
        if pos != -1:
            text = text[:pos] + helper_perm + "\n\n" + text[pos:]

    if "def queryset_meus_envios(" in text:
        text, _ = replace_function(text, "queryset_meus_envios", helper_qs)
    else:
        pos = text.find("@login_required", max(0, text.find("def meus_envios") - 80))
        if pos == -1:
            pos = text.find("def meus_envios")
        if pos != -1:
            text = text[:pos] + helper_qs + "\n\n" + text[pos:]

    new_meus = """@login_required(login_url="login_usuario")
def meus_envios(request):
    experiencias = queryset_meus_envios(request.user)
    propostas = (
        PropostaEdicaoExperiencia.objects.filter(email_contato__iexact=request.user.email)
        .select_related("experiencia")
        .order_by("-atualizado_em")
    )
    return render(request, "praticas/meus_envios.html", {"experiencias": experiencias, "propostas": propostas})
"""
    text = re.sub(
        r'(?:@login_required\(login_url="login_usuario"\)\n)+def meus_envios\(request\):\n(?:    .*\n)+?(?=\ndef favoritos_ids)',
        new_meus.rstrip() + "\n",
        text,
        count=1,
    )

    text = text.replace(
        "experiencia = form.save(commit=False)\n            experiencia.status_iniciativa = Experiencia.StatusIniciativa.CONCLUIDA",
        "experiencia = form.save(commit=False)\n            if request.user.is_authenticated:\n                experiencia.autor = request.user\n            experiencia.status_iniciativa = Experiencia.StatusIniciativa.CONCLUIDA",
    )
    text = text.replace(
        'return redirect(f"{request.path}?rascunho_salvo=1")',
        'return redirect("meus_envios")',
    )

    text = re.sub(
        r'email = request\.GET\.get\("email"\) or request\.POST\.get\("email_contato_original"\)\n    if not email or email\.lower\(\) != \(experiencia\.email_contato or ""\)\.lower\(\):\n        messages\.error\(\n            request,\n            "Não foi possível validar o e-mail informado para edição deste envio\.",\n        \)\n        return redirect\("status_envio"\)',
        'email = request.GET.get("email") or request.POST.get("email_contato_original")\n    if not experiencia_pertence_ao_usuario(experiencia, request.user, email):\n        messages.error(\n            request,\n            "Não foi possível validar permissão para edição deste envio.",\n        )\n        return redirect("status_envio")',
        text,
        count=1,
    )

    text = text.replace(
        'Anexo.objects.filter(experiencia=experiencia, id__in=ids_remover).delete()\n            experiencia = form.save(commit=False)\n            if acao == "rascunho":',
        'Anexo.objects.filter(experiencia=experiencia, id__in=ids_remover).delete()\n            status_original = experiencia.status_publicacao\n            experiencia = form.save(commit=False)\n            if request.user.is_authenticated and request.user.is_staff:\n                experiencia.status_publicacao = status_original\n                mensagem = "Boa prática atualizada pelo revisor."\n            elif acao == "rascunho":',
    )

    text = text.replace(
        'return redirect(f"/status-envio/?email_contato={experiencia.email_contato}")',
        'return redirect("painel_revisao") if request.user.is_authenticated and request.user.is_staff else redirect(f"/status-envio/?email_contato={experiencia.email_contato}")',
    )

    text = re.sub(
        r'experiencias = \(\n        Experiencia\.objects\.exclude\(status_publicacao=Experiencia\.StatusPublicacao\.PUBLICADO\)\n        \.select_related\("efs", "pais", "tipo_experiencia", "setor"\)\n        \.order_by\("-atualizado_em"\)\n    \)',
        'experiencias = (\n        Experiencia.objects.filter(\n            status_publicacao__in=[\n                Experiencia.StatusPublicacao.ENVIADO,\n                Experiencia.StatusPublicacao.EM_REVISAO,\n                Experiencia.StatusPublicacao.APROVADO,\n                Experiencia.StatusPublicacao.REJEITADO,\n            ]\n        )\n        .select_related("efs", "pais", "tipo_experiencia", "setor")\n        .order_by("-atualizado_em")\n    )',
        text,
        count=1,
    )

    text = text.replace(
        'elif acao == "aprovar":\n                experiencia.status_publicacao = Experiencia.StatusPublicacao.APROVADO\n                mensagem = "Experiência aprovada. Ela ainda não está pública."',
        'elif acao == "aprovar":\n                experiencia.status_publicacao = Experiencia.StatusPublicacao.PUBLICADO\n                mensagem = "Experiência aprovada e publicada no catálogo público."',
    )

    text = text.replace('    ("contato_referencia", "Contato de referência"),\n', '')

    write(VIEWS, text)
    print("OK: views.py ajustado para autor, rascunho, painel, aprovação pública e edição por revisor.")

def patch_templates():
    for name in ["adicionar_boa_pratica.html", "editar_boa_pratica.html"]:
        path = TEMPLATES / name
        if path.exists():
            text = read(path)
            text = text.replace("prática e o contato", "prática e o e-mail")
            text = text.replace("práctica y el contacto", "práctica y el correo electrónico")
            text = text.replace("practice and contact", "practice and e-mail")
            text = text.replace(",contato_referencia", "")
            text = text.replace("contato_referencia,", "")
            write(path, text)

    for name in ["catalogo_experiencias.html", "favoritos_experiencias.html"]:
        path = TEMPLATES / name
        if path.exists():
            text = read(path)
            text = re.sub(
                r'\n\s*\{% if experiencia\.contato_referencia %\}\n\s*&bull; <strong>.*?</strong> \{\{ experiencia\.contato_referencia \}\}\n\s*\{% endif %\}',
                "",
                text,
                flags=re.S,
            )
            write(path, text)

    for name in ["detalhe_experiencia.html", "revisar_experiencia.html"]:
        path = TEMPLATES / name
        if path.exists():
            text = read(path)
            text = re.sub(
                r'\n\s*<div class="metadata-item">.*?experiencia\.contato_referencia\|default:"-".*?</div>\s*</div>',
                "",
                text,
                flags=re.S,
            )
            text = text.replace("{% if LANGUAGE_CODE == 'en' %}Author/contact{% elif LANGUAGE_CODE == 'es' %}Autor/contacto{% else %}Autor/contato{% endif %}", "E-mail")
            if name == "revisar_experiencia.html" and "Editar boa prática" not in text:
                text = text.replace(
                    "{% endblock %}",
                    '\n<div class="mt-3">\n    <a class="btn btn-outline-primary" href="{% url \'editar_boa_pratica\' experiencia.pk %}">Editar boa prática</a>\n</div>\n{% endblock %}',
                )
            write(path, text)

    path = TEMPLATES / "painel_revisao.html"
    if path.exists():
        text = read(path)
        text = text.replace("{% if LANGUAGE_CODE == 'en' %}Author/contact{% elif LANGUAGE_CODE == 'es' %}Autor/contacto{% else %}Autor/contato{% endif %}", "E-mail")
        if "Editar boa prática" not in text:
            text = re.sub(
                r'(<a[^>]+href="\{% url \'revisar_experiencia\' experiencia\.pk %\}"[^>]*>)',
                '<a class="btn btn-outline-primary btn-sm" href="{% url \'editar_boa_pratica\' experiencia.pk %}">Editar boa prática</a>\n                \\1',
                text,
            )
        write(path, text)

    print("OK: templates ajustados para e-mail, edição de revisor e remoção de contato.")

def create_tests():
    tests = """from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EFS, Experiencia, Pais, Setor, TipoExperiencia


class AjustesPlataforma1206Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pais = Pais.objects.create(nome="Brasil", sigla="BR")
        cls.efs = EFS.objects.create(nome="Tribunal de Contas", sigla="TC", pais=cls.pais)
        cls.tipo = TipoExperiencia.objects.create(nome="Auditoria")
        cls.setor = Setor.objects.create(nome="Infraestrutura")
        User = get_user_model()
        cls.autor = User.objects.create_user("autor16k", "autor16k@example.org", "senha12345")
        cls.revisor = User.objects.create_user("revisor16k", "revisor16k@example.org", "senha12345", is_staff=True)

    def criar_experiencia(self, titulo="Boa prática 16K", status=Experiencia.StatusPublicacao.ENVIADO, autor=None):
        return Experiencia.objects.create(
            titulo=titulo,
            efs=self.efs,
            pais=self.pais,
            tipo_experiencia=self.tipo,
            setor=self.setor,
            ano_execucao=2026,
            email_contato="autor16k@example.org",
            autor=autor,
            descricao="Descrição da prática.",
            enfoque_justica_climatica="Enfoque de justiça climática.",
            status_publicacao=status,
        )

    def test_rascunho_fica_visivel_para_autor_em_meus_envios(self):
        self.criar_experiencia("Rascunho visível", Experiencia.StatusPublicacao.RASCUNHO, self.autor)
        self.client.force_login(self.autor)
        response = self.client.get(reverse("meus_envios"))
        self.assertContains(response, "Rascunho visível")

    def test_rascunho_nao_aparece_no_painel_revisao(self):
        self.criar_experiencia("Rascunho privado", Experiencia.StatusPublicacao.RASCUNHO, self.autor)
        self.criar_experiencia("Enviada ao revisor", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.get(reverse("painel_revisao"))
        self.assertNotContains(response, "Rascunho privado")
        self.assertContains(response, "Enviada ao revisor")

    def test_revisor_consegue_acessar_edicao_da_boa_pratica(self):
        experiencia = self.criar_experiencia("Editável pelo revisor", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.get(reverse("editar_boa_pratica", args=[experiencia.pk]))
        self.assertEqual(response.status_code, 200)

    def test_aprovacao_publica_no_catalogo_aberto(self):
        experiencia = self.criar_experiencia("Aprovada e publicada", Experiencia.StatusPublicacao.ENVIADO, self.autor)
        self.client.force_login(self.revisor)
        response = self.client.post(
            reverse("revisar_experiencia", args=[experiencia.pk]),
            {"acao": "aprovar", "comentario_revisor": "Aprovada."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        experiencia.refresh_from_db()
        self.assertEqual(experiencia.status_publicacao, Experiencia.StatusPublicacao.PUBLICADO)
        public_response = self.client.get(reverse("catalogo_experiencias"))
        self.assertContains(public_response, "Aprovada e publicada")
"""
    write(BASE / "praticas" / "tests_fase16k.py", tests)
    print("OK: tests_fase16k.py criado.")

def main():
    ensure_experiencia_autor()
    ensure_autor_migration()
    patch_forms()
    patch_views()
    patch_templates()
    create_tests()
    print("\nFase 16K aplicada. Rode:")
    print("  python manage.py makemigrations --check")
    print("  python manage.py migrate")
    print("  python manage.py test praticas.tests_fase16k")
    print("  python manage.py test")

if __name__ == "__main__":
    main()
