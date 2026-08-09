from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from praticas.servicos_guia_fase2d2 import publicar, validar_executor


class Command(BaseCommand):
    help = "Publica, separadamente da importacao, uma versao em rascunho do Guia."

    def add_arguments(self, parser):
        parser.add_argument("--versao", required=True)
        parser.add_argument("--executado-por", required=True)
        parser.add_argument("--vigente", action="store_true", help="Torna esta a unica versao vigente.")

    def handle(self, *args, **options):
        usuario = get_user_model().objects.filter(username=options["executado_por"]).first()
        try:
            validar_executor(usuario)
            versao = publicar(options["versao"], usuario, options["vigente"])
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from exc
        self.stdout.write(self.style.SUCCESS(f"VERSAO PUBLICADA: {versao.codigo}; vigente={'sim' if versao.vigente else 'nao'}."))
