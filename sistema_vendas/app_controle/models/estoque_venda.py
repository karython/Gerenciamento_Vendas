from django.db import models
from .estoque import Estoque
from .venda import Venda

class EstoqueVenda(models.Model):
    ESTOQUE_idESTOQUE = models.ForeignKey(
        Estoque,
        on_delete=models.PROTECT,
        db_column='ESTOQUE_idESTOQUE'
    )
    VENDA_idVENDA = models.ForeignKey(
        Venda,
        on_delete=models.PROTECT,
        db_column='VENDA_idVENDA'
    )

    class Meta:
        db_table = 'ESTOQUE_has_VENDA'
        verbose_name = 'Estoque Venda'
        verbose_name_plural = 'Estoque Vendas'
        unique_together = (('ESTOQUE_idESTOQUE', 'VENDA_idVENDA'),)

    def __str__(self):
        return f"Estoque {self.ESTOQUE_idESTOQUE.idESTOQUE} - Venda {self.VENDA_idVENDA.idVENDA}"