# Sistema de Gerenciamento de Vendas

Um sistema web completo para gerenciamento de vendas, estoque e clientes desenvolvido em Django com interface responsiva e moderna.

## 📋 Sobre o Projeto

O **Sistema de Gerenciamento de Vendas** é uma aplicação Django que facilita o controle de:
- 📊 **Dashboard**: Visualização de dados em tempo real
- 📦 **Estoque**: Cadastro e reposição de produtos
- 💰 **Vendas**: Registro e acompanhamento de vendas
- 👥 **Clientes**: Gerenciamento de informações de clientes

## 🚀 Requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **pip** (geralmente vem com Python)
- **Git** (opcional, para clonar o repositório)

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/karython/Gerenciamento_Vendas.git
cd Gerenciamento_Vendas
```

### 2. Criar Ambiente Virtual

```bash
# No Windows
python -m venv .venv
.venv\Scripts\activate

# No macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Caso não exista `requirements.txt`, instale manualmente:**

```bash
pip install Django==5.2.8
```

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional para desenvolvimento):

```bash
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Aplicar Migrações do Banco de Dados

```bash
cd sistema_vendas
python manage.py migrate
```

### 3. Criar Superusuário (Admin)

```bash
python manage.py createsuperuser
```

Siga as instruções para criar um usuário administrador.

## 🎯 Executando o Projeto

### Iniciar Servidor de Desenvolvimento

```bash
cd sistema_vendas
python manage.py runserver
```

O servidor iniciará em: **http://127.0.0.1:8000**

### Acessar o Admin Django

Acesse em seu navegador: **http://127.0.0.1:8000/admin**

Use as credenciais do superusuário criado anteriormente.

## 📱 Funcionalidades Principais

### 🏠 Dashboard
- Visualização de estatísticas gerais
- Cards com informações resumidas
- Gráficos (integração com Chart.js)

### 📦 Estoque
- **Cadastrar Novo Produto**
  - Nome, descrição, valor unitário, IOF (opcional)
  - Modal interativa com validação de campos
  
- **Lançar Reposição**
  - Selecionar produto de uma lista filtrada
  - Informações de custo preenchidas automaticamente
  - Campos para preço de venda e quantidade
  - Validação de dados antes de envio

### 💰 Vendas
- Registrar novas vendas
- Adicionar produtos ao carrinho
- Cálculo automático de subtotal e total
- Aplicação de descontos

### 👥 Clientes
- Gerenciamento de informações de clientes
- Accordion para visualização de detalhes
- Integração com vendas

## 🛠️ Estrutura do Projeto

```
Gerenciamento_Vendas/
├── sistema_vendas/                 # Aplicação Django principal
│   ├── app_controle/              # App de controle (views, modelos)
│   │   ├── templates/             # Templates HTML
│   │   │   ├── core/
│   │   │   │   └── base.html      # Template base (navbar, sidebar)
│   │   │   ├── estoque.html       # Página de estoque
│   │   │   ├── vendas.html        # Página de vendas
│   │   │   ├── clientes.html      # Página de clientes
│   │   │   ├── dashboard.html     # Dashboard
│   │   │   └── nova_venda.html    # Nova venda
│   │   ├── static/                # Arquivos estáticos
│   │   │   ├── css/              # Estilos CSS
│   │   │   │   ├── style.css     # Estilos principais
│   │   │   │   ├── media.css     # Media queries responsivas
│   │   │   │   └── modais/       # Estilos das modais
│   │   │   │       └── estoque.css
│   │   │   └── js/               # Scripts JavaScript
│   │   │       ├── main.js       # Script principal
│   │   │       └── modais/       # Scripts das modais
│   │   │           └── estoque.js
│   │   ├── models.py             # Modelos do banco (a definir)
│   │   ├── views.py              # Views/Controladores
│   │   ├── admin.py              # Configuração do admin
│   │   └── urls.py               # Rotas da aplicação
│   ├── sistema_vendas/
│   │   ├── settings.py           # Configurações Django
│   │   ├── urls.py               # URLs principais
│   │   ├── wsgi.py               # WSGI para produção
│   │   └── asgi.py               # ASGI para async
│   ├── manage.py                 # Gerenciador Django
│   ├── db.sqlite3               # Banco de dados SQLite
│   └── requirements.txt          # Dependências Python
├── DB/                           # Arquivos de banco de dados
│   ├── MODELO.mwb               # Modelo MySQL Workbench
│   └── MODELO.mwb.bak           # Backup do modelo
├── .gitignore
├── .venv/                        # Ambiente virtual
└── README.md                     # Este arquivo
```

## 🎨 Componentes de Interface

### Modais
O projeto possui modais interativas para:

#### 1. **Cadastrar Novo Produto** (Modal: `novoProdutoModal`)
```
- Nome do Produto (obrigatório)
- Descrição
- Valor Unitário (obrigatório)
- IOF (opcional, %)
- Botões: Cancelar, Salvar
```

#### 2. **Lançar Reposição** (Modal: `reposicaoModal`)
```
- Seleção de Produto (com busca/filtro)
- Exibição automática de:
  - Código do produto
  - Preço de custo
- Campos de entrada:
  - Preço de Venda (obrigatório)
  - Quantidade (obrigatório)
- Botões: Cancelar, Confirmar Reposição
```

### Design
- **Responsivo**: Funciona em desktop, tablet e mobile
- **Tema**: Paleta azul/cinza profissional
- **CSS Framework**: Estilos customizados com variáveis CSS

## 📝 Exemplos de Uso

### 1. Acessar o Dashboard
```
1. Iniciar servidor: python manage.py runserver
2. Abrir: http://127.0.0.1:8000/
3. Visualizar dados em tempo real
```

### 2. Cadastrar um Novo Produto
```
1. Acessar: http://127.0.0.1:8000/estoque
2. Clicar no botão "Cadastrar Novo Produto"
3. Preencher o formulário na modal
4. Clicar em "Salvar Produto"
```

### 3. Lançar Reposição de Estoque
```
1. Acessar: http://127.0.0.1:8000/estoque
2. Clicar no botão "Lançar Reposição"
3. Buscar o produto na lista/select
4. Selecionar o produto (custo será preenchido automaticamente)
5. Informar preço de venda e quantidade
6. Clicar em "Confirmar Reposição"
```

### 4. Registrar Nova Venda
```
1. Acessar: http://127.0.0.1:8000/nova-venda
2. Buscar e adicionar produtos ao carrinho
3. Visualizar subtotal e total
4. Aplicar desconto (se necessário)
5. Confirmar venda
```

## 🔗 Rotas Disponíveis

| Rota | Descrição | Status |
|------|-----------|--------|
| `/` | Home/Dashboard | ✅ |
| `/estoque` | Gerenciamento de Estoque | ✅ |
| `/vendas` | Histórico de Vendas | ✅ |
| `/nova-venda` | Registrar Nova Venda | ✅ |
| `/clientes` | Gerenciamento de Clientes | ✅ |
| `/admin` | Painel Administrativo | ✅ |

## 🔒 Segurança

### Em Desenvolvimento
- ⚠️ `DEBUG = True` (mudar para `False` em produção)
- ⚠️ `SECRET_KEY` exposta (usar variáveis de ambiente)
- ⚠️ `ALLOWED_HOSTS = []` (configurar para produção)

### Passos para Produção
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
```

## 📊 Banco de Dados

### SQLite (Desenvolvimento)
- Arquivo: `sistema_vendas/db.sqlite3`
- Criado automaticamente na primeira execução

### Modelo Disponível
- Arquivo: `DB/MODELO.mwb` (MySQL Workbench)
- Para produção, considere migrar para PostgreSQL ou MySQL

## 🐛 Troubleshooting

### Erro: Módulo não encontrado
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: Porta 8000 já em uso
```bash
# Usar porta diferente
python manage.py runserver 8001
```

### Erro: Banco de dados não sincronizado
```bash
# Aplicar todas as migrações
python manage.py migrate
```

### CSS/JS não carregando
```bash
# Coletar arquivos estáticos
python manage.py collectstatic
```

## 📚 Recursos Úteis

- [Documentação Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Documentation](https://docs.python.org/)

## 📝 Licença

Este projeto é fornecido como está. Sinta-se livre para modificar e usar conforme necessário.

## 👤 Autor

**Karython**  
GitHub: [@karython](https://github.com/karython)

## 🤝 Contribuições

Contribuições são bem-vindas! Para reportar bugs ou sugerir melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório ou entre em contato.

---

**Desenvolvido com ❤️ usando Django**
