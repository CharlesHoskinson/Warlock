/* Gallery playback owns decoration only. It never establishes application state. */
const demo = document.querySelector('.wl-effects-demo');
const effect = demo.querySelector('.wl-effect-portal');
const tier = document.querySelector('#tier');
const status = document.querySelector('#effect-status');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
let timer, active = false, cycle = 0, lastFullStart = -Infinity, expected = '';
function settle(message) {
  clearTimeout(timer);
  active = false;
  effect.removeAttribute('data-portal-phase');
  status.textContent = message;
}
document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click', () => {
  if (active) { status.textContent = 'An effect is already playing'; return; }
  demo.dataset.effectsTier = tier.value;
  if (tier.value === 'off' || motion.matches) { settle('Effects off'); return; }
  const now = performance.now();
  if (tier.value === 'full' && now - lastFullStart < 1000) { settle('Ready'); return; }
  if (tier.value === 'full') lastFullStart = now;
  active = true;
  cycle += 1;
  effect.dataset.effectCycle = String(cycle);
  expected = tier.value === 'reduced' ? 'wl-portal-fade' : `wl-portal-${button.dataset.play}`;
  effect.dataset.portalPhase = button.dataset.play;
  status.textContent = button.dataset.play === 'open' ? 'Opening' : 'Closing';
  const current = cycle;
  timer = setTimeout(() => { if (active && current === cycle) settle('Complete'); }, (tier.value === 'reduced' ? (button.dataset.play === 'open' ? 120 : 90) : (button.dataset.play === 'open' ? 520 : 360)) + 100);
}));
function finish(event, message) {
  if (active && event.target === effect && event.animationName === expected && effect.dataset.effectCycle === String(cycle)) settle(message);
}
effect.addEventListener('animationend', event => finish(event, 'Complete'));
effect.addEventListener('animationcancel', event => finish(event, 'Cancelled'));
tier.addEventListener('change', () => settle('Ready'));
motion.addEventListener('change', () => settle('Cancelled'));
document.addEventListener('visibilitychange', () => { if (document.hidden) settle('Cancelled'); });
