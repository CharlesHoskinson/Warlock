import { focusedWindowAction } from './pointer.js';
import { inventory as defaultInventory } from '../services/preferences.js';

export function effectiveShortcut(snapshot, route) {
  const row = (snapshot?.services?.shortcutInventory || defaultInventory)[route];
  const selected = row?.active;
  if (selected !== 'default' && selected !== 'alternate') return null;
  return row && row[selected + 'Available'] ? row[selected + 'Chord'] : null;
}

/** Keyboard translation is limited to a focused desktop or one of its frames. */
export function installKeyboard({ documents, host, root }) {
  let switching = false;
  let altCode = null;
  let blurTimer;
  let epoch = host.getSnapshot?.().epoch;
  const unsubscribe = host.subscribe?.(snapshot => { if (snapshot.epoch !== epoch) { cancel(); epoch = snapshot.epoch; } });
  const listeners = [];
  const dispatch = (input) => host.dispatchInput(input);
  const cancel = () => {
    if (switching) dispatch({ kind: 'switcher', action: 'cancel' });
    switching = false;
    altCode = null;
  };
  const editable = (target) => typeof target?.closest === 'function' &&
    !!target.closest('input, textarea, select, [contenteditable]:not([contenteditable="false"])');
  function down(event) {
    if ((event.currentTarget === root.ownerDocument || event.currentTarget === root.ownerDocument.defaultView) && !root.contains(event.target)) return;
    if (event.defaultPrevented || event.isComposing || event.key === 'Process' || editable(event.target)) return;
    const key = event.key.toLowerCase();
    if (event.altKey && !event.ctrlKey && !event.metaKey && key === 'tab') {
      event.preventDefault();
      if (!switching) { switching = true; altCode = event.getModifierState('Alt') ? 'Alt' : null; }
      dispatch({ kind: 'switcher', action: event.shiftKey ? 'previous' : 'next', repeat: event.repeat });
      return;
    }
    if (switching && key === 'escape') { event.preventDefault(); cancel(); return; }
    if (event.repeat) return;
    if (event.metaKey && !event.ctrlKey && !event.altKey && !event.shiftKey) {
      const action = {arrowleft:'left', arrowright:'right', arrowup:'maximize', arrowdown:'restore-or-minimize'}[key];
      if (action) { event.preventDefault(); focusedWindowAction(host, action); return; }
    }
    let input = null;
    if (event.metaKey && !event.ctrlKey && !event.altKey && !event.shiftKey && key === 'tab') input = { kind: 'utility', action: 'task-view' };
    else if (event.metaKey && !event.ctrlKey && !event.altKey && !event.shiftKey && key === 'z') input = { kind: 'utility', action: 'snap' };
    else if (event.altKey && !event.metaKey && !event.ctrlKey && !event.shiftKey && key === ' ') input = { kind: 'utility', action: 'window-menu' };
    else {
      const snapshot = host.getSnapshot?.();
      for (const route of ['applications', 'system', 'notifications']) {
        const chord = effectiveShortcut(snapshot, route);
        if (chord && matchesChord(event, chord)) { input = { kind: 'shortcut', route }; break; }
      }
    }
    if (!input && event.metaKey && !event.ctrlKey && /^Digit[1-9]$/.test(event.code) && !(event.shiftKey && event.altKey)) input = { kind: 'taskbar-number', index: Number(event.code.slice(-1)), action: event.altKey ? 'menu' : event.shiftKey ? 'launch' : 'activate' };
    if (input) { event.preventDefault(); dispatch(input); }
  }
  function up(event) {
    if (event.currentTarget === root.ownerDocument && !root.contains(event.target)) { cancel(); return; }
    if (typeof root.ownerDocument.hasFocus === 'function' && !root.ownerDocument.hasFocus()) { cancel(); return; }
    if (switching && altCode && (event.key === 'Alt' || event.code === 'AltLeft' || event.code === 'AltRight')) {
      switching = false; altCode = null;
      if (!event.isComposing && !editable(event.target)) dispatch({ kind: 'switcher', action: 'activate' });
    }
  }
  const addDocument = doc => {
    const win = doc.defaultView;
    // A frame blur can mean focus moved to another registered frame. Wait until
    // the browser has settled focus before deciding that the desktop lost it.
    const blur = () => { clearTimeout(blurTimer); blurTimer = setTimeout(() => {
      const top = root.ownerDocument;
      if (typeof top.hasFocus === 'function' && !top.hasFocus()) cancel();
      else if (top.activeElement && !root.contains(top.activeElement) && !documentsSet.has(top.activeElement.contentDocument)) cancel();
    }, 0); };
    documentsSet.add(doc);
    // Window capture runs before the popup adapter's document capture listener.
    // Handling the chord here also prevents the adapter from advancing it twice.
    const captureChord = event => {
      if (event.altKey && !event.ctrlKey && !event.metaKey && event.key.toLowerCase() === 'tab') down(event);
    };
    win.addEventListener('keydown', captureChord, true);
    doc.addEventListener('keydown', down); doc.addEventListener('keyup', up); win.addEventListener('blur', blur);
    doc.addEventListener('compositionstart', cancel);
    const remove = () => { documentsSet.delete(doc); win.removeEventListener('keydown', captureChord, true); doc.removeEventListener('keydown', down); doc.removeEventListener('keyup', up); win.removeEventListener('blur', blur); doc.removeEventListener('compositionstart', cancel); };
    listeners.push(remove); return remove;
  };
  const documentsSet = new Set();
  documents.forEach(addDocument);
  const dispose = () => { clearTimeout(blurTimer); cancel(); unsubscribe?.(); listeners.forEach((remove) => remove()); };
  dispose.addDocument = addDocument;
  return dispose;
}

export function matchesChord(event, chord) {
  const parts = chord.toLowerCase().split('+').map(part => part.trim());
  const key = parts.pop();
  const actual = event.code === 'Comma' ? 'comma' : event.key === ' ' ? 'space' : event.key.toLowerCase();
  return key === actual && event.metaKey === parts.includes('super') && event.ctrlKey === parts.includes('ctrl') && event.altKey === parts.includes('alt') && event.shiftKey === parts.includes('shift');
}
