/** Minimized taskbar ownership: home desktop, named output, and identity. */
module monitor_owner {
  type Event = Minimize | Restore | DeleteHome | MoveHome(int) | RemoveOutput | AddOutput(str) | ReuseAddress
  var s: {minimized:bool, raw:int, home:int, desktop:int, homeExists:bool,
          savedHome:int, savedIdentity:int, identity:int, savedMonitor:str,
          present:bool, outputName:str}
  def name(id:int):str = if (id==0) "physical" else s.outputName
  val metadataValid = s.savedIdentity==s.identity and s.savedHome==s.desktop
  val owner = if (not(s.minimized) or not(metadataValid)) s.raw
    else if (s.homeExists) s.home
    else if (s.savedMonitor=="physical") 0
    else if (s.present and s.savedMonitor==s.outputName) 1 else 0
  action init = s'={minimized:false,raw:1,home:1,desktop:1,homeExists:true,
                   savedHome:1,savedIdentity:1,identity:1,savedMonitor:"virtual",
                   present:true,outputName:"virtual"}
  action fire(e:Event):bool = s'=match e {
    | Minimize => if (s.minimized) s else {...s,minimized:true,raw:0,home:s.raw,
        savedHome:s.desktop,savedIdentity:s.identity,savedMonitor:name(s.raw)}
    | Restore => {...s,minimized:false,raw:owner,home:owner,homeExists:true}
    | DeleteHome => if (s.minimized) {...s,homeExists:false} else s
    | MoveHome(id) => if (id==1 and not(s.present)) s
        else {...s,home:id,desktop:id,savedHome:id,homeExists:true,savedMonitor:name(id),raw:if(s.minimized) 0 else id}
    | RemoveOutput => {...s,present:false,raw:0,home:if(s.homeExists) 0 else s.home}
    | AddOutput(output) => {...s,present:true,outputName:output}
    | ReuseAddress => {...s,minimized:true,raw:0,identity:3-s.identity}
  }
  pure val EVENTS=Set(Minimize,Restore,DeleteHome,MoveHome(0),MoveHome(1),RemoveOutput,AddOutput("virtual"),AddOutput("different"),ReuseAddress)
  action step = { nondet event=EVENTS.oneOf(); fire(event) }
  val allProps = (owner==0 or (owner==1 and s.present))
    and (s.minimized and metadataValid and s.homeExists implies owner==s.home)
    and (s.minimized and not(metadataValid) implies owner==s.raw)
}
