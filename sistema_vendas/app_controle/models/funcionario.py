from django.db import models

class Funcionario(models.Model):
    idFUNCIONARIO = models.AutoField(primary_key=True)
    NOME_FUNCIONARIO = models.CharField(max_length=120)
    CPF_CNPJ = models.CharField(max_length=45)
    TELEFONE_FUNCIONARIO = models.CharField(max_length=45)
    ATIVO = models.BooleanField(default=True)

    class Meta:
        db_table = 'FUNCIONARIO'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return self.NOME_FUNCIONARIO