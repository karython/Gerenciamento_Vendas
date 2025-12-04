# app_controle/models/endereco.py
from django.db import models
from .cliente import Cliente
from .cidades import Cidades

class Endereco(models.Model):
    idENDERECO = models.AutoField(primary_key=True)
    LOGRADOURO = models.CharField(max_length=200)
    NUMERO = models.CharField(max_length=20, null=True, blank=True)
    BAIRRO = models.CharField(max_length=100, null=True, blank=True)
    CEP = models.CharField(max_length=20, null=True, blank=True)
    REFERENCIA = models.CharField(max_length=100, null=True, blank=True)
    CIDADES_idCIDADES = models.ForeignKey(
        Cidades,
        on_delete=models.PROTECT,
        db_column='CIDADES_idCIDADES'
    )
    CLIENTE_idCLIENTE = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='CLIENTE_idCLIENTE',
        related_name='enderecos'
    )

    class Meta:
        db_table = 'ENDERECO'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.LOGRADOURO}, {self.NUMERO}"