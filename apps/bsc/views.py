"""Vista del módulo BSC / Mapa estratégico.

Constructor y visualizador del mapa estratégico (perspectivas, objetivos y
relaciones causa–efecto). El renderizado del mapa es en el cliente (SVG); no
requiere cálculo en el servidor, por lo que solo expone `index`.
"""
from django.shortcuts import render


def index(request):
    return render(request, 'bsc/index.html')
