module receipt_visual {
 type Reply={receipt:int,sameContext:bool}
 type Event=Reserve(bool)|Context(Reply)|Validate(int)|Commit(int)|Fail(int)|Close
 type State={receipt:int,visual:int,context:int,validated:int,failed:int,closed:bool,effect:bool,effectReceipt:int,queued:bool}
 var s:State
 action init=s'={receipt:1,visual:1,context:1,validated:1,failed:0,closed:false,effect:false,effectReceipt:0,queued:false}
 action fire(e:Event):bool={
  val b={...s,effect:false,queued:false}
  s'=match e {
   | Reserve(retained)=>if(not(s.closed)){...b,receipt:s.receipt+1,context:0,validated:0,visual:if(retained){s.receipt+1}else{0},queued:retained} else b
   | Context(r)=>if(not(s.closed) and r.receipt==s.receipt and s.failed!=r.receipt){...b,context:if(r.sameContext){r.receipt}else{0},visual:if(r.sameContext){s.visual}else{0},failed:if(r.sameContext){s.failed}else{r.receipt}} else b
   | Validate(r)=>if(not(s.closed) and r==s.receipt and s.context==r and s.failed!=r){...b,validated:r} else b
   | Commit(r)=>if(not(s.closed) and r==s.receipt and s.context==r and s.validated==r and s.failed!=r){...b,effect:true,effectReceipt:r} else b
   | Fail(r)=>if(r==s.receipt){...b,failed:r,visual:0,context:0,validated:0} else b
   | Close=>{...b,closed:true,visual:0,context:0,validated:0}
  }
 }
 val provisionalHasNoNativeAuthority=s.effect implies (s.effectReceipt==s.receipt and s.context==s.receipt and s.validated==s.receipt and s.failed!=s.receipt and not(s.closed))
 val latestVisualOnly=(s.visual>0 implies (s.visual==s.receipt and s.failed!=s.receipt and not(s.closed)))
 val reserveQueuesBeforeContext=s.queued implies (s.visual==s.receipt and s.context==0 and s.validated==0)
 val allProps=provisionalHasNoNativeAuthority and latestVisualOnly and reserveQueuesBeforeContext
 action step={nondet e=Set(Reserve(true),Reserve(false),Context({receipt:s.receipt,sameContext:true}),Context({receipt:s.receipt,sameContext:false}),Context({receipt:s.receipt-1,sameContext:true}),Validate(s.receipt),Validate(s.receipt-1),Commit(s.receipt),Commit(s.receipt-1),Fail(s.receipt),Fail(s.receipt-1),Close).oneOf();fire(e)}
}
