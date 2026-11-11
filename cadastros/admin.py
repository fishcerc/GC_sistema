from django.contrib import admin
from .models import Cliente, Filial, DadosEnergia


class FilialInline(admin.StackedInline):
    model = Filial
    extra = 0
    classes = ['collapse']  # Permite recolher se houver muitas filiais


class DadosEnergiaInline(admin.TabularInline):
    model = DadosEnergia
    extra = 0
    fields = ('unidade_consumidora', 'concessionaria', 'tensao_fornecimento', 'demanda_contratada_kw', 'potencia_trafo_kva', 'tipo_subestacao')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'nome_fantasia', 'tipo_pessoa', 'cnpj', 'cidade', 'estado', 'pessoa_contato', 'celular')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'cidade')
    list_filter = ('tipo_pessoa', 'cidade', 'estado')
    
    fieldsets = (
        ('Identificação do Cliente (PF / PJ)', {
            'fields': (
                ('tipo_pessoa', 'razao_social', 'nome_fantasia'),
                ('cnpj', 'inscricao_estadual', 'inscricao_municipal'),
            )
        }),
        ('Endereço da Matriz', {
            'fields': (
                ('logradouro', 'numero', 'complemento'),
                ('bairro', 'cidade', 'estado', 'cep'),
            )
        }),
        ('Contatos Principais', {
            'fields': (
                ('pessoa_contato', 'email'),
                ('telefone', 'celular'),
            )
        }),
        ('Campos Extras (Flexível)', {
            'classes': ('collapse',),
            'fields': ('dados_adicionais',),
        }),
    )
    
    inlines = [FilialInline, DadosEnergiaInline]


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('identificacao', 'cliente', 'cidade', 'estado', 'celular')
    search_fields = ('identificacao', 'cliente__nome_fantasia', 'cidade')
    inlines = [DadosEnergiaInline]