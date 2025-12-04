from django.db import models

class UF(models.Model):
    idUF = models.AutoField(primary_key=True)
    NOME_ESTADO = models.CharField(max_length=45)

    class Meta:
        db_table = 'UF'
        verbose_name = 'UF'
        verbose_name_plural = 'UFs'

    def __str__(self):
        return self.NOME_ESTADO