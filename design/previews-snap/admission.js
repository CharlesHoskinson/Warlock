/* Static specimen admission demonstration. Production authority belongs to Elm and the host. */
(() => {
  const popups = [...document.querySelectorAll('.surface-popup[data-mode="picker"]')];
  const slots = ['state', 'title', 'fidelity', 'label', 'detail'];
  const selectors = ['.preview-state', '.preview-title', '.preview-fidelity', '.control-label', '.control-detail'];
  const stateVariants = ['Live preview', 'Historical preview', 'Preview loading', 'Waiting for preview capacity', 'Waiting for preview', 'Preview request expired', 'Preview request changed', 'Preview unavailable'];
  let held = false;
  const pending = new Set();
  function retire(popup) {
    popup.inert = true;
    popup.removeAttribute('data-picker-admitted');
    pending.add(popup);
  }
  function measure(popup) {
    if (held || !pending.has(popup)) return;
    const rows = [...popup.querySelectorAll('button[data-surface-control^="family:"]')];
    if (!rows.length) return;
    const row = rows[0];
    const style = getComputedStyle(row);
    const paddingX = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight) + parseFloat(style.borderLeftWidth) + parseFloat(style.borderRightWidth);
    const paddingY = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom) + parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    const controls = popup.querySelector(".surface-controls");
    const cs = getComputedStyle(controls);
    const ps = getComputedStyle(popup);
    const parentStyle = getComputedStyle(popup.parentElement);
    const available = Math.min(popup.clientWidth, popup.parentElement.clientWidth - parseFloat(parentStyle.paddingLeft) - parseFloat(parentStyle.paddingRight), document.documentElement.clientWidth - 80);
    const inner = available - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight) - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - paddingX;
    if (inner <= 0) return;
    const profile = inner < 300 ? 'stacked' : 'normal';
    const textWidth = profile === 'normal' ? inner - 172 : inner;
    const heights = slots.map(() => 0);
    const probe = document.createElement('div');
    probe.style.cssText = `position:fixed;left:-10000px;top:0;visibility:hidden;pointer-events:none;width:${textWidth}px;`;
    popup.append(probe);
    selectors.forEach((selector, i) => {
      const examples = rows.flatMap(r => [...r.querySelectorAll(selector)]);
      const representative = examples[0];
      const sample = representative ? representative.cloneNode(false) : document.createElement('span');
      if (!representative) sample.className = selector.slice(1);
      sample.removeAttribute('id');
      sample.style.cssText = 'display:block;position:static;box-sizing:border-box;width:100%;height:auto;min-height:0;max-height:none;white-space:normal;overflow:visible;overflow-wrap:anywhere;margin:0;';
      probe.append(sample);
      const candidates = examples.map(e => e.textContent);
      if (i === 0) candidates.push(...stateVariants);
      for (const text of candidates) {
        sample.textContent = text;
        if (text) heights[i] = Math.max(heights[i], Math.ceil(sample.getBoundingClientRect().height));
      }
      sample.remove();
    });
    probe.remove();
    const textHeight = heights.reduce((a, b) => a + b, 0) + 8;
    const normalHeight = Math.min(parseFloat(getComputedStyle(document.documentElement).fontSize) * 7.5 + 16, innerHeight - 30);
    const chosen = profile === 'normal' && Math.max(100, textHeight) + paddingY > normalHeight ? 'expanded' : profile;
    const height = chosen === 'normal' ? normalHeight : Math.ceil((chosen === 'stacked' ? 100 + 2 + textHeight : Math.max(100, textHeight)) + paddingY);
    slots.forEach((name, i) => popup.style.setProperty(`--wl-picker-${name}-slot`, `${heights[i]}px`));
    popup.style.setProperty('--wl-picker-row-height', `${height}px`);
    popup.dataset.pickerProfile = chosen;
    popup.dataset.pickerAdmitted = 'true';
    pending.delete(popup);
    popup.inert = false;
  }
  function refresh(popup) { retire(popup); requestAnimationFrame(() => measure(popup)); }
  document.addEventListener('pointerdown', () => { held = true; }, true);
  for (const event of ['pointerup', 'pointercancel']) document.addEventListener(event, () => { held = false; pending.forEach(measure); }, true);
  const widths = new WeakMap();
  const observer = new ResizeObserver(entries => entries.forEach(({target, contentRect}) => {
    if (widths.get(target) !== contentRect.width) { widths.set(target, contentRect.width); refresh(target); }
  }));
  popups.forEach(popup => {
    const sentinel = document.createElement('span');
    sentinel.textContent = 'Measurement sample';
    sentinel.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none;white-space:nowrap;width:max-content;';
    popup.append(sentinel);
    new ResizeObserver(() => refresh(popup)).observe(sentinel);
    observer.observe(popup); refresh(popup);
  });
  window.addEventListener('resize', () => popups.forEach(refresh));
  document.fonts.ready.then(() => popups.forEach(refresh));
  document.fonts.addEventListener('loading', () => popups.forEach(retire));
  document.fonts.addEventListener('loadingdone', () => popups.forEach(refresh));
})();
