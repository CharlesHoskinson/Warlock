module qml_lifetime {
 val Engines=Set(1,2)
 val Objects=Set(1,2,3,4)
 val Limit=12
 type Witness={available:bool,engine:int,widget:int,delegate:int,eg:int,ep:int,pg:int,wg:int,dg:int}
 type State={loader:bool,refused:bool,engines:Set[int],providers:Set[int],objects:Set[int],contextGood:Set[int],eg:int->int,ep:int->int,pg:int->int,og:int->int,oe:int->int,oeg:int->int,parent:int->int,nextEngine:int,nextEpoch:int,nextObject:int,lastEngine:int,lastEpoch:int,lastObject:int,w:Witness,accepted:bool,nativeWrites:int}
 type Event=PinLoader(bool)|NewEngine(int)|DestroyEngine(int)|DestroyProvider(int)|Factory(int)|Bind({o:int,e:int,parent:int})|DestroyObject(int)|OldDestroyed({o:int,g:int})|ObservedReload(int)|ContextFault(int)|AncestryFault(int)|ThreadFault|SourceFault|ProcessFault|LoaderReset|Capture({e:int,w:int,d:int})|Confirm|CallerEpoch(int)|InstanceId|NativeLayer|Exhaust
 var s:State
 val empty={available:false,engine:1,widget:1,delegate:2,eg:0,ep:0,pg:0,wg:0,dg:0}
 action init=s'={loader:false,refused:false,engines:Set(),providers:Set(),objects:Set(),contextGood:Set(),eg:Engines.mapBy(e=>0),ep:Engines.mapBy(e=>0),pg:Engines.mapBy(e=>0),og:Objects.mapBy(o=>0),oe:Objects.mapBy(o=>1),oeg:Objects.mapBy(o=>0),parent:Objects.mapBy(o=>o),nextEngine:1,nextEpoch:1,nextObject:1,lastEngine:1,lastEpoch:1,lastObject:1,w:empty,accepted:false,nativeWrites:0}
 val usable=s.loader and not(s.refused)
 pure def eligible(a:State,e:int,w:int,d:int):bool=all{a.loader,not(a.refused),a.engines.contains(e),a.providers.contains(e),a.objects.contains(w),a.objects.contains(d),w!=d,a.contextGood.contains(w),a.contextGood.contains(d),a.oe.get(w)==e,a.oe.get(d)==e,a.oeg.get(w)==a.eg.get(e),a.oeg.get(d)==a.eg.get(e),a.parent.get(d)==w}
 pure def matches(a:State,v:Witness):bool=all{v.available,eligible(a,v.engine,v.widget,v.delegate),v.eg==a.eg.get(v.engine),v.ep==a.ep.get(v.engine),v.pg==a.pg.get(v.engine),v.wg==a.og.get(v.widget),v.dg==a.og.get(v.delegate)}
 action fire(e:Event):bool={
  val b={...s,accepted:false,lastEngine:s.nextEngine,lastEpoch:s.nextEpoch,lastObject:s.nextObject}
  s'=match e {
  |PinLoader(ok)=>if(not(s.loader) and not(s.refused) and ok){...b,loader:true}else if(not(ok)){...b,refused:true}else b
  |NewEngine(e)=>if(usable and not(s.engines.contains(e))){
   if(s.nextEngine>=Limit or s.nextEpoch>=Limit or s.nextObject>=Limit){...b,refused:true}
   else {...b,engines:s.engines.union(Set(e)),providers:s.providers.union(Set(e)),eg:s.eg.set(e,s.nextEngine),ep:s.ep.set(e,s.nextEpoch),pg:s.pg.set(e,s.nextObject),nextEngine:s.nextEngine+1,nextEpoch:s.nextEpoch+1,nextObject:s.nextObject+1}
  }else b
  |DestroyEngine(e)=>{...b,engines:s.engines.exclude(Set(e)),providers:s.providers.exclude(Set(e)),objects:s.objects.filter(o=>s.oe.get(o)!=e),contextGood:s.contextGood.filter(o=>s.oe.get(o)!=e)}
  |DestroyProvider(e)=>{...b,providers:s.providers.exclude(Set(e))}
  |Factory(e)=>if(usable and s.engines.contains(e) and not(s.providers.contains(e))){
   if(s.nextEpoch>=Limit or s.nextObject>=Limit){...b,refused:true}
   else {...b,providers:s.providers.union(Set(e)),ep:s.ep.set(e,s.nextEpoch),pg:s.pg.set(e,s.nextObject),nextEpoch:s.nextEpoch+1,nextObject:s.nextObject+1}
  }else b
  |Bind(v)=>if(usable and s.engines.contains(v.e) and s.providers.contains(v.e) and not(s.objects.contains(v.o))){
   if(s.nextObject>=Limit){...b,refused:true}
   else {...b,objects:s.objects.union(Set(v.o)),contextGood:s.contextGood.union(Set(v.o)),og:s.og.set(v.o,s.nextObject),oe:s.oe.set(v.o,v.e),oeg:s.oeg.set(v.o,s.eg.get(v.e)),parent:s.parent.set(v.o,v.parent),nextObject:s.nextObject+1}
  }else b
  |DestroyObject(o)=>{...b,objects:s.objects.exclude(Set(o)),contextGood:s.contextGood.exclude(Set(o))}
  |OldDestroyed(v)=>if(s.og.get(v.o)==v.g){...b,objects:s.objects.exclude(Set(v.o)),contextGood:s.contextGood.exclude(Set(v.o))}else b
  |ObservedReload(e)=>if(usable and s.engines.contains(e)){
   if(s.nextEpoch>=Limit){...b,refused:true}else {...b,ep:s.ep.set(e,s.nextEpoch),nextEpoch:s.nextEpoch+1}
  }else b
  |ContextFault(o)=>{...b,contextGood:s.contextGood.exclude(Set(o))}
  |AncestryFault(o)=>{...b,parent:s.parent.set(o,o)}
  |ThreadFault=>{...b,refused:true}
  |SourceFault=>{...b,refused:true}
  |ProcessFault=>{...b,refused:true}
  |LoaderReset=>{...b,refused:true,loader:false}
  |Capture(v)=>{...b,w:{available:eligible(s,v.e,v.w,v.d),engine:v.e,widget:v.w,delegate:v.d,eg:s.eg.get(v.e),ep:s.ep.get(v.e),pg:s.pg.get(v.e),wg:s.og.get(v.w),dg:s.og.get(v.d)}}
  |Confirm=>{...b,accepted:matches(s,s.w)}
  |CallerEpoch(n)=>b
  |InstanceId=>b
  |NativeLayer=>b
  // Test-only finite abstraction of a process counter reaching its protocol bound.
  |Exhaust=>{...b,nextEpoch:Limit}
  }
 }
 val allProps=all{s.nativeWrites==0,s.nextEngine>=s.lastEngine,s.nextEpoch>=s.lastEpoch,s.nextObject>=s.lastObject,s.nextEngine<=Limit,s.nextEpoch<=Limit,s.nextObject<=Limit,s.accepted implies matches(s,s.w),s.refused implies not(s.accepted)}
 action step={nondet e=Engines.oneOf();nondet o=Objects.oneOf();nondet p=Objects.oneOf();nondet q=Set(true,false).oneOf();nondet ev=Set(PinLoader(q),NewEngine(e),DestroyEngine(e),DestroyProvider(e),Factory(e),Bind({o:o,e:e,parent:p}),DestroyObject(o),OldDestroyed({o:o,g:1}),ObservedReload(e),ContextFault(o),AncestryFault(o),ThreadFault,SourceFault,ProcessFault,LoaderReset,Capture({e:e,w:o,d:p}),Confirm,CallerEpoch(1),InstanceId,NativeLayer,Exhaust).oneOf();fire(ev)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action ready=fire(PinLoader(true)).then(fire(NewEngine(1))).then(fire(Bind({o:1,e:1,parent:1}))).then(fire(Bind({o:2,e:1,parent:1})))
 action captured=fire(Capture({e:1,w:1,d:2}))
 run genuineSameEngineObjectsTest=init.then(ready).then(captured).then(fire(Confirm)).then(check(s.accepted))
 run missingLoaderRefusedTest=init.then(fire(NewEngine(1))).then(captured).then(fire(Confirm)).then(check(not(s.accepted)))
 run failedLoaderPinRefusedTest=init.then(fire(PinLoader(false))).then(ready).then(captured).then(fire(Confirm)).then(check(not(s.accepted)))
 run crossEngineDelegateRefusedTest=init.then(fire(PinLoader(true))).then(fire(NewEngine(1))).then(fire(NewEngine(2))).then(fire(Bind({o:1,e:1,parent:1}))).then(fire(Bind({o:2,e:2,parent:1}))).then(captured).then(fire(Confirm)).then(check(not(s.accepted)))
 run wrongAncestryRefusedTest=init.then(ready).then(fire(AncestryFault(2))).then(captured).then(fire(Confirm)).then(check(not(s.accepted)))
 run contextChangeBetweenSnapshotsRefusedTest=init.then(ready).then(captured).then(fire(ContextFault(2))).then(fire(Confirm)).then(check(not(s.accepted)))
 run widgetDestructionBetweenSnapshotsRefusedTest=init.then(ready).then(captured).then(fire(DestroyObject(1))).then(fire(Confirm)).then(check(not(s.accepted)))
 run delegateDestructionBetweenSnapshotsRefusedTest=init.then(ready).then(captured).then(fire(DestroyObject(2))).then(fire(Confirm)).then(check(not(s.accepted)))
 run widgetAddressSlotReuseRefusesOldTest=init.then(ready).then(captured).then(fire(DestroyObject(1))).then(fire(Bind({o:1,e:1,parent:1}))).then(fire(Confirm)).then(check(not(s.accepted) and s.og.get(1)>s.w.wg))
 run delegateAddressSlotReuseRefusesOldTest=init.then(ready).then(captured).then(fire(DestroyObject(2))).then(fire(Bind({o:2,e:1,parent:1}))).then(fire(Confirm)).then(check(not(s.accepted) and s.og.get(2)>s.w.dg))
 run lateOldDestroyedCallbackCannotRetireNewTest=init.then(ready).then(fire(DestroyObject(1))).then(fire(Bind({o:1,e:1,parent:1}))).then(captured).then(fire(OldDestroyed({o:1,g:2}))).then(fire(Confirm)).then(check(s.accepted))
 run currentDestroyedCallbackRetiresTest=init.then(ready).then(captured).then(fire(OldDestroyed({o:1,g:2}))).then(fire(Confirm)).then(check(not(s.accepted)))
 run engineDestructionRefusesOldTest=init.then(ready).then(captured).then(fire(DestroyEngine(1))).then(fire(Confirm)).then(check(not(s.accepted)))
 run engineAddressSlotReuseNeverResetsTest=init.then(ready).then(captured).then(fire(DestroyEngine(1))).then(fire(NewEngine(1))).then(fire(Bind({o:1,e:1,parent:1}))).then(fire(Bind({o:2,e:1,parent:1}))).then(fire(Confirm)).then(check(not(s.accepted) and s.eg.get(1)>s.w.eg and s.ep.get(1)>s.w.ep))
 run actualSingletonRecreationRefusesOldTest=init.then(ready).then(captured).then(fire(DestroyProvider(1))).then(fire(Factory(1))).then(fire(Confirm)).then(check(not(s.accepted) and s.eg.get(1)==s.w.eg and s.ep.get(1)>s.w.ep and s.pg.get(1)>s.w.pg))
 run observedReloadRefusesOldTest=init.then(ready).then(captured).then(fire(ObservedReload(1))).then(fire(Confirm)).then(check(not(s.accepted) and s.eg.get(1)==s.w.eg and s.ep.get(1)>s.w.ep))
 run newSnapshotAfterObservedReloadTest=init.then(ready).then(fire(ObservedReload(1))).then(captured).then(fire(Confirm)).then(check(s.accepted))
 run loaderResetCannotRestartEpochTest=init.then(ready).then(captured).then(fire(LoaderReset)).then(fire(PinLoader(true))).then(fire(Confirm)).then(check(not(s.accepted) and s.refused))
 run sourceReplacementRefusesTest=init.then(ready).then(captured).then(fire(SourceFault)).then(fire(Confirm)).then(check(not(s.accepted)))
 run processReplacementRefusesTest=init.then(ready).then(captured).then(fire(ProcessFault)).then(fire(Confirm)).then(check(not(s.accepted)))
 run wrongThreadRefusesTest=init.then(ready).then(captured).then(fire(ThreadFault)).then(fire(Confirm)).then(check(not(s.accepted)))
 run callerNonceInstanceIdLayerCannotGrantTest=init.then(fire(CallerEpoch(1))).then(fire(InstanceId)).then(fire(NativeLayer)).then(captured).then(fire(Confirm)).then(check(not(s.accepted)))
 run representabilityExhaustionNeverWrapsTest=init.then(ready).then(captured).then(fire(Exhaust)).then(fire(ObservedReload(1))).then(fire(Confirm)).then(check(not(s.accepted) and s.refused and s.nextEpoch==Limit))
 run absentDelegateRefusedTest=init.then(ready).then(fire(Capture({e:1,w:1,d:3}))).then(fire(Confirm)).then(check(not(s.accepted)))
 run widgetCannotBeItsOwnDelegateTest=init.then(ready).then(fire(Capture({e:1,w:1,d:1}))).then(fire(Confirm)).then(check(not(s.accepted)))
 run queryDoesNotIncrementGenerationsTest=init.then(ready).then(captured).then(fire(Confirm)).then(captured).then(fire(Confirm)).then(check(s.accepted and s.nextEngine==2 and s.nextEpoch==2 and s.nextObject==4))
}
