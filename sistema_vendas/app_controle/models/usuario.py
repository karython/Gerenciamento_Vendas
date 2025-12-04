from django.db import models

class Usuario(models.Model):
    idUSUARIO = models.AutoField(primary_key=True)
    NOME_USUARIO = models.CharField(max_length=120)
    EMAIL = models.CharField(max_length=120)
    SENHA = models.CharField(max_length=255)

    class Meta:
        db_table = 'USUARIO'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.NOME_USUARIO