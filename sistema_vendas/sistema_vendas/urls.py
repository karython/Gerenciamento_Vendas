
from django.contrib import admin
from django.urls import path
from app_controle import views


urlpatterns = [
    path('admin/', admin.site.urls),
    # rota - view - nome
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoque', views.estoque, name='estoque'),
    path('vendas', views.vendas, name='vendas'),
    path('clientes', views.clientes, name='clientes'),
    path('nova_venda', views.nova_venda, name='nova_venda'),
    path('logout', views.logout, name='logout'),
  
]
