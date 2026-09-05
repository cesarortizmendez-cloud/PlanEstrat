/* PlanEstrat · Store del estudio (trabajo individual, en el navegador)
   -----------------------------------------------------------------
   Mantiene el "estudio" del usuario mientras trabaja de forma individual
   (arquitectura stateless heredada de Pronostat: los datos viven en el cliente).
   El trabajo COLABORATIVO no usa esto: se persiste en el servidor (app decisiones).

   API mínima (se ampliará por módulo en fases siguientes):
     EstudioStore.get(clave)         -> valor | null
     EstudioStore.set(clave, valor)  -> guarda (y persiste en localStorage)
     EstudioStore.all()              -> objeto completo
     EstudioStore.exportJSON()       -> string JSON descargable
     EstudioStore.importJSON(texto)  -> carga desde JSON
     EstudioStore.clear()            -> limpia el estudio
*/
window.EstudioStore = (function () {
  'use strict';
  var KEY = 'planestrat_estudio_v0';
  var data = {};

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
  }
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      data = raw ? JSON.parse(raw) : {};
    } catch (e) { data = {}; }
  }

  load();

  return {
    get: function (k) { return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null; },
    set: function (k, v) { data[k] = v; persist(); return v; },
    all: function () { return JSON.parse(JSON.stringify(data)); },
    exportJSON: function () { return JSON.stringify(data, null, 2); },
    importJSON: function (texto) {
      try { data = JSON.parse(texto) || {}; persist(); return true; }
      catch (e) { return false; }
    },
    clear: function () { data = {}; persist(); }
  };
})();
