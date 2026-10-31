const focusButton = document.querySelector('#focus-loss');
focusButton.addEventListener('click', () => {
 const lost = focusButton.dataset.lost !== 'true';
 focusButton.dataset.lost = String(lost);
 document.querySelectorAll('#attention-scenes .wl-specimen-window[data-window-focused]').forEach(window => {
  if (window.querySelector('.surface-popup')) window.dataset.windowFocused = String(!lost);
 });
 focusButton.textContent = lost ? 'Restore focus' : 'Show focus loss';
});
/* Effects off applies to the Settings scenes only; the comparison keeps its labelled tiers. */
document.querySelector('#effects-off').addEventListener('click', event => {
 const scenes = document.querySelector('#attention-scenes');
 const off = scenes.dataset.effects !== 'off';
 scenes.dataset.effects = off ? 'off' : 'on';
 event.currentTarget.textContent = off ? 'Restore effects' : 'Toggle effects off';
});
/* The readout names the element that holds document focus, so keyboard focus is observable. */
const readout = document.querySelector('#focus-readout');
const describe = element => {
 const theme = element.closest('[data-theme]:not(html)');
 const name = (element.getAttribute('aria-label') || element.textContent || element.tagName).trim().replace(/\s+/g, ' ');
 return theme && theme.querySelector('h3') ? `${name} (${theme.querySelector('h3').textContent})` : name;
};
document.addEventListener('focusin', event => { readout.textContent = `Keyboard focus: ${describe(event.target)}`; });
document.addEventListener('focusout', event => { if (!event.relatedTarget) readout.textContent = 'Keyboard focus: page'; });
document.querySelector('#focus-start').addEventListener('click', () => {
 document.querySelector('.wl-specimen-compare .wl-specimen-action').focus({ focusVisible: true });
});
