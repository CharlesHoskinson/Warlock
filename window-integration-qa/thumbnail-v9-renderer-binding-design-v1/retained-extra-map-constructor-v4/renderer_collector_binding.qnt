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
 type Terminal={renderer:Renderer,transportClosed:bool,launchClosed:bool,returncode:Scalar,jobs:Set[int],children:Set[int],keeperClosed:bool,keeperCode:Scalar}
 type State={package:Package,linked:bool,liveConfirmed:bool,captured:Renderer,terminalCaptured:Terminal,terminalRaw:bool,terminalConfirmed:bool,refused:bool,passed:int,featureFailure:bool,featureAccepted:bool}
 type Event=Link({package:Package,observation:Live})|ConfirmLive({package:Package,observation:Live})|RawTerminal({package:Package,observation:Terminal})|ConfirmTerminal({package:Package,observation:Terminal})|Gates({count:int,failed:bool})|AcceptFeature
 pure val moduleKeys=1.to(19)
 pure val roles=1.to(5)
 pure def callbackOwner(role:int):int=if(role<=3)7 else 0
 pure val goodCallbacks=roles.mapBy(role=>{function:role,owner:callbackOwner(role),source:V24})
 pure val required=Set(FrozenV24,FrozenV7,FailedV7,ComponentV8)
 pure val goodPackage={modules:moduleKeys.mapBy(_=>V24),closure:required,callbacks:goodCallbacks}
 pure val metadata={pid:Integer(101),start:Integer(203),device:Integer(1),inode:Integer(307),sha:Text("producer"),session:Text("session")}
 pure val renderer={binding:5,transport:7,launch:11,process:13,keeper:17,job:19,actor:Integer(1),producer:"producer",owner:metadata}
 pure val live={renderer:renderer,transportProcess:13,launchProcess:13,child:13,wrapperPID:Integer(101),processClass:CanonicalPopen,registryOwner:metadata,launchOwner:metadata,released:true,ownJobs:Set(19),alive:true}
 pure val terminal={renderer:renderer,transportClosed:true,launchClosed:true,returncode:Integer(0),jobs:Set(),children:Set(),keeperClosed:true,keeperCode:Integer(0)}
 pure def validPackage(p:Package):bool=p.modules.keys()==moduleKeys and moduleKeys.forall(key=>p.modules.get(key)==V24) and p.closure==required and p.callbacks==goodCallbacks
 pure def validLive(o:Live):bool=o.renderer==renderer and o.transportProcess==13 and o.launchProcess==13 and o.child==13 and o.wrapperPID==metadata.pid and o.processClass==CanonicalPopen and o.registryOwner==metadata and o.launchOwner==metadata and o.released and o.ownJobs==Set(19) and o.alive
 pure def validTerminal(o:Terminal):bool=o.renderer==renderer and o.transportClosed and o.launchClosed and o.returncode==Integer(0) and o.jobs==Set() and o.children==Set() and o.keeperClosed and o.keeperCode==Integer(0)
 var s:State
 action init=s'={package:goodPackage,linked:false,liveConfirmed:false,captured:renderer,terminalCaptured:terminal,terminalRaw:false,terminalConfirmed:false,refused:false,passed:0,featureFailure:false,featureAccepted:false}
 pure def transition(current:State,e:Event):State=if(current.refused)current else match e {
 |Link(pair)=>{val p=pair.package;val o=pair.observation;if(not(current.linked) and validPackage(p) and validLive(o)){...current,package:p,linked:true,captured:o.renderer}else {...current,refused:true,featureAccepted:false}}
 |ConfirmLive(pair)=>{val p=pair.package;val o=pair.observation;if(current.linked and validPackage(p) and p==current.package and validLive(o) and o.renderer==current.captured){...current,liveConfirmed:true}else {...current,refused:true,featureAccepted:false}}
 |RawTerminal(pair)=>{val p=pair.package;val o=pair.observation;if(current.liveConfirmed and validPackage(p) and p==current.package and validTerminal(o) and o.renderer==current.captured){...current,terminalRaw:true,terminalCaptured:o,terminalConfirmed:false}else {...current,refused:true,featureAccepted:false}}
 |ConfirmTerminal(pair)=>{val p=pair.package;val o=pair.observation;if(current.terminalRaw and validPackage(p) and p==current.package and validTerminal(o) and o==current.terminalCaptured and o.renderer==current.captured){...current,terminalConfirmed:true}else {...current,refused:true,featureAccepted:false}}
 |Gates(pair)=>{val count=pair.count;val failed=pair.failed;{...current,passed:count,featureFailure:current.featureFailure or failed,featureAccepted:false}}
 |AcceptFeature=>{...current,featureAccepted:current.liveConfirmed and current.terminalConfirmed and current.passed==38 and not(current.featureFailure)}
 }
 action fire(e:Event):bool=s'=transition(s,e)
 action acceptFeature=s'=if(s.refused)s else {...s,featureAccepted:s.liveConfirmed and s.terminalConfirmed and s.passed==38 and not(s.featureFailure)}
 val allProps=(s.featureAccepted implies s.linked and s.liveConfirmed and s.terminalRaw and s.terminalConfirmed and s.passed==38 and not(s.featureFailure) and not(s.refused) and validPackage(s.package) and validTerminal(s.terminalCaptured)) and (s.terminalConfirmed implies s.terminalCaptured.renderer==s.captured)
 action step={
  nondet m=moduleKeys.oneOf();nondet v=Set(V23,V24,Foreign).oneOf();nondet owner=Set(0,7,29).oneOf();nondet role=roles.oneOf();nondet fn=roles.oneOf()
  val p={...goodPackage,modules:goodPackage.modules.set(m,v),callbacks:goodCallbacks.set(role,{function:fn,owner:owner,source:v})}
  nondet r=Set(renderer,{...renderer,transport:29},{...renderer,actor:Boolean(true)}).oneOf()
  nondet o=Set(live,{...live,renderer:r},{...live,registryOwner:{...metadata,device:Boolean(true)}},{...live,processClass:FakeProcess}).oneOf()
  nondet t=Set(terminal,{...terminal,renderer:r},{...terminal,returncode:Decimal(0)},{...terminal,jobs:Set(19)}).oneOf()
  nondet count=Set(0,11,38).oneOf();nondet failed=Set(true,false).oneOf()
  nondet e=Set(Link({package:p,observation:o}),ConfirmLive({package:p,observation:o}),RawTerminal({package:p,observation:t}),ConfirmTerminal({package:p,observation:t}),Gates({count:count,failed:failed}),AcceptFeature).oneOf();fire(e)
 }
}
