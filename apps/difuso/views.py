"""Vistas del módulo de métodos difusos (Fuzzy VIKOR). Stateless."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'difuso/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        tfn = data.get('tfn')
        pesos = data.get('pesos')
        beneficio = data.get('beneficio')
        v = float(data.get('v', 0.5))
        alternativas = data.get('alternativas') or []
        if not tfn or not pesos or beneficio is None:
            return JsonResponse({'error': 'Faltan datos (evaluaciones, pesos u orientación).'}, status=400)

        res = solver.vikor_difuso(tfn, pesos, beneficio, v=v)
        if not alternativas or len(alternativas) != res['A']:
            alternativas = ['A%d' % (i + 1) for i in range(res['A'])]
        res['ranking'] = solver.ranking(alternativas, res['Q'], res['orden'], res['S'], res['R'])
        res['alternativas'] = alternativas
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo calcular VIKOR difuso.'}, status=400)
