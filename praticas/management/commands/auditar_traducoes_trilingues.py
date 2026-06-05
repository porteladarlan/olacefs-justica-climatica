from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = "Audita páginas renderizadas em EN/ES procurando possíveis resíduos de textos em português."

    TERMOS_SUSPEITOS = [
        "Início",
        "Meu espaço",
        "Meus envios",
        "Status do envio",
        "Favoritos",
        "Sair",
        "Gestão",
        "Painel de revisão",
        "Edições publicadas",
        "Buscar",
        "Enviar boa prática",
        "Boa prática",
        "Boas práticas",
        "Recursos técnicos",
        "Normas internacionais",
        "Conteúdo",
        "Conteúdos",
        "Conteúdo em desenvolvimento",
        "Conteúdo em curadoria técnica",
        "A Guia orienta",
        "plataforma demonstra",
        "Revisar",
        "Revisão",
        "Enviado",
        "Em revisão",
        "Aprovado",
        "Rejeitado",
        "Rascunho",
        "Filtrar",
        "Limpar",
        "Contato",
        "País",
        "Setor",
        "Tipo",
        "Ano",
        "Pessoa responsável",
        "Breve descrição",
        "Justiça climática",
        "Problema climático",
        "Riscos climáticos",
        "Metodologias e instrumentos",
        "Resultados",
        "Recomendações",
        "Replicabilidade",
        "Nenhum",
        "Nenhuma",
        "Nenhum anexo informado",
        "Salvar",
        "Publicar",
        "Aprovar",
        "Devolver",
        "Rejeitar",
        "comentário",
        "Comentário",
        "Autor",
    ]

    URLS = [
        "/",
        "/catalogo/",
        "/banco-tecnico/",
        "/normas-internacionais/",
        "/sobre/",
        "/adicionar-boa-pratica/",
        "/meus-envios/",
        "/status-envio/",
        "/favoritos/",
        "/painel-revisao/",
        "/painel-revisao-edicoes/",
        "/entrar/",
        "/registrar/",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--falhar",
            action="store_true",
            help="Retorna erro se encontrar possíveis resíduos em EN/ES.",
        )

    def handle(self, *args, **options):
        client = Client()
        total_alertas = 0

        self.stdout.write(self.style.MIGRATE_HEADING("Auditoria trilíngue de páginas renderizadas"))

        for idioma in ["en", "es"]:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_LABEL(f"Idioma: {idioma.upper()}"))

            for url in self.URLS:
                caminho = f"/{idioma}{url}" if url != "/" else f"/{idioma}/"
                response = client.get(caminho)

                if response.status_code in [301, 302, 403, 404]:
                    self.stdout.write(f"  {caminho} -> {response.status_code} (ignorado)")
                    continue

                if response.status_code >= 500:
                    total_alertas += 1
                    self.stdout.write(self.style.ERROR(f"  {caminho} -> {response.status_code}"))
                    continue

                conteudo = response.content.decode("utf-8", errors="ignore")
                encontrados = [
                    termo for termo in self.TERMOS_SUSPEITOS
                    if termo in conteudo
                ]

                if encontrados:
                    total_alertas += len(encontrados)
                    termos = ", ".join(encontrados[:12])
                    extra = "" if len(encontrados) <= 12 else f" (+{len(encontrados) - 12})"
                    self.stdout.write(self.style.WARNING(f"  {caminho} -> possíveis resíduos: {termos}{extra}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"  {caminho} -> OK"))

        self.stdout.write("")
        if total_alertas:
            self.stdout.write(self.style.WARNING(f"Auditoria concluída com {total_alertas} alerta(s)."))
            self.stdout.write("Revise os alertas antes de fechar a Fase 15M. Nem todo alerta é necessariamente erro; alguns podem ser nomes próprios, dados de demonstração ou conteúdo do usuário.")
            if options.get("falhar"):
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Auditoria concluída sem alertas."))
