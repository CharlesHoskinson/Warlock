'use strict';
// Project only the committed appearance emitted by the typed Elm renderer.
// There is no storage, draft preview, settings request or effect policy here.
(() => {
  const root = document.documentElement;
  const base = parseFloat(getComputedStyle(root).fontSize);
  let previous = '';
  const project = () => {
    const surface = document.querySelector('.surface-bar[data-theme],.surface-popup[data-theme]');
    if (!surface) return;
    const theme = surface.dataset.theme, scale = Number(surface.dataset.textScale);
    if (!['night','dawn','high-contrast'].includes(theme) || ![100,125,150,200].includes(scale)) return;
    const key = `${theme}:${scale}`;
    if (key === previous) return;
    previous = key;
    root.dataset.theme = theme;
    root.dataset.textScale = String(scale);
    root.style.fontSize = `${base * scale / 100}px`;
  };
  new MutationObserver(project).observe(document.body, {subtree:true,childList:true,attributes:true,attributeFilter:['data-theme','data-text-scale']});
  project();
})();
