# ⚡ Sistema de Gestão de Projetos Elétricos e Ordens de Serviço

Sistema web desenvolvido em **Django** com banco de dados **MariaDB / MySQL** para controle operacional de escritórios e empresas de engenharia elétrica, manutenção preventiva, inspeções termográficas, subestações e emissão de laudos técnicos.

---

## 📋 Principais Funcionalidades

### 1. Painel Operacional (Dashboard)
- **Indicadores Rápidos**: total de projetos em aberto, central de laudos ativos/a vencer e total de clientes cadastrados.
- **Minhas Tarefas Designadas**: quando o usuário logado está vinculado a um perfil de técnico, suas tarefas pendentes aparecem em destaque no topo do painel.
- **Visão Geral de Projetos**: tabela em largura total com acesso rápido à edição de cada Ordem de Serviço (OS).
- **Tarefas por Técnico**: distribuição da carga de trabalho ativa por profissional da equipe.

### 2. Gestão de Clientes, Filiais e Dados de Energia (`cadastros`)
- **Seleção de Tipo de Cliente (2 Cards)**: ao criar um novo cliente, o sistema apresenta 2 cards para escolha entre **Pessoa Física (CPF)** (com identificação simplificada de Nome e CPF) e **Pessoa Jurídica (CNPJ)**.
- **Validação Flexível**: apenas o campo **Razão Social / Nome** é obrigatório; todos os demais campos cadastrais, de endereço, contatos, filiais e energia são opcionais.
- **Múltiplas Filiais Dinâmicas (`+`)**: adição ilimitada de unidades/filiais vinculadas ao cliente na mesma tela.
- **Integração com API ViaCEP**: preenchimento automático de Logradouro, Bairro, Cidade e UF ao digitar o CEP tanto na Matriz quanto em qualquer Filial.
- **Dados de Entrada de Energia / Subestação (`+`)**: registro de Unidades Consumidoras (UC), Concessionária, Tensão de Fornecimento, Demanda Contratada (kW), Potência do Transformador (kVA) e Tipo de Subestação.

### 3. Gestão de Projetos e Ordens de Serviço (`projetos`)
- **Identificação e Escopo**: título do escopo e previsão de entrega final em destaque na primeira linha, número da OS, data de abertura, status e seleção dinâmica de **Cliente** (com **botão de Lupa** para busca instantânea por nome) e **Filial de Atendimento** via AJAX.
- **Checklist Automático por Tipo de Serviço**: ao selecionar o Tipo de Projeto (ex: *Projeto Elétrico*, *Laudo SPDA*, *Inspeção Termográfica*), a tabela de tarefas é preenchida automaticamente com as etapas padrão daquele tipo.
- **Delegação e Conclusão de Tarefas**:
  - Escolha do **Técnico Responsável** e **Data Programada** para cada etapa, preservando a ordem exata da lista, além de inclusão de tarefas avulsas (`+`) ou exclusão de etapas não aplicáveis.
  - **Flag de Conclusão**: cada tarefa possui uma marcação de concluída na primeira coluna; ao marcar todas as tarefas da OS como concluídas, o sistema pergunta automaticamente se deseja alterar o status do projeto para **Concluído**.
- **Diário do Projeto com Anexos (até 50 MB)**:
  - Histórico cronológico ao final da página do projeto com registro automático de data e hora (`timestamp`) de criação.
  - Suporte para anexar **qualquer tipo de arquivo** (`.pdf`, `.dwg`, `.xlsx`, imagens, `.zip`, etc.) de até **50 MB** por arquivo, com download direto no histórico do diário.
- **Cálculo Automático de Renovação Periódica**: para tipos de projeto configurados com validade (laudos/inspeções), o bloco de renovação é exibido automaticamente e calcula a data futura exata com base nos meses de validade.

### 4. Central de Laudos Ativos (`/projetos/laudos/`)
- Tela dedicada ao monitoramento de validade de laudos e inspeções periódicas.
- Filtros combinados por **Intervalo de Datas de Vencimento (De / Até)**, **Tipo de Projeto** e **Busca por Cliente ou Nº da OS**.
- Indicadores visuais de prazo (*Vencido*, *Vence em até 30 dias*, *Vence em até 60 dias*, *Ativo*).

### 5. Agenda Técnica (`/projetos/agenda/`)
- Cronograma das tarefas e visitas técnicas programadas em campo.
- Filtros rápidos por **Profissional Técnico** e por **Período** (*Todas*, *Hoje*, *Esta Semana*, *Este Mês*).

### 6. Central de Gerenciamento Modular (`/projetos/gerenciamento/`)
Painel administrativo próprio no menu lateral (dispensando o uso do Django Admin na operação diária), organizado em 5 módulos:
1. **Equipe Técnica**: CRUD de técnicos integrado diretamente à criação e atualização do **Usuário de Login e Senha** no sistema Django.
2. **Tipos de Projetos**: cadastro de categorias de serviço e ativação da flag *"Exige Lembrete de Renovação?"*.
3. **Tarefas Padrão por Tipo**: seleção do Tipo de Projeto em menu dropdown e tabela dinâmica na mesma página com botão **`+ Adicionar Tarefa`** para gerenciar o checklist exclusivo de cada tipo.
4. **Usuários do Sistema**: controle de contas de acesso (logins, nomes de exibição, status ativo e redefinição de senhas).
5. **Estados do Projeto (Status)**: personalização dos status operacionais das OS, cores das etiquetas visuais, ordem de exibição e definição do status de conclusão.

---

## 🛠️ Tecnologias Utilizadas

- **Back-end**: Python 3 + Django
- **Banco de Dados**: MariaDB / MySQL (`mysqlclient`)
- **Front-end**: HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons e JavaScript (ES6 / Fetch API)
- **Integrações**: API pública [ViaCEP](https://viacep.com.br/) para consulta de endereços

---

## 📂 Estrutura do Projeto

```text
gestao_eletrica/
├── cadastros/                  # App de Clientes (Matriz), Filiais e Dados de Energia
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py                # ModelForms e InlineFormSets (Filiais e Energia)
│   ├── models.py               # Cliente, Filial, DadosEnergia
│   ├── urls.py
│   └── views.py                # Dashboard principal e CRUD de Clientes
├── projetos/                   # App de Projetos/OS, Laudos, Agenda e Gerenciamento
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py                # Formulários de Projeto, Técnico+Login, Tipo, Status e Tarefas
│   ├── models.py               # StatusProjeto, TipoProjeto, Tecnico, TarefaPadrao, Projeto, Tarefa
│   ├── urls.py
│   └── views.py                # Views operacionais, Central de Gerenciamento e endpoints JSON
├── core/                       # Configurações centrais do projeto Django
│   ├── settings.py             # Configuração MariaDB, Templates, Autenticação e Idioma (pt-br)
│   ├── urls.py                 # Rotas principais e Autenticação (/login/ e /logout/)
│   └── wsgi.py
├── templates/                  # Templates HTML (Bootstrap 5)
│   ├── base.html               # Layout base com Menu Lateral (Sidebar) e identificação do usuário
│   ├── login.html              # Tela de autenticação no sistema
│   ├── dashboard.html          # Painel operacional principal
│   ├── cadastros/              # Telas de listagem e formulário de clientes
│   └── projetos/               # Telas de OS, Laudos, Agenda e módulos de Gerenciamento
├── manage.py
└── README.md
```

---

## 🚀 Como Executar o Projeto (Windows)

### 1. Configurar o Banco de Dados no MariaDB / MySQL
Crie o banco de dados com suporte completo a caracteres UTF-8:
```sql
CREATE DATABASE gestao_eletrica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Verifique as credenciais de conexão (`USER`, `PASSWORD`, `HOST`, `PORT`) no arquivo `core/settings.py` dentro do bloco `DATABASES`.

### 2. Ativar o Ambiente Virtual e Instalar Dependências
No PowerShell, dentro da pasta raiz do projeto:
```powershell
.\venv4\Scripts\Activate.ps1
pip install django mysqlclient pillow
```

### 3. Executar as Migrações do Banco de Dados
```powershell
python manage.py migrate
```

### 4. Criar um Superusuário Inicial (caso necessário)
```powershell
python manage.py createsuperuser
```

### 5. Iniciar o Servidor
```powershell
python manage.py runserver
```

Acesse no navegador:
- **Sistema Operacional**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Login**: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
