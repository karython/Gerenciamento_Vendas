from django.db import models
from .uf import UF

class Cidades(models.Model):
    idCIDADES = models.AutoField(primary_key=True)
    NOME_CIDADE = models.CharField(max_length=100)
    UF_idUF = models.ForeignKey(
        UF,  # declara a model com quem ele se relaciona
        on_delete=models.PROTECT,
        db_column='UF_idUF'
    )

    class Meta:     #define alguns nomes para facilitar a visualização
        db_table = 'CIDADES'
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

    def __str__(self):   # ajusta a saida dos dados retornando seu valor
        return self.NOME_CIDADE