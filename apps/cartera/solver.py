"""Cartera de proyectos — índice estratégico.

Prioriza proyectos (planes de acción) según su contribución a los objetivos
estratégicos, no solo por costo o rentabilidad:

    IE_i = sum_j  w_j * t_ij

donde t_ij es el impacto del proyecto i sobre el objetivo j y w_j la importancia
del objetivo j (por ejemplo, obtenida de AHP/ANP/DEMATEL).
"""
import numpy as np


def indice_estrategico(pesos, impactos):
    """Calcula el índice estratégico de cada proyecto.

    pesos    : lista de w_j (uno por objetivo). Se normaliza a suma 1.
    impactos : matriz P x m (proyectos x objetivos) con t_ij.
    """
    w = np.asarray(pesos, dtype=float)
    T = np.asarray(impactos, dtype=float)
    if T.ndim != 2:
        raise ValueError("Los impactos deben ser una matriz proyectos x objetivos.")
    if T.shape[1] != w.shape[0]:
        raise ValueError("El nº de objetivos no coincide entre pesos e impactos.")
    if w.sum() <= 0:
        raise ValueError("Los pesos deben sumar un valor positivo.")

    w = w / w.sum()                 # pesos normalizados
    IE = T @ w                      # índice estratégico por proyecto
    contrib = T * w                 # contribución de cada objetivo (P x m)

    total = IE.sum()
    IE_rel = (IE / total) if total > 0 else IE

    return {
        "pesos_norm": w.tolist(),
        "IE": IE.tolist(),
        "IE_relativo": IE_rel.tolist(),
        "contribucion": contrib.tolist(),
    }


def ranking(nombres, IE, IE_rel):
    idx = sorted(range(len(nombres)), key=lambda i: IE[i], reverse=True)
    return [{"nombre": nombres[i], "IE": float(IE[i]), "IE_rel": float(IE_rel[i])} for i in idx]
