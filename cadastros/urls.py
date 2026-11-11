from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/novo/', views.cliente_escolher_tipo, name='cliente_novo'),
    path('clientes/novo/pj/', views.cliente_criar_ou_editar, {'tipo': 'PJ'}, name='cliente_novo_pj'),
    path('clientes/novo/pf/', views.cliente_criar_ou_editar, {'tipo': 'PF'}, name='cliente_novo_pf'),
    path('clientes/<int:pk>/editar/', views.cliente_criar_ou_editar, name='cliente_editar'),
    path('clientes/<int:pk>/excluir/', views.cliente_excluir, name='cliente_excluir'),
]