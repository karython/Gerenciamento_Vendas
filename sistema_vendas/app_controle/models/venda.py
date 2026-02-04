# app_controle/models/venda.py
from django.db import models
from .cliente import Cliente
from .pagamento import Pagamento
from django.utils import timezone

# Importação circular evitada com lazy reference
class Venda(models.Model):
    idVENDA = models.AutoField(primary_key=True)
    CLIENTE_idCLIENTE = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='CLIENTE_idCLIENTE',
        related_name='vendas'
    )
    PAGAMENTO_idPAGAMENTO = models.ForeignKey(
        Pagamento,
        on_delete=models.PROTECT,
        db_column='PAGAMENTO_idPAGAMENTO',
        related_name='vendas'
    )
    QTD_VENDIDA = models.IntegerField(default=0)
    DT_VENDA = models.DateTimeField(default=timezone.now)
    VLR_SUBTOTAL = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    DESCONTO = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    VLR_FRETE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    OBSERVACAO = models.TextField(max_length=3000, null=True, blank=True)
    PARCELAMENTO = models.CharField(max_length=45, null=True, blank=True)
    VLR_TOTAL = models.DecimalField(max_digits=10, decimal_places=2)
    ORCAMENTO_ORIGEM = models.ForeignKey(
        'Orcamento',
        on_delete=models.SET_NULL,
        db_column='ORCAMENTO_idORCAMENTO',
        related_name='vendas_convertidas',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'VENDA'
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'

    def __str__(self):
        return f"Venda #{self.idVENDA}"