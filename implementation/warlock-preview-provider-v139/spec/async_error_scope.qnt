module async_error_scope {
 type Scope={view:int,epoch:int,navigation:int,projection:int}
 type State={scope:Scope,finished:bool,failed:bool,stale:bool,artifact:bool,policy:int,nativeOwned:bool}
 var s:State
 pure val currentScope={view:2,epoch:2,navigation:2,projection:2}
 pure val oldScope={view:1,epoch:1,navigation:1,projection:1}
 pure def complete(st:State,scope:Scope,success:bool,guardFirst:bool):State={
  if(st.finished)st
  else {
   val consumed={...st,finished:true};
   if(not(success) and not(guardFirst)){...consumed,failed:true}
   else if(scope!=st.scope){...consumed,stale:true}
   else if(not(success)){...consumed,failed:true}
   else {...consumed,artifact:true}
  }
 }
 action init=s'={scope:currentScope,finished:false,failed:false,stale:false,artifact:false,policy:1,nativeOwned:true}
 action finish(scope:Scope,success:bool,guardFirst:bool):bool=s'=complete(s,scope,success,guardFirst)
 action step={nondet scope=Set(currentScope,oldScope,{...currentScope,view:1},{...currentScope,epoch:1},{...currentScope,navigation:1},{...currentScope,projection:1}).oneOf();nondet ok=Set(true,false).oneOf();finish(scope,ok,true)}
 val safety=all{s.policy==1,s.nativeOwned,not(s.failed and s.stale),not(s.artifact and s.stale),s.artifact implies s.finished}
}
