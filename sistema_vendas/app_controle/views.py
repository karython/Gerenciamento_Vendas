from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'base.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def estoque(request):
    return render(request, 'estoque.html')


def vendas(request):
    return render(request, 'vendas.html')


def clientes(request):
    return render(request, 'clientes.html')


def nova_venda(request):
    return render(request, 'nova_venda.html')


def logout(request):
    return render(request, 'logout.html')