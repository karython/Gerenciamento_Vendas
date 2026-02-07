# tests/test_middleware.py
"""
Testes para middlewares
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_vendas.settings')

import django
django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from app_controle.middleware import SessionExpireMiddleware
from app_controle.models import Loja


class TestSessionExpireMiddleware(TestCase):
    """Testes do middleware de expiração de sessão"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SessionExpireMiddleware(lambda x: None)
        
        # Criar loja de teste
        self.loja = Loja.objects.create(
            nome='Loja Teste',
            cnpj='11.222.333/0001-81',
            ativo=True
        )
        self.loja.set_password('senha123')
        self.loja.save()
    
    def _add_session_to_request(self, request):
        """Adiciona sessão à requisição de teste"""
        session_middleware = SessionMiddleware(lambda x: None)
        session_middleware.process_request(request)
        request.session.save()
    
    def test_middleware_com_loja_ativa(self):
        """Testa middleware com loja ativa"""
        request = self.factory.get('/')
        self._add_session_to_request(request)
        
        # Simular login
        request.session['loja_id'] = self.loja.id
        
        # Processar requisição
        response = self.middleware.process_request(request)
        
        # Deve retornar None (continuar processamento)
        self.assertIsNone(response)
    
    def test_middleware_com_loja_inativa(self):
        """Testa middleware com loja inativa"""
        # Desativar loja
        self.loja.ativo = False
        self.loja.save()
        
        request = self.factory.get('/')
        self._add_session_to_request(request)
        
        # Simular login
        request.session['loja_id'] = self.loja.id
        
        # Processar requisição
        response = self.middleware.process_request(request)
        
        # Deve redirecionar para login
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
    
    def test_middleware_sem_sessao(self):
        """Testa middleware sem sessão"""
        request = self.factory.get('/')
        self._add_session_to_request(request)
        
        # Processar requisição
        response = self.middleware.process_request(request)
        
        # Deve retornar None (sem sessão é OK)
        self.assertIsNone(response)


if __name__ == '__main__':
    import unittest
    unittest.main()