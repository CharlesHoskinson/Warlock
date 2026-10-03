module transport_dispatch {
 type Event=WriteFrame | WriteCallback | Drain | Dispatch | Finish | Reserve | Close | Fail
 type State={pipe:List[bool],queue:List[int],busy:bool,workingEpoch:int,epoch:int,failed:bool,alive:bool,closed:bool,normal:bool,effect:bool,effectEpoch:int,drained:int}
 var s:State
 action init=s'={pipe:List(),queue:List(),busy:false,workingEpoch:0,epoch:1,failed:false,alive:true,closed:false,normal:false,effect:false,effectEpoch:0,drained:0}
 action fire(e:Event):bool={
  val b={...s,effect:false}
  s'=match e {
   | WriteFrame=>if(s.alive and s.pipe.length()<4){...b,pipe:s.pipe.append(false)} else b
   | WriteCallback=>if(s.alive and s.pipe.length()<4){...b,pipe:s.pipe.append(true)} else b
   | Drain=>if(s.pipe.length()>0){
      val callback=s.pipe.head()
      val d={...b,pipe:s.pipe.tail(),drained:s.drained+1}
      if(callback and not(s.failed)){
       if(s.queue.length()<2){...d,queue:s.queue.append(s.epoch)} else {...d,failed:true,alive:false}
      } else d
     } else b
   | Dispatch=>if(not(s.failed) and not(s.busy) and s.queue.length()>0){...b,busy:true,workingEpoch:s.queue.head(),queue:s.queue.tail()} else b
   | Finish=>if(s.busy){...b,busy:false,effect:not(s.failed) and not(s.closed) and s.workingEpoch==s.epoch,effectEpoch:s.workingEpoch} else b
   | Reserve=>{...b,epoch:s.epoch+1}
   | Close=>{...b,closed:true,alive:false,normal:not(s.failed) and not(s.busy) and s.queue.length()==0 and s.pipe.length()==0}
   | Fail=>{...b,failed:true,alive:false,normal:false}
  }
 }
 val latestOnly=s.effect implies (not(s.failed) and not(s.closed) and s.effectEpoch==s.epoch)
 val normalMeansComplete=s.normal implies (s.closed and not(s.failed) and not(s.busy) and s.queue.length()==0 and s.pipe.length()==0)
 val failedRetiresActor=s.failed implies not(s.alive)
 val queuesBounded=s.pipe.length()<=4 and s.queue.length()<=2
 val allProps=latestOnly and normalMeansComplete and failedRetiresActor and queuesBounded
 action step={nondet e=Set(WriteFrame,WriteCallback,Drain,Dispatch,Finish,Reserve,Close,Fail).oneOf();fire(e)}
}
