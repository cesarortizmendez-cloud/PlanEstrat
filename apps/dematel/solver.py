"""DEMATEL — Decision Making Trial and Evaluation Laboratory.

Matemática pura (solo numpy), sin dependencias de Django. Calcula, a partir de una
matriz de influencia directa, la matriz de influencia total y clasifica cada
elemento como causa o efecto según su prominencia (r+c) y su relación (r-c).
"""
import numpy as np


def dematel(A, umbral=None):
    """Analiza una matriz de influencia directa A (n x n, diagonal 0).

    Parámetros
    ----------
    A : lista de listas / array n x n. a_ij = influencia directa de i sobre j
        (escala típica 0..4). La diagonal se ignora (se fuerza a 0).
    umbral : float opcional. Umbral para considerar una relación significativa en
        la matriz total T. Si es None, se usa la media de T.

    Devuelve un dict con las matrices y los indicadores por elemento.
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("La matriz debe ser cuadrada.")
    n = A.shape[0]
    np.fill_diagonal(A, 0.0)
    if np.any(A < 0):
        raise ValueError("Las influencias no pueden ser negativas.")

    # Factor de normalización: máximo entre la mayor suma de filas y de columnas.
    row_max = A.sum(axis=1).max()
    col_max = A.sum(axis=0).max()
    s = max(row_max, col_max)
    if s == 0:
        raise ValueError("La matriz no tiene influencias (todo cero).")
    D = A / s

    # Matriz de influencia total: T = D (I - D)^-1
    I = np.eye(n)
    T = D @ np.linalg.inv(I - D)

    r = T.sum(axis=1)          # suma de filas: influencia ejercida
    c = T.sum(axis=0)          # suma de columnas: influencia recibida
    prominencia = r + c        # importancia total (r + c)
    relacion = r - c           # rol causal (r - c)

    if umbral is None:
        umbral = float(T.mean())

    # Relaciones significativas: t_ij por encima del umbral
    relaciones = []
    for i in range(n):
        for j in range(n):
            if i != j and T[i, j] > umbral:
                relaciones.append({"de": i, "a": j, "valor": float(T[i, j])})

    elementos = []
    for i in range(n):
        elementos.append({
            "i": i,
            "r": float(r[i]),
            "c": float(c[i]),
            "prominencia": float(prominencia[i]),
            "relacion": float(relacion[i]),
            "tipo": "causa" if relacion[i] > 0 else "efecto",
        })

    return {
        "n": n,
        "s": float(s),
        "umbral": float(umbral),
        "T": T.tolist(),
        "D": D.tolist(),
        "elementos": elementos,
        "relaciones": relaciones,
    }


def agregar_promedio(matrices):
    """Agrega las matrices de influencia de varios expertos por promedio simple."""
    A = np.asarray(matrices, dtype=float)
    if A.ndim != 3 or A.shape[1] != A.shape[2]:
        raise ValueError("Se esperaba una lista de matrices cuadradas del mismo tamaño.")
    return A.mean(axis=0).tolist()
