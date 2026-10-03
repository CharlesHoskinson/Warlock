module refusal_counterexample {
 import readonly_ipc.* from "./readonly_ipc"
 action check(p:bool):bool=all{assert(p),s'=s}
 run wrongPeerCanReusePriorReplyCounterexampleTest=init
 .then(fire(Begin({id:1,request:1,owner:owner,durable:true})))
 .then(fire(Connect({owner:owner,peer:true})))
 .then(fire(Reply({eof:true,bounded:true,decoded:true,deadline:true})))
 .then(fire(Connect({owner:owner,peer:false})))
 .then(fire(Close(true))).then(fire(Confirm({owner:owner,durable:true})))
 .then(fire(Consume)).then(check(s.usable and s.consumed))
}
