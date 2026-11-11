from django.contrib import admin
from .models import TipoProjeto, Projeto, Tarefa, TarefaPadrao, Tecnico, StatusProjeto, DiarioProjeto


@admin.register(StatusProjeto)
class StatusProjetoAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'nome', 'cor', 'eh_concluido', 'ativo')
    list_editable = ('cor', 'eh_concluido', 'ativo')
    ordering = ('ordem', 'nome')


class TarefaPadraoInline(admin.TabularInline):
    model = TarefaPadrao
    extra = 3
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
    list_display = ('nome', 'usuario', 'telefone', 'ativo')
    search_fields = ('nome', 'usuario__username')
    list_filter = ('ativo',)


class TarefaInline(admin.TabularInline):
    model = Tarefa
    extra = 0
    fields = ('concluida', 'nome', 'tecnico_responsavel', 'data_agendada')


class DiarioProjetoInline(admin.TabularInline):
    model = DiarioProjeto
    extra = 0
    readonly_fields = ('criado_em',)
    fields = ('criado_em', 'autor', 'texto', 'arquivo')


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('numero_os', 'cliente', 'filial', 'tipo_projeto', 'status', 'data_abertura')
    inlines = [TarefaInline, DiarioProjetoInline]
