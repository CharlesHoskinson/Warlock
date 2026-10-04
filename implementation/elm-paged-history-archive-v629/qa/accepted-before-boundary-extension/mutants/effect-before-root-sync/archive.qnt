module archive {
 // Fact k*10+t binds exact immutable symbolic record k: t0 Admission,
 // t1 Unknown, t2 terminal receipt, t3 Prepared proof+join, t4 Released, t5 delivery.
 type State={archive:Set[int],visible:Set[int],staged:Set[int],pagesWritten:bool,pagesSynced:bool,pageDirSynced:bool,manifestWritten:bool,manifestSynced:bool,published:bool,rootReady:bool,conserved:Set[int],mark:int,visibleMark:int,migration:bool,visibleMigration:bool,old:Set[int],files:Set[int],durableFiles:Set[int],effects:Set[int],acks:Set[int],delivery:Set[int],quota:int,locked:bool}
 type Event=Stage({key:int,kind:int}) | WritePages | SyncPages | SyncPageDir | WriteManifest | SyncManifest | Publish | RootSync | Unlink(int) | SyncAdmissionDir | Effect(int) | Ack(int) | DeliverHistory(int) | LateC(int) | Replay(int) | Migrate | ProcessCrash | RestartSync | PowerLoss | Compact | Collect | Unlock | Exhaust | Noop
 var s:State
 pure val KEYS=Set(1,2,3,4,5,6,7,8)
 pure def has(st:State,k:int,t:int):bool=st.archive.contains(k*10+t)
 pure def hot(st:State):Set[int]=KEYS.filter(k=>has(st,k,0) and not(has(st,k,2)) and not(has(st,k,4)))
 pure def valid(st:State,k:int,t:int):bool=
  if(t==0) st.migration and k>st.mark and hot(st).size()<2
  else if(t==1) has(st,k,0) and not(has(st,k,2)) and not(has(st,k,4))
  else if(t==2) has(st,k,0) and not(has(st,k,3)) and not(has(st,k,4))
  else if(t==3) has(st,k,1) and not(has(st,k,2)) and not(has(st,k,4))
  else if(t==4) has(st,k,3) and not(st.durableFiles.contains(k))
  else if(t==5) has(st,k,4) else false
 action init=s'={archive:Set(),visible:Set(),staged:Set(),pagesWritten:false,pagesSynced:false,pageDirSynced:false,manifestWritten:false,manifestSynced:false,published:false,rootReady:true,conserved:Set(),mark:0,visibleMark:0,migration:false,visibleMigration:false,old:Set(10,12),files:Set(),durableFiles:Set(),effects:Set(),acks:Set(),delivery:Set(),quota:24,locked:true}
 action fire(e:Event):bool={val candidate=match e {
 | Stage(r)=>if(s.locked and s.rootReady and not(s.published) and s.staged.size()==0 and KEYS.contains(r.key) and valid(s,r.key,r.kind) and not(has(s,r.key,r.kind)) and s.archive.size()+1<=s.quota) {...s,staged:Set(r.key*10+r.kind),pagesWritten:false,pagesSynced:false,pageDirSynced:false,manifestWritten:false,manifestSynced:false} else s
 | Migrate=>if(s.locked and s.rootReady and not(s.migration) and s.archive.size()==0 and not(s.published)) {...s,staged:s.old,pagesWritten:false,pagesSynced:false,pageDirSynced:false,manifestWritten:false,manifestSynced:false} else s
 | WritePages=>if(s.locked and s.staged.size()>0) {...s,pagesWritten:true} else s
 | SyncPages=>if(s.pagesWritten) {...s,pagesSynced:true} else s
 | SyncPageDir=>if(s.pagesSynced) {...s,pageDirSynced:true} else s
 | WriteManifest=>if(s.pageDirSynced) {...s,manifestWritten:true} else s
 | SyncManifest=>if(s.manifestWritten) {...s,manifestSynced:true} else s
 | Publish=>if(s.locked and s.manifestSynced and s.pageDirSynced) {...s,visible:s.archive.union(s.staged),visibleMigration:s.migration or s.staged==s.old,visibleMark:s.staged.fold(s.mark,(m,f)=>if(f%10==0 and f/10>m) f/10 else m),published:true} else s
 | RootSync=>if(s.locked and s.published and s.manifestSynced and s.pageDirSynced) {...s,archive:s.visible,conserved:s.conserved.union(s.visible),mark:s.visibleMark,migration:s.visibleMigration or s.migration,rootReady:true,staged:Set(),published:false} else s
 | RestartSync=>if(s.locked and (not(s.published) or (s.manifestSynced and s.pageDirSynced))) {...s,archive:s.visible,conserved:s.conserved.union(s.visible),mark:s.visibleMark,migration:s.visibleMigration or s.migration,rootReady:true,staged:Set(),published:false} else s
 | Effect(k)=>if(s.locked and s.visible.contains(k*10) and not(has(s,k,2)) and not(has(s,k,3)) and not(has(s,k,4)) and not(s.effects.contains(k))) {...s,effects:s.effects.union(Set(k)),files:s.files.union(Set(k)),durableFiles:s.durableFiles.union(Set(k))} else s
 | Unlink(k)=>if(s.locked and s.rootReady and has(s,k,3)) {...s,files:s.files.exclude(Set(k))} else s
 | SyncAdmissionDir=>if(s.locked and s.rootReady) {...s,durableFiles:s.files} else s
 | Ack(k)=>if(s.rootReady and has(s,k,4) and not(s.durableFiles.contains(k))) {...s,acks:s.acks.union(Set(k))} else s
 | DeliverHistory(k)=>if(s.rootReady and has(s,k,4) and has(s,k,5)) {...s,delivery:s.delivery.union(Set(k))} else s
 | LateC(k)=>if(s.locked) {if(has(s,k,4) and s.rootReady) s else {...s,files:s.files.union(Set(k)),durableFiles:s.durableFiles.union(Set(k))}} else s
 | Replay(k)=>if(s.rootReady and k>s.mark and not(has(s,k,0))) s else s
 | ProcessCrash=>{...s,rootReady:false,locked:true,acks:Set(),delivery:Set()}
 | PowerLoss=>{...s,visible:s.archive,visibleMark:s.mark,visibleMigration:s.migration,staged:Set(),published:false,manifestSynced:false,pageDirSynced:false,pagesSynced:false,pagesWritten:false,manifestWritten:false,rootReady:false,files:s.durableFiles,acks:Set(),delivery:Set(),locked:true}
 | Compact=>if(s.locked and s.rootReady and not(s.published) and s.staged.size()==0) {...s,visible:s.archive,visibleMark:s.mark,visibleMigration:s.migration,pagesWritten:true,pagesSynced:true,pageDirSynced:true,manifestWritten:true,manifestSynced:true,published:true} else s
 | Collect=>if(s.rootReady and not(s.published) and s.visible==s.archive) s else s
 | Exhaust=>{...s,quota:s.archive.size()}
 | Unlock=>{...s,locked:false}
 | Noop=>s
 };s'=candidate}
 val conserved=s.conserved.subseteq(s.archive)
 val boundedHot=hot(s).size()<=2 and s.staged.size()<=2
 val anchored=KEYS.forall(k=>(not(has(s,k,4)) or has(s,k,3)) and (not(has(s,k,5)) or has(s,k,4)))
 val watermark=KEYS.forall(k=>not(has(s,k,0)) or k<=s.mark)
 val ackDurable=s.acks.forall(k=>s.rootReady and has(s,k,4) and not(s.durableFiles.contains(k)))
 val migrationConserved=not(s.migration) or s.old.subseteq(s.archive)
 val noEffectWithoutArchive=s.effects.forall(k=>has(s,k,0))
 val safety=conserved and boundedHot and anchored and watermark and ackDurable and migrationConserved and noEffectWithoutArchive
 pure val EVENTS=Set(Migrate,WritePages,SyncPages,SyncPageDir,WriteManifest,SyncManifest,Publish,RootSync,RestartSync,SyncAdmissionDir,ProcessCrash,PowerLoss,Compact,Collect,Unlock,Exhaust,Noop).union(KEYS.map(k=>Stage({key:k,kind:0}))).union(KEYS.map(k=>Stage({key:k,kind:1}))).union(KEYS.map(k=>Stage({key:k,kind:2}))).union(KEYS.map(k=>Stage({key:k,kind:3}))).union(KEYS.map(k=>Stage({key:k,kind:4}))).union(KEYS.map(k=>Stage({key:k,kind:5}))).union(KEYS.map(k=>Effect(k))).union(KEYS.map(k=>Unlink(k))).union(KEYS.map(k=>Ack(k))).union(KEYS.map(k=>LateC(k))).union(KEYS.map(k=>DeliverHistory(k)))
 action step={nondet e=EVENTS.oneOf();fire(e)}
 action commit=fire(WritePages).then(fire(SyncPages)).then(fire(SyncPageDir)).then(fire(WriteManifest)).then(fire(SyncManifest)).then(fire(Publish)).then(fire(RootSync))
 action bootstrap=fire(Migrate).then(commit)
 action persistFact(k:int,t:int):bool=fire(Stage({key:k,kind:t})).then(commit)
 action release2=persistFact(2,0).then(fire(Effect(2))).then(persistFact(2,1)).then(persistFact(2,3)).then(fire(Unlink(2))).then(fire(SyncAdmissionDir)).then(persistFact(2,4))
 run migrateBeforeEffectTest=init.then(fire(Stage({key:2,kind:0}))).then(fire(Effect(2))).then(all {assert(s.archive.size()==0 and s.effects.size()==0 and safety),bootstrap})
 run historyGrowsHotBoundedTest=init.then(bootstrap).then(persistFact(2,0)).then(persistFact(2,2)).then(persistFact(3,0)).then(persistFact(3,2)).then(persistFact(4,0)).then(persistFact(4,2)).then(all {assert(s.archive.size()==8 and hot(s).size()==0 and safety),fire(Compact)}).then(fire(RootSync)).then(all {assert(s.archive.size()==8 and safety),fire(Collect)})
 run hotExhaustionBeforeEffectTest=init.then(bootstrap).then(persistFact(2,0)).then(persistFact(3,0)).then(persistFact(4,0)).then(fire(Effect(4))).then(all {assert(not(has(s,4,0)) and not(s.effects.contains(4)) and hot(s).size()==2 and safety),fire(Noop)})
 run visibleManifestRestartBarrierTest=init.then(bootstrap).then(fire(Stage({key:2,kind:0}))).then(fire(WritePages)).then(fire(SyncPages)).then(fire(SyncPageDir)).then(fire(WriteManifest)).then(fire(SyncManifest)).then(fire(Publish)).then(fire(ProcessCrash)).then(fire(Effect(2))).then(all {assert(s.visible.contains(20) and not(has(s,2,0)) and not(s.effects.contains(2)) and not(s.rootReady) and safety),fire(RestartSync)}).then(fire(Effect(2))).then(all {assert(s.effects.contains(2) and safety),fire(Noop)})
 run unsyncedManifestPowerLossTest=init.then(bootstrap).then(fire(Stage({key:2,kind:0}))).then(fire(WritePages)).then(fire(SyncPages)).then(fire(SyncPageDir)).then(fire(WriteManifest)).then(fire(SyncManifest)).then(fire(Publish)).then(fire(PowerLoss)).then(fire(RestartSync)).then(fire(Effect(2))).then(all {assert(not(s.visible.contains(20)) and not(s.effects.contains(2)) and safety),fire(Noop)})
 run pagesBeforeManifestTest=init.then(bootstrap).then(fire(Stage({key:2,kind:0}))).then(fire(WritePages)).then(fire(WriteManifest)).then(fire(SyncManifest)).then(fire(Publish)).then(fire(RootSync)).then(all {assert(not(has(s,2,0)) and safety),fire(Noop)})
 run unknownReleaseAndDeliveryTest=init.then(bootstrap).then(release2).then(persistFact(2,5)).then(fire(Ack(2))).then(fire(DeliverHistory(2))).then(all {assert(has(s,2,1) and has(s,2,3) and has(s,2,4) and has(s,2,5) and not(has(s,2,2)) and s.acks.contains(2) and s.delivery.contains(2) and safety),fire(Noop)})
 run lateExactReleasedCAdmissionTest=init.then(bootstrap).then(release2).then(fire(LateC(2))).then(all {assert(not(s.files.contains(2)) and not(s.durableFiles.contains(2)) and safety),fire(Noop)})
 run lateOtherCRemainsBlockedTest=init.then(bootstrap).then(release2).then(fire(LateC(3))).then(all {assert(s.files.contains(3) and not(has(s,3,4)) and safety),fire(Noop)})
 run preparedUnlinkNeedsRestartBarrierTest=init.then(bootstrap).then(persistFact(2,0)).then(fire(Effect(2))).then(persistFact(2,1)).then(persistFact(2,3)).then(fire(ProcessCrash)).then(fire(Unlink(2))).then(all {assert(s.files.contains(2) and not(s.rootReady) and safety),fire(RestartSync)}).then(fire(Unlink(2))).then(all {assert(not(s.files.contains(2)) and safety),fire(Noop)})
 run unlinkPowerLossRetainsReservationTest=init.then(bootstrap).then(persistFact(2,0)).then(fire(Effect(2))).then(persistFact(2,1)).then(persistFact(2,3)).then(fire(Unlink(2))).then(fire(PowerLoss)).then(fire(RestartSync)).then(persistFact(2,4)).then(all {assert(s.files.contains(2) and not(has(s,2,4)) and safety),fire(Noop)})
 run immutableMigrationAndCompactionTest=init.then(bootstrap).then(release2).then(fire(Compact)).then(fire(ProcessCrash)).then(fire(Collect)).then(fire(RestartSync)).then(fire(Collect)).then(all {assert(s.old.subseteq(s.archive) and has(s,2,1) and has(s,2,4) and safety),fire(Noop)})
 run archivedKeyCannotReadmitTest=init.then(bootstrap).then(release2).then(persistFact(2,0)).then(fire(Effect(2))).then(all {assert(not(hot(s).contains(2)) and s.mark==2 and safety),fire(Noop)})
 run lockRefusesMutationTest=init.then(bootstrap).then(fire(Unlock)).then(fire(Stage({key:2,kind:0}))).then(fire(Effect(2))).then(all {assert(not(has(s,2,0)) and not(s.effects.contains(2)) and safety),fire(Noop)})
 run archiveQuotaRefusesBeforeEffectTest=init.then(bootstrap).then(fire(Exhaust)).then(persistFact(2,0)).then(fire(Effect(2))).then(all {assert(not(has(s,2,0)) and not(s.effects.contains(2)) and safety),fire(Noop)})
 run unanchoredDeliveryRefusedTest=init.then(bootstrap).then(persistFact(2,0)).then(persistFact(2,5)).then(fire(DeliverHistory(2))).then(all {assert(not(has(s,2,5)) and not(s.delivery.contains(2)) and safety),fire(Noop)})
 run noReleasedWithoutProofTest=init.then(bootstrap).then(persistFact(2,0)).then(persistFact(2,4)).then(fire(Ack(2))).then(all {assert(not(has(s,2,4)) and not(s.acks.contains(2)) and safety),fire(Noop)})
 run stagedMigrationRestartCannotActivateTest=init.then(fire(Migrate)).then(fire(ProcessCrash)).then(fire(RestartSync)).then(all {assert(not(s.migration) and s.mark==0 and s.archive.size()==0 and safety),fire(Noop)})
}
