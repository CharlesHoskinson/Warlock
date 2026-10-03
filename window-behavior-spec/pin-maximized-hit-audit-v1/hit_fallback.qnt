module hit_fallback {
 type Request={fs:int,protectedFs:bool,band:int,bandEligible:bool,ordinary:int,ordinaryEligible:bool,skip:bool,priority:bool,floatingOnly:bool,layer:bool,special:bool,idealProtected:bool,idealFloatingAllowed:bool}
 pure val base:Request={fs:1,protectedFs:true,band:1,bandEligible:false,ordinary:2,ordinaryEligible:true,skip:false,priority:false,floatingOnly:false,layer:false,special:false,idealProtected:false,idealFloatingAllowed:false}
 pure def bandResult(r:Request):int=if(r.bandEligible)r.band else 0
 pure def ordinaryResult(r:Request):int=if(r.ordinaryEligible)r.ordinary else 0
 pure def oldHit(r:Request):int=if(bandResult(r)!=0)bandResult(r) else if(r.floatingOnly)ordinaryResult(r) else if(r.fs!=0 and not(r.skip) and not(r.priority))if(r.protectedFs)0 else 1 else ordinaryResult(r)
 pure def fixedHit(r:Request):int=if(r.fs==1 and r.protectedFs and bandResult(r)==0)ordinaryResult(r) else oldHit(r)
 pure def oldPointer(r:Request,ideal:int):int=if(r.layer)4 else if(r.fs==1)if(r.special)1 else if(ideal!=0 and r.idealFloatingAllowed)ideal else 1 else ideal
 pure def fixedPointer(r:Request,ideal:int):int=if(r.layer)4 else if(r.fs==1 and not(r.special))if(ideal!=0 and (r.idealFloatingAllowed or r.idealProtected))ideal else if(r.protectedFs)ideal else 1 else oldPointer(r,ideal)
 var request:Request
 action init={request'=base}
 action check(ok:bool):bool=all{assert(ok),request'=request}
 action step={
  nondet fs=0.to(2).oneOf()
  nondet protectedFs=Set(true,false).oneOf()
  nondet band=0.to(3).oneOf()
  nondet bandEligible=Set(true,false).oneOf()
  nondet ordinary=0.to(3).oneOf()
  nondet ordinaryEligible=Set(true,false).oneOf()
  nondet skip=Set(true,false).oneOf()
  nondet priority=Set(true,false).oneOf()
  nondet floatingOnly=Set(true,false).oneOf()
  nondet layer=Set(true,false).oneOf()
  nondet special=Set(true,false).oneOf()
  nondet idealProtected=Set(true,false).oneOf()
  nondet idealFloatingAllowed=Set(true,false).oneOf()
  request'={fs:fs,protectedFs:protectedFs,band:band,bandEligible:bandEligible,ordinary:ordinary,ordinaryEligible:ordinaryEligible,skip:skip,priority:priority,floatingOnly:floatingOnly,layer:layer,special:special,idealProtected:idealProtected,idealFloatingAllowed:idealFloatingAllowed}
 }
 val allProps=all {
  not(request.protectedFs) implies fixedHit(request)==oldHit(request),
  request.fs!=1 implies fixedHit(request)==oldHit(request),
  bandResult(request)!=0 implies fixedHit(request)==bandResult(request),
  request.protectedFs and request.fs==1 and bandResult(request)==0 implies fixedHit(request)==ordinaryResult(request),
  not(request.layer) and not(request.special) and request.protectedFs and request.fs==1 implies fixedPointer(request,fixedHit(request))==fixedHit(request),
  not(request.layer) and not(request.special) and request.idealProtected and fixedHit(request)!=0 implies fixedPointer(request,fixedHit(request))==fixedHit(request),
  request.layer implies fixedPointer(request,fixedHit(request))==4,
  request.special implies fixedPointer(request,fixedHit(request))==oldPointer(request,fixedHit(request)),
  not(request.protectedFs) and not(request.idealProtected) implies fixedPointer(request,fixedHit(request))==oldPointer(request,oldHit(request)),
  request.fs!=1 implies fixedPointer(request,fixedHit(request))==oldPointer(request,oldHit(request)),
 }
 run ignoredProtectedOldCounterexample=init.then(check(oldHit(base)==0 and ordinaryResult(base)==2))
 run ignoredProtectedFallsThrough=init.then(check(fixedHit(base)==2))
 run inputRefusalDoesNotReviveProtected=init.then(check(fixedHit(base.with("ordinaryEligible",false))==0))
 run outsideProtectedUsesEligibleOrdinary=init.then(check(fixedHit(base)==2))
 run nofocusOrdinaryStillRefuses=init.then(check(fixedHit(base.with("ordinaryEligible",false))==0))
 run ordinaryMaxConserved=init.then(check(fixedHit(base.with("protectedFs",false))==oldHit(base.with("protectedFs",false))))
 run exclusiveConserved=init.then(check(fixedHit(base.with("protectedFs",false).with("fs",2))==oldHit(base.with("protectedFs",false).with("fs",2))))
 run noFullscreenConserved=init.then(check(fixedHit(base.with("fs",0))==oldHit(base.with("fs",0))))
 run skipPriorityConserved=init.then(check(fixedHit(base.with("skip",true))==oldHit(base.with("skip",true))))
 run onlyPriorityConserved=init.then(check(fixedHit(base.with("priority",true))==oldHit(base.with("priority",true))))
 run floatingOnlyConserved=init.then(check(fixedHit(base.with("floatingOnly",true))==oldHit(base.with("floatingOnly",true))))
 run protectedBandWinnerPreserved=init.then(check(fixedHit(base.with("bandEligible",true).with("band",3))==3))
 run protectedTiledPointerOldCounterexample=init.then(check(oldPointer(base,3)==1))
 run protectedTiledPointerWinnerPreserved=init.then(check(fixedPointer(base.with("idealProtected",true),3)==3))
 run nullProtectedPointerRemainsNull=init.then(check(fixedPointer(base,0)==0))
 run ordinaryMaxPointerConserved=init.then(check(fixedPointer(base.with("protectedFs",false),3)==oldPointer(base.with("protectedFs",false),3)))
 run exclusivePointerConserved=init.then(check(fixedPointer(base.with("fs",2).with("protectedFs",false),3)==oldPointer(base.with("fs",2).with("protectedFs",false),3)))
 run protectedExclusivePriorityConserved=init.then(check(fixedHit(base.with("fs",2))==oldHit(base.with("fs",2))))
 run protectedExclusivePointerConserved=init.then(check(fixedPointer(base.with("fs",2),3)==oldPointer(base.with("fs",2),3)))
 run layerPriorityPreserved=init.then(check(fixedPointer(base.with("layer",true),3)==4))
 run ordinaryMaxProtectedTiledOldCounterexample=init.then(check(oldPointer(base.with("protectedFs",false).with("idealProtected",true),3)==1))
 run ordinaryMaxProtectedTiledWinnerPreserved=init.then(check(fixedPointer(base.with("protectedFs",false).with("idealProtected",true),3)==3))
 run specialWorkspaceSelectionConserved=init.then(check(fixedPointer(base.with("special",true).with("idealProtected",true),3)==oldPointer(base.with("special",true).with("idealProtected",true),3)))
 run ordinaryAllowedFloatingConserved=init.then(check(fixedPointer(base.with("protectedFs",false).with("idealFloatingAllowed",true),3)==3))
}
