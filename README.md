# 🏪 Sistema de Gerenciamento de Vendas

Sistema web completo para gestão de vendas, estoque, orçamentos e clientes desenvolvido em **Django 5.2.8** com interface responsiva e moderna.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Executando](#-executando)
- [Rotas da Aplicação](#-rotas-da-aplicação)
- [Modelos de Dados](#-modelos-de-dados)
- [Serviços](#-serviços)
- [APIs Disponíveis](#-apis-disponíveis)
- [Geração de PDFs](#-geração-de-pdfs)
- [Banco de Dados](#-banco-de-dados)

---

## 📌 Sobre o Projeto

O **Sistema de Gerenciamento de Vendas** é uma aplicação Django completa que permite:

- **Gerenciar lojas** com autenticação por CNPJ e senha
- **Controlar estoque** de produtos físicos e serviços
- **Registrar vendas** com baixa automática no estoque
- **Criar orçamentos** com conversão posterior em vendas
- **Gerenciar clientes** com endereços completos
- **Visualizar dashboard** com estatísticas em tempo real
- **Gerar PDFs** de recibos e orçamentos

---

## ✨ Funcionalidades

### 🔐 Autenticação

| Funcionalidade | Descrição |
|----------------|-----------|
| Cadastro de Loja | Cadastro com CNPJ, nome, telefone, email e endereço |
| Login | Autenticação por CNPJ e senha com criptografia PBKDF2 |
| Logout | Encerra a sessão e limpa todos os dados |
| Sessão Expira | Sessão encerra ao fechar o navegador |

### 📊 Dashboard

| Funcionalidade | Descrição |
|----------------|-----------|
| Receita Bruta | Total das vendas do mês (sem descontos) |
| Receita Líquida | Total das vendas do mês (com descontos) |
| Total de Vendas | Quantidade de vendas no mês |
| Estoque Total | Soma de todas as unidades em estoque |
| Gráfico de Vendas | Visualização dos últimos 30 dias |
| Comparativo | Receita bruta vs líquida dos últimos 30 dias |

### 📦 Estoque

| Funcionalidade | Descrição |
|----------------|-----------|
| Listar Produtos | Exibe todos os produtos com informações de estoque |
| Cadastrar Produto | Cria produto com nome, preço de custo (IOF), preço de venda |
| Editar Produto | Atualiza dados do produto e quantidade |
| Deletar Produto | Remove produto do banco de dados |
| Adicionar Reposição | Aumenta a quantidade em estoque |
| Controle de Estoque | Suporte a produtos físicos (controlados) e serviços (não controlados) |
| Cálculo de Lucro | Exibe lucro unitário (preço venda - preço custo) |

### 💰 Vendas

| Funcionalidade | Descrição |
|----------------|-----------|
| Nova Venda | Registra venda com seleção de cliente e produtos |
| Busca de Clientes | Autocomplete por nome e CPF |
| Busca de Produtos | Lista produtos disponíveis com estoque |
| Carrinho de Compras | Adiciona múltiplos produtos |
| Cálculo Automático | Subtotal, desconto, frete e total |
| Baixa no Estoque | Deduz quantidade automaticamente |
| Produtos/Serviços | Produtos sem estoque (serviços) não afetam controle |
| Geração de PDF | Recibo completo da venda |
| Histórico | Lista todas as vendas com filtros |
| Exclusão | Remove venda do sistema |

### 📄 Orçamentos

| Funcionalidade | Descrição |
|----------------|-----------|
| Novo Orçamento | Cria orçamento sem afetar estoque |
| Status PENDENTE | Orçamento aguardando aprovação |
| Status APROVADO | Orçamento aprovado pelo cliente |
| Status REJEITADO | Orçamento não aprovado |
| Status CONVERTIDO | Orçamento transformado em venda |
| Conversão em Venda | Transforma orçamento em venda mantendo itens |
| Geração de PDF | Orçamento imprimível com validade de 30 dias |
| Listagem | Filtros por nome, data e status |
| Exclusão | Remove orçamentos (exceto os convertidos) |

### 👥 Clientes

| Funcionalidade | Descrição |
|----------------|-----------|
| Listar Clientes | Exibe todos os clientes cadastrados |
| Novo Cliente | Cadastra com nome, CPF, telefone, email, data de nascimento |
| Endereço Completo | Logradouro, número, bairro, CEP, cidade, estado |
| Editar Cliente | Atualiza dados do cliente e endereço |
| Exclusão Protegida | Impede删除ção se houver vendas associadas |

### 💳 Pagamentos

| Funcionalidade | Descrição |
|----------------|-----------|
| Formas de Pagamento | Dinheiro, Cartão, Boleto, Pix, etc. |
| Parcelamento | Registro de número de parcelas |
| Totais | Subtotal, desconto, frete, valor final |

---

## 🛠 Tecnologias

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Django** | 5.2.8 | Framework web |
| **Python** | 3.12+ | Linguagem de programação |
| **MySQL** | 5.7+ | Banco de dados |
| **ReportLab** | 4.4.5 | Geração de PDFs |
| **Pillow** | 12.0.0 | Manipulação de imagens |
| **HTML/CSS/JS** | - | Interface frontend |
| **Bootstrap** | - | Estilos e componentes |

---

## 📁 Estrutura do Projeto

```
Gerenciamento_Vendas/
├── DB/
│   ├── MODELO.mwb           # Modelo do banco (MySQL Workbench)
│   └── MODELO.mwb.bak       # Backup do modelo
├── sistema_vendas/
│   ├── app_controle/
│   │   ├── migrations/      # Migrações do Django
│   │   ├── models/          # Modelos de dados
│   │   │   ├── cliente.py      # Modelo Cliente
│   │   │   ├── produto.py       # Modelo Produto
│   │   │   ├── estoque.py       # Modelo Estoque
│   │   │   ├── venda.py         # Modelo Venda
│   │   │   ├── orcamento.py     # Modelo Orçamento
│   │   │   ├── item_venda.py    # Modelo ItemVenda
│   │   │   ├── item_orcamento.py# Modelo ItemOrcamento
│   │   │   ├── pagamento.py     # Modelo Pagamento
│   │   │   ├── funcionario.py  # Modelo Funcionario
│   │   │   ├── usuario.py       # Modelo Usuario
│   │   │   ├── loja.py          # Modelo Loja
│   │   │   ├── endereco.py      # Modelo Endereco
│   │   │   ├── estoque_venda.py # Modelo EstoqueVenda
│   │   │   ├── cidades.py       # Modelo Cidades
│   │   │   └── uf.py            # Modelo UF
│   │   ├── services/        # Camada de serviços
│   │   │   ├── auth_services.py     # Autenticação
│   │   │   ├── cliente_services.py  # Clientes
│   │   │   ├── estoque_services.py  # Estoque
│   │   │   ├── venda_services.py     # Vendas
│   │   │   └── orcamento_services.py # Orçamentos
│   │   ├── views/           # Controladores
│   │   │   ├── auth_views.py      # Login/Cadastro
│   │   │   ├── cliente_views.py   # Clientes
│   │   │   ├── dashboard_views.py # Dashboard
│   │   │   ├── estoque_views.py   # Estoque
│   │   │   ├── vendas_views.py    # Vendas
│   │   │   ├── novavenda_views.py # Nova venda
│   │   │   └── orcamento_views.py  # Orçamentos
│   │   ├── templates/       # Templates HTML
│   │   │   ├── core/
│   │   │   │   └── base.html      # Template base
│   │   │   ├── auth/
│   │   │   │   ├── login.html      # Login
│   │   │   │   └── cadastro.html  # Cadastro
│   │   │   ├── dashboard.html      # Dashboard
│   │   │   ├── estoque.html        # Estoque
│   │   │   ├── clientes.html       # Clientes
│   │   │   ├── vendas.html         # Lista vendas
│   │   │   ├── nova_venda.html    # Nova venda
│   │   │   ├── orcamentos.html     # Lista orçamentos
│   │   │   └── novo_orcamento.html # Novo orçamento
│   │   ├── static/          # Arquivos estáticos
│   │   │   ├── css/
│   │   │   │   ├── style.css
│   │   │   │   ├── media.css
│   │   │   │   ├── message.css
│   │   │   │   └── modais/
│   │   │   └── js/
│   │   │       ├── main.js
│   │   │       ├── charts.js
│   │   │       ├── loader.js
│   │   │       └── modais/
│   │   ├── forms.py         # Formulários Django
│   │   ├── middleware.py    # Middleware de sessão
│   │   └── apps.py          # Configuração do app
│   ├── sistema_vendas/
│   │   ├── settings.py      # Configurações
│   │   ├── urls.py         # Rotas principais
│   │   ├── asgi.py         # ASGI config
│   │   └── wsgi.py         # WSGI config
│   └── manage.py           # Gerenciador Django
├── requirements.txt         # Dependências
├── TODO.md                 # Tarefas
└── README.md               # Este arquivo
```

---

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/karython/Gerenciamento_Vendas.git
cd Gerenciamento_Vendas
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências necessárias:**
```
asgiref==3.10.0
charset-normalizer==3.4.4
Django==5.2.8
pillow==12.0.0
reportlab==4.4.5
sqlparse==0.5.3
tzdata==2025.2
mysqlclient
```

---

## ⚙️ Configuração

### Banco de Dados

O sistema está configurado para MySQL remoto. Você pode alterar em `sistema_vendas/sistema_vendas/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u275872813_gen_estoque',
        'USER': 'u275872813_admin_estoque',
        'PASSWORD': 'GestaoEstoque25',
        'HOST': 'srv1061.hstgr.io',
        'PORT': '3306',
    }
}
```

### Para Desenvolvimento Local (SQLite)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Aplicar Migrações

```bash
cd sistema_vendas
python manage.py migrate
```

---

## 🚀 Executando

### Iniciar Servidor

```bash
cd sistema_vendas
python manage.py runserver
```

**Acesso:** http://127.0.0.1:8000

### Login Inicial

Acesse `/cadastro/` para criar a primeira loja, depois faça login em `/login/`.

---

## 🔗 Rotas da Aplicação

### Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Página inicial (redireciona para login ou dashboard) |
| GET/POST | `/login/` | Login de lojas |
| GET/POST | `/cadastro/` | Cadastro de nova loja |
| GET | `/logout/` | Encerrar sessão |

### Dashboard

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/dashboard/` | Dashboard com estatísticas |

### Estoque

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/estoque/` | Lista produtos em estoque |
| POST | `/estoque/cadastrar/` | Cadastra novo produto |
| GET | `/estoque/buscar/<id>/` | Busca produto para edição |
| POST | `/estoque/editar/<id>/` | Edita produto |
| POST | `/estoque/deletar/<id>/` | Remove produto |
| POST | `/estoque/reposicao/<id>/` | Adiciona reposição |

### Vendas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/vendas/` | Lista todas as vendas |
| GET | `/vendas/nova/` | Página de nova venda |
| POST | `/vendas/criar/` | Cria nova venda |
| GET | `/vendas/pdf/<id>/` | Gera PDF do recibo |
| POST | `/vendas/deletar/<id>/` | Remove venda |
| POST | `/vendas/deletar-multiplas/` | Remove múltiplas vendas |

### Orçamentos

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/orcamentos/` | Lista orçamentos |
| GET | `/orcamentos/novo/` | Página de novo orçamento |
| POST | `/orcamentos/criar/` | Cria orçamento |
| POST | `/orcamentos/status/<id>/` | Atualiza status |
| POST | `/orcamentos/converter/<id>/` | Converte em venda |
| GET | `/orcamentos/pdf/<id>/` | Gera PDF do orçamento |
| POST | `/orcamentos/deletar/<id>/` | Remove orçamento |

### Clientes

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/clientes/` | Lista clientes |
| POST | `/clientes/criar/` | Cadastra cliente |
| GET/POST | `/clientes/editar/<id>/` | Edita cliente |
| POST | `/clientes/deletar/<id>/` | Remove cliente |

### APIs

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/clientes/` | Lista clientes (autocomplete) |
| GET | `/api/produtos/` | Lista produtos (autocomplete) |
| GET | `/api/formas-pagamento/` | Lista formas de pagamento |
| GET | `/api/orcamento/clientes/` | Clientes para orçamentos |
| GET | `/api/orcamento/produtos/` | Produtos para orçamentos |
| GET | `/api/orcamento/formas-pagamento/` | Formas de pagamento |

---

## 🗃 Modelos de Dados

### Loja
```
idLOJA (PK) | NOME_LOJA | CNPJ (único) | SENHA | TELEFONE | EMAIL | ENDERECO | DATA_CADASTRO | ATIVO
```

### Cliente
```
idCLIENTE (PK) | NOME_CLIENTE | DATA_NASCIMENTO | CPF | TELEFONE | EMAIL | FUNCIONARIO_idFUNCIONARIO (FK)
```

### Endereco
```
idENDERECO (PK) | LOGRADOURO | NUMERO | BAIRRO | CEP | REFERENCIA | CIDADES_idCIDADES (FK) | CLIENTE_idCLIENTE (FK)
```

### Produto
```
idPRODUTO (PK) | DESCRICAO | VLR_UNIT | IOF | DT_MOVIMENTADA | TRACK_STOCK (bool)
```

### Estoque
```
idESTOQUE (PK) | PRODUTO_idPRODUTO (FK) | QTD_DISPONIVEL
```

### Pagamento
```
idPAGAMENTO (PK) | TP_PAGAMENTO
```

### Venda
```
idVENDA (PK) | CLIENTE_idCLIENTE (FK) | PAGAMENTO_idPAGAMENTO (FK) | QTD_VENDIDA | DT_VENDA | 
VLR_SUBTOTAL | DESCONTO | VLR_FRETE | OBSERVACAO | PARCELAMENTO | VLR_TOTAL | ORCAMENTO_ORIGEM (FK)
```

### Orcamento
```
idORCAMENTO (PK) | CLIENTE_idCLIENTE (FK) | PAGAMENTO_idPAGAMENTO (FK) | QTD_ITENS | DT_ORCAMENTO |
VLR_SUBTOTAL | DESCONTO | VLR_FRETE | OBSERVACAO | PARCELAMENTO | VLR_TOTAL | STATUS
```

### ItemVenda
```
idITEM_VENDA (PK) | VENDA_idVENDA (FK) | PRODUTO_idPRODUTO (FK) | QUANTIDADE | VLR_UNITARIO | VLR_TOTAL
```

### ItemOrcamento
```
idITEM_ORCAMENTO (PK) | ORCAMENTO_idORCAMENTO (FK) | PRODUTO_idPRODUTO (FK) | QUANTIDADE | VLR_UNITARIO | VLR_TOTAL
```

### Funcionario
```
idFUNCIONARIO (PK) | NOME_FUNCIONARIO | CPF_CNPJ | TELEFONE_FUNCIONARIO | ATIVO
```

---

## 🔧 Serviços

### AuthService
- `validar_cnpj(cnpj)` → Valida formato do CNPJ
- `formatar_cnpj(cnpj)` → Formata CNPJ para exibição
- `cadastrar_loja(dados)` → Cadastra nova loja
- `autenticar_loja(cnpj, senha)` → Autentica loja
- `loja_logada(request)` → Retorna loja da sessão
- `fazer_login(request, loja)` → Salva sessão
- `fazer_logout(request)` → Limpa sessão
- `requer_login` → Decorator para views protegidas

### ClienteService
- `listar_clientes()` → Lista todos
- `criar_cliente(dados)` → Cria com endereço
- `atualizar_cliente(id, dados)` → Atualiza dados
- `verificar_vendas_cliente(id)` → Verifica vendas
- `deletar_cliente(id)` → Remove (se sem vendas)

### EstoqueService
- `listar_estoque()` → Lista com cálculos de lucro
- `cadastrar_produto_estoque(dados)` → Cria produto e estoque
- `adicionar_reposicao(id, quantidade)` → Adiciona estoque
- `atualizar_produto(id, dados)` → Atualiza dados
- `buscar_produto(id)` → Busca com flag is_service
- `deletar_produto(id)` → Remove produto

### VendaService
- `listar_clientes()` → Para autocomplete
- `listar_produtos()` → Com estoque disponível
- `listar_formas_pagamento()` → Retorna formas
- `criar_venda(dados)` → Cria e atualiza estoque
- `listar_vendas(filtros)` → Lista com filtros
- `buscar_venda(id)` → Detalhes da venda
- `deletar_venda(id)` → Remove venda

### OrcamentoService
- `criar_orcamento(dados)` → Cria sem baixa estoque
- `listar_orcamentos(filtros)` → Lista com filtros
- `obter_orcamento(id)` → Detalhes completos
- `atualizar_status(id, status)` → Atualiza status
- `deletar_orcamento(id)` → Remove (exceto convertidos)
- `converter_para_venda(id)` → Prepara dados para venda
- `obter_estatisticas()` → Totais por status

---

## 🌐 APIs Disponíveis

### GET /api/clientes/
Retorna lista de clientes para autocomplete:
```json
{
  "success": true,
  "clientes": [
    {"id": 1, "nome": "João Silva", "cpf": "123.456.789-00", "label": "João Silva - CPF: 123.456.789-00"}
  ]
}
```

### GET /api/produtos/
Retorna lista de produtos com estoque:
```json
{
  "success": true,
  "produtos": [
    {
      "id": 1,
      "descricao": "Produto A",
      "valor": 99.90,
      "estoque": 50,
      "is_service": false,
      "label": "#1 - Produto A - R$ 99.90 (Estoque: 50)"
    }
  ]
}
```

### GET /api/formas-pagamento/
Retorna formas de pagamento:
```json
{
  "success": true,
  "formas_pagamento": [
    {"id": 1, "tipo": "Dinheiro"},
    {"id": 2, "tipo": "Cartão de Crédito"}
  ]
}
```

---

## 📄 Geração de PDFs

### Recibo de Venda

**Rota:** `GET /vendas/pdf/<venda_id>/`

Gera PDF com:
- Logo da loja
- Dados da loja (nome, telefone, CNPJ, email)
- Dados do cliente (nome, CPF, telefone, endereço)
- Tabela de produtos (quantidade, descrição, valor unitário, total)
- Forma de pagamento e parcelamento
- Observações
- Totais (subtotal, desconto, frete, total)
- Assinaturas

### Orçamento

**Rota:** `GET /orcamentos/pdf/<orcamento_id>/`

Gera PDF com:
- Mesmas informações do recibo
- Status do orçamento
- Validade de 30 dias
- Mensagem de confirmação

---

## 🗄 Banco de Dados

### Modelo Conceitual

![Modelo ER](DB/MODELO.mwb)

### Tabelas Principais
- `LOJA` - Cadastro de lojas
- `CLIENTE` - Clientes
- `ENDERECO` - Endereços dos clientes
- `PRODUTO` - Produtos/Serviços
- `ESTOQUE` - Quantidades disponíveis
- `PAGAMENTO` - Formas de pagamento
- `VENDA` - Registros de vendas
- `ITEM_VENDA` - Itens das vendas
- `ORCAMENTO` - Orçamentos
- `ITEM_ORCAMENTO` - Itens dos orçamentos
- `FUNCIONARIO` - Funcionários
- `USUARIO` - Usuários do sistema

### Relações
- 1:N entre Cliente e Endereço
- 1:N entre Produto e Estoque
- 1:N entre Cliente e Venda
- 1:N entre Cliente e Orçamento
- 1:N entre Venda e ItemVenda
- 1:N entre Orçamento e ItemOrcamento
- N:N entre Estoque e Venda (EstoqueVenda)

---

## 🔒 Segurança

### Implementado
- ✅ Criptografia de senhas (PBKDF2)
- ✅ Sessões seguras
- ✅ Middleware de expiração de sessão
- ✅ Validação de CNPJ
- ✅ Validação de campos obrigatórios

### Para Produção
```python
# settings.py
DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ALLOWED_HOSTS = ['seudominio.com']
```

---

## 📝 Uso do Sistema

### 1. Cadastrar Loja
```
Acesse /cadastro/
Preencha: nome, CNPJ, senha, telefone, email, endereço
Clique em "Cadastrar"
```

### 2. Fazer Login
```
Acesse /login/
Informe CNPJ e senha
Clique em "Entrar"
```

### 3. Cadastrar Produto
```
Acesse /estoque/
Clique em "Cadastrar Novo Produto"
Preencha: nome, preço custo, preço venda, quantidade
Marque "É serviço?" para produtos sem estoque
```

### 4. Cadastrar Cliente
```
Acesse /clientes/
Clique em "Novo Cliente"
Preencha dados pessoais e endereço
```

### 5. Criar Venda
```
Acesse /vendas/nova/
Busque e adicione clientes
Busque e adicione produtos
Ajuste desconto e frete se necessário
Selecione forma de pagamento
Clique em "Finalizar Venda"
```

### 6. Criar Orçamento
```
Acesse /orcamentos/novo/
Processo similar à venda
Não afeta estoque
Após aprovação, converta em venda
```

---

## 📈 Fluxo de Venda

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cliente   │────▶│  Orçamento  │────▶│    Venda    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           │ Status            │ Baixa no
                           │ APROVADO          │ Estoque
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ Converter   │     │   Recibo   │
                    │ em Venda    │     │    PDF     │
                    └─────────────┘     └─────────────┘
```

---

## 🐛 Solução de Problemas

### Erro de Conexão MySQL
```
Verifique se o servidor MySQL está online
Confirme dados de acesso em settings.py
```

### CSS/JS não carrega
```bash
python manage.py collectstatic
```

### Migrações pendentes
```bash
python manage.py makemigrations
python manage.py migrate
```

### Porta em uso
```bash
python manage.py runserver 8001
```

---

## 📚 Licença

Este projeto é fornecido como está. Sinta-se livre para modificar e usar conforme necessário.

---

## 👤 Autor

**Karython**  
GitHub: [@karython](https://github.com/karython)

---

**Desenvolvido com ❤️ usando Django 5.2.8**

