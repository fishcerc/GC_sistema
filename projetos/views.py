import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Count
from .models import Projeto, Tecnico, Tarefa, TarefaPadrao, TipoProjeto, StatusProjeto
from .forms import ProjetoForm, TecnicoForm, TipoProjetoForm, TarefaPadraoForm, UsuarioSistemaForm, StatusProjetoForm
from cadastros.models import Filial


# ==========================================
# GESTÃO OPERACIONAL DE PROJETOS E OS
# ==========================================

@login_required
def projeto_lista(request):
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

    estados_ativos = list(StatusProjeto.objects.filter(ativo=True).order_by('ordem', 'nome'))
    if estados_ativos:
        status_choices = [(s.nome, s.nome) for s in estados_ativos]
    else:
        status_choices = Projeto.STATUS_CHOICES

    return render(request, 'projetos/projeto_lista.html', {
        'projetos': projetos,
        'termo_busca': termo_busca,
        'status_filtro': status_filtro,
        'status_choices': status_choices,
    })


@login_required
def projeto_criar_ou_editar(request, pk=None):
    projeto = get_object_or_404(Projeto, pk=pk) if pk else None
    tecnicos = Tecnico.objects.filter(ativo=True).order_by('nome')
    tipos_lembrete_map = {t.id: t.requer_lembrete for t in TipoProjeto.objects.all()}

    status_concluido_obj = StatusProjeto.objects.filter(eh_concluido=True, ativo=True).first()
    status_concluido_nome = status_concluido_obj.nome if status_concluido_obj else 'Concluído'

    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        nomes_tarefas = request.POST.getlist('tarefa_nome[]')
        tecnicos_ids = request.POST.getlist('tarefa_tecnico[]')
        datas_agendadas = request.POST.getlist('tarefa_data[]')
        concluidas = request.POST.getlist('tarefa_concluida[]')

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
                    concluida_val = (concluidas[i] == '1') if i < len(concluidas) else False

                    Tarefa.objects.create(
                        projeto=proj_salvo,
                        nome=nome,
                        tecnico_responsavel=tecnico_obj,
                        data_agendada=data_val,
                        concluida=concluida_val
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
                'data': t.data_agendada.strftime('%Y-%m-%d') if t.data_agendada else '',
                'concluida': t.concluida,
            }
            for t in projeto.tarefas.all()
        ]

    return render(request, 'projetos/projeto_form.html', {
        'form': form,
        'projeto': projeto,
        'tecnicos': tecnicos,
        'tarefas_iniciais': tarefas_iniciais,
        'tipos_lembrete_json': json.dumps(tipos_lembrete_map),
        'status_concluido_nome': status_concluido_nome,
    })


@login_required
def projeto_excluir(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)
    if request.method == 'POST':
        num = projeto.numero_os
        projeto.delete()
        messages.success(request, f'Projeto OS {num} excluído.')
    return redirect('projeto_lista')


# ==========================================
# GESTÃO DE LAUDOS ATIVOS E VENCIMENTOS
# ==========================================

@login_required
def laudos_lista(request):
    """Listagem dedicada de todos os laudos ativos com filtro por data e tipo de projeto"""
    hoje = date.today()
    termo_busca = request.GET.get('busca', '').strip()
    tipo_id = request.GET.get('tipo', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()

    projetos_qs = Projeto.objects.select_related('cliente', 'filial', 'tipo_projeto').filter(
        Q(requer_renovacao=True) | Q(tipo_projeto__requer_lembrete=True)
    ).exclude(status='cancelado')

    if termo_busca:
        projetos_qs = projetos_qs.filter(
            Q(numero_os__icontains=termo_busca) |
            Q(cliente__nome_fantasia__icontains=termo_busca) |
            Q(cliente__razao_social__icontains=termo_busca) |
            Q(titulo_escopo__icontains=termo_busca)
        )

    if tipo_id and tipo_id.isdigit():
        projetos_qs = projetos_qs.filter(tipo_projeto_id=int(tipo_id))

    if data_inicio:
        projetos_qs = projetos_qs.filter(data_alerta_renovacao__gte=data_inicio)

    if data_fim:
        projetos_qs = projetos_qs.filter(data_alerta_renovacao__lte=data_fim)

    projetos_qs = projetos_qs.order_by('data_alerta_renovacao', '-data_abertura')

    laudos = []
    for proj in projetos_qs:
        dias_restantes = (proj.data_alerta_renovacao - hoje).days if proj.data_alerta_renovacao else None
        laudos.append({
            'projeto': proj,
            'dias_restantes': dias_restantes,
            'vencido': dias_restantes is not None and dias_restantes < 0,
            'urgente': dias_restantes is not None and 0 <= dias_restantes <= 30,
            'proximo': dias_restantes is not None and 30 < dias_restantes <= 60,
        })

    tipos_laudo = TipoProjeto.objects.filter(ativo=True).order_by('nome')

    return render(request, 'projetos/laudos_lista.html', {
        'laudos': laudos,
        'tipos_laudo': tipos_laudo,
        'termo_busca': termo_busca,
        'tipo_filtro': tipo_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hoje': hoje,
    })


# ==========================================
# AGENDA TÉCNICA
# ==========================================

@login_required
def agenda_tecnica(request):
    """Cronograma de tarefas agendadas por técnico e por período"""
    hoje = date.today()
    tecnico_id = request.GET.get('tecnico', '').strip()
    periodo = request.GET.get('periodo', 'todos').strip()

    tarefas = Tarefa.objects.select_related(
        'projeto', 'projeto__cliente', 'projeto__filial', 'projeto__tipo_projeto', 'tecnico_responsavel'
    ).exclude(projeto__status__in=['concluido', 'cancelado'])

    if tecnico_id:
        if tecnico_id == 'sem_tecnico':
            tarefas = tarefas.filter(tecnico_responsavel__isnull=True)
        elif tecnico_id.isdigit():
            tarefas = tarefas.filter(tecnico_responsavel_id=int(tecnico_id))

    if periodo == 'hoje':
        tarefas = tarefas.filter(data_agendada=hoje)
    elif periodo == 'semana':
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        tarefas = tarefas.filter(data_agendada__range=[inicio_semana, fim_semana])
    elif periodo == 'mes':
        tarefas = tarefas.filter(data_agendada__year=hoje.year, data_agendada__month=hoje.month)
    elif periodo == 'atrasadas':
        tarefas = tarefas.filter(data_agendada__lt=hoje)

    tarefas = tarefas.order_by('data_agendada', 'tecnico_responsavel__nome', 'id')
    tecnicos = Tecnico.objects.filter(ativo=True).order_by('nome')

    return render(request, 'projetos/agenda_tecnica.html', {
        'tarefas': tarefas,
        'tecnicos': tecnicos,
        'tecnico_filtro': tecnico_id,
        'periodo_filtro': periodo,
        'hoje': hoje,
    })


# ==========================================
# HUB MODULAR DE GERENCIAMENTO (3 CARDS)
# ==========================================

@login_required
def gerenciamento_hub(request):
    """Página central de gerenciamento modular"""
    total_tecnicos = Tecnico.objects.count()
    total_tipos = TipoProjeto.objects.count()
    total_tarefas = TarefaPadrao.objects.count()
    total_usuarios = User.objects.count()
    total_status = StatusProjeto.objects.count()

    return render(request, 'projetos/gerenciamento_hub.html', {
        'total_tecnicos': total_tecnicos,
        'total_tipos': total_tipos,
        'total_tarefas': total_tarefas,
        'total_usuarios': total_usuarios,
        'total_status': total_status,
    })


# --- MODULO 5: ESTADOS / STATUS DO PROJETO ---
@login_required
def gerenciamento_status(request):
    estados = StatusProjeto.objects.all().order_by('ordem', 'nome')
    form = StatusProjetoForm()

    if request.method == 'POST':
        form = StatusProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estado do projeto cadastrado com sucesso!')
            return redirect('gerenciamento_status')

    return render(request, 'projetos/gerenciamento_status.html', {
        'estados': estados,
        'form': form,
    })


@login_required
def status_projeto_editar(request, pk):
    estado = get_object_or_404(StatusProjeto, pk=pk)
    if request.method == 'POST':
        form = StatusProjetoForm(request.POST, instance=estado)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado "{estado.nome}" atualizado!')
            return redirect('gerenciamento_status')
    else:
        form = StatusProjetoForm(instance=estado)

    return render(request, 'projetos/status_projeto_form.html', {
        'form': form,
        'estado': estado,
    })


@login_required
def status_projeto_excluir(request, pk):
    estado = get_object_or_404(StatusProjeto, pk=pk)
    if request.method == 'POST':
        nome = estado.nome
        estado.delete()
        messages.success(request, f'Estado "{nome}" removido.')
    return redirect('gerenciamento_status')


# --- MODULO 4: USUÁRIOS DO SISTEMA (LOGIN) ---
@login_required
def gerenciamento_usuarios(request):
    usuarios = User.objects.select_related('tecnico').all().order_by('username')
    form = UsuarioSistemaForm()

    if request.method == 'POST':
        form = UsuarioSistemaForm(request.POST)
        if form.is_valid():
            novo_user = form.save()
            messages.success(request, f'Usuário "{novo_user.username}" criado com sucesso!')
            return redirect('gerenciamento_usuarios')

    return render(request, 'projetos/gerenciamento_usuarios.html', {
        'usuarios': usuarios,
        'form': form,
    })


@login_required
def usuario_editar(request, pk):
    usuario_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioSistemaForm(request.POST, instance=usuario_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{usuario_obj.username}" atualizado!')
            return redirect('gerenciamento_usuarios')
    else:
        form = UsuarioSistemaForm(instance=usuario_obj)

    return render(request, 'projetos/usuario_form.html', {
        'form': form,
        'usuario_obj': usuario_obj,
    })


@login_required
def usuario_excluir(request, pk):
    usuario_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if usuario_obj == request.user:
            messages.error(request, 'Você não pode excluir o seu próprio usuário logado.')
        else:
            uname = usuario_obj.username
            usuario_obj.delete()
            messages.success(request, f'Usuário "{uname}" removido.')
    return redirect('gerenciamento_usuarios')


# --- MODULO 1: TECNICOS ---
@login_required
def gerenciamento_tecnicos(request):
    tecnicos = Tecnico.objects.all().order_by('nome')
    form = TecnicoForm()

    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Técnico cadastrado com sucesso!')
            return redirect('gerenciamento_tecnicos')

    return render(request, 'projetos/gerenciamento_tecnicos.html', {
        'tecnicos': tecnicos,
        'form': form
    })


def tecnico_editar(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        form = TecnicoForm(request.POST, instance=tecnico)
        if form.is_valid():
            form.save()
            messages.success(request, f'Técnico "{tecnico.nome}" atualizado!')
            return redirect('gerenciamento_tecnicos')
    else:
        form = TecnicoForm(instance=tecnico)

    return render(request, 'projetos/tecnico_form.html', {'form': form, 'tecnico': tecnico})


def tecnico_excluir(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        nome = tecnico.nome
        tecnico.delete()
        messages.success(request, f'Técnico "{nome}" removido.')
    return redirect('gerenciamento_tecnicos')


# --- MODULO 2: TIPOS DE PROJETOS ---
@login_required
def gerenciamento_tipos(request):
    tipos = TipoProjeto.objects.annotate(qtd_tarefas=Count('tarefas_padrao')).order_by('nome')
    form = TipoProjetoForm()

    if request.method == 'POST':
        form = TipoProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Projeto cadastrado!')
            return redirect('gerenciamento_tipos')

    return render(request, 'projetos/gerenciamento_tipos.html', {
        'tipos': tipos,
        'form': form
    })


def tipo_projeto_editar(request, pk):
    tipo = get_object_or_404(TipoProjeto, pk=pk)
    if request.method == 'POST':
        form = TipoProjetoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo "{tipo.nome}" atualizado!')
            return redirect('gerenciamento_tipos')
    else:
        form = TipoProjetoForm(instance=tipo)

    return render(request, 'projetos/tipo_projeto_form.html', {'form': form, 'tipo': tipo})


def tipo_projeto_excluir(request, pk):
    tipo = get_object_or_404(TipoProjeto, pk=pk)
    if request.method == 'POST':
        nome = tipo.nome
        tipo.delete()
        messages.success(request, f'Tipo de Projeto "{nome}" removido.')
    return redirect('gerenciamento_tipos')


# --- MODULO 3: TAREFAS PADRAO POR TIPO ---
@login_required
def gerenciamento_tarefas_padrao(request):
    tipos = TipoProjeto.objects.all().order_by('nome')
    tipo_id = request.GET.get('tipo') or request.POST.get('tipo_projeto_id')
    tipo_selecionado = TipoProjeto.objects.filter(pk=tipo_id).first() if tipo_id else None

    if request.method == 'POST' and tipo_selecionado:
        ids_enviados = request.POST.getlist('tarefa_id[]')
        ordens = request.POST.getlist('tarefa_ordem[]')
        nomes = request.POST.getlist('tarefa_nome[]')
        ativos = request.POST.getlist('tarefa_ativo[]')

        with transaction.atomic():
            ids_mantidos = []
            for i in range(len(nomes)):
                nome = nomes[i].strip()
                if not nome:
                    continue

                t_id = ids_enviados[i] if i < len(ids_enviados) and ids_enviados[i] else None
                try:
                    ordem_val = int(ordens[i]) if i < len(ordens) and ordens[i] else (i + 1)
                except ValueError:
                    ordem_val = i + 1
                ativo_val = (ativos[i] == '1') if i < len(ativos) else True

                if t_id and t_id.isdigit():
                    tarefa_obj = TarefaPadrao.objects.filter(
                        pk=int(t_id), tipo_projeto=tipo_selecionado
                    ).first()
                    if tarefa_obj:
                        tarefa_obj.nome = nome
                        tarefa_obj.ordem = ordem_val
                        tarefa_obj.ativo = ativo_val
                        tarefa_obj.save()
                        ids_mantidos.append(tarefa_obj.id)
                else:
                    nova = TarefaPadrao.objects.create(
                        tipo_projeto=tipo_selecionado,
                        nome=nome,
                        ordem=ordem_val,
                        ativo=ativo_val
                    )
                    ids_mantidos.append(nova.id)

            # Remove tarefas desse tipo que foram excluídas na tela
            TarefaPadrao.objects.filter(tipo_projeto=tipo_selecionado).exclude(id__in=ids_mantidos).delete()

        messages.success(request, f'Tarefas padrão de "{tipo_selecionado.nome}" salvas com sucesso!')
        return redirect(f"/projetos/gerenciamento/tarefas-padrao/?tipo={tipo_selecionado.id}")

    tarefas = []
    if tipo_selecionado:
        tarefas = TarefaPadrao.objects.filter(tipo_projeto=tipo_selecionado).order_by('ordem', 'id')

    return render(request, 'projetos/gerenciamento_tarefas.html', {
        'tipos': tipos,
        'tipo_selecionado': tipo_selecionado,
        'tarefas': tarefas,
    })


def tarefa_padrao_editar(request, pk):
    tarefa = get_object_or_404(TarefaPadrao, pk=pk)
    if request.method == 'POST':
        form = TarefaPadraoForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa padrão atualizada!')
            return redirect('gerenciamento_tarefas_padrao')
    else:
        form = TarefaPadraoForm(instance=tarefa)

    return render(request, 'projetos/tarefa_padrao_form.html', {'form': form, 'tarefa': tarefa})


def tarefa_padrao_excluir(request, pk):
    tarefa = get_object_or_404(TarefaPadrao, pk=pk)
    if request.method == 'POST':
        tarefa.delete()
        messages.success(request, 'Tarefa padrão removida.')
    return redirect('gerenciamento_tarefas_padrao')


# --- ENDPOINTS AJAX ---
def tarefas_padrao_por_tipo_json(request, tipo_id):
    tarefas = TarefaPadrao.objects.filter(tipo_projeto_id=tipo_id, ativo=True).order_by('ordem', 'nome')
    return JsonResponse([{'id': t.id, 'nome': t.nome} for t in tarefas], safe=False)


def filiais_por_cliente_json(request, cliente_id):
    filiais = Filial.objects.filter(cliente_id=cliente_id).values('id', 'identificacao', 'cidade')
    return JsonResponse(list(filiais), safe=False)