"""Vistas del módulo DEMATEL (patrón index + solve_api, stateless).

Dos modos en solve_api:
- Priorización de proyectos (`proyectos` + `impacto`): método de Quezada et al. (2022).
- Causa/efecto genérico (`matriz`): clasificación DEMATEL de un conjunto de elementos.
"""
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

        # --- Modo priorización de proyectos ---
        if data.get('proyectos') and data.get('impacto') is not None:
            objetivos = data.get('objetivos') or []
            relaciones = data.get('relaciones') or []
            proyectos = data.get('proyectos') or []
            impacto = data.get('impacto')
            meta = (data.get('meta') or 'F').strip().upper()[:1] or 'F'
            res = solver.priorizar_proyectos(objetivos, relaciones, proyectos, impacto, meta=meta)
            return JsonResponse(res)

        # --- Modo causa/efecto genérico (compatibilidad) ---
        matriz = data.get('matriz')
        nombres = data.get('nombres') or []
        umbral = data.get('umbral')
        umbral = None if umbral in ('', None) else float(umbral)
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
    except Exception as e:
        return JsonResponse({'error': 'No se pudo procesar la solicitud.', 'detalle': str(e)}, status=400)
