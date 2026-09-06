"""Vistas de la decisión colaborativa.

Flujo: el facilitador crea una decisión (nombre, criterios, clave) y recibe un
enlace de administración; comparte nombre + clave; cada participante se une y envía
su matriz de comparación; el administrador ve el avance, agrega por media geométrica
y obtiene las prioridades del grupo con el solver AHP (reutilizado).
"""
import json
import secrets

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.ahp import solver as ahp
from .models import Decision, Participacion


def index(request):
    return render(request, 'decisiones/index.html')


@csrf_exempt
@require_POST
def crear(request):
    try:
        data = json.loads(request.body or '{}')
        nombre = (data.get('nombre') or '').strip()
        clave = (data.get('clave') or '').strip()
        criterios = [c.strip() for c in (data.get('criterios') or []) if c.strip()]
        privacidad = data.get('privacidad', 'privada')
        if not nombre or not clave or len(criterios) < 2:
            return JsonResponse({'error': 'Indica nombre, clave y al menos 2 criterios.'}, status=400)
        d = Decision(nombre=nombre, criterios=criterios, privacidad=privacidad,
                     admin_token=secrets.token_urlsafe(16))
        d.set_clave(clave)
        d.save()
        return JsonResponse({
            'ok': True, 'nombre': d.nombre,
            'admin_url': request.build_absolute_uri('/decisiones/admin/%s/' % d.admin_token),
        })
    except Exception:
        return JsonResponse({'error': 'No se pudo crear la decisión.'}, status=400)


def _buscar(nombre, clave):
    qs = Decision.objects.filter(nombre__iexact=nombre.strip()).order_by('-creado')
    for d in qs:
        if d.check_clave(clave):
            return d
    return None


@csrf_exempt
@require_POST
def unirse(request):
    try:
        data = json.loads(request.body or '{}')
        d = _buscar(data.get('nombre', ''), data.get('clave', ''))
        if not d:
            return JsonResponse({'error': 'Nombre o clave incorrectos.'}, status=400)
        if d.estado != 'abierta':
            return JsonResponse({'error': 'Esta decisión está cerrada.'}, status=400)
        return JsonResponse({'ok': True, 'decision': {
            'id': d.id, 'nombre': d.nombre, 'criterios': d.criterios, 'privacidad': d.privacidad,
        }})
    except Exception:
        return JsonResponse({'error': 'No se pudo acceder a la decisión.'}, status=400)


@csrf_exempt
@require_POST
def enviar(request):
    try:
        data = json.loads(request.body or '{}')
        d = _buscar(data.get('nombre', ''), data.get('clave', ''))
        if not d:
            return JsonResponse({'error': 'Nombre o clave incorrectos.'}, status=400)
        if d.estado != 'abierta':
            return JsonResponse({'error': 'Esta decisión está cerrada.'}, status=400)
        matriz = data.get('matriz')
        participante = (data.get('participante') or '').strip()
        if d.privacidad != 'anonima' and not participante:
            return JsonResponse({'error': 'Indica tu nombre.'}, status=400)
        if not matriz:
            return JsonResponse({'error': 'Falta la evaluación.'}, status=400)
        cr = float(ahp.prioridades_ahp(matriz)['CR'])
        Participacion.objects.create(
            decision=d,
            participante='' if d.privacidad == 'anonima' else participante,
            juicios=matriz, consistencia=cr,
        )
        return JsonResponse({'ok': True, 'consistencia': cr, 'consistente': cr <= 0.10})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'No se pudo registrar la evaluación.'}, status=400)


def admin(request, token):
    d = get_object_or_404(Decision, admin_token=token)
    parts_qs = list(d.participaciones.all().order_by('enviado'))
    parts = [{
        'nombre': (p.participante or 'Anónimo') if d.privacidad != 'anonima' else 'Anónimo',
        'cr': p.consistencia,
        'consistente': (p.consistencia is not None and p.consistencia <= 0.10),
        'fecha': p.enviado,
    } for p in parts_qs]

    resultado = None
    if parts_qs:
        try:
            matrices = [p.juicios for p in parts_qs]
            grupo = ahp.agregar_geometrica(matrices) if len(matrices) > 1 else matrices[0]
            r = ahp.prioridades_ahp(grupo)
            ranking = ahp.ranking(d.criterios, r['pesos'])
            for item in ranking:
                item['pct'] = round(item['peso'] * 100, 1)
            resultado = {'ranking': ranking, 'CR': r['CR'], 'consistente': r['consistente']}
        except Exception:
            resultado = None

    return render(request, 'decisiones/admin.html', {
        'd': d, 'parts': parts, 'n_parts': len(parts), 'resultado': resultado, 'token': token,
    })


@csrf_exempt
@require_POST
def cerrar(request, token):
    d = get_object_or_404(Decision, admin_token=token)
    d.estado = 'cerrada'
    d.save(update_fields=['estado'])
    return redirect('decisiones:admin', token=token)
