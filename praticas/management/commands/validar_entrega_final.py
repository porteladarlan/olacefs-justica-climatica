from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Executa uma validação consolidada da entrega final da versão de validação."

    COMANDOS = [
        ("auditar_traducoes_trilingues", "Auditoria trilíngue"),
        ("auditar_autenticacao_perfis", "Auditoria de autenticação e perfis"),
        ("validar_fluxo_ponta_a_ponta", "Validação funcional ponta a ponta"),
        ("checar_prontidao_ambiente", "Checagem de prontidão técnica"),
        ("validar_release_validacao", "Validação dos documentos de release"),
        ("exibir_roteiro_teste_externo", "Materiais de teste externo"),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Interrompe se algum comando interno retornar erro.",
        )

    def handle(self, *args, **options):
        erros = []

        self.stdout.write(self.style.MIGRATE_HEADING("Validação consolidada da entrega final"))
        self.stdout.write("")

        for comando, descricao in self.COMANDOS:
            self.stdout.write(self.style.MIGRATE_LABEL(f"Executando: {descricao}"))
            try:
                call_command(comando)
                self.stdout.write(self.style.SUCCESS(f"OK: {descricao}"))
            except SystemExit as exc:
                if exc.code not in [0, None]:
                    erros.append(f"{descricao}: SystemExit({exc.code})")
                    self.stdout.write(self.style.WARNING(f"ALERTA: {descricao} retornou SystemExit({exc.code})"))
                    if options.get("falhar"):
                        raise
            except Exception as exc:
                erros.append(f"{descricao}: {exc}")
                self.stdout.write(self.style.ERROR(f"ERRO: {descricao}: {exc}"))
                if options.get("falhar"):
                    raise

            self.stdout.write("")

        if erros:
            self.stdout.write(self.style.WARNING(f"Validação consolidada concluída com {len(erros)} ocorrência(s)."))
            for erro in erros:
                self.stdout.write(self.style.WARNING(f"- {erro}"))
        else:
            self.stdout.write(self.style.SUCCESS("Validação consolidada concluída sem ocorrências."))
