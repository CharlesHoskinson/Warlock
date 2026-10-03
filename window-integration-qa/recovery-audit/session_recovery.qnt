/** Session-scoped Snap Group persistence. Legacy state is admitted only through
 * current PID/stable identity matching. This models helper disk reconciliation,
 * not native application survival or a physical compositor restart. */
module session_recovery {
  type Event = Reload | NewSession | IdentityCollisionSession | Close(int)
    | Reuse(int) | Record(int) | Launch(int) | ExplicitTarget | UniqueTarget
    | AmbiguousTarget | MissingTarget
  type Target = Explicit | Unique | Ambiguous | Missing
  pure val ADDRESSES = Set(1,2)
  var current: int
  var tag: int
  var live: int -> int
  var saved: int -> int
  var normal: int -> int
  var lastEvent: Event
  var target: Target
  val canSelect = target == Explicit or target == Unique
  val sameSession = tag == 0 or tag == current
  val members = if (sameSession and canSelect) saved.keys().filter(a => live.keys().contains(a)
      and saved.get(a) == live.get(a)) else Set()
  val recalledGroup = if (members.size() >= 2) members else Set()
  def cleaned: int -> int = members.mapBy(a => saved.get(a))
  def normalCleaned: int -> int = members.mapBy(a => normal.get(a))
  action init = all { current'=1, tag'=0, live'=Map(1->1,2->1),
    saved'=Map(1->1,2->1), normal'=Map(1->640,2->800), lastEvent'=Reload, target'=Explicit }
  action fire(e:Event):bool = all {
    current' = match e { | NewSession => current+1 | IdentityCollisionSession => current+1 | _ => current },
    tag' = match e { | Reload => if(canSelect) current else tag | Record(_) => if(canSelect) current else tag | _ => tag },
    target' = match e { | ExplicitTarget => Explicit | UniqueTarget => Unique
      | AmbiguousTarget => Ambiguous | MissingTarget => Missing | _ => target },
    live' = match e {
      | NewSession => Map()
      | Close(a) => live.keys().exclude(Set(a)).mapBy(k => live.get(k))
      | Reuse(a) => if(live.keys().contains(a)) live.put(a,3-live.get(a)) else live
      | Launch(a) => live.put(a,1)
      | _ => live
    },
    saved' = match e {
      | Reload => if(canSelect) cleaned else saved
      | Record(a) => if(not(canSelect)) saved else if(live.keys().contains(a)) cleaned.put(a,live.get(a)) else cleaned
      | _ => saved
    },
    normal' = match e {
      | Reload => if(canSelect) normalCleaned else normal
      | Record(a) => if(not(canSelect)) normal else if(live.keys().contains(a)) normalCleaned.put(a,640) else normalCleaned
      | _ => normal
    },
    lastEvent'=e
  }
  pure val EVENTS = Set(Reload,NewSession,IdentityCollisionSession,ExplicitTarget,UniqueTarget,AmbiguousTarget,MissingTarget)
    .union(ADDRESSES.map(a => Close(a))).union(ADDRESSES.map(a => Reuse(a)))
    .union(ADDRESSES.map(a => Record(a))).union(ADDRESSES.map(a => Launch(a)))
  action step = { nondet event=EVENTS.oneOf(); fire(event) }
  val allProps = saved.keys()==normal.keys()
    and members.forall(a => live.keys().contains(a) and saved.get(a)==live.get(a))
    and (not(sameSession) implies members.size()==0 and recalledGroup.size()==0)
    and (not(canSelect) implies members.size()==0 and recalledGroup.size()==0)
    and (recalledGroup.size()==0 or recalledGroup.size()>=2)
}
