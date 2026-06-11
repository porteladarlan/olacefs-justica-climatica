from django.core.management.base import BaseCommand

from praticas.models import EFS, Pais, Setor, TemaTransversal


PAISES = [
    ("ABW", "Aruba", "Aruba", "Aruba"),
    ("BLZ", "Bélice", "Bélice", "Belize"),
    ("ARG", "Argentina", "Argentina", "Argentina"),
    ("MEX", "México", "México", "Mexico"),
    ("DOM", "República Dominicana", "República Dominicana", "Dominican Republic"),
    ("GTM", "Guatemala", "Guatemala", "Guatemala"),
    ("VEN", "Venezuela", "Venezuela", "Venezuela"),
    ("CHL", "Chile", "Chile", "Chile"),
    ("COL", "Colombia", "Colombia", "Colombia"),
    ("CRI", "Costa Rica", "Costa Rica", "Costa Rica"),
    ("CUB", "Cuba", "Cuba", "Cuba"),
    ("CUW", "Curazao", "Curazao", "Curaçao"),
    ("NIC", "Nicaragua", "Nicaragua", "Nicaragua"),
    ("PAN", "Panamá", "Panamá", "Panama"),
    ("PRY", "Paraguay", "Paraguay", "Paraguay"),
    ("PER", "Perú", "Perú", "Peru"),
    ("ECU", "Ecuador", "Ecuador", "Ecuador"),
    ("BOL", "Bolivia", "Bolivia", "Bolivia"),
    ("SLV", "El Salvador", "El Salvador", "El Salvador"),
    ("PRI", "Puerto Rico", "Puerto Rico", "Puerto Rico"),
    ("URY", "Uruguay", "Uruguay", "Uruguay"),
    ("BRA", "Brasil", "Brasil", "Brazil"),
    ("HND", "Honduras", "Honduras", "Honduras"),
    ("ITA", "Italia", "Italia", "Italy"),
    ("ESP", "España", "España", "Spain"),
    ("PRT", "Portugal", "Portugal", "Portugal"),
    ("OUTRO", "Otro", "Otro", "Other"),
]

# Lista ampliada conforme retroalimentação. Mantemos as denominações oficiais em espanhol
# nas três línguas para evitar tradução indevida de nomes institucionais.
EFS_DADOS = [
    ("AGB", "Auditoria General de Bélice", "BLZ"),
    ("AGN-ARG", "Auditoria General de la Nacion Argentina", "ARG"),
    ("ASF", "Auditoría Superior de la Federación de México", "MEX"),
    ("CC-RD", "Cámara de Cuentas de la República Dominicana", "DOM"),
    ("CGC-GTM", "Contraloría General de Cuentas de la República de Guatemala", "GTM"),
    ("CGR-VEN", "Contraloría General de la República Bolivariana de Venezuela", "VEN"),
    ("CGR Chile", "Contraloria General de la República de Chile", "CHL"),
    ("CGR Colombia", "Contraloria General de la República de Colombia", "COL"),
    ("CGR Costa Rica", "Contraloria General de la República de Costa Rica", "CRI"),
    ("CGR-CUB", "Contraloria General de la República de Cuba", "CUB"),
    ("SOAB Curaçao", "Contraloria General de la República de Curazao", "CUW"),
    ("CGR-NIC", "Contraloría General de la República de Nicaragua", "NIC"),
    ("CGR-PAN", "Contraloría General de la República de Panamá", "PAN"),
    ("CGR Paraguay", "Contraloría General de la República de Paraguay", "PRY"),
    ("CGR-PER", "Contraloría General de la República de Perú", "PER"),
    ("CGE Ecuador", "Contraloría General del Estado de Ecuador", "ECU"),
    ("CGE-BOL", "Contraloría General del Estado Plurinacional de Bolivia", "BOL"),
    ("CCR-SLV", "Corte de Cuentas de El Salvador", "SLV"),
    ("OC-PRI", "Oficina del Contralor del Estado Libre Asociado de Puerto Rico", "PRI"),
    ("TCR-URY", "Tribunal de Cuentas de la República Oriental del Uruguay", "URY"),
    ("TCU", "Tribunal de Cuentas de la Unión de Brasil", "BRA"),
    ("TSC-HND", "Tribunal Superior de Cuentas de la República de Honduras", "HND"),
    ("GAC-ABW", "General Audit Chamber of Aruba", "ABW"),
    ("TC-ESP", "Tribunal de Cuentas de España", "ESP"),
    ("ATRICON", "ATRICON – Asociación de Miembros de los Tribunales de Cuentas de Brasil", "BRA"),
    ("AGR-COL", "Auditoria General de la Republica de Colombia", "COL"),
    ("CDV-COL", "Contraloría Departamental del Valle del Cauca - Colombia", "COL"),
    ("CGB-COL", "Contraloría General de Bogotá", "COL"),
    ("CGR-DOM", "Contraloría General de la República Dominicana", "DOM"),
    ("CC-ITA", "Corte dei Conti de Italia", "ITA"),
    ("HTC-BA", "Honorable Tribunal de Cuentas de la Provincia de Buenos Aires", "ARG"),
    ("IRB", "IRB – Instituto Rui Barbosa", "BRA"),
    ("TC-SFE", "Tribunal de Cuentas de la Provincia de Santa Fé", "ARG"),
    ("TC-PRT", "Tribunal de Cuentas de Portugal", "PRT"),
    ("TCDF", "Tribunal de Cuentas del Distrito Federal", "BRA"),
    ("TCE-AC", "Tribunal de Cuentas del Estado de Acre", "BRA"),
    ("TCE-AL", "Tribunal de Cuentas del Estado de Alagoas", "BRA"),
    ("TCE-BA", "Tribunal de Cuentas del Estado de Bahía", "BRA"),
    ("TCE-CE", "Tribunal de Cuentas del Estado de Ceará", "BRA"),
    ("TCE-ES", "Tribunal de Cuentas del Estado de Espirito Santo", "BRA"),
    ("TCE-MT", "Tribunal de Cuentas del Estado de Mato Grosso", "BRA"),
    ("TCE-MG", "Tribunal de Cuentas del Estado de Minas Gerais", "BRA"),
    ("TCE-PA", "Tribunal de Cuentas del Estado de Pará", "BRA"),
    ("TCE-PR", "Tribunal de Cuentas del Estado de Paraná", "BRA"),
    ("TCE-PE", "Tribunal de Cuentas del Estado de Pernambuco", "BRA"),
    ("TCE-RJ", "Tribunal de Cuentas del Estado de Rio de Janeiro", "BRA"),
    ("TCE-RN", "Tribunal de Cuentas del Estado de Rio Grande do Norte", "BRA"),
    ("TCE-RS", "Tribunal de Cuentas del Estado de Río Grande do Sul", "BRA"),
    ("TCE-RO", "Tribunal de Cuentas del Estado de Rondonia", "BRA"),
    ("TCE-SC", "Tribunal de Cuentas del Estado de Santa Catarina", "BRA"),
    ("TCE-TO", "Tribunal de Cuentas del Estado de Tocantins", "BRA"),
    ("TCM-RJ", "Tribunal de Cuentas del Municipio de Rio de Janeiro", "BRA"),
    ("OUTRO-EFS", "Otro", "OUTRO"),
]

# Compatibilidade com siglas antigas eventualmente criadas antes da retroalimentação.
ALIASES_SIGLA = {
    "CGR-CHL": "CGR Chile",
    "CGR-COL": "CGR Colombia",
    "CGR-CRI": "CGR Costa Rica",
    "CGR-PRY": "CGR Paraguay",
    "CGE-ECU": "CGE Ecuador",
    "ASF-MEX": "ASF",
    "TCU-BRA": "TCU",
    "CGR-CUW": "SOAB Curaçao",
}


class Command(BaseCommand):
    help = "Aplica taxonomias solicitadas na retroalimentação do formulário."

    def handle(self, *args, **options):
        paises = {}
        for sigla, nome, nome_es, nome_en in PAISES:
            pais, _ = Pais.objects.update_or_create(
                sigla=sigla,
                defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en},
            )
            paises[sigla] = pais

        oficiais = {}
        for sigla, nome, sigla_pais in EFS_DADOS:
            efs, _ = EFS.objects.update_or_create(
                sigla=sigla,
                defaults={"nome": nome, "nome_es": nome, "nome_en": nome, "pais": paises[sigla_pais]},
            )
            oficiais[sigla] = efs

        # Remove/mescla duplicidades criadas por versões intermediárias do comando,
        # preservando referências existentes em experiências publicadas.
        for sigla_antiga, sigla_oficial in ALIASES_SIGLA.items():
            antigo = EFS.objects.filter(sigla=sigla_antiga).first()
            oficial = oficiais.get(sigla_oficial) or EFS.objects.filter(sigla=sigla_oficial).first()
            if antigo and oficial and antigo.pk != oficial.pk:
                from praticas.models import Experiencia
                Experiencia.objects.filter(efs=antigo).update(efs=oficial)
                antigo.delete()
            elif antigo and not oficial:
                # Caso raro: se só existir a sigla antiga, renomeia para o padrão atual.
                antigo.sigla = sigla_oficial
                antigo.save(update_fields=["sigla"])

        Setor.objects.update_or_create(nome="Outro", defaults={"nome_es": "Otro", "nome_en": "Other"})
        for nome, nome_es, nome_en in [
            ("Outro", "Otro", "Other"),
            ("Crianças", "Niños, niñas y adolescentes", "Children and adolescents"),
            ("Idosos", "Personas mayores", "Older persons"),
        ]:
            TemaTransversal.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        self.stdout.write(self.style.SUCCESS("Retroalimentação do formulário aplicada com sucesso."))
