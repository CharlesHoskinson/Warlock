module family_query {
 type Event=EndpointQuery|WatchdogLock|EndpointHelper|WatchdogQuery|CompleteWatchdog|CompleteEndpoint|ReplaceReceipt|BadObservation|Evidence(int)|NativeEffect|OldMutex
 type State={manager:int,family:int,endpointQuery:bool,watchdogQuery:bool,endpointWaiting:bool,watchdogWaiting:bool,watchdogDone:bool,endpointDone:bool,oldMutex:bool,current:int,observed:int,valid:bool,write:bool,tls0:int,tls1:int,lastWorker:int,lastEvidence:int}
 var s:State
 action init=s'={manager:0,family:0,endpointQuery:false,watchdogQuery:false,endpointWaiting:false,watchdogWaiting:false,watchdogDone:false,endpointDone:false,oldMutex:false,current:1,observed:1,valid:true,write:false,tls0:0,tls1:0,lastWorker:0,lastEvidence:0}
 action fire(e:Event):bool={val b={...s,write:false,lastWorker:0,lastEvidence:0};s'=match e {
 | OldMutex=>if(not(s.endpointQuery) and not(s.watchdogQuery)){...b,oldMutex:true} else b
 | EndpointQuery=>if(not(s.endpointQuery) and (not(s.oldMutex) or s.family==0)){...b,endpointQuery:true,endpointDone:false,family:if(s.oldMutex)1 else 0,observed:s.current} else b
 | WatchdogLock=>if(s.manager==0){...b,manager:2,watchdogDone:false} else b
 | EndpointHelper=>if(s.endpointQuery and s.manager==2){...b,endpointWaiting:true} else if(s.endpointQuery and s.manager==0){...b,manager:1,endpointWaiting:false} else b
 | WatchdogQuery=>if(s.manager==2 and s.oldMutex and s.family==1){...b,watchdogWaiting:true} else if(s.manager==2){...b,watchdogQuery:true,watchdogWaiting:false} else b
 | CompleteWatchdog=>if(s.manager==2 and s.watchdogQuery and not(s.watchdogWaiting)){...b,manager:0,watchdogDone:true,watchdogQuery:false} else b
 | CompleteEndpoint=>if(s.endpointQuery and s.manager==1){...b,manager:0,family:0,endpointQuery:false,endpointDone:true,endpointWaiting:false} else b
 | ReplaceReceipt=>{...b,current:s.current+1}
 | BadObservation=>{...b,valid:false}
 | Evidence(w)=>if(w==1){...b,tls0:s.current,lastWorker:1,lastEvidence:s.current} else {...b,tls1:s.current+10,lastWorker:2,lastEvidence:s.current+10}
 | NativeEffect=>if(s.endpointDone and s.observed==s.current and s.valid and s.manager==0){...b,write:true} else b
 }}
 val cycle=s.manager==2 and s.family==1 and s.endpointWaiting and s.watchdogWaiting
 val allProps=(not(s.oldMutex) implies not(cycle)) and (s.write implies(s.endpointDone and s.observed==s.current and s.valid)) and (s.lastWorker==1 implies s.lastEvidence==s.tls0) and (s.lastWorker==2 implies s.lastEvidence==s.tls1)
 action step={nondet e=Set(EndpointQuery,WatchdogLock,EndpointHelper,WatchdogQuery,CompleteWatchdog,CompleteEndpoint,ReplaceReceipt,BadObservation,Evidence(1),Evidence(2),NativeEffect).oneOf();fire(e)}
}
