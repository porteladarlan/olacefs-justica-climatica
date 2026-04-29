from django import forms

from .models import Anexo, Experiencia, PropostaEdicaoExperiencia


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
            "contribui_para_guia",
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
            "contribui_para_guia": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "efs": "EFS",
            "pais": "País",
            "titulo": "Nome da boa prática / iniciativa",
            "tipo_experiencia": "Tipo de boa prática",
            "setor": "Setor",
            "temas_transversais": "Temas transversais",
            "normas_internacionais": "Normas internacionais relacionadas",
            "contato_referencia": "Contato de referência da EFS",
            "email_contato": "E-mail institucional de referência",
            "pessoa_responsavel": "Pessoa responsável",
            "descricao": "Resumo da boa prática",
            "enfoque_justica_climatica": "Vínculo com justiça climática",
            "objetivo": "Objetivo",
            "perguntas_chave": "Perguntas de auditoria utilizadas",
            "criterios_utilizados": "Critérios utilizados",
            "metodologia": "Metodologia",
            "ferramentas_utilizadas": "Ferramentas, matrizes ou instrumentos utilizados",
            "resultados": "Resultados",
            "recomendacoes": "Recomendações",
            "replicabilidade": "Replicabilidade",
            "ano_execucao": "Ano",
            "contribui_para_guia": "Esta experiência pode contribuir como exemplo para a Guia?",
        }
        help_texts = {
            "descricao": "Inclua um resumo objetivo, suficiente para que outra EFS entenda o que foi feito.",
            "enfoque_justica_climatica": "Explique como a experiência considera equidade, direitos humanos, vulnerabilidades ou impactos diferenciados.",
            "temas_transversais": "Marque todos os temas aplicáveis.",
            "normas_internacionais": "Marque os marcos internacionais relacionados, como Acordo de Paris ou ODS.",
            "ferramentas_utilizadas": "Exemplos: perguntas, matrizes, checklists, metodologias, painéis ou bases de dados.",
        }

    def __init__(self, *args, obrigatorio_para_envio=True, **kwargs):
        self.obrigatorio_para_envio = obrigatorio_para_envio
        super().__init__(*args, **kwargs)

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
                self.add_error(campo, "Campo obrigatório para envio da boa prática.")
        if not cleaned_data.get("temas_transversais"):
            self.add_error("temas_transversais", "Selecione pelo menos um tema transversal.")
        if not cleaned_data.get("normas_internacionais"):
            self.add_error("normas_internacionais", "Selecione pelo menos uma norma internacional.")
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


class RevisaoExperienciaForm(forms.ModelForm):
    acao = forms.ChoiceField(
        label="Decisão da revisão",
        choices=[
            ("em_revisao", "Marcar como em revisão"),
            ("aprovar", "Aprovar"),
            ("publicar", "Publicar"),
            ("devolver", "Devolver para ajuste"),
            ("rejeitar", "Rejeitar"),
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
                    "placeholder": "Registre comentários para o autor ou justificativa da decisão.",
                }
            )
        }
        labels = {
            "comentario_revisor": "Comentário do revisor",
        }


class ConsultaStatusForm(forms.Form):
    email_contato = forms.EmailField(
        label="E-mail institucional informado no envio",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "nome@efs.gob",
            }
        ),
    )


class PropostaEdicaoPublicadaForm(ExperienciaSubmissaoForm):
    comentario_autor = forms.CharField(
        label="Comentário sobre a alteração solicitada",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Explique resumidamente o que mudou e por que a alteração é necessária.",
            }
        ),
    )


class RevisaoPropostaEdicaoForm(forms.ModelForm):
    acao = forms.ChoiceField(
        label="Decisão sobre a proposta",
        choices=[
            ("em_revisao", "Marcar como em revisão"),
            ("aprovar", "Aprovar e aplicar edição"),
            ("rejeitar", "Rejeitar proposta"),
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
                    "placeholder": "Registre a justificativa da decisão ou orientação ao autor.",
                }
            )
        }
        labels = {
            "comentario_revisor": "Comentário do revisor",
        }
