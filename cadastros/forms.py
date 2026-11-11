from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Filial, DadosEnergia


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj', 
            'inscricao_estadual', 'inscricao_municipal',
            'logradouro', 'numero', 'complemento', 'bairro', 
            'cidade', 'estado', 'cep',
            'pessoa_contato', 'email', 'telefone', 'celular'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Indústria Metalúrgica SA'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Metalúrgica'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control'}),
            'inscricao_municipal': forms.TextInput(attrs={'class': 'form-control'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'pessoa_contato': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
        }


class FilialForm(forms.ModelForm):
    class Meta:
        model = Filial
        fields = [
            'identificacao', 'cnpj', 'logradouro', 'numero', 
            'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'pessoa_contato', 'celular'
        ]
        widgets = {
            'identificacao': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ex: Galpão 02 / Unidade Fabril'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'numero': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'estado': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'pessoa_contato': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'celular': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class DadosEnergiaForm(forms.ModelForm):
    class Meta:
        model = DadosEnergia
        fields = [
            'unidade_consumidora', 'concessionaria', 'tensao_fornecimento',
            'demanda_contratada_kw', 'potencia_trafo_kva', 'tipo_subestacao',
            'observacoes_eletricas'
        ]
        widgets = {
            'unidade_consumidora': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nº da UC'}),
            'concessionaria': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'tensao_fornecimento': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ex: 380/220V, 13.8 kV'}),
            'demanda_contratada_kw': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'potencia_trafo_kva': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'tipo_subestacao': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ex: Aérea, Abrigada'}),
            'observacoes_eletricas': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }


# Formsets: permitem associar múltiplas linhas dinamicamente ao mesmo Cliente
FilialFormSet = inlineformset_factory(
    Cliente, 
    Filial, 
    form=FilialForm, 
    extra=0, 
    can_delete=True
)

DadosEnergiaFormSet = inlineformset_factory(
    Cliente, 
    DadosEnergia, 
    form=DadosEnergiaForm, 
    extra=0, 
    can_delete=True
)