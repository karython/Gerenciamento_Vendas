    # app_controle/forms.py
from django import forms
from .models import Cliente, Endereco, Cidades, UF

class ClienteForm(forms.ModelForm):
    # Campos adicionais para endereço
    endereco = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cidade = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.CharField(
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cep = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Cliente
        fields = ['NOME_CLIENTE', 'DATA_NASCIMENTO', 'CPF', 'TELEFONE']
        widgets = {
            'NOME_CLIENTE': forms.TextInput(attrs={'class': 'form-control'}),
            'DATA_NASCIMENTO': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'CPF': forms.TextInput(attrs={'class': 'form-control'}),
            'TELEFONE': forms.TextInput(attrs={'class': 'form-control'}),
        }