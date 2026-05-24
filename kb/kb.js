/**
 * kb.js — client-side search for the SpecterX Help Center.
 * Fetches articles.json, attaches to all search inputs on the page,
 * and shows a dropdown of up to 8 matching articles.
 */
(function () {
  'use strict';

  // Resolve the path to articles.json relative to this script's location
  // The script lives at /kb/kb.js, so articles.json is sibling.
  const ARTICLES_URL = (function () {
    const scripts = document.querySelectorAll('script[src]');
    for (const s of scripts) {
      if (s.src.includes('kb.js')) {
        return s.src.replace('kb.js', 'articles.json');
      }
    }
    // fallback — assume we are at root
    return 'kb/articles.json';
  })();

  const CAT_TITLES = {};
  let articles = [];
  let loaded = false;

  function load() {
    if (loaded) return Promise.resolve();
    return fetch(ARTICLES_URL)
      .then(r => r.json())
      .then(data => {
        articles = data.articles || [];
        (data.categories || []).forEach(c => { CAT_TITLES[c.slug] = c.title; });
        loaded = true;
      })
      .catch(() => { articles = []; loaded = true; });
  }

  function search(query) {
    if (!query || query.trim().length < 2) return [];
    const q = query.trim().toLowerCase();
    const results = [];
    for (const a of articles) {
      const score =
        (a.title.toLowerCase().includes(q) ? 2 : 0) +
        (a.intro.toLowerCase().includes(q) ? 1 : 0);
      if (score > 0) results.push({ score, article: a });
    }
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, 8).map(r => r.article);
  }

  function artUrl(slug, dropdown) {
    // Determine correct relative path based on where the dropdown lives
    const isHome = !window.location.pathname.includes('/categories/') &&
                   !window.location.pathname.includes('/articles/');
    const isCategory = window.location.pathname.includes('/categories/');
    const isArticle  = window.location.pathname.includes('/articles/');

    if (isHome)     return `articles/${slug}.html`;
    if (isCategory) return `../articles/${slug}.html`;
    return `${slug}.html`;
  }

  function renderDropdown(dropdown, results, query) {
    if (!query || query.trim().length < 2 || results.length === 0) {
      dropdown.innerHTML = results.length === 0 && query.trim().length >= 2
        ? '<div class="kb-search-empty">No results for "' + escapeHtml(query) + '"</div>'
        : '';
      dropdown.classList.toggle('is-open', query.trim().length >= 2 && results.length === 0);
      return;
    }
    dropdown.innerHTML = results.map(a => {
      const url = artUrl(a.slug, dropdown);
      const catTitle = CAT_TITLES[a.category] || a.category;
      return `<a href="${url}" class="kb-search-result">
  <span class="kb-search-result-icon">📄</span>
  <div>
    <div class="kb-search-result-title">${highlight(escapeHtml(a.title), query)}</div>
    <div class="kb-search-result-cat">${escapeHtml(catTitle)}</div>
  </div>
</a>`;
    }).join('');
    dropdown.classList.add('is-open');
  }

  function highlight(html, query) {
    const q = escapeRegex(query.trim());
    return html.replace(new RegExp(`(${q})`, 'gi'), '<strong>$1</strong>');
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function attachToInput(input, dropdown) {
    let debounce;
    input.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        const q = input.value;
        load().then(() => renderDropdown(dropdown, search(q), q));
      }, 150);
    });

    input.addEventListener('keydown', e => {
      if (e.key === 'Escape') { dropdown.classList.remove('is-open'); input.blur(); }
    });

    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('is-open');
      }
    });
  }

  function init() {
    // Top bar
    const topInput = document.getElementById('kb-search-input');
    const topDrop  = document.getElementById('kb-search-dropdown');
    if (topInput && topDrop) attachToInput(topInput, topDrop);

    // Hero (home page only)
    const heroInput = document.getElementById('kb-hero-search-input');
    const heroDrop  = document.getElementById('kb-hero-search-dropdown');
    if (heroInput && heroDrop) attachToInput(heroInput, heroDrop);

    // Preload
    load();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
