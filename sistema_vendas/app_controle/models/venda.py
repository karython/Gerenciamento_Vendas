from django.db import models
from .cliente import Cliente

class Venda(models.Model):
    idVENDA = models.AutoField(primary_key=True)
    CLIENTE_idCLIENTE = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='CLIENTE_idCLIENTE'
    )
    PAGAMENTO_idPAGAMENTO = models.IntegerField()
    QTD_VENDIDA = models.IntegerField()
    DT_VENDA = models.DateTimeField()
    VLR_TOTAL = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'VENDA'
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'

    def __str__(self):
        return f"Venda #{self.idVENDA}"