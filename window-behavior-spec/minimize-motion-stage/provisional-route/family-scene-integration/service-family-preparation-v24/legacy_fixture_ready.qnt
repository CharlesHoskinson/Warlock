module legacy_fixture_ready {
 type Seen={gated:bool,live:bool,lifetime:int,env:int,argv:int,exe:int,source:int,fd:int,complete:bool,error:bool,expired:bool}
 type Event=See(Seen)|Verify(bool)|Release
 type State={ready:bool,fault:bool,verified:bool,released:bool}
 var s:State
 action init=s'={ready:false,fault:false,verified:false,released:false}
 pure def matches(p:Seen):bool=p.gated and p.live and p.lifetime==1 and p.env==1 and p.argv==1 and p.exe==1 and p.source==1 and p.fd==1 and not(p.error) and not(p.expired)
 action fire(e:Event):bool=s'=match e {
 | See(p)=>if(s.fault or s.released)s else if(not(p.gated) and not(p.error) and not(p.expired) and p.live and p.lifetime==1){...s,ready:false,verified:false} else if(p.error or p.expired or not(p.live) or p.lifetime!=1 or p.exe!=1 or p.source!=1 or p.fd!=1 or p.complete and (p.env!=1 or p.argv!=1)){...s,ready:false,fault:true,verified:false} else {...s,ready:p.complete and matches(p),verified:false}
 | Verify(valid)=>if(s.fault or s.released)s else if(s.ready and valid){...s,verified:true} else {...s,ready:false,fault:true,verified:false}
 | Release=>if(s.ready and s.verified and not(s.fault)){...s,released:true} else s
 }
 val allProps=s.released implies (s.ready and s.verified and not(s.fault))
 action step={nondet token=Set(0,1,2).oneOf();nondet complete=Set(true,false).oneOf();nondet error=Set(true,false).oneOf();nondet expired=Set(true,false).oneOf();nondet e=Set(See({gated:true,live:true,lifetime:1,env:token,argv:1,exe:1,source:1,fd:1,complete:complete,error:error,expired:expired}),See({gated:true,live:true,lifetime:token,env:1,argv:1,exe:1,source:1,fd:1,complete:true,error:false,expired:false}),Verify(true),Verify(false),Release).oneOf();fire(e)}
}
