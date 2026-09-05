# 🎯 PlanEstrat — Fase 0 (esqueleto)

**Plataforma de planificación estratégica con decisión multicriterio colaborativa**

Desarrollado por **Dr. César Ortiz Méndez** · 🔗 [cv-cesarortiz.vercel.app](https://cv-cesarortiz.vercel.app)

Software hermano de **IO-Lab Pro** y **Pronostat**: misma arquitectura (Django + apps
independientes + cálculo *stateless* + WhiteNoise + Vercel + PWA), ahora orientada a la
**planificación estratégica** y con una capa diferenciadora de **decisión colaborativa**.

---

## ¿Qué es PlanEstrat?

Un sistema que acompaña el ciclo completo de gestión estratégica —diagnóstico, mapa
estratégico (BSC), laboratorio multicriterio (AHP, ANP, DEMATEL, difuso), optimización,
cartera de proyectos, conciencia situacional y **planes de acción Lean**— y que permite
que las decisiones multicriterio se construyan **entre varios expertos**: el facilitador
crea una decisión con nombre y clave, y cada participante entrega su evaluación.

Esta **Fase 0** entrega el esqueleto desplegable: estructura, sistema de diseño,
navegación, portada con el roadmap y **PWA instalable**. Los módulos se agregan por fases.

## 🏗️ Arquitectura (idéntica a IO-Lab Pro / Pronostat)

```
planestrat/
├── planestrat/            # Configuración Django
│   ├── settings.py        # apps, WhiteNoise, dj-database-url (SQLite→Postgres)
│   ├── urls.py            # enrutador raíz + rutas PWA
│   ├── wsgi.py            # callable `app` para Vercel
│   └── asgi.py
├── apps/
│   └── home/              # Catálogo / portada (stateless)
├── templates/
│   ├── base.html          # sidebar + topbar + footer + botón PWA
│   ├── home/index.html
│   └── pwa/               # manifest.json · service-worker.js · offline.html
├── static/
│   ├── css/planestrat.css # Sistema de diseño
│   ├── js/pwa-install.js  # Botón "Instalar en mi equipo"
│   ├── js/estudio-store.js# Store del estudio individual (cliente)
│   └── icons/             # icon-192.png · icon-512.png
├── requirements.txt
├── manage.py
├── build_files.sh
└── vercel.json
```

### Patrón de cada módulo (tres capas, a partir de la Fase 1)

1. **`solver.py`** — matemática pura (numpy/scipy), testeable en aislamiento.
2. **`views.py`** — `index` (renderiza el template) + `solve_api` (JSON→JSON).
3. **`templates/<app>/index.html`** — teoría + formulario + resultados + Chart.js.

> **Nota de tamaño (heredada de Pronostat):** sin `statsmodels`. La optimización usa
> `scipy.optimize.linprog` y los métodos se implementan a mano, para no exceder el
> límite de tamaño de las funciones serverless de Vercel (free tier).

## 🚀 Instalación local

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # Windows: copy .env.example .env
python manage.py runserver
```

Abre **http://127.0.0.1:8000**. En la Fase 0 no hay modelos, así que **no** necesitas
`migrate` (usa SQLite solo si algo lo requiere). La app `decisiones` (Fase 3) sí traerá
modelos y migraciones.

## ☁️ Despliegue en Vercel (gratuito)

1. Sube el proyecto a GitHub.
2. Vercel → **Add New Project** → selecciona el repo. Detecta `vercel.json`.
3. En **Environment Variables** define: `SECRET_KEY`, `DEBUG=False`,
   `ALLOWED_HOSTS=tu-proyecto.vercel.app`, `CSRF_TRUSTED_ORIGINS=https://*.vercel.app`.
   (Desde la Fase 3, además `DATABASE_URL` con el Postgres gratuito de Neon/Supabase,
   usando la **cadena pooled**.)
4. **Deploy**. En 1–2 minutos queda en línea.

Rutas PWA para verificar tras el deploy: `/manifest.json`, `/service-worker.js`,
`/static/icons/icon-192.png`, `/static/js/pwa-install.js`.

## 📲 Instalación como app (PWA)

El botón flotante **“Instalar en mi equipo”** aparece en Android/Windows cuando el
navegador detecta que se cumplen las condiciones PWA. En iPhone/iPad se muestra la guía:
Safari → Compartir → Agregar a pantalla de inicio.

## 🔭 Roadmap de construcción

- **Fase 0 — Esqueleto** *(esta entrega)*: estructura, diseño, navegación, PWA, deploy.
- **Fase 1 — AHP** como plantilla de método (solver + API + template + Chart.js).
- **Fase 2 — Laboratorio**: DEMATEL, ANP, difuso, optimización (linprog), cartera.
- **Fase 3 — Decisiones colaborativas ★**: app `decisiones` + Postgres gratuito.
- **Fase 4 — Estrategia y ejecución**: formulación, BSC, situacional, planes (Lean).
- **Fase 5 — Exportación y PWA avanzada**: Excel (openpyxl) por módulo.

## 📄 Autoría

Plataforma desarrollada por el **Dr. César Ortiz Méndez**. Uso educativo.
🔗 [cv-cesarortiz.vercel.app](https://cv-cesarortiz.vercel.app)

---

*PlanEstrat v0 — construido con Django, JavaScript vanilla y despliegue serverless en Vercel.*
