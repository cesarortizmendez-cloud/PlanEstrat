"""Enrutador raíz de PlanEstrat.

Incluye las apps de módulo y las rutas PWA (manifest y service worker), que deben
servirse desde la raíz del sitio para que el service worker controle todo el scope.
"""
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('apps.home.urls')),
    path('ahp/', include('apps.ahp.urls')),
    path('dematel/', include('apps.dematel.urls')),
    path('anp/', include('apps.anp.urls')),

    # --- PWA (servidas en la raíz) ---
    path(
        'manifest.json',
        TemplateView.as_view(
            template_name='pwa/manifest.json',
            content_type='application/manifest+json',
        ),
        name='manifest',
    ),
    path(
        'service-worker.js',
        TemplateView.as_view(
            template_name='pwa/service-worker.js',
            content_type='application/javascript',
        ),
        name='service-worker',
    ),
    path(
        'offline',
        TemplateView.as_view(template_name='pwa/offline.html'),
        name='offline',
    ),
]
