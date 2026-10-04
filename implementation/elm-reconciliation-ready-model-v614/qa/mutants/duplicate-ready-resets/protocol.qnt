/** Pure typed protocol reducer composed with unchanged V605 durable reducer.
 * Queued reads retain frontend enqueue provenance independent of backend timing. */
module protocol {
 import release.* from "./release"
 type Read = {id:int,kind:int,scope:int,domain:int,output:int,fresh:bool}
 type Ready = {version:int,kind:int,current:int,old:int,scope:int}
 type Q = {active:int,announced:Set[int],delivered:bool,ackQueued:bool,ready:bool,domain:int,queued:Set[Read],processed:Set[Read],seen:Set[int],actionExpected:int,geometryExpected:int,actionAccepted:int,geometryAccepted:int,actionOutput:int,geometryOutput:int,ordinary:int,released:int,releasedScopes:Set[int]}
 type PEvent = Announce(int) | DeliverProof | EnqueueReady(Ready) | ProcessReady(Ready) | EnqueueRead({id:int,kind:int,output:int}) | ProcessRead(int) | Reply(int) | Durable(Event) | ReleaseRecords(int) | Restart
 var q:Q
 pure val GOOD = {version:3,kind:1,current:2,old:1,scope:1}
 pure def joined(st:Q):bool = st.ready and st.active>0 and st.announced.contains(st.active) and st.actionExpected>0 and st.geometryExpected>0 and st.actionAccepted==st.actionExpected and st.geometryAccepted==st.geometryExpected and st.actionOutput==st.geometryOutput
 pure def matches(st:Q,r:Ready):bool = r.version==3 and r.kind==1 and r.current==2 and r.old==1 and r.scope==st.active and st.active>0 and st.announced.contains(st.active)
 action start = all {init,q'={active:0,announced:Set(),delivered:false,ackQueued:false,ready:false,domain:1,queued:Set(),processed:Set(),seen:Set(),actionExpected:0,geometryExpected:0,actionAccepted:0,geometryAccepted:0,actionOutput:0,geometryOutput:0,ordinary:0,released:0,releasedScopes:Set()}}
 action send(e:PEvent):bool = match e {
 | Announce(scope) => all {
   q'=if(scope>0 and scope<=16 and not(q.announced.contains(scope))) {...q,active:scope,announced:q.announced.union(Set(scope)),delivered:false,ackQueued:false,ready:false,actionExpected:0,geometryExpected:0,actionAccepted:0,geometryAccepted:0,actionOutput:0,geometryOutput:0} else q,
   fire(Remember(3))
 }
 | DeliverProof => all {q'=if(q.active>0) {...q,delivered:true} else q,fire(Remember(3))}
 | EnqueueReady(r) => all {q'=if(q.delivered and matches(q,r)) {...q,ackQueued:true} else q,fire(Remember(3))}
 | ProcessReady(r) => all {q'=if(q.ackQueued and matches(q,r)) {...q,ready:true,actionAccepted:0,geometryAccepted:0} else q,fire(Remember(3))}
 | EnqueueRead(r) => all {
   q'=if(r.id>0 and r.id<=8 and not(q.seen.contains(r.id)) and (r.kind==1 or r.kind==2) and (r.output==1 or r.output==2)) {...q,seen:q.seen.union(Set(r.id)),queued:q.queued.union(Set({id:r.id,kind:r.kind,scope:q.active,domain:q.domain,output:r.output,fresh:q.ackQueued}))} else q,
   fire(Remember(3))
 }
 | ProcessRead(id) => {
   val rs=q.queued.filter(r=>r.id==id)
   val eligible=rs.filter(r=>r.fresh and q.ready and r.scope==q.active and r.domain==q.domain and q.announced.contains(r.scope))
   all {q'=if(eligible.size()==1) {val r=eligible.fold({id:0,kind:0,scope:0,domain:0,output:0,fresh:false}, (a,r)=>r);if(r.kind==1) {...q,queued:q.queued.exclude(Set(r)),processed:q.processed.union(Set(r)),actionExpected:r.id,actionAccepted:0} else {...q,queued:q.queued.exclude(Set(r)),processed:q.processed.union(Set(r)),geometryExpected:r.id,geometryAccepted:0}} else if(rs.size()==1) {val r=rs.fold({id:0,kind:0,scope:0,domain:0,output:0,fresh:false}, (a,r)=>r);{...q,queued:q.queued.exclude(Set(r)),processed:q.processed.union(Set(r))}} else q,fire(Remember(3))}
 }
 | Reply(id) => {
   val rs=q.processed.filter(r=>r.id==id)
   all {q'=if(rs.size()==1) {val r=rs.fold({id:0,kind:0,scope:0,domain:0,output:0,fresh:false}, (a,r)=>r);if(r.fresh and q.ready and r.scope==q.active and r.domain==q.domain and q.announced.contains(r.scope)) {if(r.kind==1 and r.id==q.actionExpected) {...q,actionAccepted:r.id,actionOutput:r.output,ordinary:q.ordinary+1} else if(r.kind==2 and r.id==q.geometryExpected) {...q,geometryAccepted:r.id,geometryOutput:r.output,ordinary:q.ordinary+1} else {...q,ordinary:q.ordinary+1}} else {...q,ordinary:q.ordinary+1}} else q,fire(Remember(3))}
 }
 | Durable(ev) => all {q'=q,if(joined(q)) fire(ev) else fire(Remember(3))}
 | ReleaseRecords(count) => all {q'=if(joined(q) and s.ack and s.rootReady and releaseReady(s) and count>0 and q.released+count<=64) {...q,released:q.released+count,releasedScopes:q.releasedScopes.union(Set(q.active))} else q,fire(Remember(3))}
 | Restart => all {q'={...q,ready:false,ackQueued:false,delivered:false,domain:q.domain+1,actionExpected:0,geometryExpected:0,actionAccepted:0,geometryAccepted:0},fire(Crash)}
 }
 val noUnannouncedRelease=q.releasedScopes.subseteq(q.announced)
 val acceptedFresh=q.processed.forall(r=>((r.id!=q.actionAccepted and r.id!=q.geometryAccepted) or (r.fresh and r.scope==q.active and r.domain==q.domain)))
 val acceptedReady=(q.actionAccepted==0 and q.geometryAccepted==0) or q.ready
 val boundedScopes=q.announced.size()<=16 and q.released<=64
 val protocolProps=allProps and noUnannouncedRelease and acceptedFresh and acceptedReady and boundedScopes
 pure val P_EVENTS=Set(Announce(1),Announce(2),Announce(17),DeliverProof,EnqueueReady(GOOD),ProcessReady(GOOD),EnqueueReady({...GOOD,scope:2}),ProcessReady({...GOOD,scope:2}),EnqueueReady({...GOOD,current:9}),ProcessReady({...GOOD,current:9}),EnqueueRead({id:1,kind:1,output:1}),EnqueueRead({id:2,kind:2,output:1}),EnqueueRead({id:3,kind:1,output:2}),EnqueueRead({id:4,kind:2,output:2}),ProcessRead(1),ProcessRead(2),ProcessRead(3),ProcessRead(4),Reply(1),Reply(2),Reply(3),Reply(4),ReleaseRecords(1),ReleaseRecords(64),Restart)
 action tick={nondet e=P_EVENTS.union(EVENTS.map(ev=>Durable(ev))).oneOf();send(e)}
 action ready=send(Announce(1)).then(send(DeliverProof)).then(send(EnqueueReady(GOOD))).then(send(ProcessReady(GOOD)))
 action actionRead=send(EnqueueRead({id:1,kind:1,output:1})).then(send(ProcessRead(1))).then(send(Reply(1)))
 action geometryRead=send(EnqueueRead({id:2,kind:2,output:1})).then(send(ProcessRead(2))).then(send(Reply(2)))
 action raw(ev:Event):bool=all {q'=q,fire(ev)}
 action rawEstablish=raw(NativeRetire).then(raw(Proof({kind:1,key:1,epoch:1,barrier:1}))).then(raw(RequestReads)).then(raw(Observe({kind:1,request:11,epoch:1,seq:2}))).then(raw(Observe({kind:2,request:12,epoch:1,seq:2})))
 action rawPrepare=raw(WriteProof).then(raw(SyncProof)).then(raw(SyncProofDir)).then(raw(WritePrepared)).then(raw(SyncPrepared)).then(raw(RenamePrepared)).then(raw(SyncPreparedDir))
 action rawFinish=raw(Unlink).then(raw(SyncUnlinkDir)).then(raw(WriteReleased)).then(raw(SyncReleasedFile)).then(raw(RenameReleased)).then(raw(SyncReleased))
 action durableRelease=send(Durable(NativeRetire)).then(send(Durable(Proof({kind:1,key:1,epoch:1,barrier:1})))).then(send(Durable(RequestReads))).then(send(Durable(Observe({kind:1,request:11,epoch:1,seq:2})))).then(send(Durable(Observe({kind:2,request:12,epoch:1,seq:2})))).then(rawPrepare).then(rawFinish).then(send(Durable(Ack)))
}
