/** Taskbar file-drag dwell navigation; no file operation is performed by shell. */
module drag_hover {
  type Event = App(int) | Preview(int) | Dwell | Leave | Drop | Close(int) | Reuse(int)
  var s:{target:int,token:int,generations:int->int,alive:Set[int],phase:int,activated:int,activationToken:int,offered:bool,consumed:bool}
  action init=s'={target:0,token:0,generations:Map(1->1,2->1),alive:Set(1,2),phase:0,activated:0,activationToken:0,offered:false,consumed:false}
  action fire(e:Event):bool={
    val base={...s,activated:0,activationToken:0}
    s'=match e {
      | App(id) => if(s.phase>0 and s.target==id) base else {...base,target:id,token:if(id>0) s.generations.get(id) else 0,phase:1,offered:false}
      | Preview(id) => {...base,target:id,token:s.generations.get(id),phase:3,offered:true}
      | Dwell => if(s.phase==1) {...base,phase:2,offered:s.target>=0} else if((s.phase==2 or s.phase==3) and s.target>0 and s.alive.contains(s.target) and s.generations.get(s.target)==s.token) {...base,phase:4,activated:s.target,activationToken:s.token} else base
      | Leave => {...base,target:0,token:0,phase:0}
      | Drop => {...base,target:0,token:0,phase:0,offered:false,consumed:false}
      | Close(id) => {...base,alive:s.alive.exclude(Set(id))}
      | Reuse(id) => {...base,alive:s.alive.union(Set(id)),generations:s.generations.set(id,s.generations.get(id)+1)}
    }
  }
  pure val EVENTS=Set(App(-1),App(0),App(1),App(2),Preview(1),Preview(2),Dwell,Leave,Drop,Close(1),Close(2),Reuse(1),Reuse(2))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=not(s.consumed) and (s.activated==0 or (s.alive.contains(s.activated) and s.activationToken==s.generations.get(s.activated) and s.activated==s.target))
}
