# app_controle/models/orcamento.py
from django.db import models
from .cliente import Cliente
from .pagamento import Pagamento

from .produto import Produto

class Orcamento(models.Model):
    idORCAMENTO = models.AutoField(primary_key=True)
    CLIENTE_idCLIENTE = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='CLIENTE_idCLIENTE',
        related_name='orcamentos'
    )
    PAGAMENTO_idPAGAMENTO = models.ForeignKey(
        Pagamento,
        on_delete=models.PROTECT,
        db_column='PAGAMENTO_idPAGAMENTO',
        related_name='orcamentos'
    )
    QTD_ITENS = models.IntegerField(default=0)
    DT_ORCAMENTO = models.DateTimeField(auto_now_add=True)
    VLR_SUBTOTAL = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    DESCONTO = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    VLR_FRETE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    OBSERVACAO = models.TextField(max_length=3000, null=True, blank=True)
    VLR_TOTAL = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS = models.CharField(
        max_length=20,
        choices=[
            ('PENDENTE', 'Pendente'),
            ('APROVADO', 'Aprovado'),
            ('REJEITADO', 'Rejeitado'),
            ('CONVERTIDO', 'Convertido em Venda'),
        ],
        default='PENDENTE'
    )

    class Meta:
        db_table = 'ORCAMENTO'
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'

    def __str__(self):
        return f"Orçamento #{self.idORCAMENTO}"


# models.py
# app_controle/models/item_orcamento.py

