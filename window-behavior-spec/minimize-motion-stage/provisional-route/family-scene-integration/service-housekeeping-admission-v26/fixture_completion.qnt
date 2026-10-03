module fixture_completion {
 type Event=Reserve|Context(int)|NativeReturn(int)|Cleanup(int)|Observe
 type State={receipt:int,pending:bool,current:bool,nativeReturns:int,historyReceipt:int,cleanupAck:bool,observed:bool}
 var s:State
 action init=s'={receipt:1,pending:true,current:true,nativeReturns:0,historyReceipt:0,cleanupAck:false,observed:false}
 pure def complete(v:State):bool=not(v.pending) and not(v.current) and v.historyReceipt==v.receipt and v.cleanupAck and v.nativeReturns==3
 action fire(e:Event):bool=s'=match e {
 | Reserve=>{receipt:s.receipt+1,pending:true,current:true,nativeReturns:0,historyReceipt:0,cleanupAck:false,observed:false}
 | Context(r)=>if(r==s.receipt){...s,pending:false} else s
 | NativeReturn(r)=>if(r==s.receipt and not(s.pending) and s.current and s.nativeReturns<3){...s,nativeReturns:s.nativeReturns+1} else s
 | Cleanup(r)=>if(r==s.receipt and not(s.pending) and s.nativeReturns==3){...s,current:false,historyReceipt:r,cleanupAck:true} else s
 | Observe=>{...s,observed:complete(s)}
 }
 val allProps=s.nativeReturns>=0 and s.nativeReturns<=3 and (s.observed implies complete(s)) and (s.cleanupAck implies s.historyReceipt==s.receipt and s.nativeReturns==3 and not(s.current))
 action step={nondet e=Set(Reserve,Context(s.receipt),Context(s.receipt-1),NativeReturn(s.receipt),NativeReturn(s.receipt-1),Cleanup(s.receipt),Cleanup(s.receipt-1),Observe).oneOf();fire(e)}
}
