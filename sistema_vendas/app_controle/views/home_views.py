# ============================================
# app_controle/views/home_views.py
# ============================================

from django.shortcuts import render
from ..services.auth_services import AuthService

@AuthService.requer_login
def home(request):
    """Página inicial do sistema"""
    loja = AuthService.loja_logada(request)
    return render(request, 'core/base.html', {'loja': loja})

@AuthService.requer_login
def dashboard(request):
    """Dashboard do sistema"""
    loja = AuthService.loja_logada(request)
    return render(request, 'dashboard.html', {'loja': loja})