// Omarchy uses a 6px edge and an 80px corner region on the output.
export function edgeZone(x, y, width, height) {
  const side = x <= 6 ? 'left' : x >= width - 6 ? 'right' : null;
  if (side) return y <= 80 ? `top-${side}` : y >= height - 80 ? `bottom-${side}` : side;
  return y <= 6 ? 'maximize' : null;
}

export function zoneGeometry(zone, area) {
  const gap = 10, x = area.x + gap, y = area.y + gap;
  const width = Math.max  (160, area.width - 2 * gap), height = Math.max(100, area.height - 2 * gap);
  if (zone === 'maximize') return {x, y, width, height};
  const halfW = Math.floor((width - gap) / 2), halfH = Math.floor((height - gap) / 2);
  const right = zone.endsWith('right'), quarter = zone.startsWith('top-') || zone.startsWith('bottom-');
  const bottom = zone.startsWith('bottom-');
  return {x: right ? x + halfW + gap : x, y: bottom ? y + halfH + gap : y,
    width: right ? width - halfW - gap : halfW, height: quarter ? (bottom ? height - halfH - gap : halfH) : height};
}

// A placement is a single compositor observation, bound to the observed window.
export function placeInZone(host, windowId, incarnation, zone, expectedEpoch = host.getSnapshot().epoch) {
  const snapshot = host.getSnapshot();
  if (!['left','right','top-left','top-right','bottom-left','bottom-right','maximize'].includes(zone) ||
      snapshot.epoch !== expectedEpoch || !snapshot.workArea || !snapshot.windows.some(w => w.id === windowId && w.incarnation === incarnation && !w.minimized)) return false;
  return host.dispatchInput({kind:'placement', epoch:snapshot.epoch, windowId, incarnation, zone,
    geometry:zoneGeometry(zone, snapshot.workArea)});
}

/** Pointer input forwards captured geometry and never focuses a window on hover. */
export function installPointer({ root, host }) {
  let drag = null;
  let suppressClick = false;
  let epoch = host.getSnapshot?.().epoch;
  const cancelDrag = () => {
    if (drag?.started) {
      const snapshot = host.getSnapshot();
      if (snapshot.epoch === epoch && snapshot.windows.some(w => w.id === drag.input.windowId && w.incarnation === drag.input.incarnation))
        host.dispatchInput({ kind: 'pointer', action: 'cancel', ...drag.input });
    }
    drag = null;
    suppressClick = false;
  };
  const unsubscribe = host.subscribe?.(snapshot => { if (snapshot.epoch !== epoch) { cancelDrag(); epoch = snapshot.epoch; } });
  function start(event) {
    suppressClick = false;
    const origin = event.target;
    const target = origin.closest('[data-window-id]');
    const titlebar = origin.closest('.stage-titlebar');
    const control = origin.closest('button, a, input, select, textarea, [role="button"]');
    if (titlebar && control && !control.matches('button.stage-title')) return;
    const titleDrag = event.button === 0 && titlebar && target?.contains(titlebar) &&
      (!control || control.matches('button.stage-title'));
    if (!target || origin.closest('[disabled], [aria-disabled="true"]') ||
        !(titleDrag || (event.altKey && [0, 2].includes(event.button)))) return;
    cancelDrag();
    const snapshot = host.getSnapshot();
    const window = snapshot?.windows?.find(w => w.id === target.dataset.windowId && !w.minimized);
    if (!window) return;
    const input = { epoch: snapshot.epoch, incarnation: window.incarnation, pointerId: event.pointerId, windowId: window.id, mode: event.button === 0 ? 'move' : 'resize', x: event.clientX, y: event.clientY };
    drag = {input, started:false, titleDrag:!!titleDrag};
    origin.setPointerCapture?.(event.pointerId);
    if (!titleDrag) {
      drag.started = host.dispatchInput({ kind: 'pointer', action: 'start', ...input }) !== false;
      if (!drag.started) drag = null;
      event.preventDefault();
    }
  }
  function move(event) {
    if (!drag || drag.input.pointerId !== event.pointerId) return;
    const captured = drag.input;
    const snapshot = host.getSnapshot();
    if (snapshot.epoch !== epoch || !snapshot.windows.some(w => w.id === captured.windowId && w.incarnation === captured.incarnation && !w.minimized)) { cancelDrag(); return; }
    if (!drag.started) {
      if (Math.hypot(event.clientX - captured.x, event.clientY - captured.y) < 4) return;
      drag.started = host.dispatchInput({kind:'pointer', action:'start', ...captured}) !== false;
      if (!drag.started) { drag = null; return; }
    }
    if (drag.titleDrag) suppressClick = true;
    host.dispatchInput({ kind: 'pointer', action: 'move', ...captured, currentX: event.clientX, currentY: event.clientY });
    event.preventDefault();
  }
  function finish(event, action) {
    if (!drag || drag.input.pointerId !== event.pointerId) return;
    const {input:captured, started} = drag; drag = null;
    if (action === 'cancel') suppressClick = false;
    if (!started) return;
    const snapshot = host.getSnapshot();
    if (snapshot.epoch !== captured.epoch || !snapshot.windows.some(w => w.id === captured.windowId && w.incarnation === captured.incarnation)) return;
    let zone = null;
    if (action === 'end' && captured.mode === 'move') {
      const bounds = root.getBoundingClientRect(), output = snapshot.output;
      const x = (event.clientX - bounds.left) * output.width / bounds.width;
      const y = (event.clientY - bounds.top) * output.height / bounds.height;
      zone = edgeZone(x, y, output.width, output.height);
    }
    // Retire the transient drag first so the compositor saves the pre-drag
    // placement for a later restore. A cancelled gesture never places.
    host.dispatchInput({ kind: 'pointer', action: zone ? 'cancel' : action, ...captured, currentX: event.clientX, currentY: event.clientY });
    if (zone) placeInZone(host, captured.windowId, captured.incarnation, zone, captured.epoch);
  }
  const end = (e) => finish(e, 'end'); const cancel = (e) => finish(e, 'cancel');
  root.ownerDocument.defaultView.addEventListener('blur', cancelDrag);
  const lost = event => { if (drag?.input.pointerId === event.pointerId) cancelDrag(); };
  const click = event => { if (suppressClick) { suppressClick = false; event.preventDefault(); event.stopImmediatePropagation(); } };
  root.addEventListener('lostpointercapture', lost);
  root.addEventListener('click', click, true);
  root.addEventListener('pointerdown', start); root.addEventListener('pointermove', move); root.addEventListener('pointerup', end); root.addEventListener('pointercancel', cancel);
  return () => { cancelDrag(); unsubscribe?.(); root.ownerDocument.defaultView.removeEventListener('blur', cancelDrag); root.removeEventListener('lostpointercapture', lost); root.removeEventListener('click', click, true); root.removeEventListener('pointerdown', start); root.removeEventListener('pointermove', move); root.removeEventListener('pointerup', end); root.removeEventListener('pointercancel', cancel); };
}

// Bind the action to the currently observed focused window and its incarnation.
export function focusedWindowAction(host, action) {
  const snapshot = host.getSnapshot();
  const window = snapshot.windows?.find(w => w.focused && !w.minimized && (w.workspace === snapshot.activeWorkspace || w.pinned));
  if (!window) return false;
  if (action === 'restore-or-minimize') {
    if (window.maximized || window.placementMode === 'maximized' || window.placementMode === 'snapped')
      return host.dispatchInput({kind:'window', action:'restore-geometry', epoch:snapshot.epoch, windowId:window.id, incarnation:window.incarnation});
    return host.dispatchInput({kind:'window', action:'minimize', epoch:snapshot.epoch, windowId:window.id, incarnation:window.incarnation});
  }
  if (action === 'maximize' && (window.maximized || window.placementMode === 'maximized')) return false;
  return placeInZone(host, window.id, window.incarnation, action);
}
