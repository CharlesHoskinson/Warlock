/** Whole-window export must include every visible compositor-owned frame pixel.
 * Off-output decoration extents may be clipped only with the client fully inside
 * its output; spanning client rectangles use FailedCapture, never clipped pixels. A cached frame
 * is usable only by its captured PID/stable ID; pixel bounds never resize native.
 */
module whole_snapshot {
 type Event=Capture | Hide | Restore | Close | Reuse | OldCapture | FailedCapture | Prune | ClipDecoration
 type State={live:bool,id:int,pid:int,nativeRect:int,savedRect:int,cacheId:int,cachePid:int,
   whole:bool,hidden:bool,visual:bool,header:bool,snapshotRect:int}
 var s:State
 action init=s'={live:true,id:1,pid:100,nativeRect:42,savedRect:42,cacheId:0,cachePid:0,whole:false,hidden:false,visual:false,header:false,snapshotRect:0}
 action fire(e:Event):bool={s'=match e {
  | Capture => if(not(s.live) or s.hidden)s else {...s,cacheId:s.id,cachePid:s.pid,whole:true,header:true,snapshotRect:66}
  | ClipDecoration => if(not(s.live) or s.hidden)s else {...s,cacheId:s.id,cachePid:s.pid,whole:true,header:true,snapshotRect:55}
  | Hide => if(not(s.live))s else {...s,hidden:true,visual:s.whole and s.cacheId==s.id and s.cachePid==s.pid}
  | Restore => if(not(s.live))s else {...s,hidden:false,visual:s.whole and s.cacheId==s.id and s.cachePid==s.pid}
  | Close => {...s,live:false,whole:false,visual:false,header:false}
  | Reuse => if(s.live)s else {...s,live:true,id:s.id+1,pid:s.pid+1,nativeRect:73,savedRect:73,hidden:false,whole:false,visual:false,header:false}
  | Prune => if(s.live and s.cacheId==s.id and s.cachePid==s.pid)s else {...s,cacheId:0,cachePid:0,whole:false,header:false,visual:false}
  | OldCapture => s
  | FailedCapture => {...s,whole:false,visual:false,header:false}
 }}
 action step={nondet e=Set(Capture,Hide,Restore,Close,Reuse,OldCapture,FailedCapture,Prune,ClipDecoration).oneOf();fire(e)}
 val nativePreserved=s.nativeRect==s.savedRect
 val frameRequired=s.visual implies (s.whole and s.header and s.cacheId==s.id and s.cachePid==s.pid)
 val noDeadImage=not(s.live) implies not(s.visual)
 val allProps=nativePreserved and frameRequired and noDeadImage
}
