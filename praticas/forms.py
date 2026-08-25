from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.db.models import Q
from django.utils.translation import get_language

from .models import (
    Anexo,
    Experiencia,
    Ferramenta,
    NormaInternacional,
    SETORES_OFICIAIS_CODIGOS,
    TIPOS_BOA_PRATICA_OFICIAIS,
    PropostaEdicaoExperiencia,
    Setor,
)
from .uploads import validar_anexo_upload, validar_ficha_tecnica_upload


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


class CadastroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rotulos = {
            "first_name": texto_idioma("Nome", "Nombre", "First name"),
            "last_name": texto_idioma("Sobrenome", "Apellido", "Last name"),
            "username": texto_idioma("Usuário", "Usuario", "Username"),
            "email": texto_idioma("E-mail", "Correo electrónico", "E-mail"),
            "password1": texto_idioma("Senha", "Contraseña", "Password"),
            "password2": texto_idioma(
                "Confirmação da senha",
                "Confirmación de la contraseña",
                "Password confirmation",
            ),
        }
        autocompletes = {
            "first_name": "given-name",
            "last_name": "family-name",
            "username": "username",
            "email": "email",
            "password1": "new-password",
            "password2": "new-password",
        }
        for nome, field in self.fields.items():
            field.label = rotulos[nome]
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("autocomplete", autocompletes[nome])

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                texto_idioma(
                    "Já existe uma conta com este e-mail.",
                    "Ya existe una cuenta con este correo electrónico.",
                    "An account with this e-mail already exists.",
                )
            )
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data["first_name"].strip()
        usuario.last_name = self.cleaned_data["last_name"].strip()
        usuario.email = self.cleaned_data["email"]
        usuario.is_active = False
        if commit:
            usuario.save()
        return usuario


class ReenviarConfirmacaoForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = texto_idioma(
            "E-mail", "Correo electrónico", "E-mail"
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "email"}
        )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class RecuperarSenhaForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = texto_idioma(
            "E-mail", "Correo electrónico", "E-mail"
        )
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "email"}
        )

    def save(self, *args, extra_email_context=None, **kwargs):
        contexto = {"LANGUAGE_CODE": get_language() or "pt-br"}
        contexto.update(extra_email_context or {})
        return super().save(
            *args,
            extra_email_context=contexto,
            **kwargs,
        )


class RedefinirSenhaForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = texto_idioma(
            "Nova senha", "Nueva contraseña", "New password"
        )
        self.fields["new_password2"].label = texto_idioma(
            "Confirmação da nova senha",
            "Confirmación de la nueva contraseña",
            "New password confirmation",
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("autocomplete", "new-password")


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
    "paises_participantes": {
        "pt": "Demais países envolvidos",
        "es": "Demás países involucrados",
        "en": "Other countries involved",
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
    "tipo_auditoria": {
        "pt": "Tipo de auditoria",
        "es": "Tipo de auditoría",
        "en": "Type of audit",
    },
    "outras_efs_envolvidas": {
        "pt": "Em caso de auditoria coordenada, liste as demais EFS envolvidas",
        "es": "En caso de auditoría coordinada, indique las demás EFS involucradas",
        "en": "For a coordinated audit, list the other SAIs involved",
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
        "email_contato": {
        "pt": "E-mail",
        "es": "Correo electrónico",
        "en": "E-mail",
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
        "pt": "Fontes de informação ou evidências",
        "es": "Fuentes de Información o evidencia",
        "en": "Sources of information or evidence",
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
    "informacoes_adicionais": {
        "pt": "Informações adicionais",
        "es": "Información adicional",
        "en": "Additional information",
    },
    "ano_execucao": {
        "pt": "Ano",
        "es": "Año",
        "en": "Year",
    },
}

EXPERIENCIA_HELP_TEXTS = {
    "pais": {
        "pt": "Em caso de auditoria coordenada, escolha o país líder.",
        "es": "En caso de auditoría coordinada, seleccione el país líder.",
        "en": "For a coordinated audit, select the lead country.",
    },
    "efs": {
        "pt": "Em caso de auditoria coordenada, escolha a EFS líder.",
        "es": "En caso de auditoría coordinada, seleccione la EFS líder.",
        "en": "For a coordinated audit, select the lead SAI.",
    },
    "paises_participantes": {
        "pt": "Não repita o país líder nesta lista.",
        "es": "No repita el país líder en esta lista.",
        "en": "Do not repeat the lead country in this list.",
    },
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
    "criterios_utilizados": {
        "pt": "Critérios não são apenas normas. Inclua normas, políticas, planos, parâmetros técnicos, indicadores, linhas de base ou referências usadas para avaliar a prática.",
        "es": "Los criterios no son solamente normas. Incluya normas, políticas, planes, parámetros técnicos, indicadores, líneas de base o referencias usadas para evaluar la práctica.",
        "en": "Criteria are not only legal standards. Include standards, policies, plans, technical parameters, indicators, baselines or references used to assess the practice.",
    },
    "metodologia": {
        "pt": "Descreva a abordagem geral do trabalho: como a experiência foi planejada, executada e analisada.",
        "es": "Describa el enfoque general del trabajo: cómo se planificó, ejecutó y analizó la experiencia.",
        "en": "Describe the overall work approach: how the experience was planned, implemented and analysed.",
    },
    "ferramentas_utilizadas": {
        "pt": "Informe as principais fontes de informação ou evidências utilizadas na boa prática.",
        "es": "Informe las principales fuentes de información o evidencias utilizadas en la buena práctica.",
        "en": "Provide the main sources of information or evidence used in the good practice.",
    },
    "informacoes_adicionais": {
        "pt": "Use este campo para registrar observações complementares, contexto institucional ou informações que não se encaixem nos campos anteriores.",
        "es": "Use este campo para registrar observaciones complementarias, contexto institucional o información que no encaje en los campos anteriores.",
        "en": "Use this field to record complementary observations, institutional context or information that does not fit the previous fields.",
    },
    "titulo": {
        "pt": "Use um título curto e específico, que identifique claramente a experiência.",
        "es": "Use un título breve y específico, que identifique claramente la experiencia.",
        "en": "Use a short and specific title that clearly identifies the experience.",
    },
    "email_contato": {
        "pt": "Informe o e-mail institucional para acompanhar o envio e receber orientações de revisão.",
        "es": "Informe el correo institucional para acompañar el envío y recibir orientaciones de revisión.",
        "en": "Provide the institutional e-mail to track the submission and receive review guidance.",
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


class TipoExperienciaSelect(forms.Select):
    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        instancia = getattr(value, "instance", None)
        if instancia is not None:
            option["attrs"]["data-tipo-codigo"] = instancia.codigo or ""
        return option


class ExperienciaSubmissaoForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = [
            "efs",
            "pais",
            "paises_participantes",
            "titulo",
            "tipo_experiencia",
            "tipo_auditoria",
            "outras_efs_envolvidas",
            "setor",
            "temas_transversais",
            "normas_internacionais",
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
            "informacoes_adicionais",
            "ano_execucao",
        ]
        widgets = {
            "efs": forms.Select(attrs={"class": "form-select"}),
            "pais": forms.Select(attrs={"class": "form-select"}),
            "paises_participantes": forms.CheckboxSelectMultiple(),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_experiencia": TipoExperienciaSelect(attrs={"class": "form-select"}),
            "tipo_auditoria": forms.Select(attrs={"class": "form-select"}),
            "outras_efs_envolvidas": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "setor": forms.Select(attrs={"class": "form-select"}),
            "temas_transversais": forms.CheckboxSelectMultiple(),
            "normas_internacionais": forms.CheckboxSelectMultiple(),
            "email_contato": forms.EmailInput(attrs={"class": "form-control"}),
            "pessoa_responsavel": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "enfoque_justica_climatica": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "objetivo": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "perguntas_chave": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "criterios_utilizados": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "metodologia": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "ferramentas_utilizadas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "resultados": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "recomendacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "replicabilidade": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "informacoes_adicionais": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "ano_execucao": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, obrigatorio_para_envio=True, **kwargs):
        self.obrigatorio_para_envio = obrigatorio_para_envio
        super().__init__(*args, **kwargs)
        aplicar_textos_experiencia(self)

        tipo_atual = self.instance.tipo_experiencia_id if self.instance.pk else None
        setor_atual = self.instance.setor_id if self.instance.pk else None
        if self.fields["tipo_experiencia"].queryset.filter(
            codigo__in=TIPOS_BOA_PRATICA_OFICIAIS
        ).exists():
            filtro_tipos = Q(codigo__in=TIPOS_BOA_PRATICA_OFICIAIS)
        else:
            filtro_tipos = Q()
        if self.fields["setor"].queryset.filter(
            codigo__in=SETORES_OFICIAIS_CODIGOS
        ).exists():
            filtro_setores = Q(codigo__in=SETORES_OFICIAIS_CODIGOS)
        else:
            filtro_setores = Q()
        if tipo_atual:
            filtro_tipos |= Q(pk=tipo_atual)
        if setor_atual:
            filtro_setores |= Q(pk=setor_atual)
        self.fields["tipo_experiencia"].queryset = (
            self.fields["tipo_experiencia"].queryset.filter(filtro_tipos).distinct()
        )
        self.fields["setor"].queryset = (
            self.fields["setor"].queryset.filter(filtro_setores).distinct()
        )
        self.fields["tipo_auditoria"].choices = [
            ("", "---------"),
            (
                Experiencia.TipoAuditoria.DESEMPENHO,
                texto_idioma(
                    "Auditoria de Desempenho / Gestão",
                    "Auditoría de Desempeño / Gestión",
                    "Performance / Management Audit",
                ),
            ),
            (
                Experiencia.TipoAuditoria.CUMPRIMENTO,
                texto_idioma(
                    "Auditoria de Cumprimento",
                    "Auditoría de Cumplimiento",
                    "Compliance Audit",
                ),
            ),
            (
                Experiencia.TipoAuditoria.FINANCEIRA,
                texto_idioma(
                    "Auditoria Financeira",
                    "Auditoría Financiera",
                    "Financial Audit",
                ),
            ),
        ]

        if self.is_bound:
            self.perguntas_auditoria_valores = self.data.getlist(
                "perguntas_auditoria"
            )
        elif self.instance.pk:
            self.perguntas_auditoria_valores = list(
                self.instance.perguntas_auditoria.order_by("ordem").values_list(
                    "texto", flat=True
                )
            )
        else:
            self.perguntas_auditoria_valores = [""]
        if not self.perguntas_auditoria_valores:
            self.perguntas_auditoria_valores = [""]
        self.perguntas_auditoria_limpas = []

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo_experiencia")
        tipo_codigo = getattr(tipo, "codigo", None)
        eh_auditoria = tipo_codigo in {"auditoria", "auditoria_coordenada"}
        eh_coordenada = tipo_codigo == "auditoria_coordenada"
        pais = cleaned_data.get("pais")
        efs = cleaned_data.get("efs")
        paises_participantes = cleaned_data.get("paises_participantes")

        # O texto legado continua editável apenas para avaliação de política
        # pública. Auditorias usam PerguntaAuditoria e nunca podem apagar ou
        # sobrescrever um histórico já armazenado neste campo.
        if eh_auditoria:
            cleaned_data["perguntas_chave"] = (
                self.instance.perguntas_chave if self.instance.pk else ""
            )

        if pais and efs and efs.pais_id != pais.pk:
            self.add_error(
                "efs",
                texto_idioma(
                    "A EFS líder deve pertencer ao país líder selecionado.",
                    "La EFS líder debe pertenecer al país líder seleccionado.",
                    "The lead SAI must belong to the selected lead country.",
                ),
            )
        if pais and paises_participantes and paises_participantes.filter(pk=pais.pk).exists():
            self.add_error(
                "paises_participantes",
                texto_idioma(
                    "O país líder não pode ser repetido entre os participantes.",
                    "El país líder no puede repetirse entre los participantes.",
                    "The lead country cannot be repeated among participants.",
                ),
            )
        if not eh_coordenada and (
            cleaned_data.get("outras_efs_envolvidas") or paises_participantes
        ):
            mensagem = texto_idioma(
                "Esses dados só podem ser informados para auditoria coordenada.",
                "Estos datos solo pueden informarse para una auditoría coordinada.",
                "These data may only be provided for a coordinated audit.",
            )
            if cleaned_data.get("outras_efs_envolvidas"):
                self.add_error("outras_efs_envolvidas", mensagem)
            if paises_participantes:
                self.add_error("paises_participantes", mensagem)
        if not eh_auditoria and cleaned_data.get("tipo_auditoria"):
            self.add_error(
                "tipo_auditoria",
                texto_idioma(
                    "Tipo de auditoria não se aplica a esta categoria.",
                    "El tipo de auditoría no se aplica a esta categoría.",
                    "Audit type does not apply to this category.",
                ),
            )

        for indice, valor in enumerate(self.perguntas_auditoria_valores, start=1):
            texto = valor.strip()
            if not texto:
                continue
            if len(texto) > 2000:
                self.add_error(
                    None,
                    texto_idioma(
                        f"A pergunta {indice} excede 2.000 caracteres.",
                        f"La pregunta {indice} supera los 2.000 caracteres.",
                        f"Question {indice} exceeds 2,000 characters.",
                    ),
                )
                continue
            self.perguntas_auditoria_limpas.append(texto)

        if not eh_auditoria and self.perguntas_auditoria_limpas:
            self.add_error(
                None,
                texto_idioma(
                    "Perguntas de auditoria só podem ser informadas para categorias de auditoria.",
                    "Las preguntas de auditoría solo pueden informarse para categorías de auditoría.",
                    "Audit questions may only be provided for audit categories.",
                ),
            )

        if not self.obrigatorio_para_envio:
            return cleaned_data

        obrigatorios = [
            "efs",
            "pais",
            "titulo",
            "tipo_experiencia",
            "setor",
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
        if eh_auditoria and not cleaned_data.get("tipo_auditoria"):
            self.add_error(
                "tipo_auditoria",
                texto_idioma(
                    "Campo obrigatório para categorias de auditoria.",
                    "Campo obligatorio para categorías de auditoría.",
                    "Required field for audit categories.",
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


class FerramentaSubmissaoForm(forms.Form):
    nome = forms.CharField(max_length=220)
    ano = forms.IntegerField(min_value=1900, max_value=2100)
    descricao = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    setor = forms.ModelChoiceField(queryset=Setor.objects.none())
    link_acesso = forms.URLField(max_length=500)
    pais_ou_instancia = forms.CharField(max_length=255)

    def __init__(self, *args, obrigatorio_para_envio=True, **kwargs):
        self.obrigatorio_para_envio = obrigatorio_para_envio
        super().__init__(*args, **kwargs)
        setores = Setor.objects.all()
        if setores.filter(codigo__in=SETORES_OFICIAIS_CODIGOS).exists():
            setores = setores.filter(codigo__in=SETORES_OFICIAIS_CODIGOS)
        self.fields["setor"].queryset = setores.order_by("nome")
        textos = {
            "nome": ("Nome", "Nombre", "Name"),
            "ano": ("Ano", "Año", "Year"),
            "descricao": ("Descrição", "Descripción", "Description"),
            "setor": ("Setor", "Sector", "Sector"),
            "link_acesso": ("Link de acesso", "Enlace de acceso", "Access link"),
            "pais_ou_instancia": (
                "País ou Instância",
                "País o Instancia",
                "Country or Body",
            ),
        }
        for nome, (pt, es, en) in textos.items():
            self.fields[nome].label = texto_idioma(pt, es, en)
            classe = "form-select" if nome == "setor" else "form-control"
            self.fields[nome].widget.attrs.setdefault("class", classe)
            if not obrigatorio_para_envio:
                self.fields[nome].required = False
        self.fields["pais_ou_instancia"].help_text = texto_idioma(
            "Instância OLACEFS pode ser uma comissão, grupo de trabalho ou outra instância da organização relacionada à iniciativa.",
            "Una instancia de la OLACEFS puede ser una comisión, un grupo de trabajo u otra instancia de la organización relacionada con la iniciativa.",
            "An OLACEFS body may be a commission, working group or another organizational body related to the initiative.",
        )

    def clean(self):
        cleaned_data = super().clean()
        if self.obrigatorio_para_envio:
            for nome in self.fields:
                if not cleaned_data.get(nome):
                    self.add_error(
                        nome,
                        texto_idioma(
                            "Campo obrigatório para envio da ferramenta.",
                            "Campo obligatorio para enviar la herramienta.",
                            "Required field to submit the tool.",
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

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        validar_anexo_upload(arquivo)
        return arquivo


class AnexoAdminForm(AnexoSubmissaoForm):
    class Meta(AnexoSubmissaoForm.Meta):
        fields = "__all__"


class ExperienciaAdminForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo_experiencia")
        tipo_codigo = getattr(tipo, "codigo", None)
        pais = cleaned_data.get("pais")
        paises_participantes = cleaned_data.get("paises_participantes")

        if tipo_codigo in {"auditoria", "auditoria_coordenada"}:
            valor_historico = self.instance.perguntas_chave if self.instance.pk else ""
            if cleaned_data.get("perguntas_chave", "") != valor_historico:
                self.add_error(
                    "perguntas_chave",
                    "Auditorias usam perguntas estruturadas; o texto legado não pode ser alterado.",
                )

        if paises_participantes and tipo_codigo != "auditoria_coordenada":
            self.add_error(
                "paises_participantes",
                "Países participantes só podem ser informados em auditoria coordenada.",
            )
        if (
            pais
            and paises_participantes
            and paises_participantes.filter(pk=pais.pk).exists()
        ):
            self.add_error(
                "paises_participantes",
                "O país líder não pode ser repetido entre os países participantes.",
            )
        return cleaned_data


class NormaInternacionalAdminForm(forms.ModelForm):
    class Meta:
        model = NormaInternacional
        fields = "__all__"

    def clean_ficha_tecnica(self):
        arquivo = self.cleaned_data.get("ficha_tecnica")
        validar_ficha_tecnica_upload(arquivo)
        return arquivo


class RevisaoExperienciaForm(forms.ModelForm):
    acao = forms.ChoiceField(
        choices=[
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar", "Aprobar", "Approve")),
            ("publicar", texto_idioma("Publicar", "Publicar", "Publish")),
            ("arquivar", texto_idioma("Arquivar", "Archivar", "Archive")),
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
        choices = [
            ("em_revisao", texto_idioma("Marcar como em revisão", "Marcar como en revisión", "Mark as under review")),
            ("aprovar", texto_idioma("Aprovar", "Aprobar", "Approve")),
            ("publicar", texto_idioma("Publicar", "Publicar", "Publish")),
            ("arquivar", texto_idioma("Arquivar", "Archivar", "Archive")),
            ("devolver", texto_idioma("Devolver para ajuste", "Devolver para ajustes", "Return for adjustments")),
            ("rejeitar", texto_idioma("Rejeitar", "Rechazar", "Reject")),
        ]
        if self.instance.status_publicacao == Experiencia.StatusPublicacao.PUBLICADO:
            choices = [("arquivar", texto_idioma("Arquivar", "Archivar", "Archive"))]
        elif self.instance.status_publicacao == Experiencia.StatusPublicacao.ARQUIVADO:
            choices = [("publicar", texto_idioma("Restaurar / Publicar", "Restaurar / Publicar", "Restore / Publish"))]
        self.fields["acao"].choices = choices
        self.fields["acao"].label = texto_idioma("Decisão da revisão", "Decisión de la revisión", "Review decision")
        self.fields["comentario_revisor"].label = texto_idioma("Comentário do revisor", "Comentario del revisor", "Reviewer comment")


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
