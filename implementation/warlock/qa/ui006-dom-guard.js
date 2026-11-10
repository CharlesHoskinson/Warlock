/* Private source proposal: synthetic DOM/component only; no native authority. */
'use strict';
window.runUi006IndependentDomGuard = async function () {
  const ids = ['overview:workspace-create','overview:workspace-delete','overview:workspace-rename'];
  const labels = ['Create workspace','Delete workspace','Rename workspace'];
  const wantedOrder = ['control:close','overview:all',...ids];
  const expected = [
    {kind:'probe',snapshotChecks:true,sourceChecks:true,rowChecks:true,staleChecks:true},
    {kind:'tap',action:{surface:'popup',surfaceProtocol:2,kind:'surface-action',publication:'1',lease:'1',id:'control:close'}}
  ];
  const fail = message => { throw Error(message); };
  const need = (yes, message) => { if (!yes) fail(message); };
  const recordOK = (value, index) => index >= 0 && index < expected.length && JSON.stringify(value) === JSON.stringify(expected[index]);
  // Zero opacity on this element or an ancestor hides text despite a layout box.
  const visiblyPresented = element => {
    if (!element.getClientRects().length || getComputedStyle(element).visibility !== 'visible') return false;
    for (let node = element; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === 'none' || Number(style.opacity) === 0) return false;
    }
    return true;
  };
  // These counterfactuals are local data only; they do not impersonate a host.
  need(!recordOK({},0) && !recordOK({...expected[0],extra:true},0), 'missing/extra probe guard');
  need(!recordOK(expected[1],0) && !recordOK(expected[0],1), 'out-of-order guard');
  need(!recordOK(expected[1],2), 'duplicate guard');
  need(recordOK(expected[0],0) && recordOK(expected[1],1), 'literal positive guard');
  const root = document.getElementById('workspace-unsupported-fixture');
  const mount = document.getElementById('workspace-unsupported-mount');
  need(root && mount && root.contains(mount) && mount.childNodes.length === 0, 'fixed fixture root');
  const app = window.Elm.WorkspaceUnsupportedDomReplay.init({node:mount,flags:null});
  need(app.ports && app.ports.outgoing && app.ports.probe, 'ports unavailable');
  let stage = 'initial', fault = null;
  const received = [];
  app.ports.outgoing.subscribe(value => {
    const expectedIndex = stage === 'await-probe' ? 0 : stage === 'await-close' ? 1 : -1;
    if (fault || expectedIndex < 0 || received.length !== expectedIndex || !recordOK(value,expectedIndex)) {
      fault = 'missing, extra, duplicate or out-of-order callback';
      return;
    }
    received.push(value);
  });
  const settle = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  await settle();
  need(!fault && received.length === 0, 'unsolicited initial callback');
  const get = id => {
    const matches = Array.from(root.querySelectorAll('[data-surface-control]')).filter(x => x.getAttribute('data-surface-control') === id);
    need(matches.length === 1, `${id}: missing or duplicate`);
    return matches[0];
  };
  need(root.querySelector('[data-mode="overview"]'), 'overview missing');
  const ordered = Array.from(root.querySelectorAll('[data-surface-control]')).map(x => x.getAttribute('data-surface-control')).filter(x => wantedOrder.includes(x));
  need(JSON.stringify(ordered) === JSON.stringify(wantedOrder), 'control order or duplicate');
  const close = get('control:close');
  need(close.tagName === 'BUTTON' && close.getAttribute('role') === 'button' && !close.disabled && close.getAttribute('aria-disabled') === 'false' && close.getAttribute('data-focus-only') === 'false' && close.getAttribute('aria-label') === 'Close Task View and return to windows', 'close semantics');
  close.focus();
  need(document.activeElement === close, 'synthetic close focus');
  ids.forEach((id, index) => {
    const button = get(id), label = button.querySelector('.control-label'), detail = button.querySelector('.control-detail');
    need(button.tagName === 'BUTTON' && button.getAttribute('role') === 'button' && button.disabled && button.getAttribute('aria-disabled') === 'true' && button.getAttribute('data-focus-only') === 'false', `${id}: disabled role`);
    need(button.getAttribute('aria-label') === labels[index] + '; unavailable' && label && label.textContent === labels[index] && detail && detail.textContent === 'Not supported', `${id}: label/detail`);
    need(visiblyPresented(button), `${id}: hidden or transparent`);
    // Local counterfactuals only: do not confuse layout boxes with visibility.
    const ownOpacity = button.style.opacity;
    button.style.opacity = '0';
    const ownInvisible = !visiblyPresented(button);
    button.style.opacity = ownOpacity;
    const ancestor = button.parentElement;
    need(ancestor, `${id}: missing ancestor`);
    const ancestorOpacity = ancestor.style.opacity;
    ancestor.style.opacity = '0';
    const ancestorInvisible = !visiblyPresented(button);
    ancestor.style.opacity = ancestorOpacity;
    need(ownInvisible && ancestorInvisible && visiblyPresented(button), `${id}: opacity counterfactual`);
    button.focus(); need(document.activeElement === close, `${id}: disabled focus`);
    button.click();
    button.dispatchEvent(new MouseEvent('click',{bubbles:true}));
    button.disabled = false;
    button.dispatchEvent(new MouseEvent('click',{bubbles:true}));
    button.disabled = true;
  });
  await settle();
  need(!fault && received.length === 0, 'disabled action emitted');
  stage = 'await-probe'; app.ports.probe.send(null);
  await settle();
  need(!fault && received.length === 1, 'probe missing or invalid');
  stage = 'await-close'; close.click();
  await settle();
  need(!fault && received.length === 2, 'close missing or invalid');
  stage = 'closed';
  await settle();
  need(!fault && received.length === 2, 'duplicate callback within window');
  return {kind:'ui006-dom-component',status:'observed',cases:3,receipts:2,scope:'synthetic component only',originalAccepted:false,nativeAccepted:false};
};
