"""
WSGI config for sistema_vendas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_vendas.settings')

application = get_wsgi_application()

# Start background keepalive thread to ping external host every 3 minutes.
try:
	from app_controle.utils.keepalive import start_keepalive
	start_keepalive("https://gerenciamento-vendas-b87g.onrender.com", interval_seconds=180)
except Exception:
	import logging
	logging.getLogger(__name__).exception("Failed to start keepalive thread")
