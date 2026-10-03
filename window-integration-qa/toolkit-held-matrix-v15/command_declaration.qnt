module command_declaration {
 type State={declaration:int,requestDeclaration:int,launchedArgv:int,requested:bool,started:bool,pid:int,normal:bool,source:bool,failed:bool,accepted:bool}
 type Event=Submit|Rebind|Start|NormalExit|BadExit|SourceChanged|Drain|OldCommandComparison
 var s:State
 pure val initial={declaration:1,requestDeclaration:0,launchedArgv:0,requested:false,started:false,pid:0,normal:false,source:true,failed:false,accepted:false}
 action init=s'=initial
 pure def advance(x:State,e:Event):State=(if(x.failed)x else match e {
 |Submit=>if(x.requested){...x,failed:true,accepted:false}else {...x,requested:true,requestDeclaration:x.declaration,launchedArgv:x.declaration}
 |Rebind=>{...x,declaration:2}
 |Start=>if(x.requested and not(x.started)){...x,started:true,pid:42}else {...x,failed:true,accepted:false}
 |NormalExit=>if(x.started and x.pid==42){...x,pid:0,normal:true}else {...x,failed:true,accepted:false}
 |BadExit=>{...x,failed:true,accepted:false}
 |SourceChanged=>{...x,source:false,failed:true,accepted:false}
 |Drain=>if(x.requested and x.started and x.pid==0 and x.normal and x.source){...x,accepted:true}else x
 |OldCommandComparison=>if(x.started and x.declaration!=x.requestDeclaration){...x,failed:true,accepted:false}else x
 })
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=(s.requested implies s.launchedArgv==s.requestDeclaration) and (s.accepted implies s.requested and s.started and s.pid==0 and s.normal and s.source and not(s.failed))
 action step={nondet e=Set(Submit,Rebind,Start,NormalExit,BadExit,SourceChanged,Drain).oneOf();fire(e)}
}
