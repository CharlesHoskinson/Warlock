module pin_case {
 type Event=Setup|Capture|Press({actual:bool,owner:bool})|Release(bool)|NativeReceipt({typed:bool,owner:bool,complete:bool})|Observe({lifetime:bool,stack:bool,peer:bool,focus:bool})|Accept|Invalidate|DirectAPI|Retry
 type State={captured:bool,pressed:bool,released:bool,receipt:bool,observed:bool,accepted:bool,current:bool,setup:int,inputs:int,retry:int}
 var s:State
 action init=s'={captured:false,pressed:false,released:false,receipt:false,observed:false,accepted:false,current:true,setup:0,inputs:0,retry:0}
 action fire(e:Event):bool={s'=match e{
 |Setup=>{...s,setup:s.setup+1}
 |Capture=>if(s.current){...s,captured:true}else s
 |Press(v)=>if(s.current and s.captured and v.actual and v.owner){...s,pressed:true,released:false,inputs:s.inputs+1}else s
 |Release(actual)=>{...s,released:s.pressed and actual}
 |NativeReceipt(v)=>{...s,receipt:s.current and s.captured and s.pressed and v.typed and v.owner and v.complete}
 |Observe(v)=>{...s,observed:s.current and v.lifetime and v.stack and v.peer and v.focus}
 |Accept=>{...s,accepted:s.current and s.captured and s.pressed and s.released and s.receipt and s.observed}
 |Invalidate=>{...s,current:false,receipt:false,observed:false,accepted:false}
 |DirectAPI=>s
 |Retry=>s
 }}
 val allProps=all{s.retry==0,s.accepted implies s.current and s.captured and s.pressed and s.released and s.receipt and s.observed and s.inputs>0}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet d=Set(true,false).oneOf();nondet e=Set(Setup,Capture,Press({actual:a,owner:b}),Release(a),NativeReceipt({typed:a,owner:b,complete:c}),Observe({lifetime:a,stack:b,peer:c,focus:d}),Accept,Invalidate,DirectAPI,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action complete=fire(Capture).then(fire(Press({actual:true,owner:true}))).then(fire(Release(true))).then(fire(NativeReceipt({typed:true,owner:true,complete:true}))).then(fire(Observe({lifetime:true,stack:true,peer:true,focus:true}))).then(fire(Accept))
 run actualInputThenReceiptAndStateTest=init.then(complete).then(check(s.accepted))
 run setupCannotCountAsPinTest=init.then(fire(Setup)).then(fire(Accept)).then(check(not(s.accepted)))
 run directAPICannotCountAsFrontendTest=init.then(fire(Capture)).then(fire(DirectAPI)).then(fire(Accept)).then(check(not(s.accepted)))
 run missingReleaseRefusedTest=init.then(fire(Capture)).then(fire(Press({actual:true,owner:true}))).then(fire(NativeReceipt({typed:true,owner:true,complete:true}))).then(fire(Observe({lifetime:true,stack:true,peer:true,focus:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run wrongOwnerInputRefusedTest=init.then(fire(Capture)).then(fire(Press({actual:true,owner:false}))).then(fire(Release(true))).then(fire(Accept)).then(check(not(s.accepted)))
 run staleObservationRefusedTest=init.then(complete).then(fire(Invalidate)).then(fire(Accept)).then(check(not(s.accepted)))
 run malformedReceiptRefusedTest=init.then(fire(Capture)).then(fire(Press({actual:true,owner:true}))).then(fire(Release(true))).then(fire(NativeReceipt({typed:false,owner:true,complete:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run noAutomaticRetryTest=init.then(fire(Retry)).then(check(s.retry==0))
}
