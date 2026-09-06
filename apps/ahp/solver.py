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


def media_geometrica(matrices):
    """Media geométrica elemento a elemento de K matrices del mismo tamaño.

    Sirve para agregar en grupo tanto las matrices de criterios (AHP) como las de
    desempeño (alternativas x criterios). Requiere valores positivos.
    """
    A = np.asarray(matrices, dtype=float)
    if A.ndim < 3:
        return A.tolist() if A.ndim == 2 else A.tolist()
    return np.exp(np.mean(np.log(A), axis=0)).tolist()


def media_aritmetica(matrices):
    """Media aritmética elemento a elemento (admite ceros; para influencias ANP)."""
    A = np.asarray(matrices, dtype=float)
    if A.ndim < 3:
        return A.tolist()
    return np.mean(A, axis=0).tolist()


def ranking(nombres, pesos):
    """Empareja nombres con pesos y los ordena de mayor a menor prioridad."""
    pares = list(zip(nombres, pesos))
    pares.sort(key=lambda p: p[1], reverse=True)
    return [{"nombre": n, "peso": float(w)} for n, w in pares]


def decidir_ahp(criterios_matriz, nombres_criterios, alternativas, desempeno):
    """AHP completo de decisión: elige la mejor alternativa.

    - criterios_matriz: matriz n_crit x n_crit de comparación por pares de los criterios.
    - nombres_criterios: lista de n_crit nombres.
    - alternativas: lista de m nombres de alternativas.
    - desempeno: matriz m x n_crit con la valoración (1..9) de cuán bien cada
      alternativa SATISFACE cada criterio (mayor = mejor). Cada columna se normaliza
      para obtener las prioridades locales por criterio.

    Devuelve los pesos de criterios (con su consistencia), la matriz de prioridades
    locales, el puntaje global de cada alternativa, el ranking y la seleccionada.
    """
    base = prioridades_ahp(criterios_matriz)
    w = np.asarray(base["pesos"], dtype=float)
    n_crit = w.shape[0]

    if not alternativas:
        raise ValueError("Define al menos una alternativa.")
    D = np.asarray(desempeno, dtype=float)
    if D.ndim != 2:
        raise ValueError("El desempeño debe ser una matriz alternativas x criterios.")
    m, c = D.shape
    if c != n_crit:
        raise ValueError("El desempeño debe tener una columna por criterio.")
    if m != len(alternativas):
        raise ValueError("Cada fila del desempeño es una alternativa.")
    if np.any(D <= 0):
        raise ValueError("Las valoraciones deben ser positivas (escala 1 a 9).")

    # Prioridades locales por criterio: normalizar cada columna a suma 1.
    col = D.sum(axis=0)
    L = D / col  # m x n_crit
    # Puntaje global de cada alternativa (suma ponderada). Suma total = 1.
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
            "lambda_max": base["lambda_max"],
            "CI": base["CI"],
            "RI": base["RI"],
            "CR": base["CR"],
            "n": base["n"],
            "consistente": base["consistente"],
        },
        "alternativas": list(alternativas),
        "local": L.tolist(),
        "scores": scores.tolist(),
        "ranking": rank,
        "seleccionado": rank[0]["nombre"],
        "margen": margen,
    }
