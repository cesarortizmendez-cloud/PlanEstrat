{% load static %}/* PlanEstrat · Service Worker (Fase 0)
   Carcasa offline básica. Se versiona con CACHE para invalidar en cada release. */
const CACHE = 'planestrat-v0';
const PRECACHE = [
  '/',
  '{% static "css/planestrat.css" %}',
  '{% static "js/pwa-install.js" %}',
  '{% static "js/estudio-store.js" %}',
  '{% static "icons/icon-192.png" %}',
  '{% url "offline" %}'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  // Navegaciones: red primero, con respaldo en caché y página offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match('{% url "offline" %}')))
    );
    return;
  }

  // Recursos estáticos: caché primero, luego red.
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => cached))
  );
});
