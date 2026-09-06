"""Vistas del módulo BSC / Mapa estratégico.

El editor del mapa se renderiza en el cliente, pero el mapa se GUARDA en la base de
datos (proceso largo y colaborativo). Endpoints: guardar (crear/actualizar),
abrir (nombre+clave) y cargar (por enlace de edición con token).
"""
import json
import secrets

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import MapaEstrategico


def index(request):
    return render(request, 'bsc/index.html')


@csrf_exempt
@require_POST
def guardar(request):
    try:
        data = json.loads(request.body or '{}')
        datos = data.get('datos')
        if not isinstance(datos, dict):
            return JsonResponse({'error': 'Faltan los datos del mapa.'}, status=400)
        token = (data.get('token') or '').strip()

        if token:
            m = MapaEstrategico.objects.filter(edit_token=token).first()
            if not m:
                return JsonResponse({'error': 'El mapa no existe (enlace inválido).'}, status=400)
            m.datos = datos
            m.save(update_fields=['datos', 'actualizado'])
            return JsonResponse({'ok': True, 'token': m.edit_token, 'nombre': m.nombre})

        nombre = (data.get('nombre') or '').strip()
        clave = (data.get('clave') or '').strip()
        if not nombre or not clave:
            return JsonResponse({'error': 'Indica un nombre y una clave para guardar el mapa.'}, status=400)
        m = MapaEstrategico(nombre=nombre, datos=datos, edit_token=secrets.token_urlsafe(16))
        m.set_clave(clave)
        m.save()
        return JsonResponse({
            'ok': True, 'token': m.edit_token, 'nombre': m.nombre,
            'edit_url': request.build_absolute_uri('/bsc/?t=%s' % m.edit_token),
        })
    except Exception as e:
        return JsonResponse({'error': 'No se pudo guardar el mapa.', 'detalle': str(e)}, status=400)


@csrf_exempt
@require_POST
def abrir(request):
    try:
        data = json.loads(request.body or '{}')
        nombre = (data.get('nombre') or '').strip()
        clave = (data.get('clave') or '').strip()
        qs = MapaEstrategico.objects.filter(nombre__iexact=nombre).order_by('-actualizado')
        for m in qs:
            if m.check_clave(clave):
                return JsonResponse({'ok': True, 'nombre': m.nombre, 'token': m.edit_token, 'datos': m.datos})
        return JsonResponse({'error': 'Nombre o clave incorrectos.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'No se pudo abrir el mapa.', 'detalle': str(e)}, status=400)


@csrf_exempt
def cargar(request, token):
    m = MapaEstrategico.objects.filter(edit_token=token).first()
    if not m:
        return JsonResponse({'error': 'Enlace inválido.'}, status=404)
    return JsonResponse({'ok': True, 'nombre': m.nombre, 'token': m.edit_token, 'datos': m.datos})
