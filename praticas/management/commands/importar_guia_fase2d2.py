from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from praticas.models import LoteImportacaoConteudo
from praticas.servicos_guia_fase2d2 import DivergenciaGuia, importar, planejar_importacao, reverter, validar_executor

from .validar_fonte_guia_fase2d2 import ErroFonteGuia, ler_e_validar


class Command(BaseCommand):
    help = "Importa ou reverte, de forma controlada, conteudo codificado do Guia."

    def add_arguments(self, parser):
        parser.add_argument("--arquivo")
        parser.add_argument("--executado-por", required=True)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--reverter-lote")
        parser.add_argument("--justificativa")

    def handle(self, *args, **options):
        usuario = get_user_model().objects.filter(username=options["executado_por"]).first()
        try:
            validar_executor(usuario)
            if options["reverter_lote"]:
                if options["arquivo"] or options["dry_run"]:
                    raise ValidationError("Reversao nao pode ser combinada com arquivo ou dry-run.")
                lote = LoteImportacaoConteudo.objects.filter(identificador=options["reverter_lote"]).first()
                if not lote:
                    raise ValidationError("Lote inexistente.")
                bloqueados = reverter(lote, usuario, options.get("justificativa") or "")
                self.stdout.write(self.style.SUCCESS(f"REVERSAO CONCLUIDA: {bloqueados} itens bloqueados."))
                return
            if not options["arquivo"]:
                raise ValidationError("Informe --arquivo para importar ou executar dry-run.")
            resultado = ler_e_validar(options["arquivo"])
            plano = planejar_importacao(resultado)
            if plano.divergencias:
                primeira = plano.divergencias[0]
                raise DivergenciaGuia(f"Divergencia em {primeira['entidade']} {primeira['codigo']}, campo {primeira['campo']}.")
            if options["dry_run"]:
                self.stdout.write(self.style.SUCCESS(f"DRY-RUN APROVADO: novos={plano.novos}; idempotentes={plano.identicos}; nenhuma escrita realizada."))
                return
            lote, plano = importar(resultado, usuario)
            self.stdout.write(self.style.SUCCESS(f"IMPORTACAO CONCLUIDA EM RASCUNHO: lote {lote.identificador}; novos={plano.novos}; idempotentes={plano.identicos}."))
        except (ValidationError, ErroFonteGuia, DivergenciaGuia) as exc:
            mensagem = "; ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc)
            raise CommandError(mensagem) from exc
