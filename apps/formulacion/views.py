"""Vista del módulo de diagnóstico y formulación estratégica (FODA / TOWS).

Captura misión, visión, valores, FODA y factores críticos, y arma la matriz de
cruce estratégico TOWS. Es la etapa que alimenta al mapa BSC. Render en cliente.
"""
from django.shortcuts import render


def index(request):
    return render(request, 'formulacion/index.html')
