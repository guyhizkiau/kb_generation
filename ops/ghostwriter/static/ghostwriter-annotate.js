/**
 * Ghostwriter annotation widget — Recogito (text) + Annotorious (images).
 * Loaded by article preview HTML; reads config from window.__GHOSTWRITER__.
 */
(function () {
  var scriptEl = document.currentScript
    || document.querySelector('script[src*="ghostwriter-annotate.js"]');
  var SLUG = (scriptEl && scriptEl.getAttribute('data-slug'))
    || (document.querySelector('main') && document.querySelector('main').getAttribute('data-slug'))
    || '';

  var CFG = window.__GHOSTWRITER__ || {};
  var API_BASE = CFG.apiBase || '';
  var N8N_WEBHOOK = CFG.n8nWebhook || '';

  function apiUrl(path) {
    return API_BASE + path;
  }

  function notifyParent() {
    try {
      window.parent.postMessage(
        { type: 'ghostwriter:annotation-created', slug: SLUG },
        '*',
      );
    } catch (e) { /* ignore */ }
  }

  function loadPriorAnnotations(recogito) {
    if (!SLUG) return;
    fetch(apiUrl('/api/feedback?slug=' + encodeURIComponent(SLUG)))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        (d.annotations || []).forEach(function (a) {
          try { recogito.addAnnotation(a); } catch (e) { /* ignore */ }
        });
      })
      .catch(function () { /* ignore */ });
  }

  function postAnnotation(annotation) {
    if (!SLUG) return;
    var name = localStorage.getItem('gw_reviewer_name') || '';
    if (!name) {
      name = prompt('Your name (for annotation attribution):') || 'anonymous';
      localStorage.setItem('gw_reviewer_name', name);
    }
    var payload = Object.assign({}, annotation, {
      slug: SLUG,
      creator: { name: name },
      'dc:creator': name,
    });

    fetch(apiUrl('/api/feedback'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (r) {
        if (r.ok) notifyParent();
      })
      .catch(function () { /* ignore */ });

    if (N8N_WEBHOOK) {
      fetch(N8N_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).catch(function () { /* ignore */ });
    }
  }

  window.addEventListener('DOMContentLoaded', function () {
    var contentEl = document.querySelector('main');
    if (contentEl && window.Recogito) {
      var r = Recogito.init({ content: contentEl, readOnly: false });
      r.on('createAnnotation', postAnnotation);
      loadPriorAnnotations(r);
    }
    document.querySelectorAll('main img').forEach(function (img) {
      if (window.Annotorious) {
        var anno = Annotorious.init({ image: img });
        anno.on('createAnnotation', postAnnotation);
      }
    });
  });
})();
