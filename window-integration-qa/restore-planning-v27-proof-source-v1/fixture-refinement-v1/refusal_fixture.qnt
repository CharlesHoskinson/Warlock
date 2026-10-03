module refusal_fixture {
 type Kind=DeadlineError|StoppedError|OtherError
 type Event=Deadline|WorkerTimeout|OrderedStopped|Other|Close|CaptureCopy|PeerReplace|Accept
 type State={expired:bool,causeDeadline:bool,delivered:Kind,closed:bool,captured:int,peer:int,accepted:bool}
 var s:State
 action init=s'={expired:false,causeDeadline:false,delivered:OtherError,closed:false,captured:1,peer:1,accepted:false}
 action fire(e:Event):bool=s'=if(s.accepted)s else match e {
 | Deadline=>{...s,expired:true}
 | WorkerTimeout=>if(s.expired){...s,causeDeadline:true,delivered:DeadlineError}else s
 | OrderedStopped=>if(s.causeDeadline){...s,delivered:StoppedError}else s
 | Other=>{...s,delivered:OtherError}
 | Close=>{...s,closed:true}
 | CaptureCopy=>{...s,captured:1}
 | PeerReplace=>{...s,peer:2}
 | Accept=>{...s,accepted:s.expired and s.causeDeadline and s.closed and (s.delivered==DeadlineError or s.delivered==StoppedError)}
 }
 val allProps=(s.accepted implies s.expired and s.causeDeadline and s.closed and s.delivered!=OtherError) and s.captured==1
 action step={nondet e=Set(Deadline,WorkerTimeout,OrderedStopped,Other,Close,CaptureCopy,PeerReplace,Accept).oneOf();fire(e)}
}
