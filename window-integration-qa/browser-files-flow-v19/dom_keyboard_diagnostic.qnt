module dom_keyboard_diagnostic {
 type Record={token:int,page:int,key:int,prevented:bool,capture:bool,bubble:bool}
 type Event=Capture({token:int,page:int,key:int,prevented:bool})|Bubble({token:int,page:int,key:int,prevented:bool})|Reload|Truncate|Exhaust|OriginalAccept(bool)
 var page:int
 var records:int->Record
 var exhausted:bool
 var accepted:bool
 var orphan:bool
 action init=all{page'=1,records'=Map(),exhausted'=false,accepted'=false,orphan'=false}
 action fire(e:Event):bool=match e{
  |Capture(v)=>all{page'=page,exhausted'=exhausted,accepted'=accepted,orphan'=orphan,
    records'=if(not(exhausted) and v.page==page and v.token>0 and v.token<=64 and not(records.keys().contains(v.token)))records.put(v.token,{token:v.token,page:v.page,key:v.key,prevented:v.prevented,capture:true,bubble:false})else records}
  |Bubble(v)=>all{page'=page,exhausted'=exhausted,accepted'=accepted,
    orphan'=(not(records.keys().contains(v.token)) or v.page!=page),
    records'=if(not(exhausted) and records.keys().contains(v.token) and v.page==page and records.get(v.token).page==v.page and records.get(v.token).key==v.key)records.put(v.token,{...records.get(v.token),prevented:v.prevented,bubble:true})else records}
  |Reload=>all{page'=page+1,records'=Map(),exhausted'=false,accepted'=accepted,orphan'=false}
  |Truncate=>all{page'=page,records'=Map(),exhausted'=exhausted,accepted'=accepted,orphan'=orphan}
  |Exhaust=>all{page'=page,records'=records,exhausted'=true,accepted'=accepted,orphan'=orphan}
  |OriginalAccept(value)=>all{page'=page,records'=records,exhausted'=exhausted,accepted'=value,orphan'=orphan}
 }
 val allProps=records.keys().forall(k=>records.get(k).capture and records.get(k).page==page and k>0 and k<=64)
 action step={nondet token=Set(0,1,2,65).oneOf();nondet e=Set(Capture({token:token,page:1,key:45,prevented:false}),Bubble({token:token,page:1,key:45,prevented:true}),Reload,Truncate,Exhaust,OriginalAccept(false),OriginalAccept(true)).oneOf();fire(e)}
 action check(value:bool):bool=all{assert(value),page'=page,records'=records,exhausted'=exhausted,accepted'=accepted,orphan'=orphan}
}
