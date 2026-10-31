const focusButton = document.querySelector('#focus-loss');
focusButton.addEventListener('click', () => {
 const lost = focusButton.dataset.lost !== 'true';
 focusButton.dataset.lost = String(lost);
 document.querySelectorAll('.wl-specimen-window[data-window-focused]').forEach(window => {
  if (window.querySelector('.surface-popup')) window.dataset.windowFocused = String(!lost);
 });
 focusButton.textContent = lost ? 'Restore focus' : 'Show focus loss';
});
document.querySelector('#effects-off').addEventListener('click', event => {
 const off = document.documentElement.dataset.effects !== 'off';
 document.documentElement.dataset.effects = off ? 'off' : 'on';
 event.currentTarget.textContent = off ? 'Restore effects' : 'Toggle effects off';
});
