module peer_refusal_counterexample {
 import readonly_ipc.* from "./old_readonly_ipc"
 action check(p:bool):bool=all{assert(p),s'=s}
 action prefix=init.then(fire(Begin({id:1,request:1,owner:owner,durable:true}))).then(fire(Connect({owner:owner,peer:true}))).then(fire(Reply({eof:true,bounded:true,decoded:true,deadline:true})))
 action badPeer=prefix.then(fire(Connect({owner:owner,peer:false}))).then(fire(Close(true))).then(fire(Confirm({owner:owner,durable:true}))).then(fire(Consume))
 run oldWrongPeerCanReassertConsumedCounterexampleTest=badPeer.then(check(s.consumed))
 run requiredWrongPeerTerminalRefusalTest=badPeer.then(check(not(s.consumed)))
 action malformed=prefix.then(fire(Reply({eof:false,bounded:true,decoded:true,deadline:true}))).then(fire(Reply({eof:true,bounded:true,decoded:true,deadline:true}))).then(fire(Close(true))).then(fire(Confirm({owner:owner,durable:true}))).then(fire(Consume))
 run oldPartialReplyCanBeOverwrittenCounterexampleTest=malformed.then(check(s.consumed))
 run requiredPartialReplyTerminalRefusalTest=malformed.then(check(not(s.consumed)))
}
