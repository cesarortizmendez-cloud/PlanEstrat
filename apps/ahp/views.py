"""Vistas del módulo AHP.

Patrón de dos vistas (igual que IO-Lab / Pronostat):
- index: renderiza la interfaz educativa.
- solve_api: recibe los datos por JSON (POST), llama al solver puro y devuelve JSON.

Dos modos en solve_api:
- Ponderación de criterios (solo `matriz`): compatibilidad con el uso previo.
- Decisión completa (`criterios`, `alternativas`, `desempeno`): elige la mejor alternativa.

El cálculo es stateless: no toca la base de datos.
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

        # --- Modo decisión: criterios + alternativas + desempeño ---
        if data.get('alternativas') and data.get('desempeno') is not None:
            criterios_matriz = data.get('criterios_matriz') or data.get('matriz')
            nombres_criterios = data.get('nombres') or data.get('nombres_criterios') or []
            alternativas = data.get('alternativas') or []
            desempeno = data.get('desempeno')
            if not criterios_matriz:
                return JsonResponse({'error': 'Falta la matriz de criterios.'}, status=400)
            n_crit = len(criterios_matriz)
            if not nombres_criterios or len(nombres_criterios) != n_crit:
                nombres_criterios = ['C%d' % (i + 1) for i in range(n_crit)]
            res = solver.decidir_ahp(criterios_matriz, nombres_criterios, alternativas, desempeno)
            return JsonResponse(res)

        # --- Modo ponderación de criterios (compatibilidad) ---
        matriz = data.get('matriz')
        nombres = data.get('nombres') or []
        if not matriz:
            return JsonResponse({'error': 'Falta la matriz de comparación.'}, status=400)
        res = solver.prioridades_ahp(matriz)
        if not nombres or len(nombres) != res['n']:
            nombres = ['C%d' % (i + 1) for i in range(res['n'])]
        res['ranking'] = solver.ranking(nombres, res['pesos'])
        res['nombres'] = nombres
        res['modo'] = 'pesos'
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'No se pudo procesar la solicitud.', 'detalle': str(e)}, status=400)
