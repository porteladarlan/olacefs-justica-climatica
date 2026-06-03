from django import forms
from django.utils.translation import get_language

from .models import Anexo, Experiencia, PropostaEdicaoExperiencia


def idioma_atual():
    idioma = (get_language() or "pt-br").lower()
    if idioma.startswith("en"):
        return "en"
    if idioma.startswith("es"):
        return "es"
    return "pt"


def texto_idioma(pt, es=None, en=None):
    idioma = idioma_atual()
    if idioma == "en":
        return en or pt
    if idioma == "es":
        return es or pt
    return pt


EXPERIENCIA_LABELS = {
    "efs": {
        "pt": "EFS",
        "es": "EFS",
        "en": "SAI",
    },
    "pais": {
        "pt": "País",
        "es": "País",
        "en": "Country",
    },
    "titulo": {
        "pt": "Nome da boa prática / iniciativa",
        "es": "Nombre de la buena práctica / iniciativa",
        "en": "Name of the good practice / initiative",
    },
    "tipo_experiencia": {
        "pt": "Tipo de boa prática",
        "es": "Tipo de buena práctica",
        "en": "Type of good practice",
    },
    "setor": {
        "pt": "Setor",
        "es": "Sector",
        "en": "Sector",
    },
    "temas_transversais": {
        "pt": "Temas transversais",
        "es": "Temas transversales",
        "en": "Cross-cutting themes",
    },
    "normas_internacionais": {
        "pt": "Normas internacionais relacionadas",
        "es": "Normas internacionales relacionadas",
        "en": "Related international standards",
    },
    "contato_referencia": {
        "pt": "Contato de referência da EFS",
        "es": "Contacto de referencia de la EFS",
        "en": "SAI reference contact",
    },
    "email_contato": {
        "pt": "E-mail institucional de referência",
        "es": "Correo institucional de referencia",
        "en": "Reference institutional e-mail",
    },
    "pessoa_responsavel": {
        "pt": "Pessoa responsável",
        "es": "Persona responsable",
        "en": "Responsible person",
    },
    "descricao": {
        "pt": "Breve descrição da boa prática",
        "es": "Breve descripción de la buena práctica",
        "en": "Brief description of the good practice",
    },
    "enfoque_justica_climatica": {
        "pt": "Vínculo com justiça climática",
        "es": "Vínculo con justicia climática",
        "en": "Climate justice link",
    },
    "objetivo": {
        "pt": "Objetivo",
        "es": "Objetivo",
        "en": "Objective",
    },
    "perguntas_chave": {
        "pt": "Perguntas de auditoria utilizadas",
        "es": "Preguntas de auditoría utilizadas",
        "en": "Audit questions used",
    },
    "criterios_utilizados": {
        "pt": "Critérios utilizados",
        "es": "Criterios utilizados",
        "en": "Criteria used",
    },
    "metodologia": {
        "pt": "Metodologia",
        "es": "Metodología",
        "en": "Methodology",
    },
    "ferramentas_utilizadas": {
        "pt": "Metodologias, matrizes ou instrumentos utilizados",
        "es": "Metodologías, matrices o instrumentos utilizados",
        "en": "Methodologies, matrices or instruments used",
    },
    "resultados": {
        "pt": "Resultados",
        "es": "Resultados",
        "en": "Results",
    },
    "recomendacoes": {
        "pt": "Recomendações",
        "es": "Recomendaciones",
        "en": "Recommendations",
    },
    "replicabilidade": {
        "pt": "Replicabilidade",
        "es": "Replicabilidad",
        "en": "Replicability",
    },
    "ano_execucao": {
        "pt": "Ano",
        "es": "Año",
        "en": "Year",
    },
}

EXPERIENCIA_HELP_TEXTS = {
    "descricao": {
        "pt": "Inclua uma descrição objetiva, suficiente para que outra EFS entenda o que foi feito.",
        "es": "Incluya una descripción objetiva, suficiente para que otra EFS entienda lo que se hizo.",
        "en": "Include an objective description, sufficient for another SAI to understand what was done.",
    },
    "enfoque_justica_climatica": {
        "pt": "Explique como a experiência considera equidade, direitos humanos, vulnerabilidades ou impactos diferenciados.",
        "es": "Explique cómo la experiencia considera equidad, derechos humanos, vulnerabilidades o impactos diferenciados.",
        "en": "Explain how the experience considers equity, human rights, vulnerabilities or differentiated impacts.",
    },
    "temas_transversais": {
        "pt": "Marque todos os temas aplicáveis.",
        "es": "Marque todos los temas aplicables.",
        "en": "Select all applicable themes.",
    },
    "normas_internacionais": {
        "pt": "Marque os marcos internacionais relacionados, como Acordo de Paris ou ODS.",
        "es": "Marque los marcos internacionales relacionados, como el Acuerdo de París o los ODS.",
        "en": "Select related international frameworks, such as the Paris Agreement or the SDGs.",
    },
    "ferramentas_utilizadas": {
        "pt": "Exemplos: perguntas, matrizes, checklists, metodologias, painéis ou bases de dados.",
        "es": "Ejemplos: preguntas, matrices, listas de verificación, metodologías, paneles o bases de datos.",
        "en": "Examples: questions, matrices, checklists, methodologies, dashboards or databases.",
    },
    "titulo": {
        "pt": "Use um título curto e específico, que identifique claramente a experiência.",
        "es": "Use un título breve y específico, que identifique claramente la experiencia.",
        "en": "Use a short and specific title that clearly identifies the experience.",
    },
    "contato_referencia": {
        "pt": "Informe a pessoa ou área de referência para eventuais contatos institucionais.",
        "es": "Indique la persona o área de referencia para eventuales contactos institucionales.",
        "en": "Provide the reference person or unit for possible institutional contact.",
    },
    "email_contato": {
        "pt": "Use preferencialmente um e-mail institucional vinculado à EFS.",
        "es": "Use preferentemente un correo institucional vinculado a la EFS.",
        "en": "Preferably use an institutional e-mail linked to the SAI.",
    },
    "ano_execucao": {
        "pt": "Informe o ano principal de execução ou conclusão da experiência.",
        "es": "Indique el año principal de ejecución o conclusión de la experiencia.",
        "en": "Provide the main year of implementation or completion of the experience.",
    },
}


def aplicar_textos_experiencia(form):
    idioma = idioma_atual()
    for campo, traducoes in EXPERIENCIA_LABELS.items():
        if campo in form.fields:
            form.fields[campo].label = traducoes[idioma]
    for campo, traducoes in EXPERIENCIA_HELP_TEXTS.items():
        if campo in form.fields:
            form.fields[campo].help_text = traducoes[idioma]


class ExperienciaSubmissaoForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = [
            "efs",
            "pais",
            "titulo",
            "tipo_experiencia",
            "setor",
            "temas_transversais",
            "normas_internacionais",
            "contato_referencia",
            "email_contato",
            "pessoa_responsavel",
            "descricao",
            "enfoque_justica_climatica",
            "objetivo",
            "perguntas_chave",
            "criterios_utilizados",
            "metodologia",
            "ferramentas_utilizadas",
            "resultados",
            "recomendacoes",
            "replicabilidade",
            "ano_execucao",
        ]
        widgets = {
            "efs": forms.Select(attrs={"class": "form-select"}),
            "pais": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_experiencia": forms.Select(attrs={"class": "form-select"}),
            "setor": forms.Select(attrs={"class": "form-select"}),
            "temas_transversais": forms.CheckboxSelectMultiple(),
            "normas_internacionais": forms.CheckboxSelectMultiple(),
            "contato_referencia": forms.TextInput(attrs={"class": "form-control"}),
            "email_contato": forms.EmailInput(attrs={"class": "form-control"}),
            "pessoa_responsavel": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "enfoque_justica_climatica": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "objetivo": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "perguntas_chave": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "criterios_utilizados": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "metodologia": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "ferramentas_utilizadas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "resultados": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "recomendacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "replicabilidade": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "ano_execucao": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, obrigatorio_para_envio=True, **kwargs):
        self.obrigatorio_para_envio = obrigatorio_para_envio
        super().__init__(*args, **kwargs)
        aplicar_textos_experiencia(self)

    def clean(self):
        cleaned_data = super().clean()

        if not self.obrigatorio_para_envio:
            return cleaned_data

        obrigatorios = [
            "efs",
            "pais",
            "titulo",
            "tipo_experiencia",
            "setor",
            "contato_referencia",
            "email_contato",
            "descricao",
            "enfoque_justica_climatica",
            "ano_execucao",
        ]
        for campo in obrigatorios:
            if not cleaned_data.get(campo):
                self.add_error(
                    campo,
                    texto_idioma(
                        "Campo obrigatório para envio da boa prática.",
                        "Campo obligatorio para enviar la buena práctica.",
                        "Required field to submit the good practice.",
                    ),
                )
        if not cleaned_data.get("temas_transversais"):
            self.add_error(
                "temas_transversais",
                texto_idioma(
                    "Selecione pelo menos um tema transversal.",
                    "Seleccione al menos un tema transversal.",
                    "Select at least one cross-cutting theme.",
                ),
            )
        if not cleaned_data.get("normas_internacionais"):
            self.add_error(
                "normas_internacionais",
                texto_idioma(
                    "Selecione pelo menos uma norma internacional.",
                    "Seleccione al menos una norma internacional.",
                    "Select at least one international standard.",
                ),
            )
        return cleaned_data


class AnexoSubmissaoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ["titulo", "arquivo", "url_externa"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "arquivo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "url_externa": forms.URLInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idioma = idioma_atual()
        textos = {
            "titulo": {
                "pt": "Título do anexo",
                "es": "Título del anexo",
                "en": "Attachment title",
            },
            "arquivo": {
                "pt": "Arquivo",
                "es": "Archivo",
                "en": "File",
            },
            "url_externa": {
                "pt": "Link externo",
                "es": "Enlace externo",
                "en": "External link",
            },
        }
        for campo, traducoes in textos.items():
            self.fields[campo].label = traducoes[idioma]


class RevisaoExperienciaForm(forms.ModelForm):
    acao = forms.ChoiceField(
        choices=[
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar", "Aprobar", "Approve")),
            ("publicar", texto_idioma("Publicar", "Publicar", "Publish")),
            ("devolver", texto_idioma("Devolver para ajuste", "Devolver para ajustes", "Return for adjustments")),
            ("rejeitar", texto_idioma("Rejeitar", "Rechazar", "Reject")),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Experiencia
        fields = ["acao", "comentario_revisor"]
        widgets = {
            "comentario_revisor": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": texto_idioma(
                        "Registre comentários para o autor ou justificativa da decisão.",
                        "Registre comentarios para el autor o la justificación de la decisión.",
                        "Record comments for the author or the reason for the decision.",
                    ),
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acao"].choices = [
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar", "Aprobar", "Approve")),
            ("publicar", texto_idioma("Publicar", "Publicar", "Publish")),
            ("devolver", texto_idioma("Devolver para ajuste", "Devolver para ajustes", "Return for adjustments")),
            ("rejeitar", texto_idioma("Rejeitar", "Rechazar", "Reject")),
        ]
        self.fields["acao"].label = texto_idioma("Decisão da revisão", "Decisión de la revisión", "Review decision")
        self.fields["comentario_revisor"].label = texto_idioma("Comentário do revisor", "Comentario del revisor", "Reviewer comment")


class ConsultaStatusForm(forms.Form):
    email_contato = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "nome@efs.gob",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email_contato"].label = texto_idioma(
            "E-mail institucional informado no envio",
            "Correo institucional informado en el envío",
            "Institutional e-mail provided in the submission",
        )


class PropostaEdicaoPublicadaForm(ExperienciaSubmissaoForm):
    comentario_autor = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": texto_idioma(
                    "Explique resumidamente o que mudou e por que a alteração é necessária.",
                    "Explique brevemente qué cambió y por qué la modificación es necesaria.",
                    "Briefly explain what changed and why the adjustment is necessary.",
                ),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comentario_autor"].label = texto_idioma(
            "Comentário sobre a alteração solicitada",
            "Comentario sobre la modificación solicitada",
            "Comment on the requested change",
        )


class RevisaoPropostaEdicaoForm(forms.ModelForm):
    acao = forms.ChoiceField(
        choices=[
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar e aplicar edição", "Aprobar y aplicar edición", "Approve and apply edit")),
            ("rejeitar", texto_idioma("Rejeitar proposta", "Rechazar propuesta", "Reject proposal")),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = PropostaEdicaoExperiencia
        fields = ["acao", "comentario_revisor"]
        widgets = {
            "comentario_revisor": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": texto_idioma(
                        "Registre a justificativa da decisão ou orientação ao autor.",
                        "Registre la justificación de la decisión u orientación al autor.",
                        "Record the reason for the decision or guidance to the author.",
                    ),
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acao"].choices = [
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar e aplicar edição", "Aprobar y aplicar edición", "Approve and apply edit")),
            ("rejeitar", texto_idioma("Rejeitar proposta", "Rechazar propuesta", "Reject proposal")),
        ]
        self.fields["acao"].label = texto_idioma("Decisão sobre a proposta", "Decisión sobre la propuesta", "Decision on the proposal")
        self.fields["comentario_revisor"].label = texto_idioma("Comentário do revisor", "Comentario del revisor", "Reviewer comment")
