"""Vistas del módulo ANP (patrón index + solve_api, stateless).

Dos modos en solve_api:
- Supermatriz (solo `matriz`): prioridades globales de una red (uso previo).
- Decisión (`influencia` + `alternativas` + `desempeno`): elige la mejor alternativa
  con pesos de criterios obtenidos de la red de interdependencia.
"""
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

        # --- Modo decisión ---
        if data.get('alternativas') and data.get('desempeno') is not None:
            influencia = data.get('influencia') or data.get('matriz')
            nombres = data.get('nombres') or data.get('nombres_criterios') or []
            alternativas = data.get('alternativas') or []
            desempeno = data.get('desempeno')
            if not influencia:
                return JsonResponse({'error': 'Falta la matriz de interdependencia entre criterios.'}, status=400)
            n = len(influencia)
            if not nombres or len(nombres) != n:
                nombres = ['C%d' % (i + 1) for i in range(n)]
            res = solver.decidir_anp(influencia, nombres, alternativas, desempeno)
            return JsonResponse(res)

        # --- Modo supermatriz (compatibilidad) ---
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
        res['modo'] = 'supermatriz'
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'No se pudo procesar la solicitud.', 'detalle': str(e)}, status=400)
