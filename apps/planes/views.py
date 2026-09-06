"""Vistas del módulo de planes de acción Lean. Stateless.

solve_api despacha según la herramienta: pareto, 5s, smed, oee.
(Ishikawa se construye en el cliente.)
"""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'planes/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        tool = data.get('tool')
        if tool == 'pareto':
            res = solver.pareto(data.get('causas', []), umbral=float(data.get('umbral', 0.8)))
        elif tool == '5s':
            res = solver.cinco_s(data.get('scores', []))
        elif tool == 'smed':
            res = solver.smed(data.get('actividades', []))
        elif tool == 'oee':
            res = solver.oee(
                data.get('tiempo_planificado', 0), data.get('paradas', 0),
                data.get('tiempo_ciclo_ideal', 0), data.get('piezas_producidas', 0),
                data.get('piezas_buenas', 0),
            )
        else:
            return JsonResponse({'error': 'Herramienta no reconocida.'}, status=400)
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo calcular.'}, status=400)
