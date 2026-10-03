module batch_preview_lock {
 type Event=Prepare|Cleanup|HelperPublish|ReleaseCapture|ReleaseReceipt
 type State={capture:bool,receipt:bool,cleanupWaiting:bool,helperWaiting:bool,cleanupDone:bool}
 var s:State
 action init=s'={capture:false,receipt:false,cleanupWaiting:false,helperWaiting:false,cleanupDone:false}
 action fire(e:Event):bool={s'=match e {
 | Prepare=>{...s,capture:true}
 | Cleanup=>if(not(s.receipt)){...s,receipt:true,cleanupDone:true,cleanupWaiting:false} else s
 | HelperPublish=>if(s.capture){...s,helperWaiting:s.receipt} else s
 | ReleaseCapture=>{...s,capture:false,helperWaiting:false}
 | ReleaseReceipt=>{...s,receipt:false,helperWaiting:false}
 }}
 val allProps=not(s.cleanupWaiting) and not(s.cleanupWaiting and s.helperWaiting)
 action step={nondet e=Set(Prepare,Cleanup,HelperPublish,ReleaseCapture,ReleaseReceipt).oneOf();fire(e)}
}
