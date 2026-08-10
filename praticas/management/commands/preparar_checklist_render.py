from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Lista os materiais e passos para preparar o Render/teste externo."

    DOCUMENTOS = [
        "docs/render/checklist_render_teste_externo.md",
        "docs/render/comandos_pos_deploy.md",
        "docs/render/usuarios_teste.md",
        "docs/teste_externo/mensagem_envio_link_teste.md",
        "docs/fase16a_preparacao_render_teste_externo.md",
    ]

    COMANDOS_LOCAIS = [
        "python manage.py test",
        "python manage.py auditar_traducoes_trilingues",
        "python manage.py auditar_autenticacao_perfis",
        "python manage.py validar_fluxo_ponta_a_ponta",
        "python manage.py checar_prontidao_ambiente",
        "python manage.py validar_entrega_final",
    ]

    COMANDOS_BUILD = [
        "pip install -r requirements.txt",
        "python manage.py collectstatic --no-input",
        "python manage.py migrate",
    ]

    OPERACOES_MANUAIS = [
        "python manage.py carregar_dados_ficticios --limpar-demo",
        "python manage.py aplicar_retroalimentacao_formulario",
        "python manage.py criar_admin_render",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se algum material obrigatório não for encontrado.",
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        faltantes = []

        self.stdout.write(self.style.MIGRATE_HEADING("Preparação do Render/teste externo"))
        self.stdout.write("")

        self.stdout.write(self.style.MIGRATE_LABEL("1. Materiais de apoio"))
        for relativo in self.DOCUMENTOS:
            caminho = base_dir / relativo
            if caminho.exists():
                self.stdout.write(self.style.SUCCESS(f"  OK  {relativo}"))
            else:
                faltantes.append(relativo)
                self.stdout.write(self.style.WARNING(f"  FALTA  {relativo}"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("2. Comandos locais antes de enviar link"))
        for comando in self.COMANDOS_LOCAIS:
            self.stdout.write(f"  - {comando}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("3. Operações técnicas automáticas do build"))
        for comando in self.COMANDOS_BUILD:
            self.stdout.write(f"  - {comando}")

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                "4. Operações manuais, somente com decisão consciente e autorização"
            )
        )
        for comando in self.OPERACOES_MANUAIS:
            self.stdout.write(f"  - {comando}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_LABEL("5. Checklist manual mínimo"))
        itens = [
            "Validar URL pública em PT/EN/ES.",
            "Confirmar dados demonstrativos no catálogo.",
            "Testar login e cadastro.",
            "Testar usuário comum.",
            "Testar usuário staff/revisor.",
            "Comunicar limitações do ambiente gratuito.",
            "Enviar roteiro, checklist e perguntas de feedback às pessoas testadoras.",
        ]
        for item in itens:
            self.stdout.write(f"  - {item}")

        self.stdout.write("")
        if faltantes:
            self.stdout.write(self.style.WARNING(f"Preparação com {len(faltantes)} material(is) faltante(s)."))
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Materiais de preparação do Render/teste externo disponíveis."))
