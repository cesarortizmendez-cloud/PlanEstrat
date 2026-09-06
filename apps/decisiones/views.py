"""Vistas de la decisión colaborativa multiusuario (paradigma de decisión).

Flujo:
  1. El facilitador crea una sala: nombre, código y clave, más el objetivo, los
     criterios y las ALTERNATIVAS. Recibe un enlace de administración.
  2. Comparte nombre + código + clave. Cada participante entra, hace su decisión
     multicriterio individual (pondera criterios y evalúa las alternativas) y la envía;
     recibe su propio resultado ("tu selección").
  3. El facilitador ve todas las participaciones y la decisión agregada del grupo
     (media geométrica de criterios y de desempeños) — "la selección del grupo".

Reutiliza los solvers de AHP y ANP.
"""
import json
import secrets

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.ahp import solver as ahp
from apps.anp import solver as anp
from .models import Decision, Participacion

ALFABETO = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # sin caracteres ambiguos


def _codigo_unico():
    for _ in range(20):
        c = ''.join(secrets.choice(ALFABETO) for _ in range(6))
        if not Decision.objects.filter(codigo=c).exists():
            return c
    return ''.join(secrets.choice(ALFABETO) for _ in range(8))


def index(request):
    return render(request, 'decisiones/index.html')


def _limpiar_lista(xs):
    return [str(x).strip() for x in (xs or []) if str(x).strip()]


@csrf_exempt
@require_POST
def crear(request):
    try:
        data = json.loads(request.body or '{}')
        nombre = (data.get('nombre') or '').strip()
        clave = (data.get('clave') or '').strip()
        objetivo = (data.get('objetivo') or '').strip()
        metodo = (data.get('metodo') or 'ahp').strip().lower()
        criterios = _limpiar_lista(data.get('criterios'))
        alternativas = _limpiar_lista(data.get('alternativas'))
        privacidad = data.get('privacidad', 'grupal')
        if metodo not in ('ahp', 'anp'):
            metodo = 'ahp'
        if not nombre or not clave:
            return JsonResponse({'error': 'Indica un nombre y una clave.'}, status=400)
        if len(criterios) < 2:
            return JsonResponse({'error': 'Define al menos 2 criterios.'}, status=400)
        if len(alternativas) < 2:
            return JsonResponse({'error': 'Define al menos 2 alternativas.'}, status=400)

        codigo = (data.get('codigo') or '').strip().upper() or _codigo_unico()
        d = Decision(nombre=nombre, codigo=codigo, objetivo=objetivo, metodo=metodo,
                     criterios=criterios, alternativas=alternativas, privacidad=privacidad,
                     admin_token=secrets.token_urlsafe(16))
        d.set_clave(clave)
        d.save()
        return JsonResponse({
            'ok': True, 'nombre': d.nombre, 'codigo': d.codigo, 'metodo': d.metodo,
            'admin_url': request.build_absolute_uri('/decisiones/admin/%s/' % d.admin_token),
        })
    except Exception as e:
        return JsonResponse({'error': 'No se pudo crear la decisión.', 'detalle': str(e)}, status=400)


def _buscar(codigo, clave):
    codigo = (codigo or '').strip().upper()
    qs = Decision.objects.filter(codigo=codigo).order_by('-creado')
    for d in qs:
        if d.check_clave(clave):
            return d
    return None


@csrf_exempt
@require_POST
def unirse(request):
    try:
        data = json.loads(request.body or '{}')
        d = _buscar(data.get('codigo', ''), data.get('clave', ''))
        if not d:
            return JsonResponse({'error': 'Código o clave incorrectos.'}, status=400)
        if d.estado != 'abierta':
            return JsonResponse({'error': 'Esta decisión está cerrada.'}, status=400)
        return JsonResponse({'ok': True, 'decision': {
            'nombre': d.nombre, 'codigo': d.codigo, 'objetivo': d.objetivo, 'metodo': d.metodo,
            'criterios': d.criterios, 'alternativas': d.alternativas, 'privacidad': d.privacidad,
        }})
    except Exception as e:
        return JsonResponse({'error': 'No se pudo acceder a la decisión.', 'detalle': str(e)}, status=400)


def _decidir(d, juicios, desempeno):
    """Calcula la decisión individual según el método de la sala."""
    if d.metodo == 'anp':
        return anp.decidir_anp(juicios, d.criterios, d.alternativas, desempeno)
    return ahp.decidir_ahp(juicios, d.criterios, d.alternativas, desempeno)


@csrf_exempt
@require_POST
def enviar(request):
    try:
        data = json.loads(request.body or '{}')
        d = _buscar(data.get('codigo', ''), data.get('clave', ''))
        if not d:
            return JsonResponse({'error': 'Código o clave incorrectos.'}, status=400)
        if d.estado != 'abierta':
            return JsonResponse({'error': 'Esta decisión está cerrada.'}, status=400)
        juicios = data.get('juicios')
        desempeno = data.get('desempeno')
        participante = (data.get('participante') or '').strip()
        if d.privacidad != 'anonima' and not participante:
            return JsonResponse({'error': 'Indica tu nombre.'}, status=400)
        if not juicios or not desempeno:
            return JsonResponse({'error': 'Falta tu evaluación.'}, status=400)

        r = _decidir(d, juicios, desempeno)
        cr = None
        if d.metodo == 'ahp':
            cr = float(r['criterios']['CR'])
        resumen = {
            'seleccionado': r['seleccionado'],
            'ranking': r['ranking'],
            'pesos': r['criterios']['pesos'],
        }
        Participacion.objects.create(
            decision=d,
            participante='' if d.privacidad == 'anonima' else participante,
            juicios=juicios, desempeno=desempeno, consistencia=cr, resultado=resumen,
        )
        return JsonResponse({'ok': True, 'seleccionado': r['seleccionado'], 'ranking': r['ranking'],
                             'consistencia': cr, 'consistente': (cr is None or cr <= 0.10)})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'No se pudo registrar la evaluación.', 'detalle': str(e)}, status=400)


def _agregar_grupo(d, parts):
    """Decisión agregada del grupo a partir de todas las participaciones."""
    juicios = [p.juicios for p in parts]
    desempenos = [p.desempeno for p in parts]
    if d.metodo == 'anp':
        agg_j = ahp.media_aritmetica(juicios) if len(juicios) > 1 else juicios[0]
        agg_d = ahp.media_geometrica(desempenos) if len(desempenos) > 1 else desempenos[0]
        return anp.decidir_anp(agg_j, d.criterios, d.alternativas, agg_d)
    agg_j = ahp.media_geometrica(juicios) if len(juicios) > 1 else juicios[0]
    agg_d = ahp.media_geometrica(desempenos) if len(desempenos) > 1 else desempenos[0]
    return ahp.decidir_ahp(agg_j, d.criterios, d.alternativas, agg_d)


def admin(request, token):
    d = get_object_or_404(Decision, admin_token=token)
    parts_qs = list(d.participaciones.all().order_by('enviado'))

    def _nombre(p):
        return 'Anónimo' if d.privacidad == 'anonima' else (p.participante or 'Anónimo')

    parts = [{
        'nombre': _nombre(p),
        'cr': p.consistencia,
        'consistente': (p.consistencia is None or (p.consistencia is not None and p.consistencia <= 0.10)),
        'seleccionado': (p.resultado or {}).get('seleccionado', '—'),
        'fecha': p.enviado,
    } for p in parts_qs]

    resultado = None
    votos = {}
    if parts_qs:
        # conteo de selecciones individuales (quién ganó para cada persona)
        for p in parts_qs:
            sel = (p.resultado or {}).get('seleccionado')
            if sel:
                votos[sel] = votos.get(sel, 0) + 1
        try:
            r = _agregar_grupo(d, parts_qs)
            ranking = [{'nombre': x['nombre'], 'pct': round(x['score'] * 100, 1)} for x in r['ranking']]
            resultado = {
                'seleccionado': r['seleccionado'],
                'ranking': ranking,
                'metodo': d.metodo.upper(),
                'consistente': r['criterios'].get('consistente', True) if d.metodo == 'ahp' else True,
                'CR': r['criterios'].get('CR') if d.metodo == 'ahp' else None,
                'pesos': [{'nombre': n, 'pct': round(w * 100, 1)}
                          for n, w in sorted(zip(d.criterios, r['criterios']['pesos']), key=lambda t: -t[1])],
            }
        except Exception:
            resultado = None

    votos_list = sorted(({'nombre': k, 'n': v} for k, v in votos.items()), key=lambda x: -x['n'])
    return render(request, 'decisiones/admin.html', {
        'd': d, 'parts': parts, 'n_parts': len(parts), 'resultado': resultado,
        'votos': votos_list, 'token': token,
    })


@csrf_exempt
@require_POST
def cerrar(request, token):
    d = get_object_or_404(Decision, admin_token=token)
    d.estado = 'cerrada'
    d.save(update_fields=['estado'])
    return redirect('decisiones:admin', token=token)
