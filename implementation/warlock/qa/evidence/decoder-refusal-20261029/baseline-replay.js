'use strict';
const Elm = require(process.argv[2]).Elm;
const app = Elm.DecoderReplay.init();
const cases = [
  ['malformed-refresh', {kind:'host-refresh',protocolVersion:3,extra:true}],
  ['unsupported-refresh', {kind:'host-refresh',protocolVersion:4}],
  ['valid-refresh', {kind:'host-refresh',protocolVersion:3}],
  ['valid-disconnected', {kind:'host-disconnected',protocolVersion:3}],
  ['malformed-attached', {kind:'attached',protocolVersion:4,binding:{lifetime:'17',session:'3',frontend:'1'}}],
  ['unknown-other-policy', {kind:'some-other-policy',protocolVersion:3}]
];
const rows=[];
app.ports.outgoing.subscribe(row => {
  rows.push({name:cases[rows.length][0],input:cases[rows.length][1],...row});
  if(rows.length<cases.length) app.ports.incoming.send(cases[rows.length][1]);
  else {
    const ok=rows.every(r=>r.setupCommandCount===1 && r.priorBinding && r.prior.phase==='Reconciling');
    const invalid=rows.slice(0,2);
    const original=invalid.every(r=>r.sameAuthority && r.commandCount===0 && r.afterNotice!==r.priorNotice && /reject|refus/i.test(r.afterNotice));
    const positive=rows[2].after.notificationQueued===true && rows[2].commandCount===0;
    const disconnected=rows[3].after.phase==='Detached' && rows[3].commandCount===0;
    const unknown=rows[5].sameModel && rows[5].commandCount===0;
    console.log(JSON.stringify({rows,checks:{validPrior:ok,originalInvalid:original,validRefresh:positive,validDisconnect:disconnected,unknownPolicyPreserved:unknown},requirementAccepted:false,nativeAcceptance:false}));
    process.exitCode=(ok && original && positive && disconnected && unknown) ? 0 : 1;
  }
});
app.ports.incoming.send(cases[0][1]);
