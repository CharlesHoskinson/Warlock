module runtime_metrics {
 // snapshotToken binds the original captured root raw maps. Fresh samples must
 // retain mappingToken and noExecAlias, but unrelated mapping changes are allowed.
 // Mutable timestamps, fileposition and data bytes are excluded from Witness.
 type Witness = {owner:bool, lifetime:int, source:bool, profile:bool, filename:bool,
   inode:bool, fdCount:int, fdAccess:int, regular:bool, uid:bool, nlink:int,
   mode:int, size:int, mount:bool, offset:int, length:int, permissions:str,
   noExecAlias:bool, currentSnapshot:bool, fdNumber:int, deviceToken:int,
   inodeToken:int, mountToken:int, profileToken:int, parentToken:int, rootToken:int,
   executableToken:int, snapshotToken:int, mappingToken:int, targetToken:int, noOPath:bool, fullFlags:int,
   parentState:str, parentPathToken:int, parentMode:int, parentError:int, runtimeToken:int}
 pure val good = {owner:true,lifetime:1,source:true,profile:true,filename:true,
   inode:true,fdCount:1,fdAccess:2,regular:true,uid:true,nlink:0,mode:384,
   size:4194304,mount:true,offset:0,length:4194304,permissions:"rw-s",
   noExecAlias:true,currentSnapshot:true,fdNumber:7,deviceToken:1,inodeToken:1,
   mountToken:1,profileToken:1,parentToken:1,rootToken:1,executableToken:1,
   snapshotToken:1,mappingToken:1,targetToken:1,noOPath:true,fullFlags:32770,
   parentState:"present",parentPathToken:1,parentMode:448,parentError:0,runtimeToken:1}
 // Absent has an exact current path/error witness, no historical inode/mode.
 pure val detached = good.with("parentState","absentENOENT").with("parentToken",0)
   .with("parentMode",0).with("parentError",2)
 pure def validParent(w:Witness):bool = w.parentPathToken>0 and
   ((w.parentState=="present" and w.parentToken>0 and w.parentMode==448 and w.parentError==0) or
    (w.parentState=="absentENOENT" and w.parentToken==0 and w.parentMode==0 and w.parentError==2))
 pure val blank = good.with("owner",false)
 pure def valid(w:Witness):bool = w.owner and w.lifetime>0 and w.source and
   w.profile and w.filename and w.inode and w.fdCount==1 and w.fdAccess==2 and
   w.regular and w.uid and w.nlink==0 and w.mode==384 and w.size==4194304 and
   w.mount and w.offset==0 and w.length==4194304 and w.permissions=="rw-s" and
   w.noExecAlias and w.currentSnapshot and w.fdNumber>=0 and
   w.deviceToken>0 and w.inodeToken>0 and w.mountToken>0 and w.profileToken>0 and
   validParent(w) and w.rootToken>0 and w.runtimeToken>0 and w.executableToken>0 and w.snapshotToken>0 and
   w.mappingToken>0 and w.targetToken>0 and w.noOPath and w.fullFlags>=0
 var before:Witness
 var after:Witness
 var current:Witness
 var epoch:int
 var capturedEpoch:int
 var phase:int
 var accepted:bool
 var inputUsable:bool
 action init=all {before'=blank,after'=blank,current'=blank,epoch'=0,capturedEpoch'=-1,phase'=0,accepted'=false,inputUsable'=false}
 action idle=all {before'=before,after'=after,current'=current,epoch'=epoch,capturedEpoch'=capturedEpoch,phase'=phase,accepted'=accepted,inputUsable'=inputUsable}
 action capture(w:Witness):bool=all {before'=w,after'=blank,current'=w,epoch'=epoch+1,capturedEpoch'=epoch+1,phase'=if(valid(w))1 else 0,accepted'=false,inputUsable'=false}
 action verify(w:Witness):bool={
   val ok=phase==1 and capturedEpoch==epoch and valid(w) and w==current and w==before
   all {before'=before,after'=w,current'=current,epoch'=epoch,capturedEpoch'=capturedEpoch,phase'=if(ok)2 else 0,accepted'=ok,inputUsable'=false}
 }
 action confirm(w:Witness):bool={
   val ok=phase==2 and capturedEpoch==epoch and valid(w) and w==current and w==before and w==after
   all {before'=before,after'=w,current'=current,epoch'=epoch,capturedEpoch'=capturedEpoch,phase'=if(ok)3 else 0,accepted'=ok,inputUsable'=ok}
 }
 // A newly observed identity/snapshot always revokes earlier partial authority.
 action changed(w:Witness):bool=all {before'=before,after'=after,current'=w,
   epoch'=epoch+1,capturedEpoch'=capturedEpoch,phase'=0,accepted'=false,inputUsable'=false}
 action invalidate=changed(blank)
 val allProps=all {
   phase>=0,phase<=3,
   accepted implies capturedEpoch==epoch and current==before and (phase==2 or phase==3) and valid(before) and before==after,
   inputUsable implies phase==3 and accepted and valid(after) and before==after,
   phase==0 implies not(accepted) and not(inputUsable),
   phase==1 implies not(accepted) and not(inputUsable)
 }
 pure val faults=Set(good.with("owner",false),good.with("lifetime",2),
   good.with("source",false),good.with("profile",false),good.with("filename",false),
   good.with("inode",false),good.with("fdCount",0),good.with("fdCount",2),
   good.with("fdAccess",0),good.with("fdAccess",2097154),good.with("regular",false),
   good.with("uid",false),good.with("nlink",1),good.with("mode",0),
   good.with("mode",256),good.with("mode",4480),good.with("mode",896),
   good.with("size",4194303),good.with("size",4194305),good.with("mount",false),
   good.with("offset",4096),good.with("length",4096),good.with("permissions","rwxp"),
   good.with("permissions","r--p"),good.with("noExecAlias",false),good.with("currentSnapshot",false),
   good.with("fdNumber",8),good.with("deviceToken",2),good.with("inodeToken",2),
   good.with("mountToken",2),good.with("profileToken",2),good.with("parentToken",2),
   good.with("rootToken",2),good.with("executableToken",2),good.with("snapshotToken",2),
   good.with("mappingToken",2),good.with("fullFlags",32778),good.with("targetToken",2),good.with("noOPath",false),detached,
   detached.with("parentError",13),detached.with("parentToken",2),
   detached.with("parentMode",448),detached.with("parentState","unknown"),
   detached.with("parentState","symlink"),detached.with("parentState","special"),
   detached.with("parentPathToken",2),good.with("parentMode",4480),
   good.with("parentError",2),good.with("parentState","dangling-symlink"),detached.with("runtimeToken",2))
 action step={
   nondet bad=faults.oneOf()
   any {capture(good),verify(good),confirm(good),capture(bad),verify(bad),confirm(bad),changed(good),changed(bad),invalidate,idle}
 }
}
