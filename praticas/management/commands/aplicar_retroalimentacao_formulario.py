from django.core.management.base import BaseCommand

from praticas.models import EFS, Pais, Setor, TemaTransversal


PAISES = [
    ("ABW", "Aruba", "Aruba", "Aruba"),
    ("BLZ", "Belize", "Bélice", "Belize"),
    ("ARG", "Argentina", "Argentina", "Argentina"),
    ("MEX", "México", "México", "Mexico"),
    ("DOM", "República Dominicana", "República Dominicana", "Dominican Republic"),
    ("GTM", "Guatemala", "Guatemala", "Guatemala"),
    ("VEN", "Venezuela", "Venezuela", "Venezuela"),
    ("CHL", "Chile", "Chile", "Chile"),
    ("COL", "Colômbia", "Colombia", "Colombia"),
    ("CRI", "Costa Rica", "Costa Rica", "Costa Rica"),
    ("CUB", "Cuba", "Cuba", "Cuba"),
    ("CUW", "Curaçao", "Curazao", "Curaçao"),
    ("NIC", "Nicarágua", "Nicaragua", "Nicaragua"),
    ("PAN", "Panamá", "Panamá", "Panama"),
    ("PRY", "Paraguai", "Paraguay", "Paraguay"),
    ("PER", "Peru", "Perú", "Peru"),
    ("ECU", "Equador", "Ecuador", "Ecuador"),
    ("BOL", "Bolívia", "Bolivia", "Bolivia"),
    ("SLV", "El Salvador", "El Salvador", "El Salvador"),
    ("PRI", "Porto Rico", "Puerto Rico", "Puerto Rico"),
    ("URY", "Uruguai", "Uruguay", "Uruguay"),
    ("BRA", "Brasil", "Brasil", "Brazil"),
    ("HND", "Honduras", "Honduras", "Honduras"),
    ("ITA", "Itália", "Italia", "Italy"),
    ("ESP", "Espanha", "España", "Spain"),
    ("PRT", "Portugal", "Portugal", "Portugal"),
    ("OUTRO", "Outro", "Otro", "Other"),
]

# Lista ampliada conforme retroalimentação, agora com rótulos em PT/ES/EN.
# As siglas permanecem estáveis para preservar referências existentes no banco.
EFS_DADOS = [
    ("AGB", "Auditoria Geral de Belize", "Auditoria General de Bélice", "Office of the Auditor General of Belize", "BLZ"),
    ("AGN-ARG", "Auditoria Geral da Nação Argentina", "Auditoria General de la Nacion Argentina", "General Audit Office of the Argentine Nation", "ARG"),
    ("ASF", "Auditoria Superior da Federação do México", "Auditoría Superior de la Federación de México", "Superior Audit Office of the Federation of Mexico", "MEX"),
    ("CC-RD", "Câmara de Contas da República Dominicana", "Cámara de Cuentas de la República Dominicana", "Chamber of Accounts of the Dominican Republic", "DOM"),
    ("CGC-GTM", "Controladoria Geral de Contas da República da Guatemala", "Contraloría General de Cuentas de la República de Guatemala", "Comptroller General of Accounts of the Republic of Guatemala", "GTM"),
    ("CGR-VEN", "Controladoria Geral da República Bolivariana da Venezuela", "Contraloría General de la República Bolivariana de Venezuela", "Comptroller General of the Bolivarian Republic of Venezuela", "VEN"),
    ("CGR Chile", "Controladoria Geral da República do Chile", "Contraloria General de la República de Chile", "Comptroller General of the Republic of Chile", "CHL"),
    ("CGR Colombia", "Controladoria Geral da República da Colômbia", "Contraloria General de la República de Colombia", "Comptroller General of the Republic of Colombia", "COL"),
    ("CGR Costa Rica", "Controladoria Geral da República da Costa Rica", "Contraloria General de la República de Costa Rica", "Comptroller General of the Republic of Costa Rica", "CRI"),
    ("CGR-CUB", "Controladoria Geral da República de Cuba", "Contraloria General de la República de Cuba", "Comptroller General of the Republic of Cuba", "CUB"),
    ("SOAB Curaçao", "Controladoria Geral da República de Curaçao", "Contraloria General de la República de Curazao", "Comptroller General of the Republic of Curaçao", "CUW"),
    ("CGR-NIC", "Controladoria Geral da República da Nicarágua", "Contraloría General de la República de Nicaragua", "Comptroller General of the Republic of Nicaragua", "NIC"),
    ("CGR-PAN", "Controladoria Geral da República do Panamá", "Contraloría General de la República de Panamá", "Comptroller General of the Republic of Panama", "PAN"),
    ("CGR Paraguay", "Controladoria Geral da República do Paraguai", "Contraloría General de la República de Paraguay", "Comptroller General of the Republic of Paraguay", "PRY"),
    ("CGR-PER", "Controladoria Geral da República do Peru", "Contraloría General de la República de Perú", "Comptroller General of the Republic of Peru", "PER"),
    ("CGE Ecuador", "Controladoria Geral do Estado do Equador", "Contraloría General del Estado de Ecuador", "Comptroller General of the State of Ecuador", "ECU"),
    ("CGE-BOL", "Controladoria Geral do Estado Plurinacional da Bolívia", "Contraloría General del Estado Plurinacional de Bolivia", "Comptroller General of the Plurinational State of Bolivia", "BOL"),
    ("CCR-SLV", "Corte de Contas de El Salvador", "Corte de Cuentas de El Salvador", "Court of Accounts of El Salvador", "SLV"),
    ("OC-PRI", "Escritório do Controlador do Estado Livre Associado de Porto Rico", "Oficina del Contralor del Estado Libre Asociado de Puerto Rico", "Office of the Comptroller of the Commonwealth of Puerto Rico", "PRI"),
    ("TCR-URY", "Tribunal de Contas da República Oriental do Uruguai", "Tribunal de Cuentas de la República Oriental del Uruguay", "Court of Accounts of the Eastern Republic of Uruguay", "URY"),
    ("TCU", "Tribunal de Contas da União do Brasil", "Tribunal de Cuentas de la Unión de Brasil", "Federal Court of Accounts of Brazil", "BRA"),
    ("TSC-HND", "Tribunal Superior de Contas da República de Honduras", "Tribunal Superior de Cuentas de la República de Honduras", "Superior Court of Accounts of the Republic of Honduras", "HND"),
    ("GAC-ABW", "Câmara Geral de Auditoria de Aruba", "General Audit Chamber of Aruba", "General Audit Chamber of Aruba", "ABW"),
    ("TC-ESP", "Tribunal de Contas da Espanha", "Tribunal de Cuentas de España", "Court of Accounts of Spain", "ESP"),
    ("ATRICON", "ATRICON – Associação dos Membros dos Tribunais de Contas do Brasil", "ATRICON – Asociación de Miembros de los Tribunales de Cuentas de Brasil", "ATRICON – Association of Members of the Courts of Accounts of Brazil", "BRA"),
    ("AGR-COL", "Auditoria Geral da República da Colômbia", "Auditoria General de la Republica de Colombia", "General Audit Office of the Republic of Colombia", "COL"),
    ("CDV-COL", "Controladoria Departamental do Valle del Cauca - Colômbia", "Contraloría Departamental del Valle del Cauca - Colombia", "Departmental Comptroller's Office of Valle del Cauca - Colombia", "COL"),
    ("CGB-COL", "Controladoria Geral de Bogotá", "Contraloría General de Bogotá", "Comptroller General of Bogotá", "COL"),
    ("CGR-DOM", "Controladoria Geral da República Dominicana", "Contraloría General de la República Dominicana", "Comptroller General of the Dominican Republic", "DOM"),
    ("CC-ITA", "Corte de Contas da Itália", "Corte dei Conti de Italia", "Court of Accounts of Italy", "ITA"),
    ("HTC-BA", "Honorável Tribunal de Contas da Província de Buenos Aires", "Honorable Tribunal de Cuentas de la Provincia de Buenos Aires", "Honorable Court of Accounts of the Province of Buenos Aires", "ARG"),
    ("IRB", "IRB – Instituto Rui Barbosa", "IRB – Instituto Rui Barbosa", "IRB – Rui Barbosa Institute", "BRA"),
    ("TC-SFE", "Tribunal de Contas da Província de Santa Fé", "Tribunal de Cuentas de la Provincia de Santa Fé", "Court of Accounts of the Province of Santa Fé", "ARG"),
    ("TC-PRT", "Tribunal de Contas de Portugal", "Tribunal de Cuentas de Portugal", "Court of Accounts of Portugal", "PRT"),
    ("TCDF", "Tribunal de Contas do Distrito Federal", "Tribunal de Cuentas del Distrito Federal", "Court of Accounts of the Federal District", "BRA"),
    ("TCE-AC", "Tribunal de Contas do Estado do Acre", "Tribunal de Cuentas del Estado de Acre", "Court of Accounts of the State of Acre", "BRA"),
    ("TCE-AL", "Tribunal de Contas do Estado de Alagoas", "Tribunal de Cuentas del Estado de Alagoas", "Court of Accounts of the State of Alagoas", "BRA"),
    ("TCE-BA", "Tribunal de Contas do Estado da Bahia", "Tribunal de Cuentas del Estado de Bahía", "Court of Accounts of the State of Bahia", "BRA"),
    ("TCE-CE", "Tribunal de Contas do Estado do Ceará", "Tribunal de Cuentas del Estado de Ceará", "Court of Accounts of the State of Ceará", "BRA"),
    ("TCE-ES", "Tribunal de Contas do Estado do Espírito Santo", "Tribunal de Cuentas del Estado de Espirito Santo", "Court of Accounts of the State of Espírito Santo", "BRA"),
    ("TCE-MT", "Tribunal de Contas do Estado de Mato Grosso", "Tribunal de Cuentas del Estado de Mato Grosso", "Court of Accounts of the State of Mato Grosso", "BRA"),
    ("TCE-MG", "Tribunal de Contas do Estado de Minas Gerais", "Tribunal de Cuentas del Estado de Minas Gerais", "Court of Accounts of the State of Minas Gerais", "BRA"),
    ("TCE-PA", "Tribunal de Contas do Estado do Pará", "Tribunal de Cuentas del Estado de Pará", "Court of Accounts of the State of Pará", "BRA"),
    ("TCE-PR", "Tribunal de Contas do Estado do Paraná", "Tribunal de Cuentas del Estado de Paraná", "Court of Accounts of the State of Paraná", "BRA"),
    ("TCE-PE", "Tribunal de Contas do Estado de Pernambuco", "Tribunal de Cuentas del Estado de Pernambuco", "Court of Accounts of the State of Pernambuco", "BRA"),
    ("TCE-RJ", "Tribunal de Contas do Estado do Rio de Janeiro", "Tribunal de Cuentas del Estado de Rio de Janeiro", "Court of Accounts of the State of Rio de Janeiro", "BRA"),
    ("TCE-RN", "Tribunal de Contas do Estado do Rio Grande do Norte", "Tribunal de Cuentas del Estado de Rio Grande do Norte", "Court of Accounts of the State of Rio Grande do Norte", "BRA"),
    ("TCE-RS", "Tribunal de Contas do Estado do Rio Grande do Sul", "Tribunal de Cuentas del Estado de Río Grande do Sul", "Court of Accounts of the State of Rio Grande do Sul", "BRA"),
    ("TCE-RO", "Tribunal de Contas do Estado de Rondônia", "Tribunal de Cuentas del Estado de Rondonia", "Court of Accounts of the State of Rondônia", "BRA"),
    ("TCE-SC", "Tribunal de Contas do Estado de Santa Catarina", "Tribunal de Cuentas del Estado de Santa Catarina", "Court of Accounts of the State of Santa Catarina", "BRA"),
    ("TCE-TO", "Tribunal de Contas do Estado do Tocantins", "Tribunal de Cuentas del Estado de Tocantins", "Court of Accounts of the State of Tocantins", "BRA"),
    ("TCM-RJ", "Tribunal de Contas do Município do Rio de Janeiro", "Tribunal de Cuentas del Municipio de Rio de Janeiro", "Court of Accounts of the Municipality of Rio de Janeiro", "BRA"),
    ("OUTRO-EFS", "Outro", "Otro", "Other", "OUTRO"),
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
        for sigla, nome, nome_es, nome_en, sigla_pais in EFS_DADOS:
            efs, _ = EFS.objects.update_or_create(
                sigla=sigla,
                defaults={"nome": nome, "nome_es": nome_es, "nome_en": nome_en, "pais": paises[sigla_pais]},
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
