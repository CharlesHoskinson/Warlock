const root = document.documentElement;
const toggle = document.querySelector('[data-theme-toggle]');
const key = 'warlock-doc-theme-v1';
let saved;
try { saved = localStorage.getItem(key); } catch { /* storage is optional */ }
if (saved === 'night' || saved === 'dawn' || saved === 'high-contrast') root.dataset.theme = saved;
function labelTheme() {
 if (!toggle) return;
 const next = root.dataset.theme === 'dawn' ? 'dark' : 'light';
 toggle.textContent = `${next === 'dark' ? 'Dark' : 'Light'} theme`;
 toggle.setAttribute('aria-label', `Use ${next} theme`);
}
labelTheme();
toggle?.addEventListener('click', () => {
 root.dataset.theme = root.dataset.theme === 'dawn' ? 'night' : 'dawn';
 try { localStorage.setItem(key, root.dataset.theme); } catch { /* theme remains usable */ }
 labelTheme();
});
const navButton = document.querySelector('[data-nav-toggle]');
const nav = document.getElementById('site-nav');
if (navButton && nav) {
 const narrow = matchMedia('(max-width: 799px)');
 const update = () => { navButton.hidden = !narrow.matches; nav.hidden = narrow.matches && navButton.getAttribute('aria-expanded') !== 'true'; };
 navButton.addEventListener('click', () => { navButton.setAttribute('aria-expanded', String(navButton.getAttribute('aria-expanded') !== 'true')); update(); });
 narrow.addEventListener('change', update); update();
}
const search = document.querySelector('body[data-page=search] input[data-search]');
if (search && document.querySelector('[data-search-results]') && document.querySelector('[data-search-status]')) {
 const list = document.querySelector('[data-search-results]');
 const status = document.querySelector('[data-search-status]');
 fetch(`${document.body.dataset.root}assets/shared/routes.json`).then(r => { if (!r.ok) throw Error('registry'); return r.json(); }).then(data => {
  const routes = data.routes;
  function render() {
   const q = search.value.trim().toLocaleLowerCase();
   list.replaceChildren();
   if (!q) { status.textContent = 'Enter a word to search the guide.'; return; }
   const matches = routes.filter(route => `${route.title} ${route.section} ${(route.keywords || []).join(' ')}`.toLocaleLowerCase().includes(q));
   status.textContent = matches.length ? `${matches.length} results` : 'No results. Try another word or browse the sections below.';
   for (const section of [...new Set(matches.map(x => x.section))]) {
    const heading = document.createElement('h3'); heading.textContent = section; list.append(heading);
    const ul = document.createElement('ul');
    for (const route of matches.filter(x => x.section === section)) { const li = document.createElement('li'); const a = document.createElement('a'); a.href = document.body.dataset.root + route.path; a.textContent = route.title; li.append(a); ul.append(li); }
    list.append(ul);
   }
  }
  search.addEventListener('input', render); render();
 }).catch(() => { status.textContent = 'Search is unavailable here. Browse the complete section links below.'; });
}
