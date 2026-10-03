module span_source_binding {
 type Event=Select(bool)|Install(bool)|Call(bool)|ChangeCode|ChangeSource|Stop|Project(bool,bool,bool)|GrantEffect
 type State={selected:bool,installed:bool,stopped:bool,sourceStable:bool,codeStable:bool,fault:bool,complete:bool,nativeAuthority:bool,calls:int,deadline:int}
 var s:State
 action init=s'={selected:false,installed:false,stopped:false,sourceStable:true,codeStable:true,fault:false,complete:false,nativeAuthority:false,calls:0,deadline:2}
 action fire(e:Event):bool={s'=match e {
 | Select(ok)=>if(not(s.selected) and not(s.installed) and not(s.stopped) and ok){...s,selected:true}else{...s,fault:true,complete:false}
 | Install(clear)=>if(s.selected and not(s.installed) and not(s.stopped) and clear and not(s.fault)){...s,installed:true}else{...s,fault:true,complete:false}
 | Call(exact)=>if(s.installed and not(s.stopped)){if(exact){...s,calls:s.calls+1}else{...s,fault:true,complete:false}}else{...s,fault:true,complete:false}
 | ChangeCode=>{...s,codeStable:false,complete:false}
 | ChangeSource=>{...s,sourceStable:false,complete:false}
 | Stop=>{...s,stopped:true,installed:false,complete:false}
 | Project(rawComplete,currentExact,persisted)=>if(s.stopped and s.selected and rawComplete and currentExact and persisted and s.sourceStable and s.codeStable and not(s.fault)){...s,complete:true}else{...s,fault:true,complete:false}
 | GrantEffect=>s
 }}
 val allProps=not(s.nativeAuthority) and s.deadline==2 and (s.complete implies s.selected and s.stopped and not(s.installed) and s.sourceStable and s.codeStable and not(s.fault))
 action step={nondet e=Set(Select(true),Select(false),Install(true),Install(false),Call(true),Call(false),ChangeCode,ChangeSource,Stop,Project(true,true,true),Project(false,true,true),Project(true,false,true),Project(true,true,false),GrantEffect).oneOf();fire(e)}
}
