module frontend_case {
 type Event=Open({actual:bool,owner:bool})|Capture({typed:bool,owner:bool})|Witness({current:bool,layer:bool,eligible:bool})|Press({actual:bool,route:bool})|Release(bool)|Receipt({normal:bool,typed:bool,owner:bool})|Observe({pin:bool,band:bool,peer:bool,focus:bool})|Accept|Change|DirectInvoke|DiagnosticQuery|Retry
 type State={open:bool,captured:bool,witnessed:bool,pressed:bool,released:bool,receipt:bool,observed:bool,current:bool,accepted:bool,inputs:int,retry:int}
 var s:State
 action init=s'={open:false,captured:false,witnessed:false,pressed:false,released:false,receipt:false,observed:false,current:true,accepted:false,inputs:0,retry:0}
 action fire(e:Event):bool={s'=match e {
 |Open(v)=>{...s,open:v.actual and v.owner,captured:false,witnessed:false,pressed:false,released:false,receipt:false,observed:false,current:true,accepted:false}
 |Capture(v)=>{...s,captured:s.current and s.open and v.typed and v.owner,witnessed:false,accepted:false}
 |Witness(v)=>{...s,witnessed:s.current and s.captured and v.current and v.layer and v.eligible,accepted:false}
 |Press(v)=>if(s.current and s.witnessed and v.actual and v.route){...s,pressed:true,released:false,receipt:false,observed:false,accepted:false,inputs:s.inputs+1}else s
 |Release(v)=>{...s,released:s.pressed and v,accepted:false}
 |Receipt(v)=>{...s,receipt:s.current and s.pressed and v.normal and v.typed and v.owner,accepted:false}
 |Observe(v)=>{...s,observed:s.current and v.pin and v.band and v.peer and v.focus,accepted:false}
 |Accept=>{...s,accepted:s.current and s.open and s.captured and s.witnessed and s.pressed and s.released and s.receipt and s.observed}
 |Change=>{...s,current:false,witnessed:false,receipt:false,observed:false,accepted:false}
 |DirectInvoke=>s
 |DiagnosticQuery=>s
 |Retry=>s
 }}
 val allProps=all{s.retry==0,s.accepted implies s.current and s.open and s.captured and s.witnessed and s.pressed and s.released and s.receipt and s.observed and s.inputs>0}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet d=Set(true,false).oneOf();nondet e=Set(Open({actual:a,owner:b}),Capture({typed:a,owner:b}),Witness({current:a,layer:b,eligible:c}),Press({actual:a,route:b}),Release(a),Receipt({normal:a,typed:b,owner:c}),Observe({pin:a,band:b,peer:c,focus:d}),Accept,Change,DirectInvoke,DiagnosticQuery,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action ready=fire(Open({actual:true,owner:true})).then(fire(Capture({typed:true,owner:true}))).then(fire(Witness({current:true,layer:true,eligible:true})))
 action input=fire(Press({actual:true,route:true})).then(fire(Release(true)))
 action complete=fire(Receipt({normal:true,typed:true,owner:true})).then(fire(Observe({pin:true,band:true,peer:true,focus:true}))).then(fire(Accept))
 run genuineFrontendTest=init.then(ready).then(input).then(complete).then(check(s.accepted))
 run diagnosticCannotOpenTest=init.then(fire(DiagnosticQuery)).then(input).then(complete).then(check(not(s.accepted)))
 run directNativeCannotInputTest=init.then(ready).then(fire(DirectInvoke)).then(complete).then(check(not(s.accepted)))
 run wrongMemberCaptureRefusedTest=init.then(fire(Open({actual:true,owner:true}))).then(fire(Capture({typed:true,owner:false}))).then(input).then(complete).then(check(not(s.accepted)))
 run wrongLayerRefusedTest=init.then(ready).then(fire(Witness({current:true,layer:false,eligible:true}))).then(input).then(complete).then(check(not(s.accepted)))
 run disabledRowRefusedTest=init.then(ready).then(fire(Witness({current:true,layer:true,eligible:false}))).then(input).then(complete).then(check(not(s.accepted)))
 run wrongKeyboardRouteRefusedTest=init.then(ready).then(fire(Press({actual:true,route:false}))).then(fire(Release(true))).then(complete).then(check(not(s.accepted)))
 run missingReleaseRefusedTest=init.then(ready).then(fire(Press({actual:true,route:true}))).then(complete).then(check(not(s.accepted)))
 run malformedReceiptRefusedTest=init.then(ready).then(input).then(fire(Receipt({normal:true,typed:false,owner:true}))).then(fire(Observe({pin:true,band:true,peer:true,focus:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run helperUncertainRefusedTest=init.then(ready).then(input).then(fire(Receipt({normal:false,typed:true,owner:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run generationChangeRefusedTest=init.then(ready).then(input).then(fire(Change)).then(complete).then(check(not(s.accepted)))
 run peerMutationRefusedTest=init.then(ready).then(input).then(fire(Receipt({normal:true,typed:true,owner:true}))).then(fire(Observe({pin:true,band:true,peer:false,focus:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run separateFocusRoutesRequiredTest=init.then(ready).then(input).then(fire(Receipt({normal:true,typed:true,owner:true}))).then(fire(Observe({pin:true,band:true,peer:true,focus:false}))).then(fire(Accept)).then(check(not(s.accepted)))
 run staleReceiptAfterReopenRefusedTest=init.then(ready).then(input).then(complete).then(fire(Open({actual:true,owner:true}))).then(fire(Receipt({normal:true,typed:true,owner:true}))).then(fire(Accept)).then(check(not(s.accepted)))
 run noRetryTest=init.then(fire(Retry)).then(check(s.retry==0))
}
