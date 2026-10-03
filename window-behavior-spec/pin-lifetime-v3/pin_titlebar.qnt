module pin_titlebar {
 type Event=Down({reserved:bool,owner:bool,box:bool})|ChangeCore|ChangeSeat|Call|Observe|Release|Accept|GenericFocus|Retry
 type State={reserved:bool,owner:bool,box:bool,down:bool,released:bool,core:bool,seat:bool,calls:int,observed:bool,accepted:bool,repair:int,retry:int}
 var s:State
 action init=s'={reserved:false,owner:false,box:false,down:false,released:false,core:true,seat:true,calls:0,observed:false,accepted:false,repair:0,retry:0}
 action fire(e:Event):bool={s'=match e{
 |Down(v)=>if(not(s.down)){...s,reserved:v.reserved,owner:v.owner,box:v.box,down:true,released:false,observed:false,accepted:false}else s
 |ChangeCore=>{...s,core:false,observed:false,accepted:false}
 |ChangeSeat=>{...s,seat:false,observed:false,accepted:false}
 |Call=>if(s.down and s.reserved and s.owner and s.box and s.core and s.seat and s.calls==0){...s,calls:1,observed:false}else s
 |Observe=>{...s,observed:s.calls==1 and s.owner and s.box and s.core and s.seat}
 |Release=>{...s,released:s.down}
 |Accept=>{...s,accepted:s.reserved and s.calls==1 and s.released and s.observed and s.core and s.seat}
 |GenericFocus=>if(not(s.reserved)){...s,core:false,seat:false}else s
 |Retry=>s
 }}
 val allProps=all{s.calls<=1,s.repair==0,s.retry==0,s.accepted implies s.reserved and s.owner and s.box and s.released and s.core and s.seat and s.observed}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet e=Set(Down({reserved:a,owner:b,box:c}),ChangeCore,ChangeSeat,Call,Observe,Release,Accept,GenericFocus,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 pure val good={reserved:true,owner:true,box:true}
 run unfocusedPeerRoutesPreservedTest=init.then(fire(Down(good))).then(fire(GenericFocus)).then(fire(Call)).then(fire(Observe)).then(fire(Release)).then(fire(Accept)).then(check(s.accepted and s.core and s.seat))
 run duplicatePhysicalDownNoSecondCallTest=init.then(fire(Down(good))).then(fire(Call)).then(fire(Down(good))).then(fire(Call)).then(check(s.calls==1))
 run changedSeatBeforeCallRefusedTest=init.then(fire(Down(good))).then(fire(ChangeSeat)).then(fire(Call)).then(check(s.calls==0))
 run changedCoreAfterCallNoCompletionTest=init.then(fire(Down(good))).then(fire(Call)).then(fire(ChangeCore)).then(fire(Release)).then(fire(Observe)).then(fire(Accept)).then(check(not(s.accepted)))
 run missingReleaseNoAcceptanceTest=init.then(fire(Down(good))).then(fire(Call)).then(fire(Observe)).then(fire(Accept)).then(check(not(s.accepted)))
 run staleOwnerNoPinTest=init.then(fire(Down({...good,owner:false}))).then(fire(Call)).then(check(s.calls==0))
 run invisibleBoxNoPinTest=init.then(fire(Down({...good,box:false}))).then(fire(Call)).then(check(s.calls==0))
 run otherButtonNoPinTest=init.then(fire(Down({...good,reserved:false}))).then(fire(GenericFocus)).then(fire(Call)).then(check(s.calls==0 and not(s.core)))
 run noQueuedRetryTest=init.then(fire(Down(good))).then(fire(ChangeCore)).then(fire(Retry)).then(fire(Call)).then(check(s.retry==0 and s.calls==0))
}
