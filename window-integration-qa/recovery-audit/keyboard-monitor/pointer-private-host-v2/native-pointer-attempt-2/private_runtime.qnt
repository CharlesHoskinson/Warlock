module private_runtime {
  type Candidate = {pathKind:str, explicit:bool, ownRuntime:bool, ownParent:bool, ownUser:bool, privateModes:bool, dirsNotLinks:bool, ownBus:bool}
  var loaded:bool
  var candidate:Candidate
  pure def authorized(c:Candidate):bool = all {
    c.pathKind=="short-lower-hex", c.explicit, c.ownRuntime, c.ownParent,
    c.ownUser,c.privateModes,c.dirsNotLinks,c.ownBus
  }
  val good = {pathKind:"short-lower-hex",explicit:true,ownRuntime:true,ownParent:true,ownUser:true,privateModes:true,dirsNotLinks:true,ownBus:true}
  action init = all {loaded'=false,candidate'=good.with("explicit",false)}
  action attempt(c:Candidate):bool = all {candidate'=c,loaded'=authorized(c)}
  action step = {
    nondet path = Set("short-lower-hex","main","legacy-tmp","uppercase","extra-component").oneOf()
    nondet a = Set(true,false).oneOf()
    nondet b = Set(true,false).oneOf()
    nondet c = Set(true,false).oneOf()
    nondet d = Set(true,false).oneOf()
    nondet e = Set(true,false).oneOf()
    nondet f = Set(true,false).oneOf()
    nondet g = Set(true,false).oneOf()
    attempt({pathKind:path,explicit:a,ownRuntime:b,ownParent:c,ownUser:d,privateModes:e,dirsNotLinks:f,ownBus:g})
  }
  val invariant = loaded == authorized(candidate)
}
