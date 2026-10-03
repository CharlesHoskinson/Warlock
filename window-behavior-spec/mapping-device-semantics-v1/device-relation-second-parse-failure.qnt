module device_relation {
 type Witness={mapDev:int,mountDev:int,namedDev:int,fdDev:int,statxDev:int,mapIno:int,namedIno:int,fdIno:int,statxIno:int,fdMount:int,fdinfoMount:int,selectedMount:int,subvol:int,mountSubvol:int,filesystem:int,mountFilesystem:int,readOnly:bool,noOPath:bool,requiredStatx:bool,strictSource:bool,exactPath:bool,exactRow:bool,stable:bool}
 var w:Witness
 var accepted:bool
 val original={mapDev:30,mountDev:30,namedDev:32,fdDev:32,statxDev:32,mapIno:7,namedIno:7,fdIno:7,statxIno:7,fdMount:33,fdinfoMount:33,selectedMount:33,subvol:256,mountSubvol:256,filesystem:1,mountFilesystem:1,readOnly:true,noOPath:true,requiredStatx:true,strictSource:true,exactPath:true,exactRow:true,stable:true}
 pure def metadata(a:Witness):bool=all{a.namedDev==a.fdDev,a.fdDev==a.statxDev,a.mapIno>0,a.mapIno==a.namedIno,a.mapIno==a.fdIno,a.mapIno==a.statxIno,a.fdMount>0,a.fdMount==a.fdinfoMount,a.fdMount==a.selectedMount,a.readOnly,a.noOPath,a.requiredStatx,a.strictSource,a.exactPath,a.exactRow,a.stable}
 pure def agreement(a:Witness):bool=metadata(a)and(if(a.filesystem==1)all{a.mountFilesystem==1,a.mapDev==a.mountDev,a.subvol>0,a.subvol==a.mountSubvol}else a.mapDev==a.fdDev)
 action init=all{w'=original,accepted'=false}
 action set(a:Witness):bool=all{w'=a,accepted'=false}
 action verify=all{w'=w,accepted'=agreement(w)}
 val allProps=not(accepted)or agreement(w)
 action check(v:bool):bool=all{assert(v),w'=w,accepted'=accepted}
 action step=nondet a=Set(original,{...original,mapDev:31},{...original,mountDev:31},{...original,fdDev:31},{...original,statxDev:31},{...original,fdMount:34},{...original,subvol:257},{...original,filesystem:2},{...original,readOnly:false},{...original,noOPath:false},{...original,requiredStatx:false},{...original,stable:false}).oneOf();set(a).then(verify)
 run distinctBtrfsDeviceDomainsTest=init.then(verify).then(check(accepted and w.mapDev!=w.fdDev))
 run identicalNonBtrfsDevicesTest=init.then(set({...original,filesystem:2,mountFilesystem:2,mapDev:32})).then(verify).then(check(accepted))
 run nonBtrfsCannotUseMountFallbackTest=init.then(set({...original,filesystem:2})).then(verify).then(check(not(accepted)))
 run wrongMapsDeviceTest=init.then(set({...original,mapDev:31})).then(verify).then(check(not(accepted)))
 run wrongMountDeviceTest=init.then(set({...original,mountDev:31})).then(verify).then(check(not(accepted)))
 run wrongStatDeviceTest=init.then(set({...original,namedDev:31})).then(verify).then(check(not(accepted)))
 run wrongFDDeviceTest=init.then(set({...original,fdDev:31})).then(verify).then(check(not(accepted)))
 run wrongStatxDeviceTest=init.then(set({...original,statxDev:31})).then(verify).then(check(not(accepted)))
 run wrongFDInodeTest=init.then(set({...original,fdIno:8})).then(verify).then(check(not(accepted)))
 run wrongMapInodeTest=init.then(set({...original,mapIno:8})).then(verify).then(check(not(accepted)))
 run wrongStatxInodeTest=init.then(set({...original,statxIno:8})).then(verify).then(check(not(accepted)))
 run wrongMountIDTest=init.then(set({...original,selectedMount:34})).then(verify).then(check(not(accepted)))
 run wrongFDInfoMountIDTest=init.then(set({...original,fdinfoMount:34})).then(verify).then(check(not(accepted)))
 run zeroMountIDTest=init.then(set({...original,fdMount:0,fdinfoMount:0,selectedMount:0})).then(verify).then(check(not(accepted)))
 run wrongSubvolumeTest=init.then(set({...original,subvol:257})).then(verify).then(check(not(accepted)))
 run zeroSubvolumeTest=init.then(set({...original,subvol:0,mountSubvol:0})).then(verify).then(check(not(accepted)))
 run falseBtrfsMountTypeTest=init.then(set({...original,mountFilesystem:2})).then(verify).then(check(not(accepted)))
 run writableFDTest=init.then(set({...original,readOnly:false})).then(verify).then(check(not(accepted)))
 run OPathFDTest=init.then(set({...original,noOPath:false})).then(verify).then(check(not(accepted)))
 run missingStatxProofTest=init.then(set({...original,requiredStatx:false})).then(verify).then(check(not(accepted)))
 run frozenSourceMismatchTest=init.then(set({...original,strictSource:false})).then(verify).then(check(not(accepted)))
 run mapFilesPathMismatchTest=init.then(set({...original,exactPath:false})).then(verify).then(check(not(accepted)))
 run changedRawVMATest=init.then(set({...original,exactRow:false})).then(verify).then(check(not(accepted)))
 run changedBoundedLifetimeTest=init.then(set({...original,stable:false})).then(verify).then(check(not(accepted)))
}
