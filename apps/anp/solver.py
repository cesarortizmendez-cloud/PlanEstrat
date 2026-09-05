"""ANP — Analytic Network Process (nivel de supermatriz).

Matemática pura (solo numpy). A partir de una supermatriz de influencias/prioridades
entre elementos de una red, calcula:
  1. la supermatriz ponderada (columna-estocástica),
  2. la supermatriz límite (elevando a potencias hasta converger),
  3. las prioridades globales (el vector de la supermatriz límite).

Se trabaja a nivel de supermatriz: la ponderación de clústeres se asume ya incorporada
en las columnas (o se obtiene normalizando cada columna para que sume 1).
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

    # Supermatriz ponderada: cada columna se normaliza para sumar 1 (estocástica).
    col_sum = W.sum(axis=0)
    Ws = np.zeros_like(W)
    columnas_cero = []
    for j in range(n):
        if col_sum[j] > 0:
            Ws[:, j] = W[:, j] / col_sum[j]
        else:
            columnas_cero.append(j)  # elemento que no depende de nada: columna nula

    # Supermatriz límite: potencias sucesivas hasta convergencia.
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

    # Prioridades globales: promedio de columnas de la supermatriz límite,
    # normalizado (si convergió, las columnas son iguales).
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


def ranking(nombres, prioridades):
    pares = sorted(zip(nombres, prioridades), key=lambda p: p[1], reverse=True)
    return [{"nombre": n, "peso": float(w)} for n, w in pares]
