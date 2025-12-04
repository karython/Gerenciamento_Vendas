from django.db import models
from .produto import Produto

class Estoque(models.Model):
    idESTOQUE = models.AutoField(primary_key=True)
    PRODUTO_idPRODUTO = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        db_column='PRODUTO_idPRODUTO'
    )
    QTD_DISPONIVEL = models.IntegerField()

    class Meta:
        db_table = 'ESTOQUE'
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return f"Estoque #{self.idESTOQUE}"