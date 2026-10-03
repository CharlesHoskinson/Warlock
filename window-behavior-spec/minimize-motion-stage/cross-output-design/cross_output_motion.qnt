/** One canonical decorated atlas and global route, including pixels outside
 * output crops. Capture/readiness carry the observed identity and epoch;
 * output topology and destination readiness are checked before native hide.
 */
module cross_output_motion {
 type Observation = {identity:int,epoch:int}
 type CaptureResult = {identity:int,epoch:int,complete:bool,pixels:int}
 type Presentation = {identity:int,epoch:int,output:int}
 type Event = Capture(CaptureResult) | Ready(Presentation) | Destination(Observation) | Start(Observation) | Tick | Reverse | Finish(Observation) | RemoveOutput(int) | AddOutput(int) | Reduce | Close | Reuse
 type State = {live:bool,identity:int,captured:int,epoch:int,phase:str,intent:bool,minimized:bool,
  completeAtlas:bool,atlasIdentity:int,atlasEpoch:int,atlasPixels:int,nativePixels:int,
  destinationSelected:bool,outputs:Set[int],required:Set[int],ready:Set[int],p:int,fromX:int,fromW:int,toX:int,toW:int,x:int,w:int,
  leftP:int,rightP:int,nativeX:int,savedX:int,stale:bool,beforeMin:bool}
 var s:State
 action init=s'={live:true,identity:1,captured:1,epoch:1,phase:"preparing",intent:true,minimized:false,
  completeAtlas:false,atlasIdentity:0,atlasEpoch:0,atlasPixels:0,nativePixels:107,
  destinationSelected:false,outputs:Set(0,1),required:Set(0,1),ready:Set(),p:0,fromX:80,fromW:80,toX:180,toW:10,x:80,w:80,
  leftP:0,rightP:0,nativeX:80,savedX:80,stale:false,beforeMin:false}
 def current(o:Observation):bool=s.live and s.identity==s.captured and o.identity==s.identity and o.epoch==s.epoch
 action fire(e:Event):bool={
  val b={...s,stale:false,beforeMin:s.minimized}
  s'=match e {
   | Capture(o) => if(not(current({identity:o.identity,epoch:o.epoch})) or s.phase!="preparing" or o.pixels!=s.nativePixels) {...b,stale:true}
     else {...b,completeAtlas:o.complete,atlasIdentity:if(o.complete)o.identity else 0,atlasEpoch:if(o.complete)o.epoch else 0,
      atlasPixels:if(o.complete)o.pixels else 0,phase:if(o.complete)"loading" else "fallback"}
   | Ready(o) => if(not(current({identity:o.identity,epoch:o.epoch})) or s.phase!="loading" or not(s.outputs.contains(o.output)) or not(s.required.contains(o.output))) {...b,stale:true}
     else {...b,ready:s.ready.union(Set(o.output))}
   | Destination(o) => if(not(current(o)) or not(s.outputs.contains(1)) or s.phase!="loading") {...b,stale:true} else {...b,destinationSelected:true}
   | Start(o) => if(not(current(o)) or s.phase!="loading" or not(s.completeAtlas) or s.atlasEpoch!=s.epoch or not(s.required.subseteq(s.ready)) or not(s.required.subseteq(s.outputs)) or not(s.destinationSelected)) {...b,stale:true}
     else {...b,phase:"running",minimized:if(s.intent)true else s.minimized}
   | Tick => if(s.phase!="running")b else {
     val p=if(s.p<10)s.p+1 else 10
     {...b,p:p,leftP:p,rightP:p,x:(s.fromX*(10-p)+s.toX*p)/10,w:(s.fromW*(10-p)+s.toW*p)/10}
   }
   | Reverse => if(not(s.live))b else {...b,epoch:s.epoch+1,captured:s.identity,phase:"preparing",intent:not(s.intent),ready:Set(),completeAtlas:false,atlasEpoch:0,destinationSelected:false,
       p:0,leftP:0,rightP:0,fromX:s.x,fromW:s.w,toX:if(s.intent)80 else 180,toW:if(s.intent)80 else 10}
   | Finish(o) => if(not(current(o)) or s.phase!="running") {...b,stale:true} else {...b,phase:"idle",minimized:s.intent}
   | RemoveOutput(out) => {...b,outputs:s.outputs.exclude(Set(out)),ready:Set(),completeAtlas:false,atlasEpoch:0,destinationSelected:false,
       epoch:s.epoch+1,phase:"idle",minimized:if(s.live and s.identity==s.captured)s.intent else s.minimized}
   | AddOutput(out) => {...b,outputs:s.outputs.union(Set(out))}
   | Reduce => {...b,epoch:s.epoch+1,phase:"idle",ready:Set(),completeAtlas:false,atlasEpoch:0,destinationSelected:false,minimized:if(s.live and s.identity==s.captured)s.intent else s.minimized}
   | Close => {...b,epoch:s.epoch+1,live:false,phase:"idle",ready:Set(),completeAtlas:false,atlasIdentity:0,atlasEpoch:0,atlasPixels:0,destinationSelected:false}
   | Reuse => if(s.live)b else {...b,epoch:s.epoch+1,identity:s.identity+1,captured:0,live:true,intent:false,minimized:false,phase:"idle",
       completeAtlas:false,atlasIdentity:0,atlasEpoch:0,atlasPixels:0,nativePixels:(s.identity+1)*100+7,ready:Set(),destinationSelected:false,nativeX:42,savedX:42}
  }
 }
 val leftW=if(s.x>=100)0 else if(s.x+s.w<=100)s.w else 100-s.x
 val rightW=s.w-leftW
 val coverage=leftW+rightW==s.w and leftW>=0 and rightW>=0
 val sharedClock=s.leftP==s.rightP and s.leftP==s.p
 val noHideBeforeAllPresent=(s.phase=="running") implies (s.live and s.identity==s.captured and s.completeAtlas and s.atlasEpoch==s.epoch and s.required.subseteq(s.ready) and s.required.subseteq(s.outputs) and s.destinationSelected)
 val pixelsBelongToCurrentIdentity=s.atlasIdentity!=0 implies (s.live and s.atlasIdentity==s.identity and s.atlasPixels==s.nativePixels)
 val freshCompleteAtlas=s.completeAtlas implies (s.atlasIdentity==s.identity and s.atlasEpoch==s.epoch)
 val geometryPreserved=s.nativeX==s.savedX
 val staleCannotCommit=s.stale implies s.minimized==s.beforeMin
 val allProps=coverage and sharedClock and noHideBeforeAllPresent and pixelsBelongToCurrentIdentity and freshCompleteAtlas and geometryPreserved and staleCannotCommit
 action step={
  val now={identity:s.identity,epoch:s.epoch}
  val old={identity:s.identity-1,epoch:s.epoch-1}
  nondet e=Set(Capture({identity:s.identity,epoch:s.epoch,complete:true,pixels:s.nativePixels}),Capture({identity:s.identity,epoch:s.epoch,complete:false,pixels:s.nativePixels}),Capture({identity:s.identity-1,epoch:s.epoch-1,complete:true,pixels:s.nativePixels-100}),
    Capture({identity:s.identity,epoch:s.epoch,complete:true,pixels:s.nativePixels-100}),Ready({identity:s.identity,epoch:s.epoch,output:0}),Ready({identity:s.identity,epoch:s.epoch,output:1}),Ready({identity:s.identity-1,epoch:s.epoch-1,output:0}),Destination(now),Destination(old),Start(now),Start(old),
    Tick,Reverse,Finish(now),Finish(old),RemoveOutput(0),RemoveOutput(1),AddOutput(0),AddOutput(1),Reduce,Close,Reuse).oneOf();fire(e)
 }
}
