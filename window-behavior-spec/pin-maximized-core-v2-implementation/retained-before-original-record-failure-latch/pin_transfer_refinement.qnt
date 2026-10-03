module pin_transfer_refinement {
 type State={owner:int,target:int,space:int,output:int,generation:int,live:bool,visible:bool,normal:bool,pinned:bool,peerPinned:bool,mode:int,client:int,geometry:int,restore:int,usable:bool,phase:int,recordOwner:int,recordTarget:int,expectedSpace:int,expectedOutput:int,expectedGeneration:int,beforeMode:int,beforeClient:int,accepted:bool,reported:bool,intentClears:int,nativeWrites:int,floatWrites:int}
 var s:State
 val initial={owner:1,target:10,space:20,output:30,generation:1,live:true,visible:true,normal:true,pinned:true,peerPinned:true,mode:1,client:1,geometry:100,restore:101,usable:true,phase:0,recordOwner:1,recordTarget:10,expectedSpace:21,expectedOutput:31,expectedGeneration:1,beforeMode:1,beforeClient:1,accepted:false,reported:false,intentClears:0,nativeWrites:0,floatWrites:0}
 action init=s'=initial
 val owned=s.live and s.visible and s.normal and s.owner==s.recordOwner and s.target==s.recordTarget and s.generation>0
 action begin=all{s.phase==0,owned,s.usable,s'=s.with("phase",1).with("expectedGeneration",s.generation).with("beforeMode",s.mode).with("beforeClient",s.client)}
 action moved=all{s.phase==1,owned,s.space==20,s.output==30,s.generation==s.expectedGeneration,s'=s.with("phase",2).with("space",s.expectedSpace).with("output",s.expectedOutput)}
 action complete(ok:bool):bool=all{s.phase==2,s'=if(owned and s.usable and s.generation==s.expectedGeneration and s.space==s.expectedSpace and s.output==s.expectedOutput and ok) s.with("phase",3).with("mode",s.beforeMode).with("client",s.beforeClient).with("accepted",true).with("reported",true) else s.with("phase",4).with("usable",false).with("accepted",false).with("reported",true)}
 action failActual(mode:int,client:int):bool=all{s.phase==2,s'=s.with("mode",mode).with("client",client).with("usable",false).with("phase",4).with("accepted",false).with("reported",true)}
 action close=s'=s.with("live",false).with("usable",false).with("accepted",false)
 action replace=s'=s.with("owner",s.owner+1).with("target",s.target+1).with("accepted",false).with("usable",false)
 action staleOutput=s'=s.with("output",s.output+1).with("accepted",false).with("usable",false)
 action staleReturn=s'=s.with("usable",false).with("accepted",false)
 action unpin(capturedOwner:int,capturedTarget:int,capturedGeneration:int):bool=s'=if(owned and s.pinned and capturedOwner==s.owner and capturedTarget==s.target and capturedGeneration==s.generation) s.with("pinned",false).with("intentClears",s.intentClears+1) else s
 action changeGeneration=s'=s.with("generation",s.generation+1).with("accepted",false)
 action step=any{begin,moved,complete(true),complete(false),failActual(0,1),close,replace,staleOutput,staleReturn,unpin(1,10,1),changeGeneration}
 val acceptedExact=s.accepted implies (s.phase==3 and owned and s.generation==s.expectedGeneration and s.usable and s.mode==s.beforeMode and s.client==s.beforeClient and s.space==s.expectedSpace and s.output==s.expectedOutput and s.reported)
 val noFabricatedRestoration=s.nativeWrites==0 and s.floatWrites==0 and s.geometry==100 and s.restore==101 and s.peerPinned
 val refusedReported=s.phase==4 implies (s.reported and not(s.accepted) and not(s.usable))
 run staleReturnCannotPromote=init.then(begin).then(moved).then(staleReturn).then(complete(true)).then(all{assert(not(s.accepted) and s.reported),s'=s})
 run changedGenerationCannotPromote=init.then(begin).then(moved).then(changeGeneration).then(complete(true)).then(all{assert(not(s.accepted) and s.reported),s'=s})
 val allProps=acceptedExact and noFabricatedRestoration and refusedReported
 run positiveTransfer=init.then(begin).then(moved).then(complete(true)).then(all{assert(allProps and s.accepted),s'=s})
 run missingHandlerRetained=init.then(begin).then(moved).then(failActual(0,1)).then(all{assert(allProps and s.mode==0 and s.client==1 and s.beforeMode==1),s'=s})
 run closeBeforeFinish=init.then(begin).then(moved).then(close).then(complete(true)).then(all{assert(allProps and not(s.accepted)),s'=s})
 run replaceBeforeFinish=init.then(begin).then(moved).then(replace).then(complete(true)).then(all{assert(allProps and not(s.accepted)),s'=s})
 run staleOutputBeforeFinish=init.then(begin).then(moved).then(staleOutput).then(complete(true)).then(all{assert(allProps and not(s.accepted)),s'=s})
 run nativeRefusalRetained=init.then(begin).then(moved).then(complete(false)).then(all{assert(allProps and not(s.accepted)),s'=s})
 run staleReturnUnpin=init.then(staleReturn).then(unpin(1,10,1)).then(all{assert(allProps and not(s.pinned) and not(s.usable)),s'=s})
 run failedTransferUnpin=init.then(begin).then(moved).then(failActual(0,1)).then(unpin(1,10,1)).then(all{assert(allProps and not(s.pinned) and s.mode==0 and s.client==1),s'=s})
 run closedUnpinRefused=init.then(close).then(unpin(1,10,1)).then(all{assert(allProps and s.pinned and s.intentClears==0),s'=s})
 run replacedUnpinRefused=init.then(replace).then(unpin(1,10,1)).then(all{assert(allProps and s.pinned and s.intentClears==0),s'=s})
 run oldGenerationUnpinRefused=init.then(changeGeneration).then(unpin(1,10,1)).then(all{assert(allProps and s.pinned and s.intentClears==0),s'=s})
 run freshGenerationUnpin=init.then(staleReturn).then(changeGeneration).then(unpin(1,10,2)).then(all{assert(allProps and not(s.pinned)),s'=s})
 run wrongOwnerUnpinRefused=init.then(staleReturn).then(unpin(2,10,1)).then(all{assert(allProps and s.pinned),s'=s})
 run wrongTargetUnpinRefused=init.then(staleReturn).then(unpin(1,11,1)).then(all{assert(allProps and s.pinned),s'=s})
 run repeatUnpinNoFurtherWrite=init.then(staleReturn).then(unpin(1,10,1)).then(unpin(1,10,1)).then(all{assert(allProps and s.intentClears==1),s'=s})
 run changedGeometryNotRestored=init.then(begin).then(moved).then(failActual(0,1)).then(unpin(1,10,1)).then(all{assert(s.geometry==100 and s.restore==101 and s.nativeWrites==0 and s.floatWrites==0),s'=s})
}
