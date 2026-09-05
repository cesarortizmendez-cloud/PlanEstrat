"""WSGI config para PlanEstrat.

Expone el callable WSGI como `application` y también como `app`, que es el nombre
que espera el runtime de Python de Vercel (@vercel/python).
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planestrat.settings')

application = get_wsgi_application()

# Alias para Vercel serverless.
app = application
