module terminal_query_drain {
 type State={ended:bool,featureFailed:bool,released:bool,fixturesGone:bool,owner:bool,source:bool,nonce:bool,quiesced:bool,ack:bool,polling:bool,queries:int,helpers:int,normal:bool,receipt:bool,now:int,deadline:int,failed:bool,quit:bool,drainProof:bool,featureCredit:bool}
 type Event=FeatureEnd|FeatureFail|Release|FixturesGone|SpawnQuery|CompleteQuery|CompleteHelper|BeginQuiesce|Drain|Quit|Tick|OwnerChanged|SourceChanged|WrongNonce|BadProcessExit|MissingReceipt|Reopen
 var s:State
 pure val initial={ended:false,featureFailed:false,released:false,fixturesGone:false,owner:true,source:true,nonce:true,quiesced:false,ack:false,polling:true,queries:0,helpers:0,normal:true,receipt:true,now:0,deadline:8,failed:false,quit:false,drainProof:false,featureCredit:false}
 action init=s'=initial
 pure def advance(x:State,e:Event):State=(if(x.failed or x.quit)x else match e {
 |FeatureEnd=>{...x,ended:true}
 |FeatureFail=>{...x,ended:true,featureFailed:true}
 |Release=>{...x,released:true}
 |FixturesGone=>{...x,fixturesGone:true}
 |SpawnQuery=>if(x.polling){...x,queries:x.queries+1,helpers:x.helpers+1}else x
 |CompleteQuery=>if(x.queries>0){...x,queries:x.queries-1}else x
 |CompleteHelper=>if(x.helpers>0){...x,helpers:x.helpers-1}else x
 |BeginQuiesce=>if(x.ended and x.released and x.fixturesGone and x.owner and x.source and x.nonce){...x,quiesced:true,ack:true,polling:false}else {...x,failed:true}
 |Drain=>if(x.quiesced and x.ack and not(x.polling) and x.queries==0 and x.helpers==0 and x.normal and x.receipt and x.owner and x.source and x.nonce and x.now<x.deadline){...x,drainProof:true}else x
 |Quit=>if(x.drainProof and x.owner and x.source and x.nonce){...x,quit:true}else {...x,failed:true}
 |Tick=>if(x.now+1>=x.deadline){...x,now:x.now+1,failed:true}else {...x,now:x.now+1}
 |OwnerChanged=>{...x,owner:false,failed:true}
 |SourceChanged=>{...x,source:false,failed:true}
 |WrongNonce=>{...x,nonce:false,failed:true}
 |BadProcessExit=>{...x,normal:false,failed:true}
 |MissingReceipt=>{...x,receipt:false,failed:true}
 |Reopen=>if(x.quiesced){...x,failed:true}else x
 })
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.deadline==8 and not(s.featureCredit)
   and (s.quiesced implies s.ended and s.released and s.fixturesGone and not(s.polling))
   and (s.quit implies s.drainProof and s.ack and s.queries==0 and s.helpers==0 and s.normal and s.receipt and s.owner and s.source and s.nonce and not(s.failed))
 action step={nondet e=Set(FeatureEnd,FeatureFail,Release,FixturesGone,SpawnQuery,CompleteQuery,CompleteHelper,BeginQuiesce,Drain,Quit,Tick,OwnerChanged,SourceChanged,WrongNonce,BadProcessExit,MissingReceipt,Reopen).oneOf();fire(e)}
}
