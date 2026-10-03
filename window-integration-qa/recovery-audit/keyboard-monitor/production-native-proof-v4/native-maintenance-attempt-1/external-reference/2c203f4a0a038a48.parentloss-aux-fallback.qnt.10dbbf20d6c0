module nested_selection {
  type State = {mode:str, chosen:bool, auxiliary:bool, implementations:Set[str], parentAttempted:bool, parentAlive:bool, headlessAlive:bool, drmAlive:bool, rejected:bool, ready:bool, drmAttempts:int, parentLost:bool}
  type Event = Select({mode:str,aux:bool}) | StartParent(bool) | StartAux(bool) | StartDrm(bool) | FinishStartup | ParentLoss | NewGpu
  var s: State
  pure val initial = {mode:"pending",chosen:false,auxiliary:false,implementations:Set(),parentAttempted:false,parentAlive:false,headlessAlive:false,drmAlive:false,rejected:false,ready:false,drmAttempts:0,parentLost:false}
  action init = s'=initial
  def transition(e:Event): State = match e {
    | Select(choice) => if (s.chosen) s else {
        ...s, mode:choice.mode, chosen:true, auxiliary:choice.aux,
        implementations:if (choice.mode=="wayland") Set("wayland").union(if(choice.aux)Set("headless")else Set()) else if(choice.mode=="unset")Set("wayland","drm").union(if(choice.aux)Set("headless")else Set())else Set(),
        rejected:choice.mode=="invalid"
      }
    | StartParent(ok) => if (not(s.chosen) or s.rejected or s.parentAttempted or not(s.implementations.contains("wayland"))) s else {...s,parentAttempted:true,parentAlive:ok,rejected:s.mode=="wayland" and not(ok)}
    | StartAux(ok) => if (not(s.chosen) or s.rejected or not(s.auxiliary) or (s.mode=="wayland" and not(s.parentAlive))) s else {...s,headlessAlive:ok}
    | StartDrm(ok) => if (not(s.chosen) or s.rejected or s.mode!="unset") s else {...s,drmAttempts:s.drmAttempts+1,drmAlive:ok}
    | NewGpu => if (not(s.chosen) or s.rejected or s.mode!="unset") s else {...s,drmAttempts:s.drmAttempts+1,drmAlive:true}
    | FinishStartup => {...s,ready:not(s.rejected) and (if(s.mode=="wayland")s.parentAlive else if(s.mode=="unset")s.parentAlive or s.headlessAlive or s.drmAlive else false)}
    | ParentLoss => if(not(s.parentAlive)) s else {...s,parentAlive:false,parentLost:true,rejected:if(s.mode=="wayland")true else s.rejected,ready:s.headlessAlive or s.drmAlive}
  }
  action apply(e:Event):bool = s'=transition(e)
  action step = {
    nondet event=Set(Select({mode:"wayland",aux:true}),Select({mode:"wayland",aux:false}),Select({mode:"invalid",aux:true}),Select({mode:"unset",aux:true}),Select({mode:"unset",aux:false}),StartParent(true),StartParent(false),StartAux(true),StartAux(false),StartDrm(true),StartDrm(false),NewGpu,FinishStartup,ParentLoss).oneOf()
    apply(event)
  }
  val noNativeFallback = s.mode!="wayland" or (s.drmAttempts==0 and not(s.drmAlive) and not(s.implementations.contains("drm")))
  val mandatoryParent = not(s.ready) or s.mode!="wayland" or (s.parentAlive and s.parentAttempted and not(s.rejected) and not(s.parentLost))
  val failedParentCannotRecover = s.mode!="wayland" or not(s.rejected) or (not(s.ready) and not(s.parentAlive))
  val invalidRefusedBeforeConstruction = s.mode!="invalid" or (s.rejected and s.implementations.size()==0 and s.drmAttempts==0 and not(s.ready))
  val auxiliaryCannotReplaceParent = s.mode!="wayland" or not(s.headlessAlive) or s.parentAttempted
  val safe = noNativeFallback and mandatoryParent and failedParentCannotRecover and invalidRefusedBeforeConstruction and auxiliaryCannotReplaceParent
  action check(p:bool):bool=all {assert(p),s'=s}
  run mandatoryWaylandConstructedWithoutDrmTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(check(s.implementations==Set("wayland","headless") and not(s.ready) and safe))
  run strictInitialDrmRequestsRefusedTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartDrm(true))).then(apply(NewGpu)).then(check(s.drmAttempts==0 and safe))
  run lateGpuCannotCreateDrmTest=init.then(apply(Select({mode:"wayland",aux:false}))).then(apply(StartParent(true))).then(apply(FinishStartup)).then(apply(NewGpu)).then(check(s.ready and s.drmAttempts==0 and safe))
  run failedMandatoryParentCannotUseAuxiliaryTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartParent(false))).then(apply(StartAux(true))).then(apply(FinishStartup)).then(check(s.rejected and not(s.ready) and not(s.headlessAlive) and safe))
  run auxiliaryBeforeMandatoryStartRefusedTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartAux(true))).then(check(not(s.headlessAlive) and safe))
  run successfulParentAllowsAuxiliaryTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartParent(true))).then(apply(StartAux(true))).then(apply(FinishStartup)).then(check(s.ready and s.parentAlive and s.headlessAlive and safe))
  run parentLossCannotFallbackToLiveAuxiliaryTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartParent(true))).then(apply(StartAux(true))).then(apply(FinishStartup)).then(apply(ParentLoss)).then(apply(FinishStartup)).then(check(s.headlessAlive and s.rejected and not(s.ready) and safe))
  run lostParentIgnoresLateStartAndGpuTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartParent(true))).then(apply(ParentLoss)).then(apply(StartParent(true))).then(apply(NewGpu)).then(apply(FinishStartup)).then(check(not(s.parentAlive) and not(s.ready) and s.drmAttempts==0 and safe))
  run invalidSelectionMakesNoBackendTest=init.then(apply(Select({mode:"invalid",aux:true}))).then(apply(StartParent(true))).then(apply(StartAux(true))).then(apply(StartDrm(true))).then(apply(NewGpu)).then(apply(FinishStartup)).then(check(s.implementations.size()==0 and not(s.ready) and safe))
  run unsetPreservesDrmStartupTest=init.then(apply(Select({mode:"unset",aux:false}))).then(apply(StartDrm(true))).then(apply(FinishStartup)).then(check(s.drmAlive and s.ready and s.drmAttempts==1 and safe))
  run unsetPreservesLateGpuTest=init.then(apply(Select({mode:"unset",aux:false}))).then(apply(NewGpu)).then(apply(FinishStartup)).then(check(s.drmAlive and s.ready and s.drmAttempts==1 and safe))
  run rejectedParentNotRetargetedByLateSelectionTest=init.then(apply(Select({mode:"wayland",aux:true}))).then(apply(StartParent(false))).then(apply(Select({mode:"unset",aux:true}))).then(apply(StartDrm(true))).then(check(s.mode=="wayland" and s.rejected and s.drmAttempts==0 and safe))
}
