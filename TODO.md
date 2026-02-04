# TODO - Correção do Problema de Status do Orçamento

## Problema
O endpoint `/orcamentos/status/8/` está retornando 404 porque a rota genérica `/orcamentos/` está definida antes das rotas específicas.

## Plano de Correção
- [x] Analisar os arquivos relevantes
- [x] Reordenar as rotas de orçamentos no `urls.py`
- [x] Adicionar rotas ausentes (status e converter) ao arquivo principal
- [x] Corrigir nomes dos campos na função converter_orcamento_venda
- [ ] Testar a conversão de orçamento em venda

## Observações
A ordem correta das rotas de orçamentos deve ser:
1. `orcamentos/novo/`
2. `orcamentos/criar/`
3. `orcamentos/status/<int:orcamento_id>/`
4. `orcamentos/converter/<int:orcamento_id>/`
5. `orcamentos/pdf/<int:orcamento_id>/`
6. `orcamentos/deletar/<int:orcamento_id>/`
7. `orcamentos/` (genérica por último)

