# app_controle/models/loja.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Loja(models.Model):
    idLOJA = models.AutoField(primary_key=True)
    NOME_LOJA = models.CharField(max_length=200, verbose_name='Nome da Loja')
    CNPJ = models.CharField(max_length=18, unique=True, verbose_name='CNPJ', db_index=True)
    SENHA = models.CharField(max_length=255, verbose_name='Senha')
    TELEFONE = models.CharField(max_length=45, null=True, blank=True)
    EMAIL = models.EmailField(max_length=120, null=True, blank=True)
    ENDERECO = models.CharField(max_length=255, null=True, blank=True)
    DATA_CADASTRO = models.DateTimeField(auto_now_add=True)
    ATIVO = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'LOJA'
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
        indexes = [
            models.Index(fields=['CNPJ', 'ATIVO'], name='idx_loja_cnpj_ativo'),
        ]
    
    def __str__(self):
        return f"{self.NOME_LOJA} - {self.CNPJ}"
    
    def set_password(self, raw_password):
        """Criptografa a senha antes de salvar"""
        self.SENHA = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica se a senha está correta"""
        return check_password(raw_password, self.SENHA)
    
    def save(self, *args, **kwargs):
        # Se a senha não estiver criptografada, criptografa
        if self.SENHA and not self.SENHA.startswith('pbkdf2_'):
            self.SENHA = make_password(self.SENHA)
        super().save(*args, **kwargs)