import { installKeyboard } from './keyboard.js';
import { installPointer } from './pointer.js';
import { mountLegend } from './legend.js';

// A Bar control owns its entire captured gesture, including a rejected stale
// action. Dismissing it here would change the stamp before the renderer can
// admit that action. Blank Bar space and the desktop are outside surfaces.
export function installOutsideDismissal({ doc, root, isDesktop, host }) {
  let held = null;
  const timers = new Set();
  const clear = () => { held = null; };
  const press = event => {
    clear();
    if (event.button !== 0 || (isDesktop && !root.contains(event.target))) return;
    if (!isDesktop && event.target?.closest?.('[data-surface-control]')) return;
    const before = host.getSnapshot(), p = before.presentation;
    if (!p || p.mode === 'closed' || !p.lease || !p.applied?.popup) return;
    if (!before.viewScope) return;
    held = { pointerId: event.pointerId, target: event.target, epoch: before.epoch, scope: {...before.viewScope}, lease: p.lease };
  };
  const release = event => {
    const gesture = held; clear();
    if (!gesture || event.button !== 0 || event.pointerId !== gesture.pointerId || event.target !== gesture.target) return;
    // Let the completed click run first. Focus can publish a new presentation
    // for the same popup; the host validates the captured scope and lease.
    const timer = setTimeout(() => {
      timers.delete(timer);
      host.dispatchInput({kind:'popup-dismiss', epoch:gesture.epoch, scope:gesture.scope, lease:gesture.lease});
    }, 0);
    timers.add(timer);
  };
  doc.addEventListener('pointerdown', press, true);
  doc.addEventListener('pointerup', release, true);
  doc.addEventListener('pointercancel', clear, true);
  doc.defaultView?.addEventListener('blur', clear);
  return () => {
    clear(); timers.forEach(clearTimeout);
    doc.removeEventListener('pointerdown', press, true);
    doc.removeEventListener('pointerup', release, true);
    doc.removeEventListener('pointercancel', clear, true);
    doc.defaultView?.removeEventListener('blur', clear);
  };
}

export function installInput({ host, stage, frames, legendRoot }) {
  const anchors = stage.getAnchors();
  const root = anchors.root || anchors.desktop;
  if (!root) throw new Error('The stage must expose its desktop root.');
  const enrolled = new Map();
  const outside = (doc, isDesktop) => installOutsideDismissal({doc, root, isDesktop, host});
  const stopOutside = outside(root.ownerDocument, true);
  const keyboard = installKeyboard({ documents: [root.ownerDocument], host, root });
  const enroll = (frame, id) => {
    enrolled.get(frame)?.();
    try {
      const doc = frame.contentDocument;
      if (doc) { const stopKeys = keyboard.addDocument(doc); const stopPress = id === 'bar' ? outside(doc, false) : () => {}; enrolled.set(frame, () => { stopKeys(); stopPress(); }); }
    } catch { enrolled.delete(frame); }
  };
  const frameList = Object.entries(frames || {}).filter(([,frame]) => frame?.addEventListener);
  const loads = frameList.map(([id, frame]) => { const load = () => enroll(frame, id); frame.addEventListener('load', load); enroll(frame, id); return () => frame.removeEventListener('load', load); });
  const stopPointer = installPointer({ root, host });
  const stopLegend = mountLegend(legendRoot, host);
  return () => { stopOutside(); loads.forEach(remove => remove()); enrolled.forEach(remove => remove()); keyboard(); stopPointer(); stopLegend(); };
}
