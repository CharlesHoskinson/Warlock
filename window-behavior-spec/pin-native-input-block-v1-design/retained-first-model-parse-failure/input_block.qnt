module input_block {
  type State={owner:int,captured:int,source:int,capturedSource:int,pinned:bool,
    mapped:bool,hidden:bool,noFocus:bool,allowsInput:bool,block:int,
    sourceMonocle:bool,nativeBlock:bool,raw:bool,physical:bool,hit:int,core:int,seat:int,
    ownerCallback:bool,confirmed:bool,accepted:bool}
  pure val empty:State={owner:1,captured:1,source:1,capturedSource:1,pinned:true,
    mapped:true,hidden:false,noFocus:false,allowsInput:false,block:0,
    sourceMonocle:false,nativeBlock:false,raw:false,physical:false,hit:0,core:0,seat:0,
    ownerCallback:false,confirmed:false,accepted:false}
  var s:State
  pure def accepts(s:State):bool=not(s.hidden) and s.block==0
  pure def usable(s:State):bool=all{s.owner==s.captured,s.source==s.capturedSource,
    s.pinned,s.mapped,not(s.hidden),not(s.noFocus),s.block==2,s.sourceMonocle,
    s.nativeBlock,s.raw,s.physical,s.confirmed,s.hit!=1,s.core!=1,s.seat!=1,not(s.ownerCallback)}
  action init={s'=empty}
  action propertyFalse={s'=s.with("allowsInput",false).with("confirmed",false).with("accepted",false)}
  action declaredMonocle={s'=s.with("sourceMonocle",true).with("raw",false).with("nativeBlock",false).with("confirmed",false).with("accepted",false)}
  // Represents source-authenticated actual current observation; no native reachability claim.
  action nativeCurrent(hidden:bool)={s'=s.with("block",2).with("hidden",hidden)
    .with("nativeBlock",true).with("raw",true).with("confirmed",false).with("accepted",false)}
  action input(hit:int,core:int,seat:int,callback:bool)={s'=s.with("physical",true)
    .with("hit",hit).with("core",core).with("seat",seat).with("ownerCallback",callback)
    .with("confirmed",false).with("accepted",false)}
  action confirm={s'=s.with("confirmed",s.raw and s.owner==s.captured and s.source==s.capturedSource)}
  action decide={s'=s.with("accepted",usable(s))}
  action replace={s'=s.with("owner",2).with("confirmed",false).with("accepted",false)}
  action replaceSource={s'=s.with("source",2).with("confirmed",false).with("accepted",false)}
  action clear={s'=s.with("block",0).with("nativeBlock",false).with("raw",false)
    .with("confirmed",false).with("accepted",false)}
  action check(ok:bool)=all{assert(ok),s'=s}
  action good=declaredMonocle.then(nativeCurrent(false)).then(input(2,2,2,false)).then(confirm).then(decide)
  val allProps=not(s.accepted)or usable(s)
  action step=any{propertyFalse,declaredMonocle,nativeCurrent(false),nativeCurrent(true),
    input(2,2,2,false),input(1,2,2,false),input(2,1,2,false),input(2,2,1,false),input(2,2,2,true),
    confirm,decide,replace,replaceSource,clear}
  run falsePropertyDoesNotBlock=init.then(propertyFalse).then(check(accepts(s)))
  run declarationAckNotNativeBlock=init.then(declaredMonocle).then(input(2,2,2,false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run actualIsolatedBlockAccepted=init.then(good).then(check(s.accepted))
  run noPhysicalInputRefused=init.then(declaredMonocle).then(nativeCurrent(false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run noCurrentConfirmationRefused=init.then(declaredMonocle).then(nativeCurrent(false)).then(input(2,2,2,false)).then(decide).then(check(not(s.accepted)))
  run revivedOwnerHitRefused=init.then(good).then(input(1,2,2,false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run ownerCoreRefused=init.then(good).then(input(2,1,2,false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run ownerSeatRefused=init.then(good).then(input(2,2,1,false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run ownerCallbackRefused=init.then(good).then(input(2,2,2,true)).then(confirm).then(decide).then(check(not(s.accepted)))
  run hiddenNotIsolated=init.then(declaredMonocle).then(nativeCurrent(true)).then(input(2,2,2,false)).then(confirm).then(decide).then(check(not(s.accepted)))
  run replacementRevokes=init.then(good).then(replace).then(confirm).then(decide).then(check(not(s.accepted)))
  run nativeClearRevokesOldBlock=init.then(good).then(clear).then(confirm).then(decide).then(check(not(s.accepted)and accepts(s)))
  run sourceReplacementRevokes=init.then(good).then(replaceSource).then(confirm).then(decide).then(check(not(s.accepted)))
  run lateDeclarationCannotRebindOldObservation=init.then(nativeCurrent(false)).then(declaredMonocle).then(input(2,2,2,false)).then(confirm).then(decide).then(check(not(s.accepted)))
}
