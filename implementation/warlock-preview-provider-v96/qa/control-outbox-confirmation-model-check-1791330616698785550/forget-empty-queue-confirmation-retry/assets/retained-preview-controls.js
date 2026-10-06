'use strict';
// Transport only. This file is deliberately not loaded by popup.html until
// native admission reserves cleanup capacity and receiver recovery is wired.
// A failed offer is backpressure before admission, never permission to discard
// an already emitted Elm command. Delivery receipts do not settle effects.
globalThis.WarlockRetainedPreviewControls = function(grant, post, confirm) {
  const maximum=18446744073709551615n;
  const fields=(value,names)=>value && typeof value==='object' && !Array.isArray(value) &&
    Object.keys(value).length===names.length && names.every(name=>Object.hasOwn(value,name));
  const counter=value=>typeof value==='string' && /^[1-9][0-9]*$/.test(value) && value.length<=20 && BigInt(value)<=maximum;
  const validBinding=value=>fields(value,['lifetime','session','frontend']) &&
    ['lifetime','session','frontend'].every(name=>counter(value[name]));
  if(!fields(grant,['binding','receiverEpoch','capacity']) || !validBinding(grant.binding) ||
     !counter(grant.receiverEpoch) || !Number.isSafeInteger(grant.capacity) || grant.capacity<=0 || typeof post!=='function' || typeof confirm!=='function')
    throw new TypeError('Original native grant and bounded reserved capacity required');
  const binding=Object.freeze({...grant.binding}),epoch=grant.receiverEpoch,capacity=grant.capacity;
  let issued=0n,confirmed=0n,sending=false,confirming=false;const queue=[];
  function transmit() {
    if(sending || !queue.length)return false;
    sending=true;
    try {post(queue[0].wire);return true;} catch(_error) {return false;}
    finally {sending=false;}
  }
  function confirmLatest() {
    if(!confirmed || confirming)return false;
    const receipt=Object.freeze({previewProtocol:3,kind:'preview-control-confirmed',binding,
      receiverEpoch:epoch,controlOrdinal:String(confirmed)});
    confirming=true;
    try {confirm(receipt);return true;} catch(_error) {return false;}
    finally {confirming=false;}
  }
  function retry() {
    // One bounded confirmation and at most one immutable data packet per call.
    // Keep the compact prefix even after posting: only native knows it arrived.
    const confirmation=false,packet=transmit();return confirmation || packet;
  }
  function offer(identity,command) {
    if(queue.length>=capacity || issued===maximum || typeof identity!=='string' || !identity ||
       !command || typeof command!=='object' || Array.isArray(command))return false;
    const ordinal=issued+1n;let wire;
    try {wire=JSON.stringify({previewProtocol:3,kind:'preview-commands',binding,
      receiverEpoch:epoch,controlOrdinal:String(ordinal),entries:[{identity,commands:[command]}]});}
    catch(_error) {return false;}
    if(new TextEncoder().encode(wire).length>4096)return false;
    // Serialize before consuming an ordinal; caller mutation can never alter a
    // retained transmission. One outstanding packet enters native at a time.
    const idle=!queue.length;queue.push(Object.freeze({ordinal,wire}));issued=ordinal;
    if(idle)transmit();return true;
  }
  function acknowledge(receipt) {
    if(!fields(receipt,['previewProtocol','kind','binding','receiverEpoch','controlOrdinal']) ||
       receipt.previewProtocol!==3 || receipt.kind!=='preview-control-delivered' ||
       !validBinding(receipt.binding) || ['lifetime','session','frontend'].some(name=>receipt.binding[name]!==binding[name]) ||
       receipt.receiverEpoch!==epoch || !counter(receipt.controlOrdinal))return false;
    const ordinal=BigInt(receipt.controlOrdinal);
    if(ordinal<=confirmed){confirmLatest();return true;}
    if(!queue.length || ordinal!==queue[0].ordinal)return false;
    confirmed=queue[0].ordinal;queue.shift();
    confirmLatest();
    // An unusually synchronous receipt cannot recursively enter post. The
    // owning host's next transport poll supplies progress for that case.
    transmit();return true;
  }
  return Object.freeze({offer,acknowledge,retry,
    snapshot:()=>Object.freeze({issued:String(issued),confirmed:String(confirmed),pending:queue.length,capacity})});
};
