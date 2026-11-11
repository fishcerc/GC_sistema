from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm, ClientePFForm, FilialFormSet, DadosEnergiaFormSet
from projetos.models import Projeto, Tarefa, Tecnico, StatusProjeto


@login_required
def dashboard(request):
    """Dashboard principal com indicadores, projetos por técnico e alertas de renovação de laudos"""
    hoje = date.today()

    nomes_concluidos = list(
        StatusProjeto.objects.filter(eh_concluido=True).values_list('nome', flat=True)
    )
    status_finais = set(['concluido', 'cancelado', 'Concluído', 'Cancelado'] + nomes_concluidos)

    total_clientes = Cliente.objects.count()
    projetos_ativos = Projeto.objects.exclude(status__in=status_finais).count()
    tarefas_agendadas = Tarefa.objects.filter(concluida=False).exclude(
        projeto__status__in=status_finais
    ).count()

    # Alertas de renovação (laudos e inspeções)
    projetos_renovacao = Projeto.objects.select_related('cliente', 'filial', 'tipo_projeto').filter(
        requer_renovacao=True,
        data_alerta_renovacao__isnull=False
    ).exclude(status__in=['cancelado', 'Cancelado']).order_by('data_alerta_renovacao')

    alertas_renovacao = []
    for proj in projetos_renovacao:
        dias_restantes = (proj.data_alerta_renovacao - hoje).days
        alertas_renovacao.append({
            'projeto': proj,
            'dias_restantes': dias_restantes,
            'vencido': dias_restantes < 0,
            'urgente': 0 <= dias_restantes <= 30,
            'proximo': 30 < dias_restantes <= 60,
        })

    total_alertas_proximos = sum(1 for a in alertas_renovacao if a['dias_restantes'] <= 60)

    # Tarefas e projetos por Técnico
    tecnicos = Tecnico.objects.filter(ativo=True).prefetch_related(
        'tarefas__projeto__cliente',
        'tarefas__projeto__tipo_projeto'
    ).order_by('nome')

    painel_tecnicos = []
    for tec in tecnicos:
        tarefas_ativas = [
            t for t in tec.tarefas.all()
            if not t.concluida and t.projeto.status not in status_finais
        ]
        painel_tecnicos.append({
            'tecnico': tec,
            'tarefas': tarefas_ativas[:5],
            'total_tarefas': len(tarefas_ativas),
        })

    # Identifica se o usuário logado está vinculado a um Técnico
    tecnico_logado = getattr(request.user, 'tecnico', None)
    minhas_tarefas = []
    if tecnico_logado:
        minhas_tarefas = Tarefa.objects.select_related(
            'projeto', 'projeto__cliente', 'projeto__filial', 'projeto__tipo_projeto'
        ).filter(
            tecnico_responsavel=tecnico_logado,
            concluida=False
        ).exclude(
            projeto__status__in=status_finais
        ).order_by('data_agendada', 'id')

    # Últimos projetos registrados
    projetos_recentes = Projeto.objects.select_related(
        'cliente', 'filial', 'tipo_projeto'
    ).order_by('-data_abertura', '-id')[:8]

    return render(request, 'dashboard.html', {
        'hoje': hoje,
        'total_clientes': total_clientes,
        'projetos_ativos': projetos_ativos,
        'tarefas_agendadas': tarefas_agendadas,
        'total_alertas_proximos': total_alertas_proximos,
        'alertas_renovacao': alertas_renovacao,
        'painel_tecnicos': painel_tecnicos,
        'tecnico_logado': tecnico_logado,
        'minhas_tarefas': minhas_tarefas,
        'projetos_recentes': projetos_recentes,
    })


@login_required
def cliente_lista(request):
    """Página principal de Clientes: lista todos com busca e botão de Novo Cliente"""
    termo_busca = request.GET.get('busca', '').strip()
    clientes = Cliente.objects.all().order_by('razao_social')

    if termo_busca:
        clientes = clientes.filter(
            Q(nome_fantasia__icontains=termo_busca) |
            Q(razao_social__icontains=termo_busca) |
            Q(cnpj__icontains=termo_busca) |
            Q(cidade__icontains=termo_busca)
        )

    return render(request, 'cadastros/cliente_lista.html', {
        'clientes': clientes,
        'termo_busca': termo_busca,
    })


@login_required
def cliente_escolher_tipo(request):
    """Janela de seleção com 2 cards: Pessoa Física (CPF) ou Pessoa Jurídica (CNPJ)"""
    return render(request, 'cadastros/cliente_tipo_escolha.html')


@login_required
def cliente_criar_ou_editar(request, pk=None, tipo=None):
    """Criação ou edição do Cliente (PJ ou PF) com suas Filiais e Dados de Energia"""
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None

    if cliente:
        tipo_efetivo = cliente.tipo_pessoa or 'PJ'
    else:
        tipo_efetivo = tipo or 'PJ'

    FormClass = ClientePFForm if tipo_efetivo == 'PF' else ClienteForm
    template_name = 'cadastros/cliente_form_pf.html' if tipo_efetivo == 'PF' else 'cadastros/cliente_form.html'

    if request.method == 'POST':
        form = FormClass(request.POST, instance=cliente)
        filiais_formset = FilialFormSet(request.POST, instance=cliente, prefix='filiais')
        energia_formset = DadosEnergiaFormSet(request.POST, instance=cliente, prefix='energia')

        if form.is_valid() and filiais_formset.is_valid() and energia_formset.is_valid():
            with transaction.atomic():
                cliente_salvo = form.save()
                filiais_formset.instance = cliente_salvo
                filiais_formset.save()
                energia_formset.instance = cliente_salvo
                energia_formset.save()

            nome_exibicao = cliente_salvo.nome_fantasia or cliente_salvo.razao_social
            messages.success(request, f'Cliente "{nome_exibicao}" salvo com sucesso!')
            return redirect('cliente_lista')
        else:
            messages.error(request, 'Erro ao salvar. Verifique se a Razão Social / Nome foi preenchido.')
    else:
        form = FormClass(instance=cliente)
        filiais_formset = FilialFormSet(instance=cliente, prefix='filiais')
        energia_formset = DadosEnergiaFormSet(instance=cliente, prefix='energia')

    return render(request, template_name, {
        'form': form,
        'filiais_formset': filiais_formset,
        'energia_formset': energia_formset,
        'cliente': cliente,
        'tipo_pessoa': tipo_efetivo,
    })


@login_required
def cliente_excluir(request, pk):
    """Exclui o cliente e suas filiais associadas"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nome = cliente.nome_fantasia or cliente.razao_social
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" excluído com sucesso.')
    return redirect('cliente_lista')