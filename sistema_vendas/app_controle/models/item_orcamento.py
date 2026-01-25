# app_controle/models/item_orcamento.py
from django.db import models
from .orcamento import Orcamento
from .produto import Produto

class ItemOrcamento(models.Model):
    idITEM_ORCAMENTO = models.AutoField(primary_key=True)
    ORCAMENTO_idORCAMENTO = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        db_column='ORCAMENTO_idORCAMENTO',
        related_name='itens'
    )
    PRODUTO_idPRODUTO = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        db_column='PRODUTO_idPRODUTO',
        related_name='itens_orcamento'
    )
    QUANTIDADE = models.DecimalField(max_digits=10, decimal_places=2)
    VLR_UNITARIO = models.DecimalField(max_digits=10, decimal_places=2)
    VLR_TOTAL = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'ITEM_ORCAMENTO'
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Itens de Orçamento'
    
    def __str__(self):
        return f"Item #{self.idITEM_ORCAMENTO} - Orçamento #{self.ORCAMENTO_idORCAMENTO.idORCAMENTO}"