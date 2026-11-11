from django.urls import path
from . import views

urlpatterns = [
    path('', views.projeto_lista, name='projeto_lista'),
    path('novo/', views.projeto_criar_ou_editar, name='projeto_novo'),
    path('<int:pk>/editar/', views.projeto_criar_ou_editar, name='projeto_editar'),
    path('<int:pk>/excluir/', views.projeto_excluir, name='projeto_excluir'),
    path('gerenciamento/', views.gerenciamento_tecnicos, name='gerenciamento'),
    path('tecnico/<int:pk>/editar/', views.tecnico_editar, name='tecnico_editar'),
    path('tecnico/<int:pk>/excluir/', views.tecnico_excluir, name='tecnico_excluir'),
    path('api/tarefas-padrao/<int:tipo_id>/', views.tarefas_padrao_por_tipo_json, name='tarefas_padrao_por_tipo_json'),
    path('api/filiais/<int:cliente_id>/', views.filiais_por_cliente_json, name='filiais_por_cliente_json'),
]