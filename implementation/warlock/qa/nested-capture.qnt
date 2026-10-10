// ELM-UX-021 supporting original combined native recording.
// One compositor thread, two live outputs; asynchronous parent callbacks may stop.
// Handoff: CScreenshareFrame::share -> deferred live request -> renderMonitor(commit=true).
// Real permissions/copy, compositor lock rendering, buffer sizes and failures stay native.
// This model proves neither pixels, physical presentation nor wall-clock completion.
module nested_capture {
 type Output = {live: bool, pending: bool, request: bool, armed: bool, committed: bool, presented: bool, copies: int}
 var s: int -> Output
 pure val fresh = {live:true,pending:true,request:false,armed:false,committed:false,presented:false,copies:0}
 action init = s'=Map(0->fresh,1->fresh)
 val safety = s.keys().forall(i => s.get(i).copies<=1 and (s.get(i).copies==0 or s.get(i).committed) and (not(s.get(i).presented) or s.get(i).committed))
 action request(i: int): bool = all {s.get(i).live,not(s.get(i).request),s.get(i).copies==0,s'=s.set(i,{...s.get(i),request:true,armed:true})}
 action demand(i: int): bool = all {s.get(i).live,s.get(i).request,s.get(i).armed,s'=s.set(i,{...s.get(i),armed:false,committed:true,copies:1})}
 action retire(i: int): bool = all {s.get(i).live,s'=s.set(i,{...s.get(i),live:false,request:false,armed:false})}
 action parentDone(i: int): bool = all {s.get(i).live,s.get(i).committed,s'=s.set(i,{...s.get(i),pending:false,presented:true})}
 action failed(i: int): bool = all {s.get(i).live,s.get(i).armed,s'=s.set(i,{...s.get(i),request:false,armed:false})}
 val bothCopied = s.keys().forall(i=>s.get(i).copies==1 and s.get(i).pending)
 val retiredNotCopied = not(s.get(0).live) and s.get(0).copies==0 and s.get(1).copies==1
 val notSyntheticPresentation = s.get(0).copies==1 and not(s.get(0).presented)
 action step = { nondet i = oneOf(Set(0,1)); any {request(i),demand(i),retire(i),parentDone(i),failed(i),s'=s} }
}
