module ipc_guard {
 type Event=Connect(bool)|SendVersion|Receive(bool)|ServerEOF|Authorize|Drop
 type State={peer:bool,sent:bool,jsonValid:bool,eof:bool,closed:bool,authority:bool}
 var s:State
 action init=s'={peer:false,sent:false,jsonValid:false,eof:false,closed:false,authority:false}
 action fire(e:Event):bool={s'=match e {
  | Connect(v)=>{peer:v,sent:false,jsonValid:false,eof:false,closed:not(v),authority:false}
  | SendVersion=>if(s.peer and not(s.closed)){...s,sent:true,jsonValid:false,eof:false,authority:false}else s
  | Receive(v)=>if(s.peer and s.sent and not(s.closed)){...s,jsonValid:v,authority:false}else s
  | ServerEOF=>if(s.sent and not(s.closed)){...s,eof:true}else s
  | Authorize=>if(s.peer and s.sent and s.jsonValid and s.eof and not(s.closed)){...s,authority:true}else s
  | Drop=>{...s,closed:true,authority:false}
 }}
 val fullReadonlyExchange=s.authority implies (s.peer and s.sent and s.jsonValid and s.eof and not(s.closed))
 val allProps=fullReadonlyExchange
 action step={nondet e=Set(Connect(true),Connect(false),SendVersion,Receive(true),Receive(false),ServerEOF,Authorize,Drop).oneOf();fire(e)}
}
