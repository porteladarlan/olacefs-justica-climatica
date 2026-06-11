from django.core.management.base import BaseCommand

from praticas.models import EFS, Pais, Setor, TemaTransversal


PAISES = [
    ("ABW", "Aruba", "Aruba", "Aruba"), ("BLZ", "Belize", "Bélice", "Belize"),
    ("ARG", "Argentina", "Argentina", "Argentina"), ("MEX", "México", "México", "Mexico"),
    ("DOM", "República Dominicana", "República Dominicana", "Dominican Republic"), ("GTM", "Guatemala", "Guatemala", "Guatemala"),
    ("VEN", "Venezuela", "Venezuela", "Venezuela"), ("CHL", "Chile", "Chile", "Chile"),
    ("COL", "Colômbia", "Colombia", "Colombia"), ("CRI", "Costa Rica", "Costa Rica", "Costa Rica"),
    ("CUB", "Cuba", "Cuba", "Cuba"), ("CUW", "Curaçao", "Curazao", "Curaçao"),
    ("NIC", "Nicarágua", "Nicaragua", "Nicaragua"), ("PAN", "Panamá", "Panamá", "Panama"),
    ("PRY", "Paraguai", "Paraguay", "Paraguay"), ("PER", "Peru", "Perú", "Peru"),
    ("ECU", "Equador", "Ecuador", "Ecuador"), ("BOL", "Bolívia", "Bolivia", "Bolivia"),
    ("SLV", "El Salvador", "El Salvador", "El Salvador"), ("PRI", "Porto Rico", "Puerto Rico", "Puerto Rico"),
    ("URY", "Uruguai", "Uruguay", "Uruguay"), ("BRA", "Brasil", "Brasil", "Brazil"),
    ("HND", "Honduras", "Honduras", "Honduras"), ("ITA", "Itália", "Italia", "Italy"),
    ("ESP", "Espanha", "España", "Spain"), ("PRT", "Portugal", "Portugal", "Portugal"),
    ("OUTRO", "Outro", "Otro", "Other"),
]

EFS_DADOS = [
    ("AGB", "Auditoria General de Bélice", "BLZ"), ("AGN-ARG", "Auditoria General de la Nacion Argentina", "ARG"),
    ("ASF-MEX", "Auditoría Superior de la Federación de México", "MEX"), ("CC-RD", "Cámara de Cuentas de la República Dominicana", "DOM"),
    ("CGC-GTM", "Contraloría General de Cuentas de la República de Guatemala", "GTM"), ("CGR-VEN", "Contraloría General de la República Bolivariana de Venezuela", "VEN"),
    ("CGR-CHL", "Contraloria General de la República de Chile", "CHL"), ("CGR-COL", "Contraloria General de la República de Colombia", "COL"),
    ("CGR-CRI", "Contraloria General de la República de Costa Rica", "CRI"), ("CGR-CUB", "Contraloria General de la República de Cuba", "CUB"),
    ("CGR-CUW", "Contraloria General de la República de Curazao", "CUW"), ("CGR-NIC", "Contraloría General de la República de Nicaragua", "NIC"),
    ("CGR-PAN", "Contraloría General de la República de Panamá", "PAN"), ("CGR-PRY", "Contraloría General de la República de Paraguay", "PRY"),
    ("CGR-PER", "Contraloría General de la República de Perú", "PER"), ("CGE-ECU", "Contraloría General del Estado de Ecuador", "ECU"),
    ("CGE-BOL", "Contraloría General del Estado Plurinacional de Bolivia", "BOL"), ("CCR-SLV", "Corte de Cuentas de El Salvador", "SLV"),
    ("OC-PRI", "Oficina del Contralor del Estado Libre Asociado de Puerto Rico", "PRI"), ("TCR-URY", "Tribunal de Cuentas de la República Oriental del Uruguay", "URY"),
    ("TCU-BRA", "Tribunal de Cuentas de la Unión de Brasil", "BRA"), ("TSC-HND", "Tribunal Superior de Cuentas de la República de Honduras", "HND"),
    ("GAC-ABW", "General Audit Chamber of Aruba", "ABW"), ("TC-ESP", "Tribunal de Cuentas de España", "ESP"),
    ("ATRICON", "ATRICON – Asociación de Miembros de los Tribunales de Cuentas de Brasil", "BRA"), ("AGR-COL", "Auditoria General de la Republica de Colombia", "COL"),
    ("CDV-COL", "Contraloría Departamental del Valle del Cauca - Colombia", "COL"), ("CGB-COL", "Contraloría General de Bogotá", "COL"),
    ("CGR-DOM", "Contraloría General de la República Dominicana", "DOM"), ("CC-ITA", "Corte dei Conti de Italia", "ITA"),
    ("HTC-BA", "Honorable Tribunal de Cuentas de la Provincia de Buenos Aires", "ARG"), ("IRB", "IRB – Instituto Rui Barbosa", "BRA"),
    ("TC-SFE", "Tribunal de Cuentas de la Provincia de Santa Fé", "ARG"), ("TC-PRT", "Tribunal de Cuentas de Portugal", "PRT"),
    ("TCDF", "Tribunal de Cuentas del Distrito Federal", "BRA"), ("TCE-AC", "Tribunal de Cuentas del Estado de Acre", "BRA"),
    ("TCE-AL", "Tribunal de Cuentas del Estado de Alagoas", "BRA"), ("TCE-BA", "Tribunal de Cuentas del Estado de Bahía", "BRA"),
    ("TCE-CE", "Tribunal de Cuentas del Estado de Ceará", "BRA"), ("TCE-ES", "Tribunal de Cuentas del Estado de Espirito Santo", "BRA"),
    ("TCE-MT", "Tribunal de Cuentas del Estado de Mato Grosso", "BRA"), ("TCE-MG", "Tribunal de Cuentas del Estado de Minas Gerais", "BRA"),
    ("TCE-PA", "Tribunal de Cuentas del Estado de Pará", "BRA"), ("TCE-PR", "Tribunal de Cuentas del Estado de Paraná", "BRA"),
    ("TCE-PE", "Tribunal de Cuentas del Estado de Pernambuco", "BRA"), ("TCE-RJ", "Tribunal de Cuentas del Estado de Rio de Janeiro", "BRA"),
    ("TCE-RN", "Tribunal de Cuentas del Estado de Rio Grande do Norte", "BRA"), ("TCE-RS", "Tribunal de Cuentas del Estado de Río Grande do Sul", "BRA"),
    ("TCE-RO", "Tribunal de Cuentas del Estado de Rondonia", "BRA"), ("TCE-SC", "Tribunal de Cuentas del Estado de Santa Catarina", "BRA"),
    ("TCE-TO", "Tribunal de Cuentas del Estado de Tocantins", "BRA"), ("TCM-RJ", "Tribunal de Cuentas del Municipio de Rio de Janeiro", "BRA"),
    ("OUTRO-EFS", "Otro", "OUTRO"),
]


class Command(BaseCommand):
    help = "Aplica taxonomias solicitadas na retroalimentação do formulário."

    def handle(self, *args, **options):
        paises = {}
        for sigla, nome, nome_es, nome_en in PAISES:
            pais, _ = Pais.objects.update_or_create(sigla=sigla, defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en})
            paises[sigla] = pais

        for sigla, nome, sigla_pais in EFS_DADOS:
            EFS.objects.update_or_create(sigla=sigla, defaults={"nome": nome, "nome_es": nome, "nome_en": nome, "pais": paises[sigla_pais]})

        Setor.objects.update_or_create(nome="Outro", defaults={"nome_es": "Otro", "nome_en": "Other"})
        for nome, nome_es, nome_en in [
            ("Outro", "Otro", "Other"),
            ("Crianças", "Niños, niñas y adolescentes", "Children and adolescents"),
            ("Idosos", "Personas mayores", "Older persons"),
        ]:
            TemaTransversal.objects.update_or_create(nome=nome, defaults={"nome_es": nome_es, "nome_en": nome_en})

        self.stdout.write(self.style.SUCCESS("Retroalimentação do formulário aplicada com sucesso."))
