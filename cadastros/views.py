from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm, FilialFormSet, DadosEnergiaFormSet


def dashboard(request):
    """Dashboard temporária"""
    return render(request, 'dashboard.html')


def cliente_lista(request):
    """Página principal de Clientes: lista todos com busca e botão de Novo Cliente"""
    termo_busca = request.GET.get('busca', '').strip()
    clientes = Cliente.objects.all().order_by('nome_fantasia')

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


def cliente_criar_ou_editar(request, pk=None):
    """Criação ou edição do Cliente com suas Filiais e Dados de Energia"""
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        filiais_formset = FilialFormSet(request.POST, instance=cliente, prefix='filiais')
        energia_formset = DadosEnergiaFormSet(request.POST, instance=cliente, prefix='energia')

        if form.is_valid() and filiais_formset.is_valid() and energia_formset.is_valid():
            with transaction.atomic():
                cliente_salvo = form.save()
                filiais_formset.instance = cliente_salvo
                filiais_formset.save()
                energia_formset.instance = cliente_salvo
                energia_formset.save()

            messages.success(request, f'Cliente "{cliente_salvo.nome_fantasia}" salvo com sucesso!')
            return redirect('cliente_lista')
        else:
            messages.error(request, 'Erro ao salvar. Verifique os campos preenchidos.')
    else:
        form = ClienteForm(instance=cliente)
        filiais_formset = FilialFormSet(instance=cliente, prefix='filiais')
        energia_formset = DadosEnergiaFormSet(instance=cliente, prefix='energia')

    return render(request, 'cadastros/cliente_form.html', {
        'form': form,
        'filiais_formset': filiais_formset,
        'energia_formset': energia_formset,
        'cliente': cliente
    })


def cliente_excluir(request, pk):
    """Exclui o cliente e suas filiais associadas"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nome = cliente.nome_fantasia
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" excluído com sucesso.')
    return redirect('cliente_lista')