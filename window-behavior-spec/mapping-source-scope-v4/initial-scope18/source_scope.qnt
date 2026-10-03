module source_scope {
 type State={started:bool,alive:bool,budget:bool,root:int,root0:int,graph:int,graph0:int,known:Set[int],launch:Set[int],mapsB:Set[int],mapsA:Set[int],fdB:Set[int],fdA:Set[int],aliasB:Set[int],aliasA:Set[int],changed:Set[int],badSource:bool,epoch:int,bEpoch:int,aEpoch:int,kernel:bool,discarded:bool,launches:int,nativeWrites:int}
 var s:State
 action init=s'={started:false,alive:true,budget:true,root:1,root0:0,graph:1,graph0:1,known:Set(1,2,3),launch:Set(2),mapsB:Set(),mapsA:Set(),fdB:Set(),fdA:Set(),aliasB:Set(),aliasA:Set(),changed:Set(),badSource:false,epoch:1,bEpoch:0,aEpoch:0,kernel:false,discarded:false,launches:0,nativeWrites:0}
 pure def relevant(images:Set[int]):Set[int]=images.fold(Set(),(a,i)=>a.union(Set(i*10+1,i*10+2)))
 pure def images(a:State):Set[int]=a.launch.union(a.mapsB).union(a.mapsA)
 pure def needed(a:State):Set[int]=relevant(images(a))
 pure def sourceExact(a:State):bool=all{a.started,a.alive,a.budget,a.root==a.root0,a.graph==a.graph0,not(a.badSource),images(a).subseteq(a.known),images(a).subseteq(a.fdB),images(a).subseteq(a.fdA),needed(a).subseteq(a.aliasB),needed(a).subseteq(a.aliasA),needed(a).intersect(a.changed)==Set(),a.bEpoch==a.epoch,a.aEpoch==a.epoch}
 pure def accepted(a:State):bool=all{sourceExact(a),a.mapsB!=Set(),a.mapsB==a.mapsA,not(a.discarded)}
 type Event=Start|MapsBefore(int)|MapsAfter(int)|BeforeFD|AfterFD|BeforeAliases|AfterAliases|AliasChange(int)|SourceChange|GraphChange|RootChange|ChildGone|Expire|Verify|Discard|CallerRelevance
 action fire(e:Event):bool={s'=match e {
 |Start=>if(s.started){...s,badSource:true,kernel:false}else {...s,started:true,root0:s.root,launches:s.launches+1}
 |MapsBefore(i)=>{...s,mapsB:Set(i),kernel:false}
 |MapsAfter(i)=>{...s,mapsA:Set(i),kernel:false}
 |BeforeFD=>{...s,fdB:images(s),bEpoch:s.epoch,kernel:false}
 |AfterFD=>{...s,fdA:images(s),aEpoch:s.epoch,kernel:false}
 |BeforeAliases=>{...s,aliasB:needed(s),kernel:false}
 |AfterAliases=>{...s,aliasA:needed(s),kernel:false}
 |AliasChange(i)=>{...s,changed:s.changed.union(Set(i)),kernel:false}
 |SourceChange=>{...s,badSource:true,kernel:false}
 |GraphChange=>{...s,graph:s.graph+1,kernel:false}
 |RootChange=>{...s,root:s.root+1,kernel:false}
 |ChildGone=>{...s,alive:false,kernel:false}
 |Expire=>{...s,budget:false,kernel:false}
 |Verify=>{...s,kernel:accepted(s)}
 |Discard=>if(sourceExact(s)and s.mapsB!=s.mapsA and s.epoch<16){...s,epoch:s.epoch+1,mapsB:Set(),mapsA:Set(),fdB:Set(),fdA:Set(),aliasB:Set(),aliasA:Set(),bEpoch:0,aEpoch:0,kernel:false,discarded:true}else {...s,kernel:false,badSource:true}
 |CallerRelevance=>s
 }}
 val allProps=all{not(s.kernel)or accepted(s),s.launches<=1,s.nativeWrites==0,s.epoch<=16}
 action step=nondet e=Set(Start,MapsBefore(1),MapsBefore(3),MapsAfter(1),MapsAfter(3),MapsAfter(99),BeforeFD,AfterFD,BeforeAliases,AfterAliases,AliasChange(11),AliasChange(21),AliasChange(31),AliasChange(99),SourceChange,GraphChange,RootChange,ChildGone,Expire,Verify,Discard,CallerRelevance).oneOf();fire(e)
 action check(v:bool):bool=all{assert(v),s'=s}
 action start=fire(Start)
 action maps=fire(MapsBefore(1)).then(fire(MapsAfter(1)))
 action full=fire(BeforeFD).then(fire(BeforeAliases)).then(fire(AfterFD)).then(fire(AfterAliases))
 action verify=fire(Verify)
 run exactMappedAndLaunchSourcesTest=init.then(start).then(maps).then(full).then(verify).then(check(s.kernel))
 run mappedAliasChangeRefusesTest=init.then(start).then(maps).then(full).then(fire(AliasChange(11))).then(verify).then(check(not(s.kernel)))
 run declaredLauncherAliasChangeRefusesTest=init.then(start).then(maps).then(full).then(fire(AliasChange(21))).then(verify).then(check(not(s.kernel)))
 run unrelatedInventoryAliasNotClaimedTest=init.then(start).then(maps).then(full).then(fire(AliasChange(99))).then(verify).then(check(s.kernel and s.changed.contains(99)))
 run unknownNewMappedSourceRefusesTest=init.then(start).then(fire(MapsBefore(1))).then(fire(MapsAfter(99))).then(full).then(verify).then(check(not(s.kernel)))
 run sourceFDHashModeMountChangeRefusesTest=init.then(start).then(maps).then(full).then(fire(SourceChange)).then(verify).then(check(not(s.kernel)))
 run declaredGraphReplacementRefusesTest=init.then(start).then(maps).then(full).then(fire(GraphChange)).then(verify).then(check(not(s.kernel)))
 run rootPIDStartReplacementRefusesTest=init.then(start).then(maps).then(full).then(fire(RootChange)).then(verify).then(check(not(s.kernel)))
 run missingBeforeAliasProofRefusesTest=init.then(start).then(maps).then(fire(BeforeFD)).then(fire(AfterFD)).then(fire(AfterAliases)).then(verify).then(check(not(s.kernel)))
 run missingAfterAliasProofRefusesTest=init.then(start).then(maps).then(fire(BeforeFD)).then(fire(BeforeAliases)).then(fire(AfterFD)).then(verify).then(check(not(s.kernel)))
 run newImageAfterOldAliasScopeRefusesTest=init.then(start).then(maps).then(full).then(fire(MapsAfter(3))).then(verify).then(check(not(s.kernel)))
 run freshNewImageCompleteScopeCanOnlyDiscardTest=init.then(start).then(fire(MapsBefore(1))).then(fire(MapsAfter(3))).then(full).then(verify).then(check(not(s.kernel))).then(fire(Discard)).then(check(s.epoch==2 and not(s.kernel)))
 run newImageAliasChangeCannotDiscardTest=init.then(start).then(fire(MapsBefore(1))).then(fire(MapsAfter(3))).then(full).then(fire(AliasChange(31))).then(fire(Discard)).then(check(s.badSource and s.epoch==1))
 run discardClearsAllCurrentProofTest=init.then(start).then(fire(MapsBefore(1))).then(fire(MapsAfter(3))).then(full).then(fire(Discard)).then(verify).then(check(not(s.kernel)and s.fdB==Set()and s.aliasB==Set()))
 run deadChildCannotCreateSourceProofTest=init.then(start).then(maps).then(full).then(fire(ChildGone)).then(verify).then(check(not(s.kernel)))
 run expiredBudgetCannotCreateSourceProofTest=init.then(start).then(maps).then(full).then(fire(Expire)).then(verify).then(check(not(s.kernel)))
 run callerCannotChooseAliasRelevanceTest=init.then(start).then(maps).then(fire(CallerRelevance)).then(verify).then(check(not(s.kernel)))
 run missingNamedFDProofCannotUseAliasAloneTest=init.then(start).then(maps).then(fire(BeforeAliases)).then(fire(AfterAliases)).then(verify).then(check(not(s.kernel)))
}
