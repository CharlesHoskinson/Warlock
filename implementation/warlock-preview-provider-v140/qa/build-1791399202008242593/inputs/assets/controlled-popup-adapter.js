'use strict';
(() => {
  const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
  let admission = Elm.NativePreviewAdmission.init({node: document.getElementById('native-preview-admission-mount')});
  let renderer = null, nativeGrant = null, pendingReceipt = null, generation = 0;
  const frame = callback => requestAnimationFrame(() => requestAnimationFrame(callback));
  const surface = value => {
    const node = document.querySelector('.surface-popup');
    return node && node.dataset.publication === value.publication && node.dataset.lease === value.lease ? node : null;
  };
  window.submitSurfaceAction = value => {
    // Native still checks the original current GTK/publication/action gates.
    if (admission) admission.ports.requestAction.send(value);
    else if (renderer) post(value);
  };
  window.receivePresentation = value => {
    if (!admission) return; // Subsequent display bytes come only from native projection.
    const current = ++generation;
    admission.ports.presentation.send(value);
    frame(() => {
      if (admission && generation === current && surface(value)) {
        post({surfaceProtocol:2, kind:'presentation-applied', publication:value.publication, lease:value.lease});
      }
    });
  };
  window.receiveFocus = value => requestAnimationFrame(() => {
    const node = surface(value);
    if (value.surfaceProtocol !== 2 || value.kind !== 'surface-focus' || !node) return;
    const focused = [];
    for (const target of value.targets) {
      const control = document.getElementById(target);
      if (control && node.contains(control) && !control.disabled) {
        control.focus(); if (document.activeElement === control) focused.push(target);
      }
    }
    post({surfaceProtocol:2, kind:'focus-applied', publication:value.publication, lease:value.lease, targets:focused});
  });
  admission.ports.actions.subscribe(post);
  // Called only by the owning native WebKit host after original GTK admission.
  // Later packets cannot establish/reset a grant or initialize a second receiver.
  window.initializeNativePreviewRenderer = grant => {
    if (renderer || nativeGrant || !admission) return false;
    generation++;
    admission.ports.actions.unsubscribe(post);
    const replacement = document.createElement('div'); replacement.id = 'native-preview-renderer-mount';
    document.getElementById('app').replaceChildren(replacement);
    admission = null; nativeGrant = grant;
    renderer = Elm.NativePreviewRenderer.init({node:replacement, flags:grant});
    renderer.ports.surfaceActions.subscribe(post);
    renderer.ports.acceptedSnapshots.subscribe(receipt => { pendingReceipt = receipt; });
    return true;
  };
  window.receiveNativeVisualProjection = packet => {
    if (!renderer) return;
    const current = ++generation; pendingReceipt = null;
    renderer.ports.visualSnapshots.send(packet);
    // Elm decoder acceptance is distinct from DOM application. These RAF and DOM
    // checks supplement it, but native keeps its physical opacity curtain closed.
    frame(() => {
      if (generation !== current || !pendingReceipt ||
          pendingReceipt.rendererLease !== packet.rendererLease ||
          pendingReceipt.visualSequence !== packet.visualSequence ||
          pendingReceipt.receiverEpoch !== packet.receiverEpoch) return;
      const shown = packet.visual.surface;
      if (shown && !surface(shown)) return;
      if (!shown && document.querySelector('.surface-popup')) return;
      post(pendingReceipt);
      if (shown) post({surfaceProtocol:2, kind:'presentation-applied', publication:shown.publication, lease:shown.lease});
      if (window.elmPreviewQA) inspectNativePreviewQA();
    });
  };
  // Private read-only observation. Native independently checks its current
  // channel, original URI and sizes before requesting an offscreen snapshot.
  // Image loading and snapshot pixels carry no physical reveal authority.
  const inspectNativePreviewQA = () => {
    if (!renderer || !pendingReceipt) return;
    const images = [...document.querySelectorAll('img.preview-image')].slice(0,2).map(image => {
      const rect = image.getBoundingClientRect();
      return {uri:image.src,complete:image.complete,naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,width:Math.round(rect.width),height:Math.round(rect.height)};
    });
    post({kind:'preview-image-report',images});
  };
  if (window.elmPreviewQA) {
    window.inspectNativePreviewQA = inspectNativePreviewQA;
    document.addEventListener('load',inspectNativePreviewQA,true);
  }
  post({surfaceProtocol:2, kind:'presentation-ready'});
})();
