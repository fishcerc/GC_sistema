from django import forms
from django.contrib.auth.models import User
from .models import Projeto, Tarefa, TipoProjeto, TarefaPadrao, Tecnico, StatusProjeto
from cadastros.models import Cliente, Filial


class TecnicoForm(forms.ModelForm):
    login_usuario = forms.CharField(
        label="Usuário do Sistema (Login)",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: carlos.fischer',
            'autocomplete': 'off'
        })
    )
    senha_usuario = forms.CharField(
        label="Senha de Acesso",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha (deixe em branco para manter a atual)',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = Tecnico
        fields = ['nome', 'telefone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Carlos Fischer'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(47) 99999-9999'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.usuario:
            self.fields['login_usuario'].initial = self.instance.usuario.username
        else:
            self.fields['senha_usuario'].widget.attrs['placeholder'] = 'Defina uma senha para o login'

    def clean_login_usuario(self):
        username = self.cleaned_data.get('login_usuario', '').strip()
        if not username:
            return ''
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk and self.instance.usuario_id:
            qs = qs.exclude(pk=self.instance.usuario_id)
        # Se já existe um User com esse username mas ainda não está vinculado a outro técnico, permitimos vincular
        outro_tecnico = Tecnico.objects.filter(usuario__username=username)
        if self.instance and self.instance.pk:
            outro_tecnico = outro_tecnico.exclude(pk=self.instance.pk)
        if outro_tecnico.exists():
            raise forms.ValidationError("Este usuário já está vinculado a outro técnico.")
        return username

    def save(self, commit=True):
        tecnico = super().save(commit=False)
        username = self.cleaned_data.get('login_usuario', '').strip()
        senha = self.cleaned_data.get('senha_usuario', '')

        if username:
            if tecnico.usuario:
                user = tecnico.usuario
                user.username = username
                user.first_name = tecnico.nome
                user.is_active = tecnico.ativo
                if senha:
                    user.set_password(senha)
                user.save()
            else:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'first_name': tecnico.nome, 'is_active': tecnico.ativo}
                )
                if not created:
                    user.first_name = tecnico.nome
                    user.is_active = tecnico.ativo
                if senha:
                    user.set_password(senha)
                elif created:
                    user.set_password('123456')
                user.save()
                tecnico.usuario = user

        if commit:
            tecnico.save()
        return tecnico


class UsuarioSistemaForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a senha (deixe em branco na edição para manter)'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: carlos.fischer'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de exibição'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@empresa.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['senha'].required = True
            self.fields['senha'].widget.attrs['placeholder'] = 'Digite a senha de acesso'

    def save(self, commit=True):
        user = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        if senha:
            user.set_password(senha)
        if commit:
            user.save()
        return user

class TipoProjetoForm(forms.ModelForm):
    class Meta:
        model = TipoProjeto
        fields = ['nome', 'requer_lembrete', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Laudo SPDA, Inspeção Termográfica'}),
            'requer_lembrete': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StatusProjetoForm(forms.ModelForm):
    class Meta:
        model = StatusProjeto
        fields = ['nome', 'cor', 'ordem', 'eh_concluido', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Em Execução, Concluído'}),
            'cor': forms.Select(attrs={'class': 'form-select'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'eh_concluido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TarefaPadraoForm(forms.ModelForm):
    class Meta:
        model = TarefaPadrao
        fields = ['tipo_projeto', 'nome', 'ordem', 'ativo']
        widgets = {
            'tipo_projeto': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Medição da Resistência de Aterramento'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
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
            'status': forms.Select(attrs={'class': 'form-select', 'id': 'select-status'}),
            'data_abertura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_previsao_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'requer_renovacao': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_requer_renovacao'}),
            'meses_validade': forms.NumberInput(attrs={'class': 'form-control', 'id': 'input-validade'}),
            'data_alerta_renovacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'input-data-alerta'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_projeto'].queryset = TipoProjeto.objects.filter(ativo=True)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome_fantasia')

        try:
            estados = list(StatusProjeto.objects.filter(ativo=True).order_by('ordem', 'nome'))
            if estados:
                opcoes = [(s.nome, s.nome) for s in estados]
            else:
                opcoes = [('Em Planejamento', 'Em Planejamento'), ('Em Execução', 'Em Execução'), ('Concluído', 'Concluído')]
        except Exception:
            opcoes = [('Em Planejamento', 'Em Planejamento'), ('Em Execução', 'Em Execução'), ('Concluído', 'Concluído')]

        if self.instance and self.instance.pk and self.instance.status:
            valores_existentes = [c[0] for c in opcoes]
            if self.instance.status not in valores_existentes:
                opcoes.append((self.instance.status, self.instance.status))

        self.fields['status'].widget = forms.Select(
            attrs={'class': 'form-select', 'id': 'select-status'},
            choices=opcoes
        )