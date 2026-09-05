"""Vistas del módulo ANP (patrón index + solve_api, stateless)."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'anp/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        matriz = data.get('matriz')
        nombres = data.get('nombres') or []
        if not matriz:
            return JsonResponse({'error': 'Falta la supermatriz.'}, status=400)

        res = solver.anp(matriz)
        n = res['n']
        if not nombres or len(nombres) != n:
            nombres = ['E%d' % (i + 1) for i in range(n)]
        res['nombres'] = nombres
        res['ranking'] = solver.ranking(nombres, res['prioridades'])
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo procesar la supermatriz.'}, status=400)
