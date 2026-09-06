"""Conciencia situacional — indicadores con los tres niveles: percepción,
comprensión y proyección.

- Percepción  (¿qué ocurre?): estado semáforo de cada indicador vs su meta.
- Comprensión (¿por qué?):   tendencia a partir de la serie histórica.
- Proyección  (¿qué puede pasar?): extrapolación lineal y riesgo de no alcanzar la meta.
"""
import numpy as np


def _tendencia(serie, direccion):
    """Pendiente de la serie y si mejora respecto de la dirección deseada."""
    y = np.asarray(serie, dtype=float)
    if y.size < 2:
        return None
    x = np.arange(y.size)
    slope = float(np.polyfit(x, y, 1)[0])
    proyeccion = float(y[-1] + slope)
    if abs(slope) < 1e-9:
        estado = "estable"
    else:
        mejora = (slope > 0) == (direccion == "mayor")
        estado = "mejora" if mejora else "empeora"
    return {"slope": slope, "estado": estado, "proyeccion": proyeccion}


def evaluar(indicadores, umbral_verde=0.9, umbral_amarillo=0.7):
    res = []
    for ind in indicadores:
        nombre = ind.get("nombre", "")
        valor = float(ind.get("valor", 0))
        meta = float(ind.get("meta", 0))
        direccion = ind.get("direccion", "mayor")  # 'mayor' = más es mejor
        serie = ind.get("serie") or []

        if meta == 0:
            cumpl = 0.0
        elif direccion == "mayor":
            cumpl = valor / meta
        else:  # menor es mejor
            cumpl = (meta / valor) if valor != 0 else 2.0
        cumpl = max(0.0, cumpl)

        if cumpl >= umbral_verde:
            semaforo = "verde"
        elif cumpl >= umbral_amarillo:
            semaforo = "amarillo"
        else:
            semaforo = "rojo"

        tend = _tendencia(serie, direccion)
        alcanza = None
        if tend is not None:
            p = tend["proyeccion"]
            alcanza = bool(p >= meta) if direccion == "mayor" else bool(p <= meta)

        res.append({
            "nombre": nombre, "valor": valor, "meta": meta, "direccion": direccion,
            "cumplimiento": round(cumpl, 4), "semaforo": semaforo,
            "tendencia": tend, "alcanza_meta_proyeccion": alcanza,
        })

    resumen = {
        "n": len(res),
        "verde": sum(1 for r in res if r["semaforo"] == "verde"),
        "amarillo": sum(1 for r in res if r["semaforo"] == "amarillo"),
        "rojo": sum(1 for r in res if r["semaforo"] == "rojo"),
        "en_riesgo": sum(1 for r in res if r["alcanza_meta_proyeccion"] is False),
    }
    return {"indicadores": res, "resumen": resumen}
