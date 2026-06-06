from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from urllib.parse import urljoin

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Audita uma URL pública do Render para detectar termos antigos e validar páginas principais."

    TERMOS_PROIBIDOS = [
        "MVP local",
        "Marcadores de logo",
        "Marcadores de logo para o MVP",
        "Ambiente de demonstração",
        "Ferramentas",
    ]

    CAMINHOS = [
        "/",
        "/catalogo/",
        "/banco-tecnico/",
        "/normas-internacionais/",
        "/sobre/",
        "/cadastro/",
        "/entrar/",
        "/en/",
        "/es/",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default="https://olacefs-justica-climatica.onrender.com/",
            help="URL base do ambiente Render.",
        )
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se encontrar alerta.",
        )

    def handle(self, *args, **options):
        base_url = options["url"].rstrip("/") + "/"
        alertas = []

        self.stdout.write(self.style.MIGRATE_HEADING("Auditoria pública do ambiente Render"))
        self.stdout.write(f"URL base: {base_url}")
        self.stdout.write("")

        for caminho in self.CAMINHOS:
            url = urljoin(base_url, caminho.lstrip("/"))
            try:
                html = self.baixar(url)
            except Exception as exc:
                alerta = f"{caminho} não carregou: {exc}"
                alertas.append(alerta)
                self.stdout.write(self.style.WARNING(f"  {caminho} -> erro"))
                continue

            encontrados = [termo for termo in self.TERMOS_PROIBIDOS if termo in html]
            if encontrados:
                alerta = f"{caminho} contém termo(s) antigo(s): {', '.join(encontrados)}"
                alertas.append(alerta)
                self.stdout.write(self.style.WARNING(f"  {caminho} -> alerta: {', '.join(encontrados)}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"  {caminho} -> OK"))

        self.stdout.write("")
        if alertas:
            self.stdout.write(self.style.WARNING(f"Auditoria concluída com {len(alertas)} alerta(s)."))
            for alerta in alertas:
                self.stdout.write(self.style.WARNING(f"- {alerta}"))
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Auditoria pública concluída sem alertas."))

    def baixar(self, url):
        req = Request(url, headers={"User-Agent": "OLACEFS-Validation-Bot/1.0"})
        try:
            with urlopen(req, timeout=20) as response:
                status = getattr(response, "status", 200)
                if status >= 400:
                    raise RuntimeError(f"HTTP {status}")
                return response.read().decode("utf-8", errors="ignore")
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc
