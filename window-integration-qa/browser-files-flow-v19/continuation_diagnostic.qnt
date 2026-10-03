module continuation_diagnostic {
 type Observation={core:int,seat:int,surface:bool,owner:int,session:int,value:int,caret:int,trusted:bool}
 type Event=Before|Ack(int)|Poll(Observation)|Accept|Change|ReadError
 pure val good={core:1,seat:1,surface:true,owner:1,session:1,value:2,caret:2,trusted:true}
 var prepared:bool
 var ack:bool
 var observed:bool
 var matched:bool
 var caret:bool
 var trusted:bool
 var accepted:bool
 var logs:int
 var seat:int
 var core:int
 action init=all{prepared'=false,ack'=false,observed'=false,matched'=false,caret'=false,trusted'=false,accepted'=false,logs'=0,seat'=0,core'=0}
 action fire(e:Event):bool=match e {
   |Before=>all{prepared'=true,ack'=false,observed'=false,matched'=false,caret'=false,trusted'=false,accepted'=false,logs'=logs+1,seat'=seat,core'=core}
   |Ack(code)=>all{prepared'=prepared,ack'=(code==0),observed'=observed,matched'=matched,caret'=caret,trusted'=trusted,accepted'=false,logs'=logs+1,seat'=seat,core'=core}
   |Poll(o)=>all{prepared'=prepared,ack'=ack,observed'=true,
      matched'=(prepared and o.owner==1 and o.session==1 and o.value==2),caret'=(o.caret==2),trusted'=o.trusted,
      accepted'=false,logs'=logs+1,seat'=o.seat,core'=o.core}
   |Accept=>all{prepared'=prepared,ack'=ack,observed'=observed,matched'=matched,caret'=caret,trusted'=trusted,
      accepted'=(prepared and ack and observed and matched and caret and trusted),logs'=logs,seat'=seat,core'=core}
   |Change=>all{prepared'=false,ack'=false,observed'=false,matched'=false,caret'=false,trusted'=false,accepted'=false,logs'=logs+1,seat'=seat,core'=core}
   |ReadError=>all{prepared'=prepared,ack'=ack,observed'=false,matched'=false,caret'=false,trusted'=false,accepted'=false,logs'=logs+1,seat'=seat,core'=core}
 }
 val allProps=accepted implies prepared and ack and observed and matched and caret and trusted
 action step={nondet e=Set(Before,Ack(0),Ack(1),Poll(good),Poll({...good,value:1}),
   Poll({...good,seat:2}),Poll({...good,trusted:false}),Change,ReadError,Accept).oneOf();fire(e)}
}
