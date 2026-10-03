/** Contract for global reader input routing. The model uses key 1 as a
 * locking custom modifier, 2 as an exact command stroke, 3 as a normal
 * compositor shortcut, and 4 as ordinary typing. Modifier masks/keymaps are
 * native proof obligations, not inferred from this abstract alphabet. */
module keyboard_monitor {
  type Event = ClaimReader(int) | Watch(int) | Unwatch(int) | GrabAll(int)
    | UngrabAll(int) | SetGrabs((int,bool,bool)) | Disconnect(int)
    | Press(int) | Release(int) | SetPermission(bool) | KeymapChange | RemoveDevice | Tick | StopService | StartService
  pure val KEYS=Set(1,2,3,4)
  var service:bool
  var permitted:bool
  var registered:Set[int]
  var watchers:Set[int]
  var fullGrabbers:Set[int]
  var modifierGrabbers:Set[int]
  var strokeGrabbers:Set[int]
  var held:Set[int]
  var captured:Set[int]
  var delivered:Set[int]
  var locked:bool
  var clock:int
  var tapTime:int
  var tapArmed:bool
  var lastEvent:Event
  var lastConsumed:bool
  var lastNotified:bool
  var lastDenied:bool
  val readerActive=service and registered.size()>0
  val watched=watchers.size()>0
  val allGrab=fullGrabbers.size()>0
  val modifierGrab=modifierGrabbers.size()>0
  val strokeGrab=strokeGrabbers.size()>0
  pure val readerEnabled=false
  def authorized(c:int):bool=service and registered.contains(c)
  def doubleTap(k:int):bool=readerActive and not(allGrab) and modifierGrab and k==1
    and not(held.contains(k)) and tapArmed and clock-tapTime<=1
  def consumedPress(k:int):bool=if(captured.contains(k)) true else if(delivered.contains(k)) false
    else permitted and readerActive and not(doubleTap(k)) and (allGrab or (modifierGrab and (k==1 or held.contains(1))) or (strokeGrab and k==2))
  def notify(k:int):bool=permitted and readerActive and (watched or allGrab or consumedPress(k) or captured.contains(k) or doubleTap(k))
  action init=all {service'=true,permitted'=true,registered'=Set(),watchers'=Set(),fullGrabbers'=Set(),modifierGrabbers'=Set(),strokeGrabbers'=Set(),
    held'=Set(),captured'=Set(),delivered'=Set(),locked'=false,clock'=0,tapTime'=0,tapArmed'=false,
    lastEvent'=StartService,lastConsumed'=false,lastNotified'=false,lastDenied'=false}
  action fire(e:Event):bool={
    val removed=match e { | Disconnect(c)=>Set(c) | StopService=>registered | _=>Set() }
    val reset=match e {
      | StopService=>true
      | SetPermission(p)=>p!=permitted
      | KeymapChange=>true
      | RemoveDevice=>true
      | Disconnect(c)=>registered.contains(c)
      | ClaimReader(c)=>service and not(registered.contains(c))
      | SetGrabs(t)=>authorized(t._1)
      | GrabAll(c)=>authorized(c)
      | UngrabAll(c)=>authorized(c)
      | _=>false
    }
    all {
      service'=match e { | StopService=>false | StartService=>true | _=>service },
      permitted'=match e { | SetPermission(p)=>p | _=>permitted },
      registered'=match e { | ClaimReader(c)=>if(service) registered.union(Set(c)) else registered | Disconnect(c)=>registered.exclude(Set(c)) | StopService=>Set() | _=>registered },
      watchers'=match e { | Watch(c)=>if(authorized(c)) watchers.union(Set(c)) else watchers | Unwatch(c)=>if(authorized(c)) watchers.exclude(Set(c)) else watchers | _=>watchers.exclude(removed) },
      fullGrabbers'=match e { | GrabAll(c)=>if(authorized(c)) fullGrabbers.union(Set(c)) else fullGrabbers | UngrabAll(c)=>if(authorized(c)) fullGrabbers.exclude(Set(c)) else fullGrabbers | _=>fullGrabbers.exclude(removed) },
      modifierGrabbers'=match e { | SetGrabs(t)=>if(authorized(t._1)) (if(t._2) modifierGrabbers.union(Set(t._1)) else modifierGrabbers.exclude(Set(t._1))) else modifierGrabbers | _=>modifierGrabbers.exclude(removed) },
      strokeGrabbers'=match e { | SetGrabs(t)=>if(authorized(t._1)) (if(t._3) strokeGrabbers.union(Set(t._1)) else strokeGrabbers.exclude(Set(t._1))) else strokeGrabbers | _=>strokeGrabbers.exclude(removed) },
      held'=match e { | Press(k)=>held.union(Set(k)) | Release(k)=>held.exclude(Set(k)) | RemoveDevice=>Set() | _=>held },
      captured'=match e { | Press(k)=>if(consumedPress(k)) captured.union(Set(k)) else captured
        | Release(k)=>captured.exclude(Set(k)) | RemoveDevice=>Set() | _=>captured },
      delivered'=match e { | Press(k)=>if(not(consumedPress(k))) delivered.union(Set(k)) else delivered
        | Release(k)=>delivered.exclude(Set(k)) | RemoveDevice=>Set() | _=>delivered },
      locked'=match e { | Press(k)=>if(k==1 and not(held.contains(k)) and not(consumedPress(k))) not(locked) else locked | _=>locked },
      clock'=if(e==Tick) clock+1 else clock,
      tapTime'=match e { | Press(k)=>if(k==1 and modifierGrab and consumedPress(k) and not(held.contains(k))) clock else tapTime | _=>tapTime },
      tapArmed'=if(reset) false else match e {
        | Press(k)=>if(doubleTap(k)) false else if(k==1 and modifierGrab and not(allGrab) and consumedPress(k) and not(held.contains(k))) true else if(k!=1) false else tapArmed
        | _=>tapArmed },
      lastEvent'=e,
      lastConsumed'=match e { | Press(k)=>consumedPress(k) | Release(k)=>captured.contains(k) | _=>false },
      lastNotified'=match e { | Press(k)=>notify(k) | Release(k)=>permitted and readerActive and (watched or allGrab or captured.contains(k) or (modifierGrab and k==1)) | _=>false },
      lastDenied'=match e { | Watch(c)=>not(authorized(c)) | Unwatch(c)=>not(authorized(c)) | GrabAll(c)=>not(authorized(c)) | UngrabAll(c)=>not(authorized(c)) | SetGrabs(t)=>not(authorized(t._1)) | _=>false }
    }
  }
  pure val EVENTS=Set(ClaimReader(1),ClaimReader(2),Watch(1),Watch(2),Unwatch(1),GrabAll(1),UngrabAll(1),
    SetGrabs((1,true,false)),SetGrabs((1,false,true)),SetGrabs((1,false,false)),SetGrabs((2,true,true)),Disconnect(1),Disconnect(2),SetPermission(true),SetPermission(false),KeymapChange,RemoveDevice,Tick,StopService,StartService)
    .union(KEYS.map(k=>Press(k))).union(KEYS.map(k=>Release(k)))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=captured.intersect(delivered).size()==0 and captured.subseteq(held) and delivered.subseteq(held)
    and (not(readerActive) implies not(watched) and not(allGrab) and not(modifierGrab) and not(strokeGrab))
    and watchers.subseteq(registered) and fullGrabbers.subseteq(registered) and modifierGrabbers.subseteq(registered) and strokeGrabbers.subseteq(registered)
    and (not(readerActive) implies not(lastNotified)) and not(readerEnabled)
    and (not(permitted) implies not(lastNotified))
}
