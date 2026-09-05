/* PlanEstrat · Instalación PWA
   Muestra el botón "Instalar en mi equipo" cuando el navegador lo permite
   (Android/Windows/Chrome/Edge) y una guía especial en iPhone/iPad. */
(function () {
  'use strict';

  var deferredPrompt = null;
  var btn = document.getElementById('pwaInstallBtn');
  var iosHint = document.getElementById('pwaIosHint');
  var iosClose = document.getElementById('pwaIosClose');

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }
  function isIos() {
    return /iphone|ipad|ipod/i.test(window.navigator.userAgent) && !window.MSStream;
  }

  // Navegadores compatibles: capturamos el evento y mostramos el botón.
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (btn) btn.hidden = false;
  });

  if (btn) {
    btn.addEventListener('click', function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      deferredPrompt.userChoice.finally(function () {
        deferredPrompt = null;
        btn.hidden = true;
      });
    });
  }

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    if (btn) btn.hidden = true;
  });

  // iOS/iPadOS: no hay beforeinstallprompt; mostramos la guía si no está instalada.
  if (iosHint && isIos() && !isStandalone()) {
    var dismissed = false;
    try { dismissed = localStorage.getItem('pe_ios_hint') === '1'; } catch (e) {}
    if (!dismissed) iosHint.hidden = false;
    if (iosClose) {
      iosClose.addEventListener('click', function () {
        iosHint.hidden = true;
        try { localStorage.setItem('pe_ios_hint', '1'); } catch (e) {}
      });
    }
  }
})();
