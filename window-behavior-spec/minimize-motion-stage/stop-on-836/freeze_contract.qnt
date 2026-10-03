/** An exact captured identity reservation holds current pixels before queries.
 * Holding has no native authority. Latest token validation/readiness is required;
 * preparation cannot advance the held rectangle. Reject/timeout/reload clear it.
 */
module freeze_contract {
 type Event = Tick | Reserve(int) | Validate(int) | Begin(int) | Ready(int) | Finish(int) | Reject(int) | Timeout(int) | Reduce(int) | Reload(int) | Replace | Close | Reuse
 type State = {live:bool,identity:int,captured:int,epoch:int,phase:str,held:bool,rect:int,frozen:int,from:int,pixels:int,frozenPixels:int,intent:bool,minimized:bool,validated:bool,nativeRect:int,savedRect:int,stale:bool,beforeMin:bool,beforeRect:int}
 var s:State
 action init=s'={live:true,identity:1,captured:1,epoch:1,phase:"running",held:false,rect:37,frozen:37,from:0,pixels:99,frozenPixels:99,intent:true,minimized:true,validated:true,nativeRect:42,savedRect:42,stale:false,beforeMin:true,beforeRect:37}
 action fire(e:Event):bool={
  val b={...s,stale:false,beforeMin:s.minimized,beforeRect:s.rect}
  s'=match e {
   | Tick => if(s.phase=="running" and not(s.held)) {...b,rect:if(s.rect<100)s.rect+1 else 100} else b
   | Reserve(id) => if(not(s.live) or id!=s.identity) {...b,stale:true} else {...b,epoch:s.epoch+1,phase:"validating",captured:id,held:true,frozen:s.rect,frozenPixels:s.pixels,validated:false,intent:not(s.intent)}
   | Validate(t) => if(t!=s.epoch or s.phase!="validating" or not(s.live) or s.captured!=s.identity) {...b,stale:true} else {...b,validated:true,phase:"preparing"}
   | Begin(t) => if(t!=s.epoch or s.phase!="preparing" or not(s.validated) or not(s.live) or s.captured!=s.identity) {...b,stale:true} else {...b,from:s.rect,pixels:s.frozenPixels,phase:"loading",held:false}
   | Ready(t) => if(t!=s.epoch or s.phase!="loading" or not(s.live) or s.captured!=s.identity) {...b,stale:true} else {...b,phase:"running",minimized:if(s.intent)true else s.minimized}
   | Finish(t) => if(t!=s.epoch or s.phase!="running" or not(s.live) or s.captured!=s.identity) {...b,stale:true} else {...b,phase:"idle",held:false,minimized:s.intent}
   | Reject(t) => if(t!=s.epoch) {...b,stale:true} else {...b,phase:"idle",held:false}
   | Timeout(currentId) => {...b,epoch:s.epoch+1,phase:"idle",held:false,minimized:if(s.live and currentId==s.captured and currentId==s.identity)s.intent else s.minimized}
   | Reduce(currentId) => {...b,epoch:s.epoch+1,phase:"idle",held:false,minimized:if(s.live and currentId==s.captured and currentId==s.identity)s.intent else s.minimized}
   | Reload(currentId) => {...b,epoch:s.epoch+1,phase:"idle",held:false,minimized:if(s.live and currentId==s.captured and currentId==s.identity)s.intent else s.minimized}
   | Replace => {...b,identity:s.identity+1,minimized:false,nativeRect:73,savedRect:73}
   | Close => {...b,live:false,epoch:s.epoch+1,phase:"idle",held:false,validated:false}
   | Reuse => if(s.live)b else {...b,live:true,identity:s.identity+1,epoch:s.epoch+1,phase:"idle",held:false,intent:false,minimized:false,validated:false,nativeRect:73,savedRect:73}
  }
 }
 action step={nondet e=Set(Tick,Reserve(s.identity),Reserve(s.identity-1),Validate(s.epoch),Validate(s.epoch-1),Begin(s.epoch),Begin(s.epoch-1),Ready(s.epoch),Ready(s.epoch-1),Finish(s.epoch),Finish(s.epoch-1),Reject(s.epoch),Timeout(s.identity),Timeout(s.identity-1),Reduce(s.identity),Reload(s.identity),Replace,Close,Reuse).oneOf();fire(e)}
 val frozenDoesNotMove=s.held implies s.rect==s.frozen
 val geometryPreserved=s.nativeRect==s.savedRect
 val staleCannotCommit=s.stale implies (s.minimized==s.beforeMin and s.rect==s.beforeRect)
 val noDeadHold=not(s.live) implies not(s.held)
 val validationBeforeTween=(s.phase=="loading" or s.phase=="running") implies s.validated
 val frozenPixelsPreserved=s.pixels==s.frozenPixels
 val allProps=frozenPixelsPreserved and frozenDoesNotMove and geometryPreserved and staleCannotCommit and noDeadHold and validationBeforeTween
}
