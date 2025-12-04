# app_controle/models/cliente.py
from django.db import models
from .funcionario import Funcionario

class Cliente(models.Model):
    idCLIENTE = models.AutoField(primary_key=True)
    NOME_CLIENTE = models.CharField(max_length=120)
    DATA_NASCIMENTO = models.DateField(null=True, blank=True)
    CPF = models.CharField(max_length=45)
    TELEFONE = models.CharField(max_length=45)
    EMAIL = models.CharField(max_length=120, null=True, blank=True)
    FUNCIONARIO_idFUNCIONARIO = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        db_column='FUNCIONARIO_idFUNCIONARIO',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'CLIENTE'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.NOME_CLIENTE