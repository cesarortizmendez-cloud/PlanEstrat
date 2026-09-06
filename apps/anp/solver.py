"""ANP — Analytic Network Process.

Matemática pura (solo numpy). Dos usos:

1. `anp(W)` — a partir de una supermatriz de influencias, calcula la supermatriz
   ponderada (columna-estocástica), la límite y las prioridades globales.

2. `decidir_anp(...)` — decisión multicriterio completa: los pesos de los criterios
   se obtienen de una red de interdependencia entre criterios (supermatriz límite),
   y con el desempeño de las alternativas se elige la mejor. Esto es lo propio de ANP
   frente a AHP: los criterios se influyen entre sí.
"""
import numpy as np


def anp(W, max_iter=300, tol=1e-12):
    """Analiza una supermatriz W (n x n).

    W[i][j] = influencia/prioridad del elemento i respecto del elemento j
    (columna j = de qué depende j y con qué peso). Valores no negativos.
    """
    W = np.asarray(W, dtype=float)
    if W.ndim != 2 or W.shape[0] != W.shape[1]:
        raise ValueError("La supermatriz debe ser cuadrada.")
    if np.any(W < 0):
        raise ValueError("Los valores no pueden ser negativos.")
    n = W.shape[0]

    col_sum = W.sum(axis=0)
    Ws = np.zeros_like(W)
    columnas_cero = []
    for j in range(n):
        if col_sum[j] > 0:
            Ws[:, j] = W[:, j] / col_sum[j]
        else:
            columnas_cero.append(j)

    P = Ws.copy()
    convergio = False
    iteraciones = max_iter
    for k in range(max_iter):
        Pn = P @ Ws
        if np.max(np.abs(Pn - P)) < tol:
            convergio = True
            P = Pn
            iteraciones = k + 1
            break
        P = Pn
    limite = P

    pri = limite.mean(axis=1)
    total = pri.sum()
    if total > 0:
        pri = pri / total

    return {
        "n": n,
        "convergio": bool(convergio),
        "iteraciones": int(iteraciones),
        "columnas_cero": columnas_cero,
        "ponderada": Ws.tolist(),
        "limite": limite.tolist(),
        "prioridades": pri.tolist(),
    }


def _pesos_red(C, max_iter=300, tol=1e-12):
    """Pesos de los criterios a partir de una matriz de interdependencia C.

    C[i][j] = cuánto influye el criterio i sobre el criterio j (>= 0). Se normaliza
    por columnas (estocástica); una columna nula (criterio que no depende de nadie)
    se reparte de forma uniforme para que la cadena esté bien definida. Luego se
    toma el límite de la supermatriz y su vector estacionario = pesos.
    """
    C = np.asarray(C, dtype=float)
    n = C.shape[0]
    cs = C.sum(axis=0)
    S = np.zeros((n, n))
    for j in range(n):
        if cs[j] > 0:
            S[:, j] = C[:, j] / cs[j]
        else:
            S[:, j] = 1.0 / n
    P = S.copy()
    convergio = False
    iteraciones = max_iter
    for k in range(max_iter):
        Pn = P @ S
        if np.max(np.abs(Pn - P)) < tol:
            convergio = True
            P = Pn
            iteraciones = k + 1
            break
        P = Pn
    w = P.mean(axis=1)
    total = w.sum()
    if total > 0:
        w = w / total
    return w, S, P, bool(convergio), int(iteraciones)


def decidir_anp(criterios_influencia, nombres_criterios, alternativas, desempeno):
    """ANP de decisión: elige la mejor alternativa considerando interdependencia
    entre criterios.

    - criterios_influencia: matriz n_crit x n_crit, C[i][j] = influencia de i sobre j.
    - nombres_criterios: n_crit nombres.
    - alternativas: lista de m nombres.
    - desempeno: matriz m x n_crit (1..9), cuán bien satisface cada alternativa cada
      criterio (mayor = mejor). Se normaliza por columnas -> prioridades locales.
    """
    C = np.asarray(criterios_influencia, dtype=float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError("La matriz de influencia entre criterios debe ser cuadrada.")
    if np.any(C < 0):
        raise ValueError("Las influencias no pueden ser negativas.")
    n = C.shape[0]
    if len(nombres_criterios) != n:
        nombres_criterios = ['C%d' % (i + 1) for i in range(n)]

    w, S, P, convergio, iteraciones = _pesos_red(C)

    if not alternativas:
        raise ValueError("Define al menos una alternativa.")
    D = np.asarray(desempeno, dtype=float)
    if D.ndim != 2:
        raise ValueError("El desempeño debe ser una matriz alternativas x criterios.")
    m, c = D.shape
    if c != n:
        raise ValueError("El desempeño debe tener una columna por criterio.")
    if m != len(alternativas):
        raise ValueError("Cada fila del desempeño es una alternativa.")
    if np.any(D <= 0):
        raise ValueError("Las valoraciones deben ser positivas (escala 1 a 9).")

    col = D.sum(axis=0)
    L = D / col
    scores = L @ w
    total = scores.sum()
    if total > 0:
        scores = scores / total

    orden = list(np.argsort(-scores))
    rank = [{
        "nombre": alternativas[i],
        "score": float(scores[i]),
        "local": [float(x) for x in L[i]],
    } for i in orden]
    margen = float(rank[0]["score"] - rank[1]["score"]) if len(rank) > 1 else 1.0

    return {
        "modo": "decision",
        "criterios": {
            "nombres": list(nombres_criterios),
            "pesos": w.tolist(),
            "convergio": convergio,
            "iteraciones": iteraciones,
            "n": n,
        },
        "estocastica": S.tolist(),
        "limite": P.tolist(),
        "alternativas": list(alternativas),
        "local": L.tolist(),
        "scores": scores.tolist(),
        "ranking": rank,
        "seleccionado": rank[0]["nombre"],
        "margen": margen,
    }


def ranking(nombres, prioridades):
    pares = sorted(zip(nombres, prioridades), key=lambda p: p[1], reverse=True)
    return [{"nombre": n, "peso": float(w)} for n, w in pares]
