/** Persistent ledger abstraction; fsync success is an explicit transition.
 * Daemon crashes preserve native authority epoch and committed disk writes. */
module release {
 type S = {nativeRetired:bool, frontendEpoch:int, proof:bool, reads:bool, actionRead:bool, geometry:bool, proofWritten:bool, proofSynced:bool, proofDurable:bool, recordWritten:bool, recordSynced:bool, stage:int, file:bool, durableFile:bool, releasedRecord:bool, ack:bool, effect:bool, history:Set[int], committed:bool}
 type Event = NativeRetire | Proof({kind:int,key:int,epoch:int,barrier:int}) | RequestReads | Observe({kind:int,request:int,epoch:int,seq:int}) | WriteProof | SyncProof | SyncProofDir | WritePrepared | SyncPrepared | SyncPreparedDir | Unlink | SyncUnlinkDir | WriteReleased | SyncReleased | Ack | Explicit(int) | Remember(int) | RecreateOld | Crash
 var s:S
 pure def observations(st:S):bool = st.proof and st.actionRead and st.geometry
 pure def releaseReady(st:S):bool = st.stage==2 and not(st.durableFile)
 pure def reserved(st:S):bool = not(releaseReady(st))
 action init = s' = {nativeRetired:false,frontendEpoch:1,proof:false,reads:false,actionRead:false,geometry:false,proofWritten:false,proofSynced:false,proofDurable:false,recordWritten:false,recordSynced:false,stage:0,file:true,durableFile:true,releasedRecord:false,ack:false,effect:false,history:Set(1),committed:false}
 action fire(e:Event):bool = { val candidate = match e {
  | NativeRetire => {...s,nativeRetired:true}
  // Proof kind1=Retired, key1=exact old admission, epoch1=current native,
  // barrier1=current retirement; barrier0 stale and barrier3 future.
  | Proof(p) => if (s.nativeRetired and p.kind==1 and p.key==1 and p.epoch==1 and p.barrier==1) {...s,proof:true} else s
  | RequestReads => if (s.proof and s.frontendEpoch<4) {...s,reads:true} else s
  // Separate kind/request pairs action1/11 and geometry2/12, both sequence2
  // strictly after barrier1 and no later than current known native watermark2.
  | Observe(o) => if (s.reads and o.epoch==s.frontendEpoch and o.seq==2) {
      if (o.kind==1 and o.request==11) {...s,actionRead:true}
      else if (o.kind==2 and o.request==12) {...s,geometry:true} else s
    } else s
  | WriteProof => if (observations(s)) {...s,proofWritten:true} else s
  | SyncProof => if (s.proofWritten) {...s,proofSynced:true} else s
  | SyncProofDir => if (s.proofSynced) {...s,proofDurable:true} else s
  | WritePrepared => if (observations(s) and s.proofDurable) {...s,recordWritten:true} else s
  | SyncPrepared => if (s.recordWritten) {...s,recordSynced:true} else s
  | SyncPreparedDir => if (s.stage==0 and s.recordSynced and observations(s) and s.proofDurable) {...s,stage:1} else s
  | Unlink => if (s.stage==1 and s.proofDurable) {...s,file:false} else s
  | SyncUnlinkDir => if (s.stage==1 and not(s.file)) {...s,durableFile:false} else s
  | WriteReleased => if (s.stage==1 and not(s.durableFile)) {...s,releasedRecord:true} else s
  | SyncReleased => if (s.releasedRecord and not(s.durableFile)) {...s,stage:2} else s
  | Ack => if (releaseReady(s)) {...s,ack:true,committed:true} else s
  | Explicit(key) => if (s.ack and s.frontendEpoch<4 and releaseReady(s) and key==2 and not(s.history.contains(key)) and s.history.size()<2) {...s,effect:true,history:s.history.union(Set(key))} else s
  | Remember(key) => if (key==2 and s.history.size()<2) {...s,history:s.history.union(Set(key))} else s
  | RecreateOld => if (s.stage==0 and not(s.file)) {...s,file:true,durableFile:true} else s
  | Crash => {...s,frontendEpoch:if(s.frontendEpoch<4) s.frontendEpoch+1 else 4,proof:false,reads:false,actionRead:false,geometry:false,proofWritten:s.proofDurable,proofSynced:s.proofDurable,recordWritten:s.stage>0,recordSynced:s.stage>0,file:s.durableFile,releasedRecord:s.stage==2,ack:false}
 }
 s' = candidate
 }
 pure val EVENTS = Set(NativeRetire,Proof({kind:1,key:1,epoch:1,barrier:1}),Proof({kind:0,key:1,epoch:1,barrier:1}),Proof({kind:1,key:2,epoch:1,barrier:1}),Proof({kind:1,key:1,epoch:0,barrier:1}),Proof({kind:1,key:1,epoch:1,barrier:0}),Proof({kind:1,key:1,epoch:1,barrier:3}),RequestReads,Observe({kind:1,request:11,epoch:1,seq:2}),Observe({kind:2,request:12,epoch:1,seq:2}),Observe({kind:1,request:12,epoch:1,seq:2}),Observe({kind:2,request:11,epoch:1,seq:2}),Observe({kind:1,request:11,epoch:0,seq:2}),Observe({kind:2,request:12,epoch:1,seq:1}),Observe({kind:1,request:11,epoch:1,seq:3}),WriteProof,SyncProof,SyncProofDir,WritePrepared,SyncPrepared,SyncPreparedDir,Unlink,SyncUnlinkDir,WriteReleased,SyncReleased,Ack,Explicit(1),Explicit(2),Explicit(3),Remember(2),RecreateOld,Crash)
 action step = {nondet e=EVENTS.oneOf();fire(e)}
 val ackDurable = not(s.ack) or releaseReady(s)
 val effectDurable = not(s.effect) or releaseReady(s)
 val unlinkPrepared = s.file or (s.stage>=1 and s.proofDurable)
 val noResurrection = s.stage!=2 or (not(s.file) and not(s.durableFile))
 val preparedHasProof = s.stage==0 or s.proofDurable
 val boundedUnknownHistory = s.history.contains(1) and s.history.size()<=2 and not(s.committed)
 val allProps = ackDurable and effectDurable and unlinkPrepared and noResurrection and preparedHasProof and boundedUnknownHistory
 action establish = fire(NativeRetire).then(fire(Proof({kind:1,key:1,epoch:1,barrier:1}))).then(fire(RequestReads)).then(fire(Observe({kind:1,request:11,epoch:1,seq:2}))).then(fire(Observe({kind:2,request:12,epoch:1,seq:2})))
 action prepare = fire(WriteProof).then(fire(SyncProof)).then(fire(SyncProofDir)).then(fire(WritePrepared)).then(fire(SyncPrepared)).then(fire(SyncPreparedDir))
 action finish = fire(Unlink).then(fire(SyncUnlinkDir)).then(fire(WriteReleased)).then(fire(SyncReleased))
}
