from django.db import models


class Cliente(models.Model):
    """Cadastro do Cliente (Pessoa Jurídica ou Pessoa Física)"""
    TIPO_PESSOA_CHOICES = [
        ('PJ', 'Pessoa Jurídica (CNPJ)'),
        ('PF', 'Pessoa Física (CPF)'),
    ]

    tipo_pessoa = models.CharField("Tipo de Pessoa", max_length=2, choices=TIPO_PESSOA_CHOICES, default='PJ')
    razao_social = models.CharField("Razão Social / Nome", max_length=200)
    nome_fantasia = models.CharField("Nome Fantasia", max_length=200, blank=True, null=True)
    cnpj = models.CharField("CNPJ / CPF", max_length=18, blank=True, null=True)
    inscricao_estadual = models.CharField("Inscrição Estadual", max_length=30, blank=True, null=True)
    inscricao_municipal = models.CharField("Inscrição Municipal", max_length=30, blank=True, null=True)
    
    # Endereço Principal (Matriz)
    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    logradouro = models.CharField("Logradouro", max_length=200, blank=True, null=True)
    numero = models.CharField("Número", max_length=20, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField("UF", max_length=2, default="SC", blank=True, null=True)
    
    # Contatos
    pessoa_contato = models.CharField("Pessoa de Contato", max_length=100, blank=True, null=True)
    telefone = models.CharField("Telefone Fixo", max_length=20, blank=True, null=True)
    celular = models.CharField("Celular / WhatsApp", max_length=20, blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    
    # Campo JSON para permitir novos atributos sem quebrar tabelas existentes
    dados_adicionais = models.JSONField("Campos Extras", default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["razao_social"]

    def __str__(self):
        nome = self.nome_fantasia or self.razao_social
        if self.cidade and self.estado:
            return f"{nome} ({self.cidade}/{self.estado})"
        elif self.cidade:
            return f"{nome} ({self.cidade})"
        return nome


class Filial(models.Model):
    """Endereços adicionais vinculados à Matriz"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="filiais")
    identificacao = models.CharField("Identificação da Unidade", max_length=100, help_text="Ex: Filial 01, Galpão Logística, Usina")
    cnpj = models.CharField("CNPJ da Filial", max_length=18, blank=True, null=True)
    
    # Endereço da Filial
    cep = models.CharField("CEP", max_length=9, blank=True, null=True)
    logradouro = models.CharField("Logradouro", max_length=200, blank=True, null=True)
    numero = models.CharField("Número", max_length=20, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField("UF", max_length=2, default="SC", blank=True, null=True)

    # Contato local (caso seja diferente da matriz)
    pessoa_contato = models.CharField("Responsável Local", max_length=100, blank=True, null=True)
    celular = models.CharField("Celular Local", max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Endereço Filial"
        verbose_name_plural = "Endereços Filiais"

    def __str__(self):
        nome_cli = self.cliente.nome_fantasia or self.cliente.razao_social
        return f"{nome_cli} - {self.identificacao}"


class DadosEnergia(models.Model):
    """Informações elétricas de concessionária e infraestrutura"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="dados_energia", null=True, blank=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="dados_energia", null=True, blank=True)
    
    unidade_consumidora = models.CharField("Unidade Consumidora (UC)", max_length=50, blank=True, null=True)
    concessionaria = models.CharField("Concessionária", max_length=50, default="CELESC", blank=True, null=True)
    tensao_fornecimento = models.CharField("Tensão de Atendimento", max_length=50, blank=True, null=True, help_text="Ex: 380/220V, 13.8 kV, 23 kV")
    demanda_contratada_kw = models.DecimalField("Demanda Contratada (kW)", max_digits=8, decimal_places=2, null=True, blank=True)
    potencia_trafo_kva = models.DecimalField("Potência do Trafo (kVA)", max_digits=8, decimal_places=2, null=True, blank=True)
    tipo_subestacao = models.CharField("Tipo de Subestação", max_length=100, blank=True, null=True, help_text="Ex: Aérea, Abrigada em Alvenaria, Blindada")
    observacoes_eletricas = models.TextField("Notas Técnicas de Entrada", blank=True, null=True)

    class Meta:
        verbose_name = "Dados de Energia / Entrada"
        verbose_name_plural = "Dados de Energia / Entradas"

    def __str__(self):
        alvo = self.filial.identificacao if self.filial else "Matriz"
        return f"UC: {self.unidade_consumidora or '-'} ({alvo})"