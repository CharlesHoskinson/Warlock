/** Native readiness requires matched actual render-submission observations.
 * Geometry/digest assigned by the route are expected values, not pixel proof.
 * The trusted renderer probe observes an exact atlas identity/epoch and rect.
 * Per-output presentation sequence/time is monotonic. Latest presented frame
 * controls endpoint acknowledgement; a newer nonendpoint clears that output.
 */
module presentation {
 type Observation={identity:int,epoch:int,output:int,sequence:int,time:int,x:int,digest:int}
 type Event=Submit(Observation) | Present(Observation) | Tick | Validate | Reverse | Cancel | Finish | Reuse
 type State={id:int,epoch:int,phase:str,x:int,digest:int,validated:bool,submittedSeq:List[int],submittedX:List[int],submittedTime:List[int],inflight:List[Observation],presentedSeq:List[int],presentedTime:List[int],ready:Set[int],endReady:Set[int],nativeMin:bool,stale:bool,beforeNative:bool}
 var s:State
 action init=s'={id:1,epoch:1,phase:"provisional",x:5,digest:107,validated:false,submittedSeq:List(0,0),submittedX:List(0,0),submittedTime:List(0,0),inflight:List(),presentedSeq:List(0,0),presentedTime:List(0,0),ready:Set(),endReady:Set(),nativeMin:false,stale:false,beforeNative:false}
 def valid(o:Observation):bool=(s.phase=="provisional" or s.phase=="running") and o.identity==s.id and o.epoch==s.epoch and o.digest==s.digest and o.output>=0 and o.output<2
 action fire(e:Event):bool={
  val b={...s,stale:false,beforeNative:s.nativeMin}
  s'=match e {
   | Submit(o)=>if(not(valid(o)) or o.x!=s.x or o.sequence<=s.submittedSeq.nth(o.output) or o.time<s.submittedTime.nth(o.output)){...b,stale:true}
       else {...b,submittedSeq:s.submittedSeq.replaceAt(o.output,o.sequence),submittedX:s.submittedX.replaceAt(o.output,o.x),submittedTime:s.submittedTime.replaceAt(o.output,o.time),inflight:s.inflight.select(q=>q.output!=o.output or q.sequence>o.sequence-4).append(o)}
   | Present(o)=>if(not(valid(o)) or s.inflight.select(q=>q.output==o.output and q.sequence==o.sequence and q.x==o.x and q.digest==o.digest and q.identity==o.identity and q.epoch==o.epoch and o.time>=q.time).length()==0 or o.sequence<=s.presentedSeq.nth(o.output) or o.time<=s.presentedTime.nth(o.output)){...b,stale:true}
       else {...b,inflight:s.inflight.select(q=>q.output!=o.output or q.sequence>o.sequence),presentedSeq:s.presentedSeq.replaceAt(o.output,o.sequence),presentedTime:s.presentedTime.replaceAt(o.output,o.time),ready:s.ready.union(Set(o.output)),endReady:if(o.x==10)s.endReady.union(Set(o.output)) else s.endReady.exclude(Set(o.output))}
   | Tick=>if(s.phase=="provisional" or s.phase=="running"){...b,x:if(s.x<10)s.x+1 else 10} else b
   | Validate=>if(s.phase!="provisional")b else {...b,phase:"running",validated:true}
   | Reverse=>{...b,epoch:s.epoch+1,phase:"provisional",validated:false,ready:Set(),endReady:Set(),submittedSeq:List(0,0),submittedX:List(0,0),submittedTime:List(0,0),inflight:List(),presentedSeq:List(0,0),presentedTime:List(0,0)}
   | Cancel=>{...b,phase:"cancelled",validated:false,ready:Set(),endReady:Set(),inflight:List()}
   | Finish=>if(s.phase!="running" or not(s.validated) or s.x!=10 or s.endReady!=Set(0,1)){...b,stale:true} else {...b,phase:"idle",nativeMin:true}
   | Reuse=>{...b,id:s.id+1,epoch:s.epoch+1,phase:"cancelled",nativeMin:false,digest:(s.id+1)*100+7,validated:false,ready:Set(),endReady:Set(),inflight:List()}
  }
 }
 val staleCannotCommit=s.stale implies s.nativeMin==s.beforeNative
 val committedNeedsEndpointProof=(s.phase=="idle" and s.nativeMin) implies (s.validated and s.endReady==Set(0,1) and s.presentedSeq.nth(0)>0 and s.presentedSeq.nth(1)>0)
 val boundedCurrentSubmissions=s.inflight.indices().forall(i=>s.inflight.nth(i).identity==s.id and s.inflight.nth(i).epoch==s.epoch and s.inflight.nth(i).digest==s.digest) and s.inflight.select(o=>o.output==0).length()<=4 and s.inflight.select(o=>o.output==1).length()<=4
 val allProps=staleCannotCommit and committedNeedsEndpointProof and boundedCurrentSubmissions
 action step={
  val o={identity:s.id,epoch:s.epoch,output:0,sequence:s.submittedSeq.nth(0)+1,time:if(s.submittedTime.nth(0)>s.presentedTime.nth(0))s.submittedTime.nth(0)+1 else s.presentedTime.nth(0)+1,x:s.x,digest:s.digest}
  val r={identity:s.id,epoch:s.epoch,output:1,sequence:s.submittedSeq.nth(1)+1,time:if(s.submittedTime.nth(1)>s.presentedTime.nth(1))s.submittedTime.nth(1)+1 else s.presentedTime.nth(1)+1,x:s.x,digest:s.digest}
  val delayed=s.inflight.foldl(Set(),(events,q)=>events.union(Set(Present({...q,time:if(q.time>s.presentedTime.nth(q.output))q.time+1 else s.presentedTime.nth(q.output)+1}))))
  nondet e=Set(Submit(o),Submit(r),Present({...o,sequence:s.submittedSeq.nth(0),x:s.submittedX.nth(0)}),Present({...r,sequence:s.submittedSeq.nth(1),x:s.submittedX.nth(1)}),Present({...o,time:s.presentedTime.nth(0)-1}),Present({...o,digest:s.digest-100}),Present({...o,identity:s.id-1}),Present({...o,x:999}),Tick,Validate,Reverse,Cancel,Finish,Reuse).union(delayed).oneOf();fire(e)
 }
}
