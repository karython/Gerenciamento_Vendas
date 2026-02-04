from django.db import models

class Produto(models.Model):
    idPRODUTO = models.AutoField(primary_key=True)
    DESCRICAO = models.CharField(max_length=120)
    VLR_UNIT = models.CharField(max_length=45)
    IOF = models.CharField(max_length=45)
    DT_MOVIMENTADA = models.DateTimeField()
    TRACK_STOCK = models.BooleanField(default=True)

    class Meta:
        db_table = 'PRODUTO'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.DESCRICAO