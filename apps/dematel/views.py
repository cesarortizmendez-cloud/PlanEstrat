"""Vistas del módulo DEMATEL (patrón index + solve_api, stateless)."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'dematel/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        matriz = data.get('matriz')
        nombres = data.get('nombres') or []
        umbral = data.get('umbral')
        if umbral in ('', None):
            umbral = None
        else:
            umbral = float(umbral)
        if not matriz:
            return JsonResponse({'error': 'Falta la matriz de influencia.'}, status=400)

        res = solver.dematel(matriz, umbral=umbral)
        n = res['n']
        if not nombres or len(nombres) != n:
            nombres = ['F%d' % (i + 1) for i in range(n)]
        res['nombres'] = nombres
        for e in res['elementos']:
            e['nombre'] = nombres[e['i']]
        for rel in res['relaciones']:
            rel['nombre_de'] = nombres[rel['de']]
            rel['nombre_a'] = nombres[rel['a']]
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo procesar la matriz.'}, status=400)
