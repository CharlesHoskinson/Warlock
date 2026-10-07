module retained_client_command {
 type Event=Ready|LateOffer|NativeUnreadyTrue|NativeUnreadyFalse|Unowned|BadJob|BadHandle|BadExpiry|BadCoverage|FlagType|MissingPacket|BadIdentity|DuplicateFlag|ExtraField
 type State={accepted:bool,legacy:bool,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Ready=>"Ready"|LateOffer=>"LateOffer"|NativeUnreadyTrue=>"NativeUnreadyTrue"|NativeUnreadyFalse=>"NativeUnreadyFalse"|Unowned=>"Unowned"|BadJob=>"BadJob"|BadHandle=>"BadHandle"|BadExpiry=>"BadExpiry"|BadCoverage=>"BadCoverage"|FlagType=>"FlagType"|MissingPacket=>"MissingPacket"|BadIdentity=>"BadIdentity"|DuplicateFlag=>"DuplicateFlag"|ExtraField=>"ExtraField"}
 action init=s'={accepted:false,legacy:false,history:[]}
 action fire(e:Event):bool=s'={accepted:e==Ready or e==LateOffer,legacy:e==Ready,history:s.history.append(label(e))}
 action step={nondet e=Set(Ready,LateOffer,NativeUnreadyTrue,NativeUnreadyFalse,Unowned,BadJob,BadHandle,BadExpiry,BadCoverage,FlagType,MissingPacket,BadIdentity,DuplicateFlag,ExtraField).oneOf();fire(e)}
 val safety=not(s.legacy) or s.accepted
}
