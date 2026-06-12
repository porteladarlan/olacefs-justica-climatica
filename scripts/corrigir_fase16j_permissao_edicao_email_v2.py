from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
views_path = BASE / "praticas" / "views.py"

if not views_path.exists():
    print(f"ERRO: arquivo não encontrado: {views_path}")
    sys.exit(1)

texto = views_path.read_text(encoding="utf-8")

inicio = texto.find("def experiencia_pertence_ao_usuario(")
fim = texto.find("\ndef queryset_meus_envios(", inicio)

if inicio == -1 or fim == -1:
    print("ERRO: não foi possível localizar o bloco experiencia_pertence_ao_usuario antes de queryset_meus_envios.")
    sys.exit(1)

nova_funcao = '''def experiencia_pertence_ao_usuario(experiencia, usuario, email_informado=None):
    email_experiencia = (experiencia.email_contato or "").strip().lower()
    email_informado = (email_informado or "").strip().lower()

    # Mantém compatibilidade com o fluxo legado por e-mail.
    # Este caso precisa vir antes do bloqueio de usuário anônimo.
    if email_informado and email_experiencia and email_informado == email_experiencia:
        return True

    if not usuario or not usuario.is_authenticated:
        return False

    if getattr(experiencia, "autor_id", None) and experiencia.autor_id == usuario.id:
        return True

    email_usuario = (getattr(usuario, "email", "") or "").strip().lower()
    return bool(email_usuario and email_experiencia and email_usuario == email_experiencia)


'''

novo_texto = texto[:inicio] + nova_funcao + texto[fim+1:]

if novo_texto == texto:
    print("ERRO: nenhum conteúdo alterado.")
    sys.exit(1)

views_path.write_text(novo_texto, encoding="utf-8")

print("OK: função experiencia_pertence_ao_usuario substituída com validação por e-mail antes do bloqueio anônimo.")
print("")
print("Confirme com:")
print("  Select-String -Path praticas/views.py -Pattern \"Mantém compatibilidade com o fluxo legado por e-mail\"")
print("")
print("Depois rode:")
print("  python manage.py test praticas.tests.RotasPublicasTests.test_autor_edita_e_reenvia")
print("  python manage.py test praticas.tests_fase16j")
print("  python manage.py test")
