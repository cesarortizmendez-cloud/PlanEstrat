"""Vistas del módulo de conciencia situacional (index + solve_api, stateless)."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'situacional/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        indicadores = data.get('indicadores')
        uv = float(data.get('umbral_verde', 0.9))
        ua = float(data.get('umbral_amarillo', 0.7))
        if not indicadores:
            return JsonResponse({'error': 'No hay indicadores.'}, status=400)
        return JsonResponse(solver.evaluar(indicadores, umbral_verde=uv, umbral_amarillo=ua))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudieron evaluar los indicadores.'}, status=400)
