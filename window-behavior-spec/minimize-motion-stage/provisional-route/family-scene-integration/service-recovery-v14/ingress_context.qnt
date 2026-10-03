module ingress_context {
 type Reply={receipt:int,consistent:bool}
 type Event=Reserve|Context(Reply)|Fail(int)|Validate(int)|Commit(int)|Close
 type State={receipt:int,activated:int,validated:int,failed:int,closed:bool,effect:bool,effectReceipt:int,retarget:bool,retargetReceipt:int}
 var s:State
 action init=s'={receipt:1,activated:1,validated:1,failed:0,closed:false,effect:false,effectReceipt:0,retarget:false,retargetReceipt:0}
 action fire(e:Event):bool={
  val b={...s,effect:false,retarget:false}
  s'=match e {
   | Reserve=>if(not(s.closed)){...b,receipt:s.receipt+1} else b
   | Context(p)=>if(not(s.closed) and p.receipt==s.receipt and p.consistent and s.failed!=p.receipt){...b,activated:p.receipt,retarget:true,retargetReceipt:p.receipt} else b
   | Fail(r)=>if(r==s.receipt){...b,failed:r,activated:0,validated:0} else b
   | Validate(r)=>if(not(s.closed) and r==s.receipt and s.activated==r and s.failed!=r){...b,validated:r} else b
   | Commit(r)=>if(not(s.closed) and r==s.receipt and s.activated==r and s.validated==r and s.failed!=r){...b,effect:true,effectReceipt:r} else b
   | Close=>{...b,closed:true,activated:0,validated:0}
  }
 }
 val currentNativeAuthority=s.effect implies (s.effectReceipt==s.receipt and s.activated==s.receipt and s.validated==s.receipt and s.failed!=s.receipt and not(s.closed))
 val latestContextOnly=s.retarget implies (s.retargetReceipt==s.receipt and s.failed!=s.receipt and not(s.closed))
 val allProps=currentNativeAuthority and latestContextOnly
 action step={nondet e=Set(Reserve,Context({receipt:s.receipt,consistent:true}),Context({receipt:s.receipt-1,consistent:true}),Context({receipt:s.receipt,consistent:false}),Validate(s.receipt),Validate(s.receipt-1),Commit(s.receipt),Commit(s.receipt-1),Fail(s.receipt),Fail(s.receipt-1),Close).oneOf();fire(e)}
}
