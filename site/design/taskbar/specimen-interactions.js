/* Apache-2.0. Specimen interaction only; Elm owns production disclosure state. */
(() => {
  const reveal = (control) => {
    const port = control.closest('.surface-actions');
    if (!port) return;
    const box = port.getBoundingClientRect();
    const item = control.getBoundingClientRect();
    const left = box.left + port.clientLeft + 6;
    const right = box.left + port.clientLeft + port.clientWidth - 6;
    if (item.left < left) port.scrollLeft += item.left - left;
    else if (item.right > right) port.scrollLeft += item.right - right;
  };
  document.addEventListener('focusin', event => {
    const item = event.target.closest('.surface-actions > button');
    if (item) reveal(item);
  });
  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-specimen-disclosure]');
    if (!trigger) return;
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    const open = trigger.getAttribute('aria-expanded') !== 'true';
    trigger.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const trigger = document.querySelector('[data-specimen-disclosure][aria-expanded="true"]');
    if (!trigger) return;
    document.getElementById(trigger.getAttribute('aria-controls')).hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    trigger.focus();
    event.preventDefault();
  });
})();
