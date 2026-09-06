"""Vistas del módulo de optimización del mapa (index + solve_api, stateless)."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'optimizacion/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        relaciones = data.get('relaciones')
        lam = float(data.get('lam', 0) or 0)
        sin_aislados = bool(data.get('sin_aislados', True))
        if not relaciones:
            return JsonResponse({'error': 'No hay relaciones candidatas.'}, status=400)

        res = solver.optimizar(relaciones, lam=lam, sin_aislados=sin_aislados)
        res['frontera'] = solver.frontera(relaciones, sin_aislados=sin_aislados)
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo optimizar.'}, status=400)
