import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from .models import Projeto, Tecnico, Tarefa, TarefaPadrao, TipoProjeto
from .forms import ProjetoForm, TecnicoForm
from cadastros.models import Filial


def projeto_lista(request):
    """Lista todos os projetos/OS com busca e botão de Novo Projeto"""
    termo_busca = request.GET.get('busca', '').strip()
    status_filtro = request.GET.get('status', '').strip()
    
    projetos = Projeto.objects.select_related('cliente', 'filial', 'tipo_projeto').all()

    if termo_busca:
        projetos = projetos.filter(
            Q(numero_os__icontains=termo_busca) |
            Q(cliente__nome_fantasia__icontains=termo_busca) |
            Q(cliente__razao_social__icontains=termo_busca) |
            Q(titulo_escopo__icontains=termo_busca)
        )

    if status_filtro:
        projetos = projetos.filter(status=status_filtro)

    return render(request, 'projetos/projeto_lista.html', {
        'projetos': projetos,
        'termo_busca': termo_busca,
        'status_filtro': status_filtro,
        'status_choices': Projeto.STATUS_CHOICES,
    })


def projeto_criar_ou_editar(request, pk=None):
    projeto = get_object_or_404(Projeto, pk=pk) if pk else None
    tecnicos = Tecnico.objects.filter(ativo=True).order_by('nome')
    
    # Mapa de {id_do_tipo: True/False} para o JavaScript controlar a exibição do bloco
    tipos_lembrete_map = {
        tipo.id: tipo.requer_lembrete 
        for tipo in TipoProjeto.objects.all()
    }

    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        nomes_tarefas = request.POST.getlist('tarefa_nome[]')
        tecnicos_ids = request.POST.getlist('tarefa_tecnico[]')
        datas_agendadas = request.POST.getlist('tarefa_data[]')

        if form.is_valid():
            with transaction.atomic():
                proj_salvo = form.save()

                if pk:
                    proj_salvo.tarefas.all().delete()

                for i in range(len(nomes_tarefas)):
                    nome = nomes_tarefas[i].strip()
                    if not nome:
                        continue
                    
                    tec_id = tecnicos_ids[i] if i < len(tecnicos_ids) and tecnicos_ids[i] else None
                    tecnico_obj = Tecnico.objects.filter(id=tec_id).first() if tec_id else None
                    data_val = datas_agendadas[i] if i < len(datas_agendadas) and datas_agendadas[i] else None

                    Tarefa.objects.create(
                        projeto=proj_salvo,
                        nome=nome,
                        tecnico_responsavel=tecnico_obj,
                        data_agendada=data_val
                    )

            messages.success(request, f'Projeto OS {proj_salvo.numero_os} gravado com sucesso!')
            return redirect('projeto_lista')
        else:
            messages.error(request, 'Erro ao gravar o projeto. Verifique os dados.')
    else:
        form = ProjetoForm(instance=projeto)

    tarefas_iniciais = []
    if projeto:
        tarefas_iniciais = [
            {
                'nome': t.nome,
                'tecnico_id': t.tecnico_responsavel_id if t.tecnico_responsavel else None,
                'data': t.data_agendada.strftime('%Y-%m-%d') if t.data_agendada else ''
            }
            for t in projeto.tarefas.all()
        ]

    return render(request, 'projetos/projeto_form.html', {
        'form': form,
        'projeto': projeto,
        'tecnicos': tecnicos,
        'tarefas_iniciais': tarefas_iniciais,
        'tipos_lembrete_json': json.dumps(tipos_lembrete_map),
    })


def projeto_excluir(request, pk):
    """Exclusão de projeto e suas tarefas vinculadas"""
    projeto = get_object_or_404(Projeto, pk=pk)
    if request.method == 'POST':
        num_os = projeto.numero_os
        projeto.delete()
        messages.success(request, f'Projeto OS {num_os} excluído com sucesso.')
    return redirect('projeto_lista')


def tarefas_padrao_por_tipo_json(request, tipo_id):
    """Endpoint chamado via fetch para devolver as tarefas padrão do tipo escolhido"""
    tarefas = TarefaPadrao.objects.filter(tipo_projeto_id=tipo_id, ativo=True).order_by('ordem', 'nome')
    return JsonResponse([{'id': t.id, 'nome': t.nome} for t in tarefas], safe=False)


def gerenciamento_tecnicos(request):
    tecnicos = Tecnico.objects.all().order_by('nome')
    form = TecnicoForm()

    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Técnico cadastrado com sucesso!')
            return redirect('gerenciamento')
        else:
            messages.error(request, 'Erro ao cadastrar técnico.')

    return render(request, 'projetos/gerenciamento.html', {'tecnicos': tecnicos, 'form': form})


def tecnico_editar(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        form = TecnicoForm(request.POST, instance=tecnico)
        if form.is_valid():
            form.save()
            messages.success(request, f'Técnico "{tecnico.nome}" atualizado!')
            return redirect('gerenciamento')
    else:
        form = TecnicoForm(instance=tecnico)

    return render(request, 'projetos/tecnico_form.html', {'form': form, 'tecnico': tecnico})


def tecnico_excluir(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        nome = tecnico.nome
        tecnico.delete()
        messages.success(request, f'Técnico "{nome}" removido com sucesso.')
    return redirect('gerenciamento')


def filiais_por_cliente_json(request, cliente_id):
    filiais = Filial.objects.filter(cliente_id=cliente_id).values('id', 'identificacao', 'cidade')
    return JsonResponse(list(filiais), safe=False)