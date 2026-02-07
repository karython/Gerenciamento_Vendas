# app_controle/forms.py
"""
Forms para validação de dados
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Loja, Cliente
from .utils.security import ValidadorSenha, ValidadorCNPJ, ValidadorCPF


# ============================================================================
# FORM DE LOJA
# ============================================================================

class LojaRegistrationForm(forms.ModelForm):
    """Form de cadastro de loja com validações de segurança"""
    
    nome = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da Loja'
        }),
        label='Nome da Loja'
    )
    
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Senha',
        help_text=(
            f'Mínimo {ValidadorSenha.MIN_LENGTH} caracteres. '
            'Deve conter letras maiúsculas, minúsculas e números.'
        )
    )
    senha_confirmacao = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Senha'
    )
    
    class Meta:
        model = Loja
        fields = ['nome', 'cnpj', 'telefone', 'email', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da Loja'
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00',
                'maxlength': '18'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo'
            }),
        }
    
    def clean_nome(self):
        """Valida nome da loja"""
        nome = self.cleaned_data.get('nome')
        
        if not nome or not nome.strip():
            raise ValidationError('Nome da loja é obrigatório')
        
        return nome.strip()
    
    def clean_senha(self):
        """Valida força da senha"""
        senha = self.cleaned_data.get('senha')
        
        if not senha:
            raise ValidationError('Senha é obrigatória')
        
        # ✅ Usar ValidadorSenha
        valida, msg = ValidadorSenha.validar(senha)
        if not valida:
            raise ValidationError(msg)
        
        return senha
    
    def clean_cnpj(self):
        """Valida e formata CNPJ"""
        cnpj = self.cleaned_data.get('cnpj')
        
        if not cnpj:
            raise ValidationError('CNPJ é obrigatório')
        
        # ✅ Usar ValidadorCNPJ
        if not ValidadorCNPJ.validar(cnpj):
            raise ValidationError('CNPJ inválido')
        
        # ✅ Formatar automaticamente
        cnpj_formatado = ValidadorCNPJ.formatar(cnpj)
        
        # Verificar duplicidade
        if Loja.objects.filter(cnpj=cnpj_formatado).exists():
            raise ValidationError('Este CNPJ já está cadastrado')
        
        return cnpj_formatado
    
    def clean(self):
        """Validação geral do form"""
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmacao = cleaned_data.get('senha_confirmacao')
        
        # Verificar se senhas coincidem
        if senha and confirmacao and senha != confirmacao:
            raise ValidationError({
                'senha_confirmacao': 'As senhas não coincidem'
            })
        
        return cleaned_data


class LojaLoginForm(forms.Form):
    """Form de login"""
    
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00.000.000/0000-00'
        }),
        label='CNPJ'
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        }),
        label='Senha'
    )
    
    def clean_cnpj(self):
        """Formata CNPJ para padronização"""
        cnpj = self.cleaned_data.get('cnpj')
        
        if not cnpj:
            raise ValidationError('CNPJ é obrigatório')
        
        # Não validar no login (para não dar dica ao atacante)
        # Apenas formatar
        return ValidadorCNPJ.formatar(cnpj)


# ============================================================================
# FORM DE CLIENTE
# ============================================================================

class ClienteForm(forms.ModelForm):
    """Form de cliente com validação de CPF"""
    
    # Campos adicionais para endereço
    logradouro = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Endereço'
    )
    numero = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Número'
    )
    bairro = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Bairro'
    )
    cep = forms.CharField(
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000'
        }),
        label='CEP'
    )
    cidade = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Cidade'
    )
    estado = forms.CharField(
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Estado (sigla)'
    )
    
    class Meta:
        model = Cliente
        fields = ['nome', 'data_nascimento', 'cpf', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'maxlength': '14'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
        }
    
    def clean_cpf(self):
        """Valida e formata CPF"""
        cpf = self.cleaned_data.get('cpf')
        
        if not cpf:
            raise ValidationError('CPF é obrigatório')
        
        # ✅ Usar ValidadorCPF
        if not ValidadorCPF.validar(cpf):
            raise ValidationError('CPF inválido')
        
        # ✅ Formatar automaticamente
        cpf_formatado = ValidadorCPF.formatar(cpf)
        
        # Verificar duplicidade (exceto se for edição)
        cliente_existente = Cliente.objects.filter(cpf=cpf_formatado)
        
        # Se estamos editando, excluir o próprio cliente da verificação
        if self.instance and self.instance.pk:
            cliente_existente = cliente_existente.exclude(pk=self.instance.pk)
        
        if cliente_existente.exists():
            raise ValidationError('Este CPF já está cadastrado')
        
        return cpf_formatado