module campaign_b {
  // Observation/acceptance protocol, not a model of actual native reachability.
  type Facts = { modesSame:bool, returnSame:bool, peersSame:bool,
    independentBits:bool, renderObserved:bool, hit:int, core:int, seat:int,
    excluded:int, revived:bool, scrollObserved:bool, scrollSame:bool,
    refused:bool, unpinUsable:bool, transferObserved:bool, truthful:bool,
    partial:bool, claimedSuccess:bool, synthetic:bool, replacementWrites:bool }
  pure val good:Facts = {modesSame:true,returnSame:true,peersSame:true,
    independentBits:true,renderObserved:true,hit:1,core:1,seat:1,
    excluded:2,revived:false,scrollObserved:true,scrollSame:true,
    refused:false,unpinUsable:true,transferObserved:true,truthful:true,
    partial:false,claimedSuccess:true,synthetic:false,replacementWrites:false}
  type State = {area:int,owner:int,source:int,session:int,epoch:int,
    capturedOwner:int,capturedSource:int,capturedSession:int,capturedEpoch:int,
    bound:bool,prepared:bool,input:bool,raw:bool,nativeReach:bool,
    after:bool,confirmed:bool,fault:bool,accepted:bool,facts:Facts}
  pure val empty:State = {area:0,owner:1,source:1,session:1,epoch:1,
    capturedOwner:0,capturedSource:0,capturedSession:0,capturedEpoch:0,
    bound:false,prepared:false,input:false,raw:false,nativeReach:false,
    after:false,confirmed:false,fault:false,accepted:false,facts:good}
  pure def same(s:State):bool = all{s.owner==s.capturedOwner,
    s.source==s.capturedSource,s.session==s.capturedSession,s.epoch==s.capturedEpoch}
  pure def oracle(s:State):bool = all{
    s.area.in(0.to(5)),s.facts.peersSame,s.facts.independentBits,
    not(s.facts.synthetic),not(s.facts.replacementWrites),
    if(s.area==0) s.facts.modesSame else true,
    if(s.area==1) s.facts.modesSame and s.facts.returnSame else true,
    if(s.area==2) all{s.facts.renderObserved,s.facts.hit==1,s.facts.core==1,s.facts.seat==1} else true,
    if(s.area==3) not(s.facts.revived) and s.facts.hit!=s.facts.excluded else true,
    if(s.area==4) s.facts.scrollObserved and
      (s.facts.scrollSame or (s.facts.refused and s.facts.unpinUsable and not(s.facts.claimedSuccess))) else true,
    if(s.area==5) s.facts.transferObserved and s.facts.truthful and
      (not(s.facts.partial) or not(s.facts.claimedSuccess)) else true
  }
  pure def usable(s:State):bool = all{s.bound,s.prepared,s.input,s.raw,
    s.nativeReach,s.after,s.confirmed,not(s.fault),same(s),oracle(s)}
  var s:State
  action init = {s'=empty}
  action bind(area:int):bool = all{not(s.bound),not(s.fault),area.in(0.to(5)),
    s'=s.with("area",area).with("bound",true).with("capturedOwner",s.owner)
      .with("capturedSource",s.source).with("capturedSession",s.session).with("capturedEpoch",s.epoch)}
  action prepare(nativeReach:bool):bool = all{s.bound,not(s.prepared),not(s.fault),same(s),
    s'=s.with("prepared",true).with("nativeReach",nativeReach)}
  action stimulus(physical:bool):bool = all{s.prepared,not(s.fault),same(s),
    s'=s.with("input",physical)}
  // Raw before/after records must be persisted before any assertion.
  action observe(f:Facts):bool = all{s.prepared,not(s.fault),
    s'=s.with("facts",f).with("raw",true).with("after",true).with("confirmed",false).with("accepted",false)}
  action confirm = all{s.raw,not(s.fault),same(s),s'=s.with("confirmed",true)}
  action decide = {s'=s.with("accepted",usable(s))}
  action refuse = {s'=s.with("fault",true).with("confirmed",false).with("accepted",false)}
  action replace(kind:int):bool = {
    s'= (if(kind==0) s.with("owner",s.owner+1)
      else if(kind==1) s.with("source",s.source+1)
      else if(kind==2) s.with("session",s.session+1)
      else s.with("epoch",s.epoch+1)).with("confirmed",false).with("accepted",false)
  }
  action check(ok:bool):bool = all{assert(ok),s'=s}
  action runGood(area:int,f:Facts):bool = bind(area).then(prepare(true))
    .then(stimulus(true)).then(observe(f)).then(confirm).then(decide)
  action step = any {
    bind(0),bind(1),bind(2),bind(3),bind(4),bind(5),prepare(true),prepare(false),
    stimulus(true),stimulus(false),observe(good),observe(good.with("peersSame",false)),
    observe(good.with("seat",0)),observe(good.with("scrollObserved",false)),
    observe(good.with("partial",true)),confirm,decide,refuse,
    replace(0),replace(1),replace(2),replace(3)
  }
  val allProps = all{s.accepted implies usable(s),s.fault implies not(s.accepted),
    s.accepted implies (s.raw and s.nativeReach and s.input),
    s.accepted implies not(s.facts.synthetic),s.accepted implies not(s.facts.replacementWrites),
    s.accepted and s.area==2 implies (s.facts.core==1 and s.facts.seat==1),
    s.accepted and s.area==5 and s.facts.partial implies not(s.facts.claimedSuccess)}
  run ordinaryConservation = init.then(runGood(0,good)).then(check(s.accepted))
  run nativeMaxReturn = init.then(runGood(1,good)).then(check(s.accepted))
  run protectedBandPhysicalFocus = init.then(runGood(2,good)).then(check(s.accepted))
  run excludedRemainsExcluded = init.then(runGood(3,good)).then(check(s.accepted))
  run actualScrollingRestore = init.then(runGood(4,good)).then(check(s.accepted))
  run truthfulTransfer = init.then(runGood(5,good)).then(check(s.accepted))
  run maxModeChangeRefused = init.then(runGood(1,good.with("modesSame",false))).then(check(not(s.accepted)))
  run maxReturnChangeRefused = init.then(runGood(1,good.with("returnSame",false))).then(check(not(s.accepted)))
  run peerChangeRefused = init.then(runGood(1,good.with("peersSame",false))).then(check(not(s.accepted)))
  run inheritedChildBitRefused = init.then(runGood(2,good.with("independentBits",false))).then(check(not(s.accepted)))
  run orderWithoutPresentationRefused = init.then(runGood(2,good.with("renderObserved",false))).then(check(not(s.accepted)))
  run coreWithoutSeatRefused = init.then(runGood(2,good.with("seat",0))).then(check(not(s.accepted)))
  run seatWithoutCoreRefused = init.then(runGood(2,good.with("core",0))).then(check(not(s.accepted)))
  run hitMismatchRefused = init.then(runGood(2,good.with("hit",2))).then(check(not(s.accepted)))
  run excludedWinnerRefused = init.then(runGood(3,good.with("hit",2))).then(check(not(s.accepted)))
  run inputRevivalRefused = init.then(runGood(3,good.with("revived",true))).then(check(not(s.accepted)))
  run geometryWithoutScrollOwnershipRefused = init.then(runGood(4,good.with("scrollObserved",false))).then(check(not(s.accepted)))
  run staleScrollRefusalWithUnpin = init.then(runGood(4,good.with("scrollSame",false).with("refused",true).with("claimedSuccess",false))).then(check(s.accepted))
  run staleScrollCannotClaimRestore = init.then(runGood(4,good.with("scrollSame",false).with("refused",true))).then(check(not(s.accepted)))
  run staleScrollTrappedPinRefused = init.then(runGood(4,good.with("scrollSame",false).with("refused",true).with("claimedSuccess",false).with("unpinUsable",false))).then(check(not(s.accepted)))
  run publicDispatchAckNotTransferWitness = init.then(runGood(5,good.with("transferObserved",false))).then(check(not(s.accepted)))
  run partialTransferTruthfulRefusal = init.then(runGood(5,good.with("partial",true).with("claimedSuccess",false))).then(check(s.accepted))
  run partialTransferFalseSuccessRefused = init.then(runGood(5,good.with("partial",true))).then(check(not(s.accepted)))
  run untruthfulActualModesRefused = init.then(runGood(5,good.with("truthful",false))).then(check(not(s.accepted)))
  run syntheticRollbackRefused = init.then(runGood(5,good.with("synthetic",true))).then(check(not(s.accepted)))
  run replacementWriteRefused = init.then(runGood(5,good.with("replacementWrites",true))).then(check(not(s.accepted)))
  run modelSeedNotNativeReachability = init.then(bind(1)).then(prepare(false)).then(stimulus(true)).then(observe(good)).then(confirm).then(decide).then(check(not(s.accepted)))
  run setupAckNotPhysicalInput = init.then(bind(1)).then(prepare(true)).then(stimulus(false)).then(observe(good)).then(confirm).then(decide).then(check(not(s.accepted)))
  run missingRawNeverAccepts = init.then(bind(1)).then(prepare(true)).then(stimulus(true)).then(decide).then(check(not(s.accepted)))
  run missingPostConfirmationRefused = init.then(bind(1)).then(prepare(true)).then(stimulus(true)).then(observe(good)).then(decide).then(check(not(s.accepted)))
  run ownerReplacementRevokes = init.then(runGood(1,good)).then(replace(0)).then(decide).then(check(not(s.accepted)))
  run sourceReplacementRevokes = init.then(runGood(1,good)).then(replace(1)).then(decide).then(check(not(s.accepted)))
  run sessionReplacementRevokes = init.then(runGood(1,good)).then(replace(2)).then(decide).then(check(not(s.accepted)))
  run episodeReplacementRevokes = init.then(runGood(1,good)).then(replace(3)).then(decide).then(check(not(s.accepted)))
  run refusedConnectionCannotRevive = init.then(runGood(1,good)).then(refuse).then(decide).then(check(not(s.accepted)))
}
