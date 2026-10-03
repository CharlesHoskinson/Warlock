module frame_capture {
 type State={generation:int,token:int,x:int,syncSequence:int,pendingGeneration:int,pendingToken:int,pendingX:int,pendingSequence:int,swappedSequence:int,records:List[{generation:int,token:int,x:int,sequence:int}],beforeRecords:int,stale:bool}
 type Event=Sync(int) | Swap(int) | Move | Reverse | Replace
 var s:State
 action init=s'={generation:1,token:1,x:0,syncSequence:0,pendingGeneration:0,pendingToken:0,pendingX:0,pendingSequence:0,swappedSequence:0,records:List(),beforeRecords:0,stale:false}
 action fire(e:Event):bool={
  val b={...s,beforeRecords:s.records.length(),stale:false}
  s'=match e {
   | Sync(g)=>if(g!=s.generation){...b,stale:true} else {...b,syncSequence:s.syncSequence+1,pendingGeneration:s.generation,pendingToken:s.token,pendingX:s.x,pendingSequence:s.syncSequence+1}
   | Swap(g)=>if(g!=s.generation or s.pendingGeneration!=g or s.pendingSequence<=s.swappedSequence){...b,stale:true} else {...b,swappedSequence:s.pendingSequence,records:s.records.append({generation:g,token:s.pendingToken,x:s.pendingX,sequence:s.pendingSequence}).slice(if(s.records.length()>=8)s.records.length()-7 else 0,s.records.length()+1)}
   | Move=>{...b,x:s.x+1}
   | Reverse=>{...b,token:s.token+1}
   | Replace=>{...b,generation:s.generation+1,pendingGeneration:0,pendingSequence:0}
  }
 }
 val staleCannotRecord=s.stale implies s.records.length()==s.beforeRecords
 val bounded=s.records.length()<=8
 val monotonic=s.records.indices().forall(i=>i==0 or s.records.nth(i).sequence>s.records.nth(i-1).sequence)
 val allProps=staleCannotRecord and bounded and monotonic
 action step={nondet e=Set(Sync(s.generation),Sync(s.generation-1),Swap(s.generation),Swap(s.generation-1),Move,Reverse,Replace).oneOf();fire(e)}
}
