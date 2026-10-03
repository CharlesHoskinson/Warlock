module runtime_authority_test {
 import runtime_authority.* from "./runtime_authority"
 pure val disk={owned:true,frozen:true,sameBytes:true,sameMode:true,deleted:false,runtime:false,cache:false,executable:true,regular:true}
 run exactDiskTest=init.then(observe(disk)).then(all{assert(accepted and allProps),observe(disk)})
 run changedBytesTest=init.then(observe(disk.with("sameBytes",false))).then(all{assert(not(accepted) and allProps),observe(disk)})
 run changedModeTest=init.then(observe(disk.with("sameMode",false))).then(all{assert(not(accepted) and allProps),observe(disk)})
 run cacheDataTest=init.then(observe(disk.with("runtime",true).with("cache",true).with("executable",false))).then(all{assert(accepted and allProps),observe(disk)})
 run runtimeExecutableRefusedTest=init.then(observe(disk.with("runtime",true).with("cache",true))).then(all{assert(not(accepted) and allProps),observe(disk)})
 run otherRuntimeRefusedTest=init.then(observe(disk.with("runtime",true).with("executable",false))).then(all{assert(not(accepted) and allProps),observe(disk)})
 run staleOwnedRefusedTest=init.then(observe(disk.with("owned",false))).then(all{assert(not(accepted) and allProps),observe(disk)})
 run deletedRefusedTest=init.then(observe(disk.with("deleted",true))).then(all{assert(not(accepted) and allProps),observe(disk)})
}
