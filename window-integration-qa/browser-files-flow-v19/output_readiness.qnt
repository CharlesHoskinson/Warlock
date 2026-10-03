module output_readiness {
 type Reply=Empty|Exact|Wrong|Malformed|NotList
 type Event=Observe({reply:Reply,before:bool,after:bool,peer:bool,eof:bool,bounded:bool,time:int})|Tick(int)|Changed|OriginalAccept(bool)
 var now:int
 var deadline:int
 var ready:bool
 var failed:bool
 var live:bool
 var accepted:bool
 var observations:int
 action init=all{now'=0,deadline'=15,ready'=false,failed'=false,live'=true,accepted'=false,observations'=0}
 action fire(e:Event):bool=match e{
 |Observe(v)=>all{now'=v.time,deadline'=deadline,live'=(live and v.before and v.after),
   accepted'=accepted,observations'=observations+1,
   failed'=(failed or v.time<now or v.time>=deadline or not(live and v.before and v.after and v.peer and v.eof and v.bounded) or (v.reply!=Empty and v.reply!=Exact)),
   ready'=(not(failed) and v.time>=now and v.time<deadline and live and v.before and v.after and v.peer and v.eof and v.bounded and v.reply==Exact)}
 |Tick(t)=>all{now'=t,deadline'=deadline,live'=live,accepted'=accepted,observations'=observations,
   failed'=(failed or t<now or t>=deadline),ready'=(ready and t>=now and t<deadline and not(failed))}
 |Changed=>all{now'=now,deadline'=deadline,live'=false,accepted'=accepted,observations'=observations,ready'=false,failed'=true}
 |OriginalAccept(v)=>all{now'=now,deadline'=deadline,live'=live,accepted'=v,observations'=observations,ready'=ready,failed'=failed}
 }
 val allProps=deadline==15 and (ready implies live and not(failed) and now<deadline and now>=0)
 action step={nondet t=Set(0,1,14,15,16).oneOf();nondet r=Set(Empty,Exact,Wrong,Malformed,NotList).oneOf();nondet b=Set(true,false).oneOf();nondet e=Set(Observe({reply:r,before:b,after:true,peer:true,eof:true,bounded:true,time:t}),Tick(t),Changed,OriginalAccept(false)).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),now'=now,deadline'=deadline,ready'=ready,failed'=failed,live'=live,accepted'=accepted,observations'=observations}
}
