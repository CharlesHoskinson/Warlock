module preview_scroll {
 type E=Observe({epoch:int,scope:int,source:int,layer:int,released:bool,valid:bool,visible:bool,counter:int,scroll:int,geometry:int})|ViewportMove|CardMove|Arrive({owner:bool,cursor:bool})|Wheel(int)|Click|Close|Timeout|Idle
 type S={epoch:int,scope:int,source:int,layer:int,released:bool,valid:bool,visible:bool,counter:int,scroll:int,geometry:int,stable:int,phase:int,baseCounter:int,baseScroll:int,direction:int,wheels:int,failed:bool,clicked:bool,clickVisible:bool,clickOwner:bool,clickReleased:bool}
 var s:S
 action init=s'={epoch:1,scope:1,source:1,layer:1,released:false,valid:false,visible:false,counter:0,scroll:0,geometry:0,stable:0,phase:0,baseCounter:0,baseScroll:0,direction:0,wheels:0,failed:false,clicked:false,clickVisible:false,clickOwner:false,clickReleased:false}
 val same=s.epoch==1 and s.scope==1 and s.source==1 and s.layer==1
 val authority=same and s.valid and s.released and not(s.failed)
 action fire(e:E):bool={s'=match e {
 | Observe(p)=>if(not(s.clicked) and not(s.failed)){val ok=p.epoch==1 and p.scope==1 and p.source==1 and p.layer==1 and p.released and p.valid and p.counter>=0 and p.scroll>=0 and p.scroll<=40;val waiting=s.phase==3;val receipt=p.counter==s.baseCounter+1 and (if(s.direction>0)p.scroll>s.baseScroll else p.scroll<s.baseScroll);val ordinary=p.counter==s.counter and p.scroll==s.scroll;val pending=waiting and p.counter==s.baseCounter and p.scroll==s.baseScroll;val fresh=ok and (if(waiting)receipt or pending else ordinary);{...s,epoch:p.epoch,scope:p.scope,source:p.source,layer:p.layer,released:p.released,valid:p.valid,visible:p.visible,counter:p.counter,scroll:p.scroll,geometry:p.geometry,stable:if(fresh and p.geometry==s.geometry)(if(s.stable<2)s.stable+1 else 2) else 1,phase:if(waiting and fresh and receipt)0 else s.phase,failed:not(fresh)}} else s
 | ViewportMove=>if(authority and s.phase==0 and not(s.visible)){...s,phase:1} else {...s,failed:true}
 | CardMove=>if(authority and s.phase==0 and s.visible and s.stable>=2){...s,phase:4} else {...s,failed:true}
 | Arrive(p)=>if(authority and p.owner and p.cursor and s.phase==1){...s,phase:2} else if(authority and p.owner and p.cursor and s.phase==4){...s,phase:5} else s
 | Wheel(d)=>if(authority and s.phase==2 and (d==1 or d== -1) and s.wheels<32 and (if(d>0)s.scroll<40 else s.scroll>0)){...s,phase:3,baseCounter:s.counter,baseScroll:s.scroll,direction:d,wheels:s.wheels+1,stable:0} else {...s,failed:true}
 | Click=>if(authority and s.phase==5 and s.visible and s.stable>=2){...s,clicked:true,clickVisible:s.visible,clickOwner:true,clickReleased:s.released} else {...s,failed:true}
 | Close=>{...s,failed:true,epoch:s.epoch+1,valid:false}
 | Timeout=>{...s,failed:true}
 | Idle=>s
 }}
 val invariant=all {s.wheels<=32,s.clicked implies all {s.clickVisible,s.clickOwner,s.clickReleased},s.phase==3 implies s.wheels>0}
 pure def obs(visible:bool,counter:int,scroll:int):E=Observe({epoch:1,scope:1,source:1,layer:1,released:true,valid:true,visible:visible,counter:counter,scroll:scroll,geometry:scroll+1})
 action ready=fire(obs(false,0,0)).then(fire(obs(false,0,0)))
 action wheel=fire(ViewportMove).then(fire(Arrive({owner:true,cursor:true}))).then(fire(Wheel(1)))
 action step={nondet e=Set(obs(false,0,0),obs(true,0,0),obs(false,1,1),obs(true,1,1),obs(false,2,2),obs(true,2,2),Observe({epoch:2,scope:1,source:1,layer:1,released:true,valid:true,visible:true,counter:1,scroll:1,geometry:2}),Observe({epoch:1,scope:2,source:1,layer:1,released:true,valid:true,visible:true,counter:1,scroll:1,geometry:2}),Observe({epoch:1,scope:1,source:2,layer:1,released:true,valid:true,visible:true,counter:1,scroll:1,geometry:2}),Observe({epoch:1,scope:1,source:1,layer:2,released:true,valid:true,visible:true,counter:1,scroll:1,geometry:2}),Observe({epoch:1,scope:1,source:1,layer:1,released:false,valid:true,visible:true,counter:1,scroll:1,geometry:2}),ViewportMove,CardMove,Arrive({owner:true,cursor:true}),Arrive({owner:false,cursor:true}),Arrive({owner:true,cursor:false}),Wheel(1),Wheel(-1),Wheel(0),Click,Close,Timeout,Idle).oneOf();fire(e)}
 action check(p:bool):bool=all {assert(p),s'=s}
 run hiddenCannotClickTest=init.then(ready).then(fire(CardMove)).then(fire(Click)).then(check(s.failed and not(s.clicked)))
 run wheelReceiptDoesNotGrantClickTest=init.then(ready).then(wheel).then(fire(obs(true,1,1))).then(fire(Click)).then(check(s.failed and not(s.clicked)))
 run realWheelStableAllocationNativeOwnerClickTest=init.then(ready).then(wheel).then(fire(obs(true,1,1))).then(fire(obs(true,1,1))).then(fire(CardMove)).then(fire(Arrive({owner:true,cursor:true}))).then(fire(Click)).then(check(s.clicked and invariant))
 run missingCounterRefusesTest=init.then(ready).then(wheel).then(fire(obs(true,0,0))).then(fire(Timeout)).then(check(s.failed))
 run duplicateCounterRefusesTest=init.then(ready).then(wheel).then(fire(obs(true,2,1))).then(check(s.failed))
 run noProgressRefusesTest=init.then(ready).then(wheel).then(fire(obs(true,1,0))).then(check(s.failed))
 run oppositeProgressRefusesTest=init.then(ready).then(wheel).then(fire(obs(true,1,-1))).then(check(s.failed))
 run exactPopupEpochABARefusesTest=init.then(ready).then(fire(Observe({epoch:2,scope:1,source:1,layer:1,released:true,valid:true,visible:true,counter:0,scroll:0,geometry:1}))).then(check(s.failed))
 run exactSourceLifetimeABARefusesTest=init.then(ready).then(fire(Observe({epoch:1,scope:1,source:2,layer:1,released:true,valid:true,visible:true,counter:0,scroll:0,geometry:1}))).then(check(s.failed))
 run exactOrderedScopeChangeRefusesTest=init.then(ready).then(fire(Observe({epoch:1,scope:2,source:1,layer:1,released:true,valid:true,visible:true,counter:0,scroll:0,geometry:1}))).then(check(s.failed))
 run exactLayerChangeRefusesTest=init.then(ready).then(fire(Observe({epoch:1,scope:1,source:1,layer:2,released:true,valid:true,visible:true,counter:0,scroll:0,geometry:1}))).then(check(s.failed))
 run heldInputRefusesTest=init.then(ready).then(fire(Observe({epoch:1,scope:1,source:1,layer:1,released:false,valid:true,visible:true,counter:0,scroll:0,geometry:1}))).then(check(s.failed))
 run wheelWithoutActualOwnerRefusesTest=init.then(ready).then(fire(ViewportMove)).then(fire(Arrive({owner:false,cursor:true}))).then(fire(Wheel(1))).then(check(s.failed))
 run invalidWheelDirectionRefusesTest=init.then(ready).then(fire(ViewportMove)).then(fire(Arrive({owner:true,cursor:true}))).then(fire(Wheel(0))).then(check(s.failed))
 run closeCannotResumeTest=init.then(ready).then(fire(Close)).then(fire(obs(true,0,0))).then(fire(CardMove)).then(check(s.failed and not(s.clicked)))
 run oldReceiptRemainsPendingWithoutClickTest=init.then(ready).then(wheel).then(fire(obs(false,0,0))).then(check(s.phase==3 and not(s.failed) and not(s.clicked)))
 run at32DetentsAnotherWheelRefusesTest=init.then(ready).then(fire(ViewportMove)).then(fire(Arrive({owner:true,cursor:true}))).then(all {s'= {...s,wheels:32}}).then(fire(Wheel(1))).then(check(s.failed and s.wheels==32))
}
