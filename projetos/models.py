from django.db import models
from cadastros.models import Cliente, Filial
from datetime import date, timedelta


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
    """Cadastro dos profissionais técnicos (gerenciado na tela de Gerenciamento)"""
    nome = models.CharField("Nome Completo", max_length=150)
    area = models.CharField("Área de Atuação", max_length=100, help_text="Ex: Termografia, SPDA, Projetos Elétricos, Subestação")
    telefone = models.CharField("Telefone / WhatsApp", max_length=20, blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Técnico"
        verbose_name_plural = "Técnicos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.area})"


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
    status = models.CharField("Status", max_length=30, choices=STATUS_CHOICES, default='planejamento')
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


class Tarefa(models.Model):
    """Tarefas atribuídas ao projeto específico com técnico e data"""
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    nome = models.CharField("Nome da Tarefa", max_length=200)
    tecnico_responsavel = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, related_name="tarefas")
    data_agendada = models.DateField("Data Programada", null=True, blank=True)

    class Meta:
        verbose_name = "Tarefa do Projeto"
        verbose_name_plural = "Tarefas do Projeto"
        ordering = ['data_agendada', 'id']

    def __str__(self):
        tec = self.tecnico_responsavel.nome if self.tecnico_responsavel else "Sem técnico"
        return f"{self.nome} ({tec})"