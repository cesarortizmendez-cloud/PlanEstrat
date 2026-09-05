"""Vistas del módulo AHP.

Patrón de dos vistas (igual que IO-Lab / Pronostat):
- index: renderiza la interfaz educativa.
- solve_api: recibe la matriz por JSON (POST), llama al solver puro y devuelve JSON.

El cálculo es stateless: no toca la base de datos. La API va exenta de CSRF por ser
un cálculo sin efectos ni autenticación (entra JSON, sale JSON).
"""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'ahp/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        matriz = data.get('matriz')
        nombres = data.get('nombres') or []
        if not matriz:
            return JsonResponse({'error': 'Falta la matriz de comparación.'}, status=400)

        res = solver.prioridades_ahp(matriz)
        if not nombres or len(nombres) != res['n']:
            nombres = ['C%d' % (i + 1) for i in range(res['n'])]
        res['ranking'] = solver.ranking(nombres, res['pesos'])
        res['nombres'] = nombres
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo procesar la matriz.'}, status=400)
