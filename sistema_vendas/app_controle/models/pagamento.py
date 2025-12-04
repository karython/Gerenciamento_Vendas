from django.db import models

class Pagamento(models.Model):
    idPAGAMENTO = models.AutoField(primary_key=True)
    TP_PAGAMENTO = models.CharField(max_length=45)

    class Meta:
        db_table = 'PAGAMENTO'
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return self.TP_PAGAMENTO