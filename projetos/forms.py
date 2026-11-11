from django import forms
from .models import Projeto, Tarefa, TipoProjeto, Tecnico
from cadastros.models import Cliente, Filial


class TecnicoForm(forms.ModelForm):
    class Meta:
        model = Tecnico
        fields = ['nome', 'area', 'telefone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Carlos Fischer'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Termografia, SPDA, Subestação'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(47) 99999-9999'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'numero_os', 'tipo_projeto', 'cliente', 'filial',
            'titulo_escopo', 'status', 'data_abertura', 'data_previsao_entrega',
            'requer_renovacao', 'meses_validade', 'data_alerta_renovacao'
        ]
        widgets = {
            'numero_os': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 4974'}),
            'tipo_projeto': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select', 'id': 'select-cliente'}),
            'filial': forms.Select(attrs={'class': 'form-select', 'id': 'select-filial'}),
            'titulo_escopo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Inspeção Anual de Subestação'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_abertura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_previsao_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'requer_renovacao': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'check-renovacao'}),
            'meses_validade': forms.NumberInput(attrs={'class': 'form-control', 'id': 'input-validade'}),
            'data_alerta_renovacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'input-data-alerta'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_projeto'].queryset = TipoProjeto.objects.filter(ativo=True)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome_fantasia')