module hit_fallback {
 type Request={fs:int,protectedFs:bool,band:int,bandEligible:bool,ordinary:int,ordinaryEligible:bool,skip:bool,priority:bool,floatingOnly:bool,layer:bool}
 pure val base:Request={fs:1,protectedFs:true,band:1,bandEligible:false,ordinary:2,ordinaryEligible:true,skip:false,priority:false,floatingOnly:false,layer:false}
 pure def bandResult(r:Request):int=if(r.bandEligible)r.band else 0
 pure def ordinaryResult(r:Request):int=if(r.ordinaryEligible)r.ordinary else 0
 pure def oldHit(r:Request):int=if(bandResult(r)!=0)bandResult(r) else if(r.floatingOnly)ordinaryResult(r) else if(r.fs!=0 and not(r.skip) and not(r.priority))if(r.protectedFs)0 else 1 else ordinaryResult(r)
 pure def fixedHit(r:Request):int=if(bandResult(r)!=0)bandResult(r) else if(r.floatingOnly)ordinaryResult(r) else if(r.fs!=0 and not(r.skip) and not(r.priority) and not(r.protectedFs))1 else ordinaryResult(r)
 pure def oldPointer(r:Request,ideal:int):int=if(r.layer)4 else if(r.fs==1)1 else ideal
 pure def fixedPointer(r:Request,ideal:int):int=if(r.layer)4 else if(r.fs==1 and not(r.protectedFs))1 else ideal
 var request:Request
 action init={request'=base}
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
  request'={fs:fs,protectedFs:protectedFs,band:band,bandEligible:bandEligible,ordinary:ordinary,ordinaryEligible:ordinaryEligible,skip:skip,priority:priority,floatingOnly:floatingOnly,layer:layer}
 }
 val allProps=all {
  not(request.protectedFs) implies fixedHit(request)==oldHit(request),
  request.bandEligible implies fixedHit(request)==request.band,
  request.protectedFs and not(request.bandEligible) implies fixedHit(request)==ordinaryResult(request),
  not(request.layer) and request.protectedFs implies fixedPointer(request,fixedHit(request))==fixedHit(request),
  request.layer implies fixedPointer(request,fixedHit(request))==4,
  not(request.protectedFs) implies fixedPointer(request,fixedHit(request))==oldPointer(request,oldHit(request)),
 }
 run ignoredProtectedOldCounterexample=init.then(assert(oldHit(base)==0 and ordinaryResult(base)==2))
 run ignoredProtectedFallsThrough=init.then(assert(fixedHit(base)==2))
 run inputRefusalDoesNotReviveProtected=init.then(assert(fixedHit(base.with("ordinaryEligible",false))==0))
 run outsideProtectedUsesEligibleOrdinary=init.then(assert(fixedHit(base)==2))
 run nofocusOrdinaryStillRefuses=init.then(assert(fixedHit(base.with("ordinaryEligible",false))==0))
 run ordinaryMaxConserved=init.then(assert(fixedHit(base.with("protectedFs",false))==oldHit(base.with("protectedFs",false))))
 run exclusiveConserved=init.then(assert(fixedHit(base.with("protectedFs",false).with("fs",2))==oldHit(base.with("protectedFs",false).with("fs",2))))
 run noFullscreenConserved=init.then(assert(fixedHit(base.with("fs",0))==oldHit(base.with("fs",0))))
 run skipPriorityConserved=init.then(assert(fixedHit(base.with("skip",true))==oldHit(base.with("skip",true))))
 run onlyPriorityConserved=init.then(assert(fixedHit(base.with("priority",true))==oldHit(base.with("priority",true))))
 run floatingOnlyConserved=init.then(assert(fixedHit(base.with("floatingOnly",true))==oldHit(base.with("floatingOnly",true))))
 run protectedBandWinnerPreserved=init.then(assert(fixedHit(base.with("bandEligible",true).with("band",3))==3))
 run protectedTiledPointerOldCounterexample=init.then(assert(oldPointer(base,3)==1))
 run protectedTiledPointerWinnerPreserved=init.then(assert(fixedPointer(base,3)==3))
 run nullProtectedPointerRemainsNull=init.then(assert(fixedPointer(base,0)==0))
 run ordinaryMaxPointerConserved=init.then(assert(fixedPointer(base.with("protectedFs",false),3)==oldPointer(base.with("protectedFs",false),3)))
 run exclusivePointerConserved=init.then(assert(fixedPointer(base.with("fs",2).with("protectedFs",false),3)==oldPointer(base.with("fs",2).with("protectedFs",false),3)))
 run layerPriorityPreserved=init.then(assert(fixedPointer(base.with("layer",true),3)==4))
}
