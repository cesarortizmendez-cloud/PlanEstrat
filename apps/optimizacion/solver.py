"""Optimización del mapa estratégico — selección de relaciones (programación entera).

A partir de un conjunto de relaciones candidatas con su importancia (por ejemplo, la
influencia total de DEMATEL o ANP), selecciona el subconjunto que:
  - maximiza la importancia conservada,
  - penaliza la cantidad de relaciones (parsimonia), con el parámetro lambda,
  - evita objetivos aislados (cada objetivo con relaciones candidatas conserva al menos
    una relación).

Usa programación lineal entera (scipy.optimize.milp).
"""
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def optimizar(relaciones, nodos=None, lam=0.0, sin_aislados=True):
    """Selecciona relaciones.

    relaciones : lista de dicts {de, a, peso}.
    nodos      : lista de nodos; si None se deduce de las relaciones.
    lam        : penalización por relación (>= 0). Mayor lambda => mapa más simple.
    sin_aislados : si True, cada nodo con relaciones candidatas conserva >= 1.
    """
    m = len(relaciones)
    if m == 0:
        raise ValueError("No hay relaciones candidatas.")
    peso = np.array([float(r["peso"]) for r in relaciones], dtype=float)

    if nodos is None:
        s = []
        for r in relaciones:
            if r["de"] not in s:
                s.append(r["de"])
            if r["a"] not in s:
                s.append(r["a"])
        nodos = s

    # Minimizar c·x  <=>  maximizar (peso - lam)·x
    c = -(peso - float(lam))

    # Cobertura: cada nodo con relaciones incidentes conserva al menos una.
    filas, nodos_cubiertos = [], []
    for v in nodos:
        fila = [1.0 if (relaciones[j]["de"] == v or relaciones[j]["a"] == v) else 0.0
                for j in range(m)]
        if sum(fila) > 0:
            filas.append(fila)
            nodos_cubiertos.append(v)

    constraints = []
    if sin_aislados and filas:
        constraints = [LinearConstraint(np.array(filas), lb=1, ub=np.inf)]

    res = milp(c, constraints=constraints, integrality=np.ones(m),
               bounds=Bounds(0, 1))

    factible = bool(res.success)
    if not factible and constraints:
        # Si la cobertura hace infactible, resolver sin ella.
        res = milp(c, constraints=[], integrality=np.ones(m), bounds=Bounds(0, 1))
        factible = bool(res.success)
        sin_aislados = False

    x = np.round(res.x).astype(int) if res.success and res.x is not None else np.zeros(m, dtype=int)

    seleccionadas, descartadas = [], []
    for j, r in enumerate(relaciones):
        item = {"de": r["de"], "a": r["a"], "peso": float(peso[j])}
        (seleccionadas if x[j] == 1 else descartadas).append(item)

    imp_total = float(peso.sum())
    imp_conservada = float(peso[x == 1].sum())

    return {
        "m": m,
        "lam": float(lam),
        "sin_aislados": bool(sin_aislados),
        "factible": factible,
        "n_seleccionadas": int(x.sum()),
        "importancia_total": imp_total,
        "importancia_conservada": imp_conservada,
        "fraccion_conservada": (imp_conservada / imp_total) if imp_total > 0 else 0.0,
        "seleccionadas": seleccionadas,
        "descartadas": descartadas,
    }


def frontera(relaciones, nodos=None, lambdas=None, sin_aislados=True):
    """Recorre distintos lambda y devuelve la frontera nº de relaciones vs importancia."""
    if lambdas is None:
        pesos = [float(r["peso"]) for r in relaciones]
        lo, hi = (min(pesos), max(pesos)) if pesos else (0, 1)
        lambdas = list(np.linspace(lo, hi, 8))
    puntos = []
    for lam in lambdas:
        r = optimizar(relaciones, nodos=nodos, lam=lam, sin_aislados=sin_aislados)
        puntos.append({
            "lam": float(lam),
            "n": r["n_seleccionadas"],
            "importancia": r["importancia_conservada"],
            "fraccion": r["fraccion_conservada"],
        })
    return puntos
