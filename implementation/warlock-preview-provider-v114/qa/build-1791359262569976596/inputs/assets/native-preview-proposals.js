'use strict';
// Pure bounded packetization of the actual Elm policy output. It allocates no
// ordinal and grants no effect authority; the native singleton ingress owns
// admission and purpose issuance. Validate the whole list before posting any.
globalThis.WarlockNativePreviewProposals=function(value){
 const fields=(v,wanted)=>v && typeof v==='object' && !Array.isArray(v) &&
  Object.keys(v).sort().join('\0')===[...wanted].sort().join('\0');
 const counter=v=>typeof v==='string' && /^[1-9][0-9]*$/.test(v) && v.length<=20 && BigInt(v)<=18446744073709551615n;
 const bind=v=>fields(v,['lifetime','session','frontend']) && ['lifetime','session','frontend'].every(k=>counter(v[k]));
 if(!fields(value,['previewProtocol','kind','binding','receiverEpoch','entries']) || value.previewProtocol!==3 ||
    value.kind!=='preview-proposals' || !bind(value.binding) || !counter(value.receiverEpoch) ||
    !Array.isArray(value.entries) || value.entries.length>1065)throw new TypeError('Exact bounded native realm proposals required');
 const wires=[];
 for(const row of value.entries){
  if(!fields(row,['identity','commands']) || typeof row.identity!=='string' || !row.identity ||
     new TextEncoder().encode(row.identity).length>512 || !Array.isArray(row.commands) || row.commands.length!==1 ||
     !row.commands[0] || typeof row.commands[0]!=='object' || Array.isArray(row.commands[0]))
   throw new TypeError('One original command per native proposal');
  const wire=JSON.stringify({...value,entries:[row]});
  if(new TextEncoder().encode(wire).length>4096)throw new TypeError('Original native ingress byte limit');
  wires.push(wire);
 }
 return Object.freeze(wires);
};
