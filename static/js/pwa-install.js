/* PlanEstrat · Instalación PWA (tarjeta, misma lógica que IO-Lab)
   Android/Windows: abre la ventana nativa cuando está disponible.
   iPhone/iPad: muestra instrucciones para agregar a pantalla de inicio. */
(function () {
  const card = document.getElementById('pwa-install-card');
  const button = document.getElementById('pwa-install-btn');
  const close = document.getElementById('pwa-install-close');
  const text = document.getElementById('pwa-install-text');
  const iosHelp = document.getElementById('pwa-ios-help');
  if (!card || !button) return;

  let deferredPrompt = null;
  const DISMISS_KEY = 'planestrat_install_dismissed_until';
  const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

  function isDismissed() {
    try { const u = Number(localStorage.getItem(DISMISS_KEY) || 0); return u && u > Date.now(); }
    catch (e) { return false; }
  }
  function showCard(mode) {
    if (isStandalone || isDismissed()) return;
    card.hidden = false;
    if (mode === 'ios') {
      button.hidden = true;
      if (iosHelp) iosHelp.hidden = false;
      if (text) text.textContent = 'En iPhone o iPad la instalación se hace desde Safari con \u201cAgregar a pantalla de inicio\u201d.';
      return;
    }
    button.hidden = false;
    if (iosHelp) iosHelp.hidden = true;
    if (text) text.textContent = 'Presiona el botón y confirma la instalación para usar PlanEstrat como una app en tu equipo.';
  }
  function hideCard(days) {
    card.hidden = true;
    if (days) { try { localStorage.setItem(DISMISS_KEY, String(Date.now() + days * 24 * 60 * 60 * 1000)); } catch (e) {} }
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/service-worker.js', { scope: '/' }).catch(function () {});
    });
  }
  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault(); deferredPrompt = event; showCard('prompt');
  });
  button.addEventListener('click', async function () {
    if (!deferredPrompt) { showCard(isIOS ? 'ios' : 'prompt'); return; }
    deferredPrompt.prompt();
    try { const c = await deferredPrompt.userChoice; hideCard(c && c.outcome === 'accepted' ? 365 : 7); }
    finally { deferredPrompt = null; }
  });
  if (close) close.addEventListener('click', function () { hideCard(14); });
  window.addEventListener('appinstalled', function () { hideCard(365); });
  window.addEventListener('load', function () {
    if (isIOS && !isStandalone && !isDismissed()) setTimeout(function () { showCard('ios'); }, 900);
  });
})();
