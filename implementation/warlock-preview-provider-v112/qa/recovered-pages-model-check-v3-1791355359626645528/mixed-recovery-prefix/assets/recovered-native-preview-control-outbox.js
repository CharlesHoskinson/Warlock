'use strict';
// Transport only. Trusted native recovery pages rebuild an original realm
// after JavaScript context loss. All pages must be complete and consistent
// before any post. Actual WebKit/host routing activation remains separate.
globalThis.WarlockRecoveredNativePreviewControlOutbox = function(grant, post, confirm, pages=[]) {
  const maximum=18446744073709551615n;
  const fields=(value,names)=>value && typeof value==='object' && !Array.isArray(value) &&
    Object.keys(value).length===names.length && names.every(name=>Object.hasOwn(value,name));
  const counter=value=>typeof value==='string' && /^[1-9][0-9]*$/.test(value) &&
    value.length<=20 && BigInt(value)<=maximum;
  const validBinding=value=>fields(value,['lifetime','session','frontend']) &&
    ['lifetime','session','frontend'].every(name=>counter(value[name]));
  if(!fields(grant,['binding','receiverEpoch','capacity']) || !validBinding(grant.binding) ||
     !counter(grant.receiverEpoch) || !Number.isSafeInteger(grant.capacity) ||
     grant.capacity<=0 || grant.capacity>1065 || typeof post!=='function' || typeof confirm!=='function')
    throw new TypeError('Exact native realm, reserved capacity and both transports required');
  const binding=Object.freeze({...grant.binding}),epoch=grant.receiverEpoch,capacity=grant.capacity;
  const realm=value=>validBinding(value.binding) &&
    ['lifetime','session','frontend'].every(name=>value.binding[name]===binding[name]) && value.receiverEpoch===epoch;
  let nativeIssuedThrough=0n,deliveredThrough=0n,sending=false,confirming=false;
  let confirmationWire=null,lastDeliveredWire=null;
  const queue=[];let recovering=true;
  function transmit() {
    if(recovering || sending || !queue.length)return false;
    sending=true;
    try {post(queue[0].wire);return true;} catch(_error) {return false;}
    finally {sending=false;}
  }
  function confirmLatest() {
    if(!confirmationWire || confirming)return false;
    confirming=true;
    try {confirm(confirmationWire);return true;} catch(_error) {return false;}
    finally {confirming=false;}
  }
  function retain(ticket) {
    if(!fields(ticket,['previewProtocol','kind','binding','receiverEpoch','controlOrdinal','alreadyDelivered','wire']) ||
       ticket.previewProtocol!==3 || ticket.kind!=='preview-control-ticket' || !realm(ticket) ||
       !counter(ticket.controlOrdinal) || typeof ticket.alreadyDelivered!=='boolean' ||
       typeof ticket.wire!=='string' || new TextEncoder().encode(ticket.wire).length>4096)return false;
    let packet;
    try {packet=JSON.parse(ticket.wire);} catch(_error) {return false;}
    if(!fields(packet,['previewProtocol','kind','binding','receiverEpoch','controlOrdinal','entries']) ||
       packet.previewProtocol!==3 || packet.kind!=='preview-commands' || !realm(packet) ||
       packet.controlOrdinal!==ticket.controlOrdinal || !Array.isArray(packet.entries) || packet.entries.length!==1 ||
       !fields(packet.entries[0],['identity','commands']) || typeof packet.entries[0].identity!=='string' ||
       !packet.entries[0].identity || !Array.isArray(packet.entries[0].commands) || packet.entries[0].commands.length!==1 ||
       !packet.entries[0].commands[0] || typeof packet.entries[0].commands[0]!=='object' ||
       Array.isArray(packet.entries[0].commands[0]))return false;
    const ordinal=BigInt(ticket.controlOrdinal),existing=queue.find(row=>row.ordinal===ordinal);
    if(existing) {
      if(existing.wire!==ticket.wire)return false;
      // alreadyDelivered is advisory. Only an original delivery receipt may
      // release a row. A repeated proposal retries the oldest exact ticket.
      transmit();return true;
    }
    if(ordinal<=deliveredThrough) {
      if(ordinal!==deliveredThrough || ticket.wire!==lastDeliveredWire)return false;
      confirmLatest();return true;
    }
    if(queue.length>=capacity || ordinal!==nativeIssuedThrough+1n)return false;
    const idle=!queue.length;
    queue.push(Object.freeze({ordinal,wire:ticket.wire}));nativeIssuedThrough=ordinal;
    if(idle)transmit();return true;
  }
  function acknowledge(receipt) {
    if(!fields(receipt,['previewProtocol','kind','binding','receiverEpoch','controlOrdinal']) ||
       receipt.previewProtocol!==3 || receipt.kind!=='preview-control-delivered' || !realm(receipt) ||
       !counter(receipt.controlOrdinal))return false;
    const ordinal=BigInt(receipt.controlOrdinal);
    if(ordinal<=deliveredThrough) {confirmLatest();return true;}
    if(!queue.length || ordinal!==queue[0].ordinal)return false;
    // Prepare the compact confirmation before releasing transport storage.
    // It proves receipt observation, never physical or Elm effect settlement.
    const wire=JSON.stringify({previewProtocol:3,kind:'preview-control-confirmed',binding,
      receiverEpoch:epoch,controlOrdinal:String(ordinal)});
    deliveredThrough=ordinal;lastDeliveredWire=queue[0].wire;queue.shift();confirmationWire=wire;
    confirmLatest();transmit();return true;
  }
  function retry() {
    const confirmation=confirmLatest(),packet=transmit();return confirmation || packet;
  }
  if(!Array.isArray(pages) || pages.length>capacity+1)throw new TypeError('Bounded original native recovery pages required');
  if(pages.length) {
    const zeroCounter=value=>typeof value==='string' && /^(0|[1-9][0-9]*)$/.test(value) && value.length<=20 && BigInt(value)<=maximum;
    const head=pages[0];
    const header=['previewProtocol','kind','binding','receiverEpoch','capacity','issuedThrough','deliveredThrough','confirmedThrough','afterOrdinal','ticket'];
    if(!fields(head,header) || head.previewProtocol!==3 || head.kind!=='preview-control-recovery' || !realm(head) || head.capacity!==capacity ||
       !['issuedThrough','deliveredThrough','confirmedThrough','afterOrdinal'].every(name=>zeroCounter(head[name])))
      throw new TypeError('Exact canonical native recovery header required');
    const issued=BigInt(head.issuedThrough),delivered=BigInt(head.deliveredThrough),confirmed=BigInt(head.confirmedThrough);
    if(confirmed>delivered || delivered>issued || issued-confirmed>BigInt(capacity) || head.afterOrdinal!==head.confirmedThrough)
      throw new TypeError('Original ordered bounded native recovery frontiers required');
    nativeIssuedThrough=deliveredThrough=confirmed;
    if(confirmed)confirmationWire=JSON.stringify({previewProtocol:3,kind:'preview-control-confirmed',binding,receiverEpoch:epoch,controlOrdinal:String(confirmed)});
    for(let index=0;index<pages.length;index++) {
      const page=pages[index];
      if(!fields(page,header) || page.previewProtocol!==3 || page.kind!=='preview-control-recovery' || !realm(page) || page.capacity!==capacity ||
         false || page.afterOrdinal!==String(nativeIssuedThrough))
        throw new TypeError('Consistent original native recovery pages required');
      if(page.ticket===null) {
        if(index!==pages.length-1 || nativeIssuedThrough!==issued)throw new TypeError('Complete native recovery inventory required');
      }else if(index===pages.length-1 || !retain(page.ticket))throw new TypeError('Exact contiguous original native recovery ticket required');
    }
    if(pages.at(-1).ticket!==null || nativeIssuedThrough!==issued)throw new TypeError('Final native recovery page required');
  }
  // Constructor recovery never posts. The host receives this completed object
  // first, then invokes its next bounded retry poll.
  recovering=false;
  return Object.freeze({retain,acknowledge,retry,
    snapshot:()=>Object.freeze({nativeIssuedThrough:String(nativeIssuedThrough),deliveredThrough:String(deliveredThrough),pending:queue.length,capacity})});
};
