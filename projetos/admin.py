from django.contrib import admin
from .models import TipoProjeto, Projeto, Tarefa, TarefaPadrao, Tecnico


class TarefaPadraoInline(admin.TabularInline):
    model = TarefaPadrao
    extra = 3  # Abre 3 linhas em branco para digitar os nomes rapidamente
    fields = ('ordem', 'nome', 'ativo')


@admin.register(TipoProjeto)
class TipoProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'requer_lembrete', 'ativo', 'total_tarefas')
    list_editable = ('requer_lembrete', 'ativo')
    search_fields = ('nome',)
    inlines = [TarefaPadraoInline]

    def total_tarefas(self, obj):
        return obj.tarefas_padrao.count()
    total_tarefas.short_description = "Tarefas Padrão"


@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'area', 'telefone', 'ativo')
    search_fields = ('nome', 'area')
    list_filter = ('area', 'ativo')


class TarefaInline(admin.TabularInline):
    model = Tarefa
    extra = 0
    fields = ('nome', 'tecnico_responsavel', 'data_agendada')


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('numero_os', 'cliente', 'filial', 'tipo_projeto', 'status', 'data_abertura')
    inlines = [TarefaInline]
