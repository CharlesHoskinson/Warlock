module package_modes {
 var sourceMode:int
 var declaredMode:int
 var installedMode:int
 var beforeMode:int
 var beforeBytes:int
 var sourceBytes:int
 var installedBytes:int
 var accepted:bool
 var applied:bool
 pure def valid(mode:int):bool=mode==420 or mode==493
 action init=all{sourceMode'=493,declaredMode'=493,installedMode'=0,beforeMode'=420,beforeBytes'=1,sourceBytes'=2,installedBytes'=1,accepted'=false,applied'=false}
 action source(mode:int,declared:int):bool=all{sourceMode'=mode,declaredMode'=declared,installedMode'=installedMode,beforeMode'=beforeMode,beforeBytes'=beforeBytes,sourceBytes'=sourceBytes,installedBytes'=installedBytes,accepted'=false,applied'=false}
 action validate=all{accepted'=(valid(sourceMode) and sourceMode==declaredMode),sourceMode'=sourceMode,declaredMode'=declaredMode,installedMode'=installedMode,beforeMode'=beforeMode,beforeBytes'=beforeBytes,sourceBytes'=sourceBytes,installedBytes'=installedBytes,applied'=applied}
 action apply=all{accepted,installedMode'=declaredMode,installedBytes'=sourceBytes,applied'=true,sourceMode'=sourceMode,declaredMode'=declaredMode,beforeMode'=beforeMode,beforeBytes'=beforeBytes,sourceBytes'=sourceBytes,accepted'=accepted}
 action rollback=all{applied,installedMode'=beforeMode,installedBytes'=beforeBytes,applied'=false,sourceMode'=sourceMode,declaredMode'=declaredMode,beforeMode'=beforeMode,beforeBytes'=beforeBytes,sourceBytes'=sourceBytes,accepted'=accepted}
 action idle=all{sourceMode'=sourceMode,declaredMode'=declaredMode,installedMode'=installedMode,beforeMode'=beforeMode,beforeBytes'=beforeBytes,sourceBytes'=sourceBytes,installedBytes'=installedBytes,accepted'=accepted,applied'=applied}
 action step=any{source(420,420),source(493,493),source(511,511),source(2541,2541),source(493,420),validate,apply,rollback,idle}
 val safe=(accepted implies (valid(sourceMode) and sourceMode==declaredMode)) and (applied implies installedMode==declaredMode and installedBytes==sourceBytes)
 run executablePreservedTest=init.then(validate).then(apply).then(all{assert(installedMode==493),idle})
 run dataPreservedTest=init.then(source(420,420)).then(validate).then(apply).then(all{assert(installedMode==420),idle})
 run unsafeModeRefusedTest=init.then(source(511,511)).then(validate).then(all{assert(not(accepted) and not(applied)),idle})
 run specialModeRefusedTest=init.then(source(2541,2541)).then(validate).then(all{assert(not(accepted)),idle})
 run mismatchedModeRefusedTest=init.then(source(493,420)).then(validate).then(all{assert(not(accepted)),idle})
 run rollbackExactModeBytesTest=init.then(validate).then(apply).then(rollback).then(all{assert(installedMode==beforeMode and installedBytes==beforeBytes),idle})
}
