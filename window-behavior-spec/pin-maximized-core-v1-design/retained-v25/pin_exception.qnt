module pin_exception {
 type Event=Begin|Invoke|Observed|Exception|SerializeFailure|Success|Retry
 type State={begun:bool,invoked:bool,observed:bool,failed:bool,complete:bool,partial:bool,retry:bool}
 var s:State
 action init=s'={begun:false,invoked:false,observed:false,failed:false,complete:false,partial:false,retry:false}
 action fire(e:Event):bool={s'=match e{
 |Begin=>if(not(s.begun)) {...s,begun:true}else s
 |Invoke=>if(s.begun and not(s.failed)and not(s.complete)){...s,invoked:true,observed:false}else s
 |Observed=>if(s.begun and not(s.failed)){...s,observed:true}else s
 |Exception=>{...s,failed:true,complete:false,partial:s.invoked}
 |SerializeFailure=>{...s,failed:true,complete:false,partial:s.invoked}
 |Success=>if(s.begun and s.observed and not(s.failed)){...s,complete:true,partial:false}else s
 |Retry=>s
 }}
 val allProps=all{not(s.retry),s.failed implies not(s.complete),s.failed and s.invoked implies s.partial,s.complete implies s.observed}
 action step={nondet e=Set(Begin,Invoke,Observed,Exception,SerializeFailure,Success,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 run noWriteExceptionTest=init.then(fire(Begin)).then(fire(Exception)).then(check(not(s.partial)and not(s.complete)))
 run afterActionSnapshotExceptionTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Exception)).then(check(s.partial and not(s.complete)))
 run serializationAfterWriteTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Observed)).then(fire(Success)).then(fire(SerializeFailure)).then(check(s.partial and not(s.complete)))
 run failureCannotBecomeCompleteTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Exception)).then(fire(Success)).then(check(s.partial and not(s.complete)))
 run noRetryTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Exception)).then(fire(Retry)).then(check(not(s.retry)))
}
