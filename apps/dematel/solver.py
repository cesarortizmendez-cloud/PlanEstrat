"""DEMATEL — Decision Making Trial and Evaluation Laboratory.

Matemática pura (solo numpy), sin dependencias de Django.

Dos usos:
1. `dematel(A)` — clasificación causa/efecto de un conjunto de elementos a partir de
   su matriz de influencia directa (prominencia r+c, relación r-c, matriz total T).
2. `priorizar_proyectos(...)` — método de Quezada, López-Ospina, Ortiz, Oddershede,
   Palominos y Jofré (IJPE, 2022): prioriza PROYECTOS estratégicos por su influencia
   total (directa e indirecta) sobre los objetivos de una perspectiva del BSC
   (típicamente la Financiera), propagada por el mapa estratégico.
"""
import numpy as np


def _total_influence(A):
    """Matriz de influencia total T = D (I - D)^-1 a partir de la directa A."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    row_max = A.sum(axis=1).max()
    col_max = A.sum(axis=0).max()
    s = max(row_max, col_max)
    if s == 0:
        raise ValueError("La matriz no tiene influencias (todo cero).")
    D = A / s
    T = D @ np.linalg.inv(np.eye(n) - D)
    return T, D, float(s)


def dematel(A, umbral=None):
    """Analiza una matriz de influencia directa A (n x n, diagonal 0)."""
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("La matriz debe ser cuadrada.")
    n = A.shape[0]
    np.fill_diagonal(A, 0.0)
    if np.any(A < 0):
        raise ValueError("Las influencias no pueden ser negativas.")

    T, D, s = _total_influence(A)
    r = T.sum(axis=1)
    c = T.sum(axis=0)
    prominencia = r + c
    relacion = r - c
    if umbral is None:
        umbral = float(T.mean())

    relaciones = []
    for i in range(n):
        for j in range(n):
            if i != j and T[i, j] > umbral:
                relaciones.append({"de": i, "a": j, "valor": float(T[i, j])})

    elementos = []
    for i in range(n):
        elementos.append({
            "i": i, "r": float(r[i]), "c": float(c[i]),
            "prominencia": float(prominencia[i]), "relacion": float(relacion[i]),
            "tipo": "causa" if relacion[i] > 0 else "efecto",
        })

    return {"n": n, "s": s, "umbral": float(umbral), "T": T.tolist(), "D": D.tolist(),
            "elementos": elementos, "relaciones": relaciones}


def agregar_promedio(matrices):
    """Agrega las matrices de influencia de varios expertos por promedio simple."""
    A = np.asarray(matrices, dtype=float)
    if A.ndim != 3 or A.shape[1] != A.shape[2]:
        raise ValueError("Se esperaba una lista de matrices cuadradas del mismo tamaño.")
    return A.mean(axis=0).tolist()


def priorizar_proyectos(objetivos, relaciones, proyectos, impacto, meta='F', inten_oo=3.0):
    """Prioriza proyectos por su influencia total sobre una perspectiva del BSC.

    Parámetros
    ----------
    objetivos : lista de dicts {'id', 'persp', 'nombre'} (los objetivos del mapa).
    relaciones : lista de [id_origen, id_destino] objetivo->objetivo (mapa estratégico).
    proyectos : lista de nombres de proyecto.
    impacto : matriz nP x nO (proyecto -> objetivo), escala 0..4.
    meta : perspectiva objetivo ('F' Financiera por defecto).
    inten_oo : intensidad por defecto de cada relación objetivo->objetivo del mapa.

    Construye una red DEMATEL con los objetivos y los proyectos como nodos, calcula la
    influencia total T y ordena los proyectos por la suma de su influencia total sobre
    los objetivos de la perspectiva `meta`.
    """
    ids = [o['id'] for o in objetivos]
    persp = {o['id']: o.get('persp', '') for o in objetivos}
    nombre_obj = {o['id']: o.get('nombre', o['id']) for o in objetivos}
    idx = {o: i for i, o in enumerate(ids)}
    nO = len(ids)
    nP = len(proyectos)
    if nO < 2:
        raise ValueError("Se necesitan al menos 2 objetivos.")
    if nP < 1:
        raise ValueError("Define al menos un proyecto.")
    imp = np.asarray(impacto, dtype=float)
    if imp.shape != (nP, nO):
        raise ValueError("El impacto debe ser una matriz proyectos x objetivos.")
    if np.any(imp < 0):
        raise ValueError("Los impactos no pueden ser negativos.")

    N = nO + nP
    A = np.zeros((N, N))
    for par in relaciones:
        if len(par) == 2 and par[0] in idx and par[1] in idx and par[0] != par[1]:
            A[idx[par[0]], idx[par[1]]] = inten_oo
    for k in range(nP):
        for j in range(nO):
            A[nO + k, j] = imp[k, j]

    T, D, s = _total_influence(A)

    metas = [idx[o] for o in ids if persp.get(o) == meta]
    if not metas:
        # si no hay objetivos de esa perspectiva, usar todos
        metas = list(range(nO))

    filas = []
    for k in range(nP):
        val = float(T[nO + k, metas].sum())
        # contribución a cada objetivo meta (para explicar la cadena)
        contrib = [{"objetivo": ids[m], "nombre": nombre_obj[ids[m]], "valor": float(T[nO + k, m])} for m in metas]
        filas.append({"nombre": proyectos[k], "valor": val, "contribucion": contrib})

    total = sum(f["valor"] for f in filas) or 1.0
    filas.sort(key=lambda f: -f["valor"])
    for f in filas:
        f["pct"] = round(f["valor"] / total * 100, 1)

    # indicadores causa/efecto de los objetivos (solo bloque objetivo->objetivo del mapa)
    Ao = A[:nO, :nO]
    objetivos_dematel = []
    try:
        To, _, _ = _total_influence(Ao)
        ro = To.sum(axis=1); co = To.sum(axis=0)
        for i, oid in enumerate(ids):
            objetivos_dematel.append({
                "id": oid, "persp": persp.get(oid, ''), "nombre": nombre_obj[oid],
                "prominencia": float(ro[i] + co[i]), "relacion": float(ro[i] - co[i]),
                "tipo": "causa" if (ro[i] - co[i]) > 0 else "efecto",
            })
    except Exception:
        objetivos_dematel = []

    return {
        "meta": meta,
        "objetivos_meta": [ids[m] for m in metas],
        "ranking": filas,
        "seleccionado": filas[0]["nombre"] if filas else None,
        "objetivos": objetivos_dematel,
        "nP": nP, "nO": nO,
    }
