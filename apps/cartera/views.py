"""Vistas del módulo Cartera de proyectos (index + solve_api, stateless)."""
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import solver


def index(request):
    return render(request, 'cartera/index.html')


@csrf_exempt
@require_POST
def solve_api(request):
    try:
        data = json.loads(request.body or '{}')
        pesos = data.get('pesos')
        impactos = data.get('impactos')
        proyectos = data.get('proyectos') or []
        objetivos = data.get('objetivos') or []
        if not pesos or not impactos:
            return JsonResponse({'error': 'Faltan pesos de objetivos o impactos de proyectos.'}, status=400)

        res = solver.indice_estrategico(pesos, impactos)
        if not proyectos or len(proyectos) != len(res['IE']):
            proyectos = ['P%d' % (i + 1) for i in range(len(res['IE']))]
        res['ranking'] = solver.ranking(proyectos, res['IE'], res['IE_relativo'])
        res['proyectos'] = proyectos
        res['objetivos'] = objetivos
        return JsonResponse(res)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo calcular la cartera.'}, status=400)
