"""AHP — Proceso Analítico Jerárquico (Saaty).

Matemática pura (solo numpy), sin dependencias de Django: testeable en aislamiento
y reutilizable. Este es el patrón de solver que se replica en cada método.
"""
import numpy as np

# Índice de consistencia aleatorio (Saaty) por tamaño de matriz.
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
      7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def prioridades_ahp(M):
    """Vector de prioridad, lambda_max, CI y CR de una matriz de comparación por pares.

    M: matriz n x n recíproca y positiva (lista de listas o array).
    Método del vector propio aproximado por media geométrica de filas.
    """
    M = np.asarray(M, dtype=float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("La matriz debe ser cuadrada.")
    n = M.shape[0]
    if np.any(M <= 0):
        raise ValueError("Todos los valores deben ser positivos.")

    # Prioridades: media geométrica por fila, normalizada.
    w = np.prod(M, axis=1) ** (1.0 / n)
    w = w / w.sum()

    # lambda_max = promedio de (M w)_i / w_i
    Aw = M @ w
    lambda_max = float(np.mean(Aw / w))

    CI = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = RI.get(n, 1.49)
    CR = (CI / ri) if ri > 0 else 0.0

    return {
        "pesos": w.tolist(),
        "lambda_max": lambda_max,
        "CI": CI,
        "RI": ri,
        "CR": CR,
        "n": n,
        "consistente": bool(CR <= 0.10),
    }


def agregar_geometrica(matrices):
    """Agrega las matrices de varios expertos por media geométrica elemento a elemento.

    matrices: lista de K matrices n x n. Devuelve una matriz n x n (lista de listas).
    Es la base de la agregación de juicios de grupo (AHP con múltiples expertos).
    """
    A = np.asarray(matrices, dtype=float)
    if A.ndim != 3 or A.shape[1] != A.shape[2]:
        raise ValueError("Se esperaba una lista de matrices cuadradas del mismo tamaño.")
    G = np.exp(np.mean(np.log(A), axis=0))
    return G.tolist()


def ranking(nombres, pesos):
    """Empareja nombres con pesos y los ordena de mayor a menor prioridad."""
    pares = list(zip(nombres, pesos))
    pares.sort(key=lambda p: p[1], reverse=True)
    return [{"nombre": n, "peso": float(w)} for n, w in pares]
