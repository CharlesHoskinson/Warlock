module preview_diagnostics {
 type E=Plan({valid:bool})|Move|Sample({owner:bool,cursor:bool,recorded:bool})|Click|Fail|Finish
 type S={proposed:bool,valid:bool,moved:bool,recorded:bool,owner:bool,cursor:bool,arrived:bool,clicked:bool,failed:bool,terminal:bool}
 var s:S
 action init=s'={proposed:false,valid:false,moved:false,recorded:false,owner:false,cursor:false,arrived:false,clicked:false,failed:false,terminal:false}
 action fire(e:E):bool={s'=match e {
 | Plan(p)=>if(not(s.moved) and not(s.failed)){...s,proposed:true,valid:p.valid} else s
 | Move=>if(s.proposed and s.valid and not(s.failed)){...s,moved:true} else {...s,failed:true}
 | Sample(p)=>if(s.moved and not(s.failed) and not(s.clicked)){...s,recorded:p.recorded,owner:p.owner,cursor:p.cursor,arrived:p.recorded and p.owner and p.cursor,failed:not(p.recorded)} else s
 | Click=>if(s.arrived and not(s.failed)){...s,clicked:true} else {...s,failed:true}
 | Fail=>{...s,failed:true,arrived:false}
 | Finish=>{...s,terminal:true}
 }}
 val invariant=all {s.clicked implies all {s.proposed,s.valid,s.moved,s.recorded,s.owner,s.cursor},s.arrived implies all {s.moved,s.recorded,s.owner,s.cursor,not(s.failed)}}
 action step={nondet e=Set(Plan({valid:true}),Plan({valid:false}),Move,Sample({owner:true,cursor:true,recorded:true}),Sample({owner:false,cursor:true,recorded:true}),Sample({owner:true,cursor:false,recorded:true}),Sample({owner:true,cursor:true,recorded:false}),Click,Fail,Finish).oneOf();fire(e)}
 action check(p:bool):bool=all {assert(p),s'=s}
 run proposedDoesNotDeliverTest=init.then(fire(Plan({valid:true}))).then(check(not(s.arrived)))
 run motionDoesNotGrantClickTest=init.then(fire(Plan({valid:true}))).then(fire(Move)).then(check(not(s.arrived)))
 run missingOwnerRefusesTest=init.then(fire(Plan({valid:true}))).then(fire(Move)).then(fire(Sample({owner:false,cursor:true,recorded:true}))).then(fire(Click)).then(check(s.failed and not(s.clicked)))
 run wrongCursorRefusesTest=init.then(fire(Plan({valid:true}))).then(fire(Move)).then(fire(Sample({owner:true,cursor:false,recorded:true}))).then(fire(Click)).then(check(s.failed and not(s.clicked)))
 run unrecordedSampleRefusesTest=init.then(fire(Plan({valid:true}))).then(fire(Move)).then(fire(Sample({owner:true,cursor:true,recorded:false}))).then(fire(Click)).then(check(s.failed and not(s.clicked)))
 run nativeOwnerCursorPermitOriginalClickTest=init.then(fire(Plan({valid:true}))).then(fire(Move)).then(fire(Sample({owner:true,cursor:true,recorded:true}))).then(fire(Click)).then(check(s.clicked and invariant))
 run failureRetainsTerminalTest=init.then(fire(Fail)).then(fire(Finish)).then(check(s.failed and s.terminal and not(s.clicked)))
 run invalidProposalNoMotionTest=init.then(fire(Plan({valid:false}))).then(fire(Move)).then(check(s.failed and not(s.moved)))
}
