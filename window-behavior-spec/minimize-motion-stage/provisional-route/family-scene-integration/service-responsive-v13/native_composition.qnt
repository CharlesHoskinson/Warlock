module native_composition {
 type Event=Select(bool)|Proof(bool)|Seal|ReplacePath|EditSource|Launch|Send|Reply|Disconnect|RetryFallback
 type State={session:bool,proof:bool,sealed:bool,launched:bool,launchObserved:bool,sent:bool,replied:bool,unknown:bool,effect:bool}
 var s:State
 action init=s'={session:false,proof:false,sealed:false,launched:false,launchObserved:false,sent:false,replied:false,unknown:false,effect:false}
 action fire(e:Event):bool={
  val b={...s,effect:false,launchObserved:false}
  s'=match e{
   | Select(v)=>{...b,session:v}
   | Proof(v)=>{...b,proof:v}
   | Seal=>if(s.proof){...b,sealed:true}else b
   | ReplacePath=>b
   | EditSource=>b
   | Launch=>if(s.session and s.proof and s.sealed){...b,launched:true,launchObserved:true}else b
   | Send=>if(s.launched and s.session and not(s.sent)){...b,sent:true}else b
   | Reply=>if(s.sent){...b,replied:true}else b
   | Disconnect=>if(s.sent and not(s.replied)){...b,unknown:true}else b
   | RetryFallback=>b
  }
 }
 val onlyExplicitProvenLaunch=s.launchObserved implies (s.session and s.proof and s.sealed)
 val unknownAcceptanceNeverFallsBack=not(s.effect)
 val allProps=onlyExplicitProvenLaunch and unknownAcceptanceNeverFallsBack
 action step={nondet e=Set(Select(true),Select(false),Proof(true),Proof(false),Seal,ReplacePath,EditSource,Launch,Send,Reply,Disconnect,RetryFallback).oneOf();fire(e)}
}
