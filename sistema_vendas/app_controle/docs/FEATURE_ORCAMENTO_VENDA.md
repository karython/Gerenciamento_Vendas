# Funcionalidade: Conversão de Orçamento em Venda

## Resumo
Implementação completa do sistema de conversão de orçamentos em vendas com rastreamento de histórico e gerenciamento de status.

## Componentes Implementados

### 1. Model Update
**Arquivo:** `app_controle/models/venda.py`
- Campo: `ORCAMENTO_ORIGEM` (ForeignKey → Orcamento)
- Permite rastrear qual orçamento originou a venda
- Usa `db_column='ORCAMENTO_idORCAMENTO'` para compatibilidade com banco
- `related_name='vendas_convertidas'` para acessar vendas de um orçamento

### 2. Views de Conversão
**Arquivo:** `app_controle/views/orcamento_views.py`

#### `atualizar_status_orcamento(request, orcamento_id)`
- Método: POST
- Endpoints: `/orcamentos/status/<orcamento_id>/`
- Atualiza status do orçamento (Pendente, Aprovado, Rejeitado, Convertido)
- Retorna JSON com sucesso/erro

#### `converter_orcamento_venda(request, orcamento_id)`
- Método: POST
- Endpoint: `/orcamentos/converter/<orcamento_id>/`
- Converte orçamento em venda:
  1. Valida se orçamento já foi convertido
  2. Cria nova Venda com dados do Orcamento
  3. Copia todos os itens (ItemOrcamento → ItemVenda)
  4. Marca orçamento como CONVERTIDO
  5. Mantém referência cruzada (ORCAMENTO_ORIGEM)

### 3. Rotas
**Arquivo:** `app_controle/urls.py`
```python
path('orcamentos/status/<int:orcamento_id>/', orcamento_views.atualizar_status_orcamento, name='atualizar_status_orcamento')
path('orcamentos/converter/<int:orcamento_id>/', orcamento_views.converter_orcamento_venda, name='converter_orcamento_venda')
path('orcamentos/pdf/<int:orcamento_id>/', orcamento_views.gerar_pdf_orcamento, name='gerar_pdf_orcamento')
```

### 4. Frontend - Template Orçamentos
**Arquivo:** `app_controle/templates/orcamentos.html`

#### Nova Coluna na Tabela
- Exibição visual do STATUS com badges coloridas:
  - Pendente: amarelo
  - Aprovado: verde
  - Rejeitado: vermelho
  - Convertido: azul

#### Botão de Conversão
- Visível apenas se STATUS ≠ CONVERTIDO
- Ícone: ⟷ (exchange)
- Cor: verde (#28a745)

#### Modal de Conversão
```html
<div id="modal-converter">
  - Confirmação com dados do orçamento
  - Número do orçamento
  - Cliente
  - Valor Total
  - Botões: Cancelar / Converter
</div>
```

#### Select de Status no Modal
- Permite alterar status diretamente
- Opções: Pendente, Aprovado, Rejeitado, Convertido
- Atualização via AJAX

#### Funções JavaScript
```javascript
abrirConverterModal(id)      // Abre modal de conversão
fecharModalConverter()        // Fecha modal
confirmarConversao()          // Envia POST para converter
atualizarStatus(id, status)  // Atualiza status com confirm
```

### 5. Frontend - Template Vendas
**Arquivo:** `app_controle/templates/vendas.html`

#### Nova Coluna
- "Nº Orçamento" entre "Nº Venda" e "Cliente"
- Exibe "OR-#####" se venda foi convertida de orçamento
- Exibe "-" se venda foi criada diretamente

#### Modal de Detalhes
- Mostra número de venda: `V-#####`
- Mostra número de orçamento: `OR-#####` (se existir)
  - Background: azul claro (#e7f3ff)
  - Cor: azul escuro (#0066cc)
  - Destaque visual para rastreabilidade

#### Dados JSON
```json
{
  "orcamentoOrigem": "OR-00042" // ou null
}
```

### 6. Atualizações em PDFs

#### PDF de Venda
**Arquivo:** `app_controle/views/novavenda_views.py`
- Número agora exibe: `Nº V-00042 | Orçamento: OR-00041`
- Mostra claramente o rastreamento

#### PDF de Orçamento
**Arquivo:** `app_controle/views/orcamento_views.py`
- Adiciona linha de STATUS abaixo do número
- Exemplos:
  - "Status: PENDENTE"
  - "Status: APROVADO"
  - "Status: CONVERTIDO EM VENDA"

### 7. Database Migration
**Arquivo:** `app_controle/migrations/0013_venda_orcamento_origem.py`
- Adiciona coluna `ORCAMENTO_idORCAMENTO` na tabela VENDA
- ForeignKey com `on_delete=SET_NULL`
- Permite vendas sem orçamento de origem

## Fluxo de Uso

### Cenário 1: Converter Orçamento Aprovado
1. Usuário acessa página de Orçamentos
2. Clica no botão "Ver Detalhes" do orçamento
3. No modal, clica em "Converter em Venda"
4. Confirma a conversão
5. Sistema cria venda com todos os dados
6. Orçamento marcado como CONVERTIDO
7. Venda aparece no histórico com referência ao orçamento

### Cenário 2: Gerenciar Status
1. Usuário visualiza orçamento no modal
2. Usa select de status para mudar:
   - PENDENTE → APROVADO
   - APROVADO → REJEITADO
   - etc.
3. Confirma a mudança
4. Status atualizado imediatamente
5. PDF reflete novo status

### Cenário 3: Rastrear Vendas por Orçamento
1. Usuário acessa Histórico de Vendas
2. Verifica coluna "Nº Orçamento"
3. Identifica quais vendas vieram de orçamentos
4. Clica em detalhes para ver número completo
5. PDF mostra ambos os números para referência

## Validações

### Conversão
- ✅ Verifica se orçamento já foi convertido
- ✅ Valida existência do orçamento
- ✅ Copia itens com segurança
- ✅ Mantém integridade referencial

### Status
- ✅ Apenas valores pré-definidos aceitos
- ✅ Confirmação do usuário antes de mudança
- ✅ Feedback imediato via JSON

## Dados Armazenados

### Em VENDA
```python
ORCAMENTO_ORIGEM_id = 42  # null se venda direta
```

### Em ORCAMENTO
```python
STATUS = 'CONVERTIDO'  # Quando convertida
```

## Exemplo de Requisição HTTP

### Atualizar Status
```bash
POST /orcamentos/status/42/
Content-Type: application/json
X-CSRFToken: ...

{
  "status": "APROVADO"
}
```

### Converter para Venda
```bash
POST /orcamentos/converter/42/
Content-Type: application/json
X-CSRFToken: ...

{}
```

## Resposta Sucesso
```json
{
  "success": true,
  "message": "Orçamento #42 convertido em Venda #101",
  "venda_id": 101,
  "orcamento_id": 42
}
```

## Benefícios

✅ **Rastreabilidade Completa**: Saber qual venda veio de qual orçamento
✅ **Histórico Preservado**: Dados do orçamento mantidos na venda
✅ **Gestão de Status**: Controlar status de orçamentos no sistema
✅ **PDFs Informativos**: Documentos mostram referência cruzada
✅ **Interface Intuitiva**: Botão visível, modal claro, confirmação segura

## Notas Técnicas

- Migration criada automaticamente pelo Django
- Foreign Key com `SET_NULL` permite deletar orçamento após conversão
- `related_name='vendas_convertidas'` permite consultas reversas
- JavaScript modular com funções separadas
- JSON responses para AJAX
- Compatibilidade com templates existentes
