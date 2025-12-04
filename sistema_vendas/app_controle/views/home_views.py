# app_controle/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from ..services.cliente_services import ClienteService
from ..models import Cliente

def home(request):
    """Página inicial"""
    return render(request, 'core/base.html')