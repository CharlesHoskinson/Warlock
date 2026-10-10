// UI-019 outputs-return; CWaylandBackend::createOutput and initial configure ACK.
// One parent output, successful nonblocking flush, no incoming events assumed.
// Backpressure/write readiness, hardware, pixels and cross-channel delays are outside this model.
module output_transport {
 var s:{stage:str,alive:bool,acked:bool,ready:bool}
 action init=s'={stage:"absent",alive:true,acked:false,ready:false}
 action create=all{s.alive,s.stage=="absent",s'={...s,stage:"flushed"}}
 action legacyCreate=all{s.alive,s.stage=="absent",s'={...s,stage:"queued"}}
 action configure=all{s.alive,s.stage=="flushed",s'={...s,stage:"configured"}}
 action acknowledge=all{s.alive,s.stage=="configured",s'={...s,stage:"acked",acked:true}}
 action publish=all{s.alive,s.acked,s.stage=="acked",s'={...s,stage:"published",ready:true}}
 action parentLost=s'={...s,stage:"failed",alive:false,ready:false}
 action idle=s'=s
 action step=any{create,configure,acknowledge,publish,parentLost,idle}
 val safety=not(s.ready) or (s.alive and s.acked and s.stage=="published")
 val returned=s.ready
 val failed=not(s.alive) and not(s.ready)
}
