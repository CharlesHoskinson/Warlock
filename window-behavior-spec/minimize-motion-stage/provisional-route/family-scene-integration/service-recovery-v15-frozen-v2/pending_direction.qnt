module pending_direction {
 type Command=Minimize|Restore|Toggle|Activate
 type Expr=Empty|Constant(bool)|Anchor({activation:bool,flipped:bool})
 type Reply={receipt:int,live:bool,minimized:bool,active:bool}
 type Event=Request(Command)|Observe(Reply)|Fail(int)|Held|Close
 type State={receipt:int,expression:Expr,commands:List[Command],validated:int,target:bool,hasHeld:bool,visual:bool,effect:bool,effectReceipt:int,closed:bool}
 var s:State
 pure def inverse(e:Expr):Expr=match e { | Empty=>Empty | Constant(m)=>Constant(not(m)) | Anchor(a)=>Anchor({...a,flipped:not(a.flipped)}) }
 pure def compose(e:Expr,c:Command):Expr=match c {
  | Minimize=>Constant(true) | Restore=>Constant(false)
  | Toggle=>if(e==Empty) Anchor({activation:false,flipped:false}) else inverse(e)
  | Activate=>if(e==Empty) Anchor({activation:true,flipped:false}) else inverse(e)
 }
 pure def resolve(e:Expr,p:Reply):bool=match e {
  | Empty=>p.minimized | Constant(m)=>m
  | Anchor(a)=>{val first=if(a.activation) not(p.minimized) and p.active else not(p.minimized);if(a.flipped) not(first) else first}
 }
 // Independent command-list semantics at the observed native state.
 pure def reference(cs:List[Command],p:Reply):bool=cs.foldl({known:false,direction:p.minimized},(a,c)=>match c {
  | Minimize=>{known:true,direction:true} | Restore=>{known:true,direction:false}
  | Toggle=>{known:true,direction:if(a.known) not(a.direction) else not(p.minimized)}
  | Activate=>{known:true,direction:if(a.known) not(a.direction) else not(p.minimized) and p.active}
 }).direction
 action init=s'={receipt:0,expression:Empty,commands:List(),validated:0,target:false,hasHeld:false,visual:false,effect:false,effectReceipt:0,closed:false}
 action fire(e:Event):bool={val b={...s,effect:false};s'=match e {
  | Request(c)=>if(not(s.closed)){...b,receipt:s.receipt+1,expression:compose(s.expression,c),commands:s.commands.append(c),validated:0} else b
  | Observe(p)=>if(not(s.closed) and p.live and p.receipt==s.receipt and s.receipt>0){val target=resolve(s.expression,p);{...b,validated:p.receipt,target:target,visual:s.hasHeld or target!=p.minimized,effect:true,effectReceipt:p.receipt}} else b
  | Fail(r)=>if(r==s.receipt){...b,expression:Empty,commands:List(),validated:0,visual:false,hasHeld:false} else b
  | Held=>{...b,hasHeld:true}
  | Close=>{...b,closed:true,validated:0,hasHeld:false,visual:false}
 }}
 val nativeAuthority=s.effect implies (not(s.closed) and s.effectReceipt==s.receipt and s.validated==s.receipt)
 val algebraCorrect=Set(false,true).forall(m=>Set(false,true).forall(a=>resolve(s.expression,{receipt:s.receipt,live:true,minimized:m,active:a})==reference(s.commands,{receipt:s.receipt,live:true,minimized:m,active:a})))
 val allProps=nativeAuthority and algebraCorrect
 action step={nondet e=Set(Request(Minimize),Request(Restore),Request(Toggle),Request(Activate),Observe({receipt:s.receipt,live:true,minimized:false,active:true}),Observe({receipt:s.receipt,live:true,minimized:true,active:false}),Observe({receipt:s.receipt-1,live:true,minimized:false,active:true}),Observe({receipt:s.receipt,live:false,minimized:false,active:true}),Fail(s.receipt),Fail(s.receipt-1),Held,Close).oneOf();fire(e)}
}
