module frontier {
 type Read={kind:int,id:int,revision:int,output:int,proof:int}
 type Pair={a:Read,g:Read,proof:int}
 type Frame=ReadFrame(Read) | ReleaseFrame(Pair)
 type State={proof:int,expectedA:int,expectedG:int,acceptedA:Read,acceptedG:Read,pendingA:bool,pendingG:bool,dirty:bool,phase:int,next:int,reserved:bool,history:int,effects:int,explicit:bool,durable:bool,wire:List[Frame],releaseA:int,releaseG:int}
 type Event=Announce(int) | RequestBatch | Dirty | QueueRead(Read) | QueueRelease(Pair) | Deliver | Accept(Read) | Release(Pair) | SyncRelease | Explicit | Noop
 pure val NONE={kind:0,id:0,revision:0,output:0,proof:0}
 pure val A1={kind:1,id:1,revision:10,output:1,proof:1}
 pure val G2={kind:2,id:2,revision:20,output:1,proof:1}
 pure val A3={kind:1,id:3,revision:11,output:1,proof:1}
 pure val G4={kind:2,id:4,revision:21,output:1,proof:1}
 pure val OLD={a:A1,g:G2,proof:1}
 pure val NEW={a:A3,g:G4,proof:1}
 var s:State
 pure def batch(st:State):State={...st,expectedA:st.next,expectedG:st.next+1,next:st.next+2,pendingA:true,pendingG:true,dirty:false,phase:1}
 pure def complete(st:State):bool=not(st.pendingA) and not(st.pendingG) and st.acceptedA.id>0 and st.acceptedG.id>0
 pure def accepted(st:State,r:Read):State={
   val admitted=st.proof>0 and r.proof==st.proof and r.id>0 and r.revision>0 and r.output>0
   val admittedState=if(admitted and r.kind==1 and st.pendingA and r.id==st.expectedA) {...st,acceptedA:r,pendingA:false} else if(admitted and r.kind==2 and st.pendingG and r.id==st.expectedG) {...st,acceptedG:r,pendingG:false} else st
   if(complete(admittedState)) {if(admittedState.dirty) batch(admittedState) else {...admittedState,phase:2}} else admittedState
 }
 pure def released(st:State,p:Pair):State=if(st.reserved and st.durable and st.proof>0 and p.proof==st.proof and p.a.id>0 and p.g.id>0 and p.a==st.acceptedA and p.g==st.acceptedG and p.a.output==p.g.output) {...st,reserved:false,releaseA:p.a.id,releaseG:p.g.id} else st
 pure def reduce(st:State,e:Event):State=match e {
 | Announce(proof)=>if(proof>st.proof and proof<=16) batch({...st,proof:proof,acceptedA:NONE,acceptedG:NONE,durable:false}) else st
 | RequestBatch=>if(st.proof>0 and st.next<=7) batch(st) else st
 | Dirty=>{...st,dirty:true}
 | QueueRead(r)=>if(st.wire.length()<8) {...st,wire:st.wire.append(ReadFrame(r))} else st
 | QueueRelease(p)=>if(st.durable and st.wire.length()<8) {...st,wire:st.wire.append(ReleaseFrame(p))} else st
 | Deliver=>if(st.wire.length()>0) {val rest={...st,wire:st.wire.tail()};match st.wire.head() {| ReadFrame(r)=>accepted(rest,r) | ReleaseFrame(p)=>released(rest,p)}} else st
 | Accept(r)=>accepted(st,r)
 | Release(p)=>released(st,p)
 | SyncRelease=>{...st,durable:true}
 | Explicit=>if(not(st.reserved) and not(st.explicit)) {...st,effects:st.effects+1,explicit:true} else st
 | Noop=>st
 }
 action init=s'={proof:0,expectedA:0,expectedG:0,acceptedA:NONE,acceptedG:NONE,pendingA:false,pendingG:false,dirty:false,phase:0,next:1,reserved:true,history:0,effects:0,explicit:false,durable:false,wire:List(),releaseA:0,releaseG:0}
 action fire(e:Event):bool=s'=reduce(s,e)
 pure val EVENTS=Set(Announce(1),Announce(2),RequestBatch,Dirty,QueueRead(A1),QueueRead(G2),QueueRead(A3),QueueRead(G4),QueueRelease(OLD),QueueRelease(NEW),Deliver,Accept(A1),Accept(G2),Accept(A3),Accept(G4),Release(OLD),Release(NEW),SyncRelease,Explicit,Noop)
 action step={nondet e=EVENTS.oneOf();fire(e)}
 val safety=s.history==0 and (s.effects==0 or s.explicit) and (s.reserved or (s.releaseA>0 and s.releaseG>0)) and s.wire.length()<=8
 action proof=fire(Announce(1))
 action pair=fire(Accept(A1)).then(fire(Accept(G2)))
 action assertBlocked=all {assert(s.reserved and safety),fire(Noop)}
 action assertReleased=all {assert(not(s.reserved) and s.history==0 and s.effects==0 and safety),fire(Noop)}
 run completedPairTest=init.then(proof).then(pair).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertReleased)
 run pendingRequestRetainsAcceptedTest=init.then(proof).then(pair).then(fire(RequestBatch)).then(all {assert(s.acceptedA==A1 and s.acceptedG==G2 and s.pendingA and s.pendingG),fire(SyncRelease)}).then(fire(Release(OLD))).then(assertReleased)
 run finalGeometryDrainQueuedReleaseTest=init.then(proof).then(fire(Accept(A1))).then(fire(Dirty)).then(fire(SyncRelease)).then(fire(QueueRead(G2))).then(fire(QueueRelease(OLD))).then(fire(Deliver)).then(all {assert(s.phase==1 and s.expectedA==3 and s.expectedG==4 and s.acceptedG==G2),fire(Deliver)}).then(assertReleased).then(fire(Explicit)).then(all {assert(s.effects==0 and not(s.explicit)),fire(Noop)})
 run finalActionDrainQueuedReleaseTest=init.then(proof).then(fire(Accept(G2))).then(fire(Dirty)).then(fire(SyncRelease)).then(fire(QueueRead(A1))).then(fire(QueueRelease(OLD))).then(fire(Deliver)).then(fire(Deliver)).then(assertReleased)
 run actualAcceptedActionInvalidatesTest=init.then(proof).then(pair).then(fire(RequestBatch)).then(fire(Accept(A3))).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertBlocked)
 run actualAcceptedGeometryInvalidatesTest=init.then(proof).then(pair).then(fire(RequestBatch)).then(fire(Accept(G4))).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertBlocked)
 run latestAcceptedPairTest=init.then(proof).then(pair).then(fire(RequestBatch)).then(fire(Accept(A3))).then(fire(Accept(G4))).then(fire(SyncRelease)).then(fire(Release(NEW))).then(assertReleased)
 run staleReplyNotAcceptedTest=init.then(proof).then(pair).then(fire(RequestBatch)).then(fire(Accept(A1))).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertReleased)
 run changedContextSameIdRefusedTest=init.then(proof).then(pair).then(fire(SyncRelease)).then(fire(Release({...OLD,a:{...A1,revision:99}}))).then(assertBlocked)
 run outputMismatchRefusedTest=init.then(proof).then(fire(Accept(A1))).then(fire(Accept({...G2,output:2}))).then(fire(SyncRelease)).then(fire(Release({...OLD,g:{...G2,output:2}}))).then(assertBlocked)
 run nextProofClearsFrontierTest=init.then(proof).then(pair).then(fire(Announce(2))).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertBlocked)
 run duplicateProofRetainsFrontierTest=init.then(proof).then(pair).then(proof).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertReleased)
 run nondurableReleaseRefusedTest=init.then(proof).then(pair).then(fire(Release(OLD))).then(assertBlocked)
 run missingGeometryRefusedTest=init.then(proof).then(fire(Accept(A1))).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertBlocked)
 run noAutomaticEffectAfterReleaseTest=init.then(proof).then(pair).then(fire(SyncRelease)).then(fire(Release(OLD))).then(assertReleased).then(fire(Explicit)).then(all {assert(s.effects==1 and s.explicit and safety),fire(Noop)})
 run fifoReleaseBeforeNewReplyTest=init.then(proof).then(fire(Accept(A1))).then(fire(Dirty)).then(fire(SyncRelease)).then(fire(QueueRead(G2))).then(fire(QueueRelease(OLD))).then(fire(Deliver)).then(fire(QueueRead(A3))).then(fire(Deliver)).then(assertReleased).then(all {assert(s.wire.length()==1 and s.acceptedA==A1),fire(Deliver)}).then(all {assert(s.acceptedA==A3 and not(s.reserved) and safety),fire(Noop)})
}
