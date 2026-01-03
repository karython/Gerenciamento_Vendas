# app_controle/models/item_venda.py
from django.db import models
from .venda import Venda
from .produto import Produto

class ItemVenda(models.Model):
    idITEM_VENDA = models.AutoField(primary_key=True)
    VENDA_idVENDA = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        db_column='VENDA_idVENDA',
        related_name='itens'
    )
    PRODUTO_idPRODUTO = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        db_column='PRODUTO_idPRODUTO'
    )
    QUANTIDADE = models.IntegerField()
    VLR_UNITARIO = models.DecimalField(max_digits=10, decimal_places=2)
    VLR_TOTAL = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'ITEM_VENDA'
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def __str__(self):
        return f"Item {self.idITEM_VENDA} - Venda #{self.VENDA_idVENDA.idVENDA}"