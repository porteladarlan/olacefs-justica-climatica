from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parents[1]
views_path = BASE / "praticas" / "views.py"

if not views_path.exists():
    print(f"ERRO: arquivo não encontrado: {views_path}")
    sys.exit(1)

texto = views_path.read_text(encoding="utf-8")

padrao = re.compile(
    r"def experiencia_pertence_ao_usuario\(experiencia, usuario, email_informado=None\):\n"
    r"(?:    .*\n)+?\n(?=\ndef |\n[A-Z_]+ =|\nANEXO_|$)",
    re.MULTILINE,
)

nova_funcao = """def experiencia_pertence_ao_usuario(experiencia, usuario, email_informado=None):
    # Valida se uma boa prática pertence ao usuário atual.
    #
    # Regras:
    # - usuário autenticado pode acessar por vínculo direto em Experiencia.autor;
    # - usuário autenticado também pode acessar quando seu e-mail é o e-mail de contato;
    # - fluxo legado por link/e-mail continua funcionando para envios antigos,
    #   inclusive sem login, desde que o e-mail informado bata com o e-mail de contato.
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

novo_texto, qtd = padrao.subn(nova_funcao, texto, count=1)

if qtd != 1:
    print("ERRO: não foi possível localizar/substituir a função experiencia_pertence_ao_usuario.")
    sys.exit(1)

views_path.write_text(novo_texto, encoding="utf-8")
print("OK: edição por e-mail validado corrigida em praticas/views.py.")
print("Agora rode:")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
