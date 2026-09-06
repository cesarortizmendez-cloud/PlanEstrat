"""Planes de acción · herramientas Lean.

Solvers puros para las herramientas cuantitativas de mejora continua:
Pareto, 5S, SMED y TPM/OEE. (Ishikawa y 5 porqués son estructurales y se
manejan en la interfaz.)
"""
import numpy as np


def pareto(causas, umbral=0.8):
    """causas: lista de {nombre, frecuencia}. Ordena y calcula el % acumulado."""
    items = sorted(causas, key=lambda c: float(c.get("frecuencia", 0)), reverse=True)
    total = sum(float(c.get("frecuencia", 0)) for c in items)
    acum = 0.0
    prev = 0.0
    out = []
    for c in items:
        f = float(c.get("frecuencia", 0))
        acum += f
        pacum = (acum / total) if total > 0 else 0.0
        # vital si el acumulado ANTERIOR aún no llegaba al umbral (corte inclusivo)
        vital = bool(prev < umbral - 1e-9)
        out.append({
            "nombre": c.get("nombre", ""),
            "frecuencia": f,
            "porcentaje": (f / total) if total > 0 else 0.0,
            "acumulado": pacum,
            "vital": vital,
        })
        prev = pacum
    n_vitales = sum(1 for o in out if o["vital"])
    return {"items": out, "total": total, "n_vitales": n_vitales, "umbral": umbral}


def cinco_s(scores):
    """scores: dict o lista con las 5 fases (0..100). Devuelve promedio y detalle."""
    fases = ["Seiri (clasificar)", "Seiton (ordenar)", "Seiso (limpiar)",
             "Seiketsu (estandarizar)", "Shitsuke (disciplina)"]
    vals = [float(s) for s in scores][:5]
    while len(vals) < 5:
        vals.append(0.0)
    prom = float(np.mean(vals))
    detalle = [{"fase": fases[i], "score": vals[i],
                "bajo": bool(vals[i] < 60)} for i in range(5)]
    return {"detalle": detalle, "promedio": prom,
            "n_bajos": sum(1 for d in detalle if d["bajo"])}


def smed(actividades):
    """actividades: lista de {nombre, tipo('interno'|'externo'), convertible(bool), tiempo}.
    Tiempo de cambio = suma de actividades internas (máquina detenida)."""
    t_int_antes = sum(float(a["tiempo"]) for a in actividades if a.get("tipo") == "interno")
    t_ext = sum(float(a["tiempo"]) for a in actividades if a.get("tipo") == "externo")
    # después: las internas convertibles pasan a externas
    t_int_despues = sum(float(a["tiempo"]) for a in actividades
                        if a.get("tipo") == "interno" and not a.get("convertible"))
    reduccion = ((t_int_antes - t_int_despues) / t_int_antes) if t_int_antes > 0 else 0.0
    return {
        "tiempo_cambio_antes": t_int_antes,
        "tiempo_cambio_despues": t_int_despues,
        "tiempo_externo": t_ext,
        "reduccion": reduccion,
    }


def oee(tiempo_planificado, paradas, tiempo_ciclo_ideal, piezas_producidas, piezas_buenas):
    """Eficiencia global del equipo (OEE) = Disponibilidad × Rendimiento × Calidad."""
    tp = float(tiempo_planificado)
    top = tp - float(paradas)
    disp = (top / tp) if tp > 0 else 0.0
    rend = ((float(tiempo_ciclo_ideal) * float(piezas_producidas)) / top) if top > 0 else 0.0
    cal = (float(piezas_buenas) / float(piezas_producidas)) if piezas_producidas > 0 else 0.0
    disp = min(max(disp, 0.0), 1.0)
    rend = min(max(rend, 0.0), 1.0)
    cal = min(max(cal, 0.0), 1.0)
    return {
        "disponibilidad": disp, "rendimiento": rend, "calidad": cal,
        "oee": disp * rend * cal, "tiempo_operativo": top,
    }
