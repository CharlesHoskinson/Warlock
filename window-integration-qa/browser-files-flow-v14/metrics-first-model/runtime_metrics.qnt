module runtime_metrics {
 type Witness = {owner:bool, lifetime:int, source:bool, profile:bool, filename:bool,
   inode:bool, fdCount:int, fdAccess:int, regular:bool, uid:bool, nlink:int,
   mode:int, size:int, mount:bool, offset:int, length:int, permissions:str,
   noExecAlias:bool, currentSnapshot:bool}
 pure val good = {owner:true,lifetime:1,source:true,profile:true,filename:true,
   inode:true,fdCount:1,fdAccess:2,regular:true,uid:true,nlink:0,mode:384,
   size:4194304,mount:true,offset:0,length:4194304,permissions:"rw-s",
   noExecAlias:true,currentSnapshot:true}
 pure val blank = good.with("owner",false)
 pure def valid(w:Witness):bool = w.owner and w.lifetime>0 and w.source and
   w.profile and w.filename and w.inode and w.fdCount==1 and w.fdAccess==2 and
   w.regular and w.uid and w.nlink==0 and w.mode==384 and w.size==4194304 and
   w.mount and w.offset==0 and w.length==4194304 and w.permissions=="rw-s" and
   w.noExecAlias and w.currentSnapshot
 var before:Witness
 var after:Witness
 var phase:int
 var accepted:bool
 var inputUsable:bool
 action init=all {before'=blank,after'=blank,phase'=0,accepted'=false,inputUsable'=false}
 action idle=all {before'=before,after'=after,phase'=phase,accepted'=accepted,inputUsable'=inputUsable}
 action capture(w:Witness):bool=all {before'=w,after'=blank,phase'=if(valid(w))1 else 0,accepted'=false,inputUsable'=false}
 action verify(w:Witness):bool={
   val ok=phase==1 and valid(w) and w==before
   all {before'=before,after'=w,phase'=if(ok)2 else 0,accepted'=ok,inputUsable'=false}
 }
 action confirm(w:Witness):bool={
   val ok=phase==2 and valid(w) and w==before and w==after
   all {before'=before,after'=w,phase'=if(ok)3 else 0,accepted'=ok,inputUsable'=ok}
 }
 action invalidate=init
 val allProps=all {
   phase>=0,phase<=3,
   accepted implies (phase==2 or phase==3) and valid(before) and before==after,
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
   good.with("permissions","r--p"),good.with("noExecAlias",false),good.with("currentSnapshot",false))
 action step={
   nondet bad=faults.oneOf()
   any {capture(good),verify(good),confirm(good),capture(bad),verify(bad),confirm(bad),invalidate,idle}
 }
}
