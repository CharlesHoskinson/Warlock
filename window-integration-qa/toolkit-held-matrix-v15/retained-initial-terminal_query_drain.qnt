module terminal_query_drain {
 type State={ended:bool,featureFailed:bool,released:bool,fixturesGone:bool,owner:bool,source:bool,nonce:bool,quiesced:bool,ack:bool,polling:bool,queries:int,helpers:int,normal:bool,receipt:bool,now:int,deadline:int,failed:bool,quit:bool,drainProof:bool,featureCredit:bool}
 type Event=FeatureEnd|FeatureFail|Release|FixturesGone|SpawnQuery|CompleteQuery|CompleteHelper|BeginQuiesce|Drain|Quit|Tick|OwnerChanged|SourceChanged|WrongNonce|BadProcessExit|MissingReceipt|Reopen
 var s:State
 pure val initial={ended:false,featureFailed:false,released:false,fixturesGone:false,owner:true,source:true,nonce:true,quiesced:false,ack:false,polling:true,queries:0,helpers:0,normal:true,receipt:true,now:0,deadline:8,failed:false,quit:false,drainProof:false,featureCredit:false}
 action init=s'=initial
 action fire(e:Event):bool=s'=(if(s.failed or s.quit)s else match e {
 |FeatureEnd=>{...s,ended:true}
 |FeatureFail=>{...s,ended:true,featureFailed:true}
 |Release=>{...s,released:true}
 |FixturesGone=>{...s,fixturesGone:true}
 |SpawnQuery=>if(s.polling){...s,queries:s.queries+1,helpers:s.helpers+1}else s
 |CompleteQuery=>if(s.queries>0){...s,queries:s.queries-1}else s
 |CompleteHelper=>if(s.helpers>0){...s,helpers:s.helpers-1}else s
 |BeginQuiesce=>if(s.ended and s.released and s.fixturesGone and s.owner and s.source and s.nonce){...s,quiesced:true,ack:true,polling:false}else {...s,failed:true}
 |Drain=>if(s.quiesced and s.ack and not(s.polling) and s.queries==0 and s.helpers==0 and s.normal and s.receipt and s.owner and s.source and s.nonce and s.now<s.deadline){...s,drainProof:true}else s
 |Quit=>if(s.drainProof and s.owner and s.source and s.nonce){...s,quit:true}else {...s,failed:true}
 |Tick=>if(s.now+1>=s.deadline){...s,now:s.now+1,failed:true}else {...s,now:s.now+1}
 |OwnerChanged=>{...s,owner:false,failed:true}
 |SourceChanged=>{...s,source:false,failed:true}
 |WrongNonce=>{...s,nonce:false,failed:true}
 |BadProcessExit=>{...s,normal:false,failed:true}
 |MissingReceipt=>{...s,receipt:false,failed:true}
 |Reopen=>if(s.quiesced){...s,failed:true}else s
 })
 val allProps=s.deadline==8 and not(s.featureCredit)
   and (s.quiesced implies s.ended and s.released and s.fixturesGone and not(s.polling))
   and (s.quit implies s.drainProof and s.ack and s.queries==0 and s.helpers==0 and s.normal and s.receipt and s.owner and s.source and s.nonce and not(s.failed))
 action step={nondet e=Set(FeatureEnd,FeatureFail,Release,FixturesGone,SpawnQuery,CompleteQuery,CompleteHelper,BeginQuiesce,Drain,Quit,Tick,OwnerChanged,SourceChanged,WrongNonce,BadProcessExit,MissingReceipt,Reopen).oneOf();fire(e)}
}
