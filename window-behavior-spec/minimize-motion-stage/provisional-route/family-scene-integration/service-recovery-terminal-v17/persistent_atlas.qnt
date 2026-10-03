module persistent_atlas {
 type Snapshot={identity:int,session:int,geometry:int,pixels:int}
 type Pointer=Empty|Published(Snapshot)
 type Event=Stage(Snapshot)|Publish(Snapshot)|Read|Reuse|Restart|Move|Prune
 type State={identity:int,session:int,geometry:int,images:Set[Snapshot],pointer:Pointer,provided:bool,source:Snapshot}
 var s:State
 val original={identity:1,session:1,geometry:1,pixels:101}
 action init=s'={identity:1,session:1,geometry:1,images:Set(),pointer:Empty,provided:false,source:original}
 action fire(e:Event):bool={
  val b={...s,provided:false}
  s'=match e {
   | Stage(c)=>{...b,images:s.images.union(Set(c))}
   | Publish(c)=>if(s.images.contains(c)){...b,pointer:Published(c)} else b
   | Read=>match s.pointer {
       | Empty=>b
       | Published(c)=>if(c.identity==s.identity and c.session==s.session and c.geometry==s.geometry and s.images.contains(c)){...b,provided:true,source:c} else b
      }
   | Reuse=>{...b,identity:s.identity+1}
   | Restart=>{...b,session:s.session+1}
   | Move=>{...b,geometry:s.geometry+1}
   | Prune=>match s.pointer {
       | Empty=>{...b,images:Set()}
       | Published(c)=>if(c.identity==s.identity and c.session==s.session){...b,images:Set(c)} else {...b,pointer:Empty,images:Set()}
      }
  }
 }
 val sourceHasExactCurrentProvenance=s.provided implies (s.source.identity==s.identity and s.source.session==s.session and s.source.geometry==s.geometry and s.images.contains(s.source))
 val completePairOnly=s.provided implies (s.pointer==Published(s.source))
 val allProps=sourceHasExactCurrentProvenance and completePairOnly
 action step={
  val c={identity:s.identity,session:s.session,geometry:s.geometry,pixels:s.identity*100+s.geometry}
  nondet e=Set(Stage(c),Publish(c),Stage(original),Publish(original),Read,Reuse,Restart,Move,Prune).oneOf();fire(e)
 }
}
