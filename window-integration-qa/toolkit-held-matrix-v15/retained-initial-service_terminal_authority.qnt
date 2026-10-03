module service_terminal_authority {
 type State={ended:bool,created:bool,noServiceObserved:bool,attempted:bool,exitNormal:bool,gone:bool,resourcesClosed:bool,rootMatch:bool,failed:bool,quiesced:bool}
 type Event=FeatureEnd|CapturedService|NoService|StopAttempt|NormalExit|UnknownExit|ExactGone|ResourcesClosed|WrongRoot|Quiesce|OriginalAfterAttempt
 var s:State
 pure val initial={ended:false,created:false,noServiceObserved:false,attempted:false,exitNormal:false,gone:false,resourcesClosed:false,rootMatch:true,failed:false,quiesced:false}
 action init=s'=initial
 pure def advance(x:State,e:Event):State=(if(x.failed)x else match e {
 |FeatureEnd=>{...x,ended:true}
 |CapturedService=>if(x.quiesced){...x,failed:true,quiesced:false}else {...x,created:true,noServiceObserved:false}
 |NoService=>if(x.created){...x,failed:true}else {...x,noServiceObserved:true}
 |StopAttempt=>{...x,attempted:true}
 |NormalExit=>if(x.created){...x,exitNormal:true}else {...x,failed:true}
 |UnknownExit=>{...x,failed:true,quiesced:false}
 |ExactGone=>if(x.created and x.rootMatch){...x,gone:true}else {...x,failed:true}
 |ResourcesClosed=>if(x.created){...x,resourcesClosed:true}else {...x,failed:true}
 |WrongRoot=>{...x,rootMatch:false,failed:true,quiesced:false}
 |Quiesce=>if(x.ended and x.rootMatch and (if(x.created)x.exitNormal and x.gone and x.resourcesClosed else x.noServiceObserved)){...x,quiesced:true}else {...x,failed:true}
 |OriginalAfterAttempt=>if(x.ended and x.attempted){...x,quiesced:true}else x
 })
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.quiesced implies s.ended and s.rootMatch and not(s.failed) and (if(s.created)s.exitNormal and s.gone and s.resourcesClosed else s.noServiceObserved)
 action step={nondet e=Set(FeatureEnd,CapturedService,NoService,StopAttempt,NormalExit,UnknownExit,ExactGone,ResourcesClosed,WrongRoot,Quiesce).oneOf();fire(e)}
}
