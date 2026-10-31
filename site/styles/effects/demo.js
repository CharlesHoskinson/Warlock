import { watchEffectCompletion } from '../../assets/shared/effect-completion.js';
const stage = document.querySelector('.t02-portal-stage');
const plane = stage.querySelector('.wl-effect-portal');
const tier = document.querySelector('#tier');
const status = document.querySelector('#effect-status');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const forced = matchMedia('(forced-colors: active)');
let cancel = null, cycle = 0, lastFull = -Infinity, lastPhase = 'opening';
function settle() {
 if (cancel) { const stop = cancel; cancel = null; stop(); }
 delete plane.dataset.portalPhase;
}
function play(phase) {
 settle(); lastPhase = phase;
 const selected = tier.value;
 const suppressed = motion.matches || forced.matches || document.documentElement.dataset.theme === 'high-contrast' || document.hidden;
 stage.dataset.effectsTier = suppressed ? 'off' : selected;
 if (suppressed || selected === 'off') { status.textContent = 'Effects are off. The example is settled.'; return; }
 const now = performance.now();
 if (selected === 'full' && now - lastFull < 1000) { status.textContent = 'The example is settled. Full effects are limited to one start per second.'; return; }
 if (selected === 'full') lastFull = now;
 const duration = selected === 'full' ? (phase === 'opening' ? 520 : 360) : (phase === 'opening' ? 120 : 90);
 const name = selected === 'full' ? (phase === 'opening' ? 'wl-portal-open' : 'wl-portal-close') : 'wl-portal-fade';
 cycle += 1; plane.dataset.effectCycle = String(cycle);
 // Restart the decorative animation after retiring the prior cycle.
 void plane.offsetWidth;
 plane.dataset.portalPhase = phase === 'opening' ? 'open' : 'close';
 status.textContent = `${phase === 'opening' ? 'Opening' : 'Closing'} effect playing for ${duration} milliseconds.`;
 cancel = watchEffectCompletion({target: plane, animationName: name, cycle, duration, onComplete: () => { delete plane.dataset.portalPhase; cancel = null; status.textContent = 'Effect settled.'; }});
}
document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click', () => play(button.dataset.play)));
document.querySelector('[data-replay]').addEventListener('click', () => play(lastPhase));
tier.addEventListener('change', settle);
motion.addEventListener('change', settle); forced.addEventListener('change', settle);
document.addEventListener('visibilitychange', () => { if (document.hidden) settle(); });
new MutationObserver(settle).observe(document.documentElement, {attributes:true, attributeFilter:['data-theme']});
