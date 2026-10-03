module readback_attribution {
 type Event=Draw(int)|Read(int)|Swap(int)|Presented(int)|Error|Cancel
 type State={drawn:int,read:int,swapped:int,presented:int,closed:bool,readObserved:bool,nativeAuthority:bool}
 var s:State
 action init=s'={drawn:0,read:0,swapped:0,presented:0,closed:false,readObserved:false,nativeAuthority:false}
 action fire(e:Event):bool={
  val b={...s,readObserved:false}
  s'=match e{
   | Draw(n)=>if(not(s.closed) and n>s.drawn){...b,drawn:n} else b
   | Read(n)=>if(not(s.closed) and n==s.drawn and n>s.read and n>s.swapped){...b,read:n,readObserved:true} else b
   | Swap(n)=>if(not(s.closed) and n==s.drawn){...b,swapped:n} else b
   | Presented(n)=>if(not(s.closed) and n==s.swapped){...b,presented:n} else b
   | Error=>{...b,closed:true}
   | Cancel=>{...b,closed:true}
  }
 }
 val readBoundToDraw=s.readObserved implies (s.read==s.drawn and s.read>s.swapped and not(s.closed))
 val diagnosticCannotPromote=not(s.nativeAuthority)
 val allProps=readBoundToDraw and diagnosticCannotPromote
 action step={nondet e=Set(Draw(s.drawn+1),Read(s.drawn),Read(s.drawn-1),Swap(s.drawn),Presented(s.drawn),Error,Cancel).oneOf();fire(e)}
}
