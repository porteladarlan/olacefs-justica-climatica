from django import forms

from .models import Anexo, Experiencia


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


class AnexoSubmissaoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ["titulo", "arquivo", "url_externa"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "arquivo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "url_externa": forms.URLInput(attrs={"class": "form-control"}),
        }
