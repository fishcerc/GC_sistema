from django.db import models
from django.contrib.auth.models import User
from cadastros.models import Cliente, Filial
from datetime import date, timedelta


class StatusProjeto(models.Model):
    """Estados operacionais do projeto configuráveis no Gerenciamento"""
    COR_CHOICES = [
        ('info', 'Azul Claro (Planejamento)'),
        ('primary', 'Azul Escuro (Em Execução)'),
        ('warning', 'Amarelo (Alerta / Pendência)'),
        ('danger', 'Vermelho (Bloqueado / Cancelado)'),
        ('success', 'Verde (Concluído)'),
        ('secondary', 'Cinza (Padrão)'),
        ('dark', 'Preto'),
    ]

    nome = models.CharField("Nome do Estado / Status", max_length=60, unique=True)
    cor = models.CharField("Cor da Etiqueta", max_length=20, choices=COR_CHOICES, default='primary')
    ordem = models.PositiveIntegerField("Ordem de Exibição", default=1)
    eh_concluido = models.BooleanField(
        "Status de Conclusão?",
        default=False,
        help_text="Marque se este estado representa que o projeto foi concluído"
    )
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Estado do Projeto"
        verbose_name_plural = "Estados do Projeto"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class TipoProjeto(models.Model):
    """Categorias de projetos: Elétrica, Preventivo, Laudo, Inspeção, Solar, etc."""
    nome = models.CharField("Nome do Tipo de Serviço", max_length=100, unique=True)
    ativo = models.BooleanField("Ativo", default=True)
    requer_lembrete = models.BooleanField(
        "Exige Lembrete / Renovação Periódica?", 
        default=False,
        help_text="Marque se este tipo de serviço tiver validade (ex: Laudos, Inspeções, NR-10)"
    )

    class Meta:
        verbose_name = "Tipo de Projeto"
        verbose_name_plural = "Tipos de Projetos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Tecnico(models.Model):
    """Cadastro dos profissionais técnicos"""
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tecnico",
        verbose_name="Usuário do Sistema"
    )
    nome = models.CharField("Nome Completo", max_length=150)
    telefone = models.CharField("Telefone / WhatsApp", max_length=20, blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Técnico"
        verbose_name_plural = "Técnicos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TarefaPadrao(models.Model):
    """Tarefas padrão vinculadas ao Tipo de Projeto cadastradas no Admin"""
    tipo_projeto = models.ForeignKey(
        TipoProjeto, 
        on_delete=models.CASCADE, 
        related_name="tarefas_padrao",
        verbose_name="Tipo de Projeto"
    )
    nome = models.CharField("Nome da Tarefa", max_length=200, help_text="Ex: Levantamento de Campo, Assinaturas, ART")
    ordem = models.PositiveIntegerField("Ordem de Execução", default=1)
    ativo = models.BooleanField("Ativo?", default=True)

    class Meta:
        verbose_name = "Tarefa Padrão"
        verbose_name_plural = "Tarefas Padrão"
        ordering = ['tipo_projeto', 'ordem', 'nome']

    def __str__(self):
        return f"{self.tipo_projeto.nome} -> {self.nome}"


class Projeto(models.Model):
    """Registro principal do Projeto / Ordem de Serviço"""
    STATUS_CHOICES = [
        ('planejamento', 'Em Planejamento'),
        ('em_andamento', 'Em Execução'),
        ('bloqueado', 'Aguardando Cliente / Bloqueado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    numero_os = models.CharField("Número da OS / Pedido", max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="projetos")
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True, related_name="projetos")
    tipo_projeto = models.ForeignKey(TipoProjeto, on_delete=models.PROTECT, related_name="projetos")
    
    titulo_escopo = models.CharField("Título / Resumo do Escopo", max_length=255)
    status = models.CharField("Status", max_length=60, default='Em Planejamento')
    data_abertura = models.DateField("Data de Abertura", default=date.today)
    data_previsao_entrega = models.DateField("Previsão de Entrega", null=True, blank=True)
    
    # Renovação futura (para Laudos/Inspeções)
    requer_renovacao = models.BooleanField("Requer Renovação Futura?", default=False)
    meses_validade = models.PositiveIntegerField("Validade (meses)", default=12, blank=True, null=True)
    data_alerta_renovacao = models.DateField("Data do Alerta de Renovação", null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projeto / OS"
        verbose_name_plural = "Projetos / OS"
        ordering = ['-data_abertura', '-numero_os']

    def save(self, *args, **kwargs):
        if self.requer_renovacao and self.meses_validade and not self.data_alerta_renovacao:
            self.data_alerta_renovacao = self.data_abertura + timedelta(days=self.meses_validade * 30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OS {self.numero_os} - {self.cliente.nome_fantasia}"

    @property
    def cor_status(self):
        st = StatusProjeto.objects.filter(nome=self.status).first()
        if st:
            return st.cor
        mapa = {
            'planejamento': 'info',
            'Em Planejamento': 'info',
            'em_andamento': 'primary',
            'Em Execução': 'primary',
            'bloqueado': 'danger',
            'Aguardando Cliente': 'danger',
            'concluido': 'success',
            'Concluído': 'success',
            'cancelado': 'secondary',
            'Cancelado': 'secondary',
        }
        return mapa.get(self.status, 'secondary')


class Tarefa(models.Model):
    """Tarefas atribuídas ao projeto específico com técnico e data"""
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    nome = models.CharField("Nome da Tarefa", max_length=200)
    tecnico_responsavel = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, related_name="tarefas")
    data_agendada = models.DateField("Data Programada", null=True, blank=True)
    concluida = models.BooleanField("Concluída?", default=False)

    class Meta:
        verbose_name = "Tarefa do Projeto"
        verbose_name_plural = "Tarefas do Projeto"
        ordering = ['data_agendada', 'id']

    def __str__(self):
        tec = self.tecnico_responsavel.nome if self.tecnico_responsavel else "Sem técnico"
        return f"{self.nome} ({tec})"