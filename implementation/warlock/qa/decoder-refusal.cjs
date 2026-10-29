'use strict';
const Elm = require(process.argv[2]).Elm;
const app = Elm.DecoderReplay.init();
const cases = [["malformed-refresh",{"kind":"host-refresh","protocolVersion":3,"extra":true}],["unsupported-refresh",{"kind":"host-refresh","protocolVersion":4}],["missing-version-refresh",{"kind":"host-refresh"}],["malformed-attached",{"kind":"attached","protocolVersion":3,"binding":{}}],["unsupported-attached",{"kind":"attached","protocolVersion":4,"binding":{"lifetime":"17","session":"3","frontend":"1"}}],["unsupported-disconnected",{"kind":"host-disconnected","protocolVersion":4}],["missing-version-disconnected",{"kind":"host-disconnected"}],["extra-disconnected",{"kind":"host-disconnected","protocolVersion":3,"extra":true}],["invalid-envelope",null],["missing-kind",{"protocolVersion":3}],["malformed-projection",{"kind":"action-projection","protocolVersion":3}],["malformed-geometry-attached",{"kind":"geometry-attached","protocolVersion":3}],["malformed-outcome",{"kind":"effect-outcome","protocolVersion":3}],["malformed-recovery",{"kind":"host-recovery-failed","protocolVersion":3,"reason":"invalid"}],["malformed-nested-recovery",{"kind":"host-uncertain","protocolVersion":3,"binding":{"lifetime":"17","session":"3","frontend":"1"},"intent":{}}],["unsupported-geometry-unnegotiated",{"kind":"geometry-facts","protocolVersion":4}],["malformed-geometry-unnegotiated",{"kind":"geometry-facts","protocolVersion":3}],["valid-refresh",{"kind":"host-refresh","protocolVersion":3}],["valid-disconnected",{"kind":"host-disconnected","protocolVersion":3}],["unknown-other-policy",{"kind":"some-other-policy","protocolVersion":3}],["unknown-other-version",{"kind":"some-other-policy","protocolVersion":1}]];
const rows=[];
app.ports.outgoing.subscribe(row => {
  rows.push({name:cases[rows.length][0],input:cases[rows.length][1],...row});
  if(rows.length<cases.length) app.ports.incoming.send(cases[rows.length][1]);
  else {
    const ok=rows.every(r=>r.setupCommandCount===1 && r.priorBinding && r.prior.phase==='Reconciling');
    const invalid=rows.slice(0,17);
    const original=invalid.every(r=>r.sameOperationalModel && r.sameAuthority && r.commandCount===0 && typeof r.refusal==='string' && r.refusal.length>0 && r.refusal.length<=128 && /reject/i.test(r.refusal));
    const positive=rows[17].after.notificationQueued===true && rows[17].commandCount===0 && rows[17].refusal===null;
    const disconnected=rows[18].after.phase==='Detached' && rows[18].commandCount===0 && rows[18].refusal===null;
    const unknown=rows.slice(19).every(r=>r.sameModel && r.commandCount===0 && r.refusal===null);
    console.log(JSON.stringify({rows,checks:{validPrior:ok,originalInvalid:original,validRefresh:positive,validDisconnect:disconnected,unknownPolicyPreserved:unknown},requirementAccepted:false,nativeAcceptance:false}));
    process.exitCode=(ok && original && positive && disconnected && unknown) ? 0 : 1;
  }
});
app.ports.incoming.send(cases[0][1]);
