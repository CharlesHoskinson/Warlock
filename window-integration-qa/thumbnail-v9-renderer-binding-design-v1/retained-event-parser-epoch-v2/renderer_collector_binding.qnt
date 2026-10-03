module renderer_collector_binding {
 type Version=V23|V24|Foreign
 type Component=FrozenV24|FrozenV7|FailedV7|ComponentV8
 type Scalar=Integer(int)|Boolean(bool)|Decimal(int)|Text(str)|Null
 type Callback={function:int,owner:int,source:Version}
 type Package={modules:int->Version,closure:Set[Component],callbacks:int->Callback}
 type Metadata={pid:Scalar,start:Scalar,device:Scalar,inode:Scalar,sha:Scalar,session:Scalar}
 type Renderer={binding:int,transport:int,launch:int,process:int,keeper:int,job:int,actor:Scalar,producer:str,owner:Metadata}
 type ProcessClass=CanonicalPopen|PopenSubclass|FakeProcess
 type Live={renderer:Renderer,transportProcess:int,launchProcess:int,child:int,wrapperPID:Scalar,processClass:ProcessClass,registryOwner:Metadata,launchOwner:Metadata,released:bool,ownJobs:Set[int],alive:bool}
 type Terminal={renderer:Renderer,transportClosed:bool,launchClosed:bool,returncode:Scalar,jobs:Set[int],children:Set[int]}
 type State={package:Package,linked:bool,liveConfirmed:bool,captured:Renderer,terminalCaptured:Terminal,terminalRaw:bool,terminalConfirmed:bool,refused:bool,passed:int,featureFailure:bool,featureAccepted:bool}
 type Event=Link(Package,Live)|ConfirmLive(Package,Live)|RawTerminal(Package,Terminal)|ConfirmTerminal(Package,Terminal)|Gates(int,bool)|AcceptFeature
 pure val moduleKeys=1.to(19)
 pure val roles=1.to(5)
 pure def callbackOwner(role:int):int=if(role<=3)7 else 0
 pure val goodCallbacks=roles.mapBy(role=>{function:role,owner:callbackOwner(role),source:V24})
 pure val required=Set(FrozenV24,FrozenV7,FailedV7,ComponentV8)
 pure val goodPackage={modules:moduleKeys.mapBy(_=>V24),closure:required,callbacks:goodCallbacks}
 pure val metadata={pid:Integer(101),start:Integer(203),device:Integer(1),inode:Integer(307),sha:Text("producer"),session:Text("session")}
 pure val renderer={binding:5,transport:7,launch:11,process:13,keeper:17,job:19,actor:Integer(1),producer:"producer",owner:metadata}
 pure val live={renderer:renderer,transportProcess:13,launchProcess:13,child:13,wrapperPID:Integer(101),processClass:CanonicalPopen,registryOwner:metadata,launchOwner:metadata,released:true,ownJobs:Set(19),alive:true}
 pure val terminal={renderer:renderer,transportClosed:true,launchClosed:true,returncode:Integer(0),jobs:Set(),children:Set()}
 pure def validPackage(p:Package):bool=p.modules.keys()==moduleKeys and moduleKeys.forall(key=>p.modules.get(key)==V24) and p.closure==required and p.callbacks==goodCallbacks
 pure def validLive(o:Live):bool=o.renderer==renderer and o.transportProcess==13 and o.launchProcess==13 and o.child==13 and o.wrapperPID==metadata.pid and o.processClass==CanonicalPopen and o.registryOwner==metadata and o.launchOwner==metadata and o.released and o.ownJobs==Set(19) and o.alive
 pure def validTerminal(o:Terminal):bool=o.renderer==renderer and o.transportClosed and o.launchClosed and o.returncode==Integer(0) and not(o.jobs.contains(19)) and not(o.children.contains(19))
 var s:State
 action init=s'={package:goodPackage,linked:false,liveConfirmed:false,captured:renderer,terminalCaptured:terminal,terminalRaw:false,terminalConfirmed:false,refused:false,passed:0,featureFailure:false,featureAccepted:false}
 pure def refuse(p:State):State={...p,refused:true,featureAccepted:false}
 action fire(e:Event):bool=s'=if(s.refused)s else match e {
 |Link(p,o)=>if(not(s.linked) and validPackage(p) and validLive(o)){...s,package:p,linked:true,captured:o.renderer}else refuse(s)
 |ConfirmLive(p,o)=>if(s.linked and validPackage(p) and p==s.package and validLive(o) and o.renderer==s.captured){...s,liveConfirmed:true}else refuse(s)
 |RawTerminal(p,o)=>if(s.liveConfirmed and validPackage(p) and p==s.package and validTerminal(o) and o.renderer==s.captured){...s,terminalRaw:true,terminalCaptured:o,terminalConfirmed:false}else refuse(s)
 |ConfirmTerminal(p,o)=>if(s.terminalRaw and validPackage(p) and p==s.package and validTerminal(o) and o==s.terminalCaptured and o.renderer==s.captured){...s,terminalConfirmed:true}else refuse(s)
 |Gates(count,failed)=>{...s,passed:count,featureFailure:s.featureFailure or failed,featureAccepted:false}
 |AcceptFeature=>{...s,featureAccepted:s.liveConfirmed and s.terminalConfirmed and s.passed==38 and not(s.featureFailure)}
 }
 val allProps=(s.featureAccepted implies s.linked and s.liveConfirmed and s.terminalRaw and s.terminalConfirmed and s.passed==38 and not(s.featureFailure) and not(s.refused) and validPackage(s.package) and validTerminal(s.terminalCaptured)) and (s.terminalConfirmed implies s.terminalCaptured.renderer==s.captured)
 action step={
  nondet m=moduleKeys.oneOf();nondet v=Set(V23,V24,Foreign).oneOf();nondet owner=Set(0,7,29).oneOf();nondet role=roles.oneOf();nondet fn=roles.oneOf()
  val p={...goodPackage,modules:goodPackage.modules.set(m,v),callbacks:goodCallbacks.set(role,{function:fn,owner:owner,source:v})}
  nondet r=Set(renderer,{...renderer,transport:29},{...renderer,actor:Boolean(true)}).oneOf()
  nondet o=Set(live,{...live,renderer:r},{...live,registryOwner:{...metadata,device:Boolean(true)}},{...live,processClass:FakeProcess}).oneOf()
  nondet t=Set(terminal,{...terminal,renderer:r},{...terminal,returncode:Decimal(0)},{...terminal,jobs:Set(19)}).oneOf()
  nondet count=Set(0,11,38).oneOf();nondet failed=Set(true,false).oneOf()
  nondet e=Set(Link(p,o),ConfirmLive(p,o),RawTerminal(p,t),ConfirmTerminal(p,t),Gates(count,failed),AcceptFeature).oneOf();fire(e)
 }
}
