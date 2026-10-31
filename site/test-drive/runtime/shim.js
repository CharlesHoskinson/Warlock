/* Installed before the unmodified native adapters. */
(() => {
  'use strict';
  const frameId = document.documentElement.dataset.frameId;
  let epoch = 0;
  let bound = false;
  const pending = [];
  const origin = location.origin;
  const allowed = new Set(['receiveBatchDisposition','receiveTopology','receiveNative','receiveAction','receiveDismiss','receiveEscape','receiveReflow','receivePresentation','receiveFocus','receiveAnnouncement','receiveNativePreview','receiveNativePreviewBatch','receiveNativePreviewRetirement']);
  window.webkit = {messageHandlers:{native:{postMessage(raw) {
    if (typeof raw !== 'string') return;
    if (!bound) { pending.push(raw); return; }
    parent.postMessage({bridgeVersion:1, epoch, frameId, kind:'native', payload:raw}, origin);
  }}}};
  addEventListener('message', event => {
    const packet = event.data;
    if (event.origin !== origin || event.source !== parent || !packet || packet.bridgeVersion !== 1 || packet.frameId !== frameId || !Number.isSafeInteger(packet.epoch)) return;
    if (packet.kind === 'bind' && !bound && packet.epoch >= epoch) { epoch = packet.epoch; bound = true; parent.postMessage({bridgeVersion:1,epoch,frameId,kind:'bound',payload:null},origin); for (const raw of pending.splice(0)) parent.postMessage({bridgeVersion:1,epoch,frameId,kind:'native',payload:raw},origin); return; }
    if (packet.epoch !== epoch || packet.kind !== 'deliver' || !packet.payload || !allowed.has(packet.payload.method)) return;
    const receiver = window[packet.payload.method];
    if (typeof receiver === 'function') receiver(packet.payload.value);
  });
})();
