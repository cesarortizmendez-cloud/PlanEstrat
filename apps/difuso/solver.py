"""Fuzzy VIKOR — priorización de alternativas con evaluaciones lingüísticas.

Las evaluaciones lingüísticas se representan como números difusos triangulares (TFN)
(l, m, u); se defuzzifican por centroide y se aplica VIKOR para hallar una solución
de compromiso entre la utilidad del grupo (S) y el arrepentimiento máximo (R).
"""
import numpy as np


def _centroide(tfn):
    tfn = np.asarray(tfn, dtype=float)          # (A, C, 3)
    return tfn.mean(axis=2)                       # (A, C)


def vikor_difuso(tfn, pesos, beneficio, v=0.5):
    """VIKOR difuso.

    tfn       : lista A x C x 3 (l, m, u) de las evaluaciones.
    pesos     : lista de C pesos de criterio (se normalizan a suma 1).
    beneficio : lista de C booleanos (True = criterio de beneficio, False = costo).
    v         : peso de la estrategia de mayoría (0..1).
    """
    X = _centroide(tfn)                           # matriz defuzzificada A x C
    A, C = X.shape
    w = np.asarray(pesos, dtype=float)
    if w.shape[0] != C:
        raise ValueError("El nº de pesos no coincide con el nº de criterios.")
    if len(beneficio) != C:
        raise ValueError("El nº de orientaciones no coincide con el nº de criterios.")
    if w.sum() <= 0:
        raise ValueError("Los pesos deben sumar un valor positivo.")
    w = w / w.sum()

    fstar = np.zeros(C)
    fminus = np.zeros(C)
    for j in range(C):
        col = X[:, j]
        if beneficio[j]:
            fstar[j], fminus[j] = col.max(), col.min()
        else:
            fstar[j], fminus[j] = col.min(), col.max()

    # distancia normalizada al ideal
    d = np.zeros((A, C))
    for j in range(C):
        rng = fstar[j] - fminus[j]
        if abs(rng) < 1e-12:
            d[:, j] = 0.0
        else:
            d[:, j] = (fstar[j] - X[:, j]) / rng
    d = np.abs(d)

    S = (w * d).sum(axis=1)
    R = (w * d).max(axis=1)

    def norm(vec):
        lo, hi = vec.min(), vec.max()
        return np.zeros_like(vec) if abs(hi - lo) < 1e-12 else (vec - lo) / (hi - lo)

    Q = v * norm(S) + (1 - v) * norm(R)

    orden = list(np.argsort(Q))                   # menor Q = mejor
    # condiciones de compromiso
    m = A
    C1 = C2 = None
    if A >= 2:
        a1, a2 = orden[0], orden[1]
        C1 = bool((Q[a2] - Q[a1]) >= (1.0 / (m - 1)))         # ventaja aceptable
        best_S = int(np.argmin(S)); best_R = int(np.argmin(R))
        C2 = bool(a1 == best_S or a1 == best_R)                # estabilidad aceptable

    return {
        "A": A, "C": C, "v": float(v),
        "X": X.tolist(),
        "S": S.tolist(), "R": R.tolist(), "Q": Q.tolist(),
        "orden": [int(i) for i in orden],
        "C1_ventaja": C1, "C2_estabilidad": C2,
    }


def ranking(nombres, Q, orden, S, R):
    out = []
    for pos, i in enumerate(orden):
        out.append({"nombre": nombres[i], "Q": float(Q[i]), "S": float(S[i]), "R": float(R[i]), "pos": pos + 1})
    return out
