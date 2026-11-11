from django.urls import path
from . import views

urlpatterns = [
    # Projetos
    path('', views.projeto_lista, name='projeto_lista'),
    path('novo/', views.projeto_criar_ou_editar, name='projeto_novo'),
    path('<int:pk>/editar/', views.projeto_criar_ou_editar, name='projeto_editar'),
    path('<int:pk>/excluir/', views.projeto_excluir, name='projeto_excluir'),

    # Laudos Ativos e Vencimentos
    path('laudos/', views.laudos_lista, name='laudos_lista'),

    # Agenda Técnica
    path('agenda/', views.agenda_tecnica, name='agenda_tecnica'),

    # Central de Gerenciamento Modular
    path('gerenciamento/', views.gerenciamento_hub, name='gerenciamento_hub'),

    # Módulo 1: Técnicos
    path('gerenciamento/tecnicos/', views.gerenciamento_tecnicos, name='gerenciamento_tecnicos'),
    path('gerenciamento/tecnicos/<int:pk>/editar/', views.tecnico_editar, name='tecnico_editar'),
    path('gerenciamento/tecnicos/<int:pk>/excluir/', views.tecnico_excluir, name='tecnico_excluir'),

    # Módulo 2: Tipos de Projetos
    path('gerenciamento/tipos/', views.gerenciamento_tipos, name='gerenciamento_tipos'),
    path('gerenciamento/tipos/<int:pk>/editar/', views.tipo_projeto_editar, name='tipo_projeto_editar'),
    path('gerenciamento/tipos/<int:pk>/excluir/', views.tipo_projeto_excluir, name='tipo_projeto_excluir'),

    # Módulo 3: Tarefas Padrão
    path('gerenciamento/tarefas-padrao/', views.gerenciamento_tarefas_padrao, name='gerenciamento_tarefas_padrao'),
    path('gerenciamento/tarefas-padrao/<int:pk>/editar/', views.tarefa_padrao_editar, name='tarefa_padrao_editar'),
    path('gerenciamento/tarefas-padrao/<int:pk>/excluir/', views.tarefa_padrao_excluir, name='tarefa_padrao_excluir'),

    # Módulo 4: Usuários do Sistema
    path('gerenciamento/usuarios/', views.gerenciamento_usuarios, name='gerenciamento_usuarios'),
    path('gerenciamento/usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('gerenciamento/usuarios/<int:pk>/excluir/', views.usuario_excluir, name='usuario_excluir'),

    # Módulo 5: Estados / Status do Projeto
    path('gerenciamento/status/', views.gerenciamento_status, name='gerenciamento_status'),
    path('gerenciamento/status/<int:pk>/editar/', views.status_projeto_editar, name='status_projeto_editar'),
    path('gerenciamento/status/<int:pk>/excluir/', views.status_projeto_excluir, name='status_projeto_excluir'),

    # APIs internas
    path('api/tarefas-padrao/<int:tipo_id>/', views.tarefas_padrao_por_tipo_json, name='tarefas_padrao_por_tipo_json'),
    path('api/filiais/<int:cliente_id>/', views.filiais_por_cliente_json, name='filiais_por_cliente_json'),
]