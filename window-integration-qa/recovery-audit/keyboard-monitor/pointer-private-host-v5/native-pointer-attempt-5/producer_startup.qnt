module producer_startup {
 type Env={privatePath:bool,ownedDirs:bool,explicit:bool,scope:bool,core:bool,ownSocket:bool,samePeer:bool,liveStart:bool,noFallback:bool}
 var env:Env
 var running:bool
 var ready:bool
 var sent:bool
 val good={privatePath:true,ownedDirs:true,explicit:true,scope:true,core:true,ownSocket:true,samePeer:true,liveStart:true,noFallback:true}
 pure def authorized(e:Env):bool=all{e.privatePath,e.ownedDirs,e.explicit,e.scope,e.core,e.ownSocket,e.samePeer,e.liveStart,e.noFallback}
 action init=all{env'=good,running'=false,ready'=false,sent'=false}
 action start(e:Env):bool=all{env'=e,running'=authorized(e),ready'=false,sent'=false}
 action sync(ok:bool):bool=all{env'=env,running'=running,ready'=(running and ok),sent'=false}
 action input=all{env'=env,running'=running,ready'=ready,sent'=(running and ready)}
 action stop=all{env'=env,running'=false,ready'=false,sent'=false}
 val invariant=all{ready implies running,running implies authorized(env),sent implies all{running,ready,authorized(env)}}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet d=Set(true,false).oneOf();nondet e=Set(true,false).oneOf();nondet f=Set(true,false).oneOf();nondet g=Set(true,false).oneOf();nondet h=Set(true,false).oneOf();nondet i=Set(true,false).oneOf();any{start({privatePath:a,ownedDirs:b,explicit:c,scope:d,core:e,ownSocket:f,samePeer:g,liveStart:h,noFallback:i}),sync(a),input,stop}}
}
