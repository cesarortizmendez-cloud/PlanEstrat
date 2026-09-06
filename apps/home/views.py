"""Vista de catálogo (página de inicio) de PlanEstrat.

Stateless: no toca la base de datos. Solo describe los módulos y su estado de
construcción por fases para el roadmap visible en la portada.
"""
from django.shortcuts import render

# Catálogo de módulos. `estado` marca el avance por fases del roadmap.
# 'activo'  -> ya funciona
# 'proximo' -> planificado en una fase siguiente
MODULOS = [
    {
        'codigo': 'M0', 'slug': 'home', 'nombre': 'Inicio / Catálogo',
        'grupo': 'Base', 'estado': 'activo', 'fase': 'Fase 0', 'url': '/',
        'desc': 'Portada, navegación y roadmap del sistema.',
    },
    {
        'codigo': 'M3', 'slug': 'ahp', 'nombre': 'AHP',
        'grupo': 'Laboratorio multicriterio', 'estado': 'activo', 'fase': 'Fase 1', 'url': '/ahp/',
        'desc': 'Proceso Analítico Jerárquico: prioridades, λmáx y consistencia (CR).',
    },
    {
        'codigo': 'M3', 'slug': 'dematel', 'nombre': 'DEMATEL',
        'grupo': 'Laboratorio multicriterio', 'estado': 'activo', 'fase': 'Fase 2', 'url': '/dematel/',
        'desc': 'Influencias directas e indirectas; prominencia y relación causa–efecto.',
    },
    {
        'codigo': 'M3', 'slug': 'anp', 'nombre': 'ANP',
        'grupo': 'Laboratorio multicriterio', 'estado': 'activo', 'fase': 'Fase 2', 'url': '/anp/',
        'desc': 'Dependencias en red; supermatriz ponderada y límite.',
    },
    {
        'codigo': 'M3', 'slug': 'difuso', 'nombre': 'Métodos difusos',
        'grupo': 'Laboratorio multicriterio', 'estado': 'activo', 'fase': 'Fase 2', 'url': '/difuso/',
        'desc': 'Fuzzy DEMATEL y Fuzzy VIKOR con números difusos triangulares.',
    },
    {
        'codigo': 'M4', 'slug': 'optimizacion', 'nombre': 'Optimización del mapa',
        'grupo': 'Estrategia', 'estado': 'activo', 'fase': 'Fase 2', 'url': '/optimizacion/',
        'desc': 'Programación lineal para depurar relaciones (scipy.linprog).',
    },
    {
        'codigo': 'M5', 'slug': 'cartera', 'nombre': 'Cartera de proyectos',
        'grupo': 'Estrategia', 'estado': 'activo', 'fase': 'Fase 2', 'url': '/cartera/',
        'desc': 'Priorización de proyectos por índice estratégico.',
    },
    {
        'codigo': '★', 'slug': 'decisiones', 'nombre': 'Decisiones colaborativas',
        'grupo': 'Diferenciador', 'estado': 'activo', 'fase': 'Fase 3', 'url': '/decisiones/',
        'desc': 'Evaluación multiusuario por nombre + clave, con opciones del administrador.',
    },
    {
        'codigo': 'M1', 'slug': 'formulacion', 'nombre': 'Diagnóstico y formulación',
        'grupo': 'Estrategia', 'estado': 'activo', 'fase': 'Fase 4', 'url': '/formulacion/',
        'desc': 'Misión, visión, FODA y factores críticos de éxito.',
    },
    {
        'codigo': 'M2', 'slug': 'bsc', 'nombre': 'BSC y mapa estratégico',
        'grupo': 'Estrategia', 'estado': 'activo', 'fase': 'Fase 4', 'url': '/bsc/',
        'desc': 'Perspectivas, objetivos y relaciones causa–efecto.',
    },
    {
        'codigo': 'M6', 'slug': 'situacional', 'nombre': 'Conciencia situacional',
        'grupo': 'Estrategia', 'estado': 'activo', 'fase': 'Fase 4', 'url': '/situacional/',
        'desc': 'Indicadores, escenarios y alertas.',
    },
    {
        'codigo': 'M7', 'slug': 'planes', 'nombre': 'Planes de acción · Lean',
        'grupo': 'Ejecución', 'estado': 'activo', 'fase': 'Fase 4', 'url': '/planes/',
        'desc': 'Ishikawa, Pareto, 5S, SMED, TPM/OEE y VSM.',
    },
    {
        'codigo': 'M8', 'slug': 'exportar', 'nombre': 'Informes y exportación',
        'grupo': 'Ejecución', 'estado': 'activo', 'fase': 'Fase 5', 'url': '/exportar/',
        'desc': 'Exportación a Excel (openpyxl) en cada módulo.',
    },
]


def index(request):
    total = len(MODULOS)
    activos = sum(1 for m in MODULOS if m['estado'] == 'activo')
    contexto = {
        'modulos': MODULOS,
        'total': total,
        'activos': activos,
    }
    return render(request, 'home/index.html', contexto)
