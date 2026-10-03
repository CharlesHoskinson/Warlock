/** An observer must select one compositor before touching persisted attention.
 * Instance availability and socket mtime cannot retarget an existing observer.
 * Model concerns local socket/query identity, not physical session restart. */
module attention_target {
  type Event = Prefer(int) | Implicit | Add(int) | Remove(int) | Start | Urgent | Disconnect
  pure val INSTANCES = Set(1,2,3)
  var preferred:int
  var instances:Set[int]
  var selected:int
  var queryTarget:int
  var streamTarget:int
  var saved:int
  var beforeSaved:int
  var lastEvent:Event
  val resolved = if(preferred>0) preferred else if(instances.size()==1) instances.fold(0,(_acc,n)=>n) else 0
  action init = all {preferred'=0,instances'=Set(1),selected'=0,queryTarget'=0,streamTarget'=0,saved'=9,beforeSaved'=9,lastEvent'=Implicit}
  action fire(event:Event):bool = all {
    preferred'=match event { | Prefer(n)=>n | Implicit=>0 | _=>preferred },
    instances'=match event { | Add(n)=>instances.union(Set(n)) | Remove(n)=>instances.exclude(Set(n)) | _=>instances },
    selected'=if(event==Start) resolved else selected,
    queryTarget'=if(event==Start) resolved else queryTarget,
    streamTarget'=if(event==Start) resolved else streamTarget,
    beforeSaved'=saved,
    saved'=if(event==Start and resolved>0) 0 else if(event==Urgent and selected>0) 1 else if(event==Disconnect and selected>0) 0 else saved,
    lastEvent'=event
  }
  pure val EVENTS = Set(Implicit,Start,Urgent,Disconnect).union(INSTANCES.map(n=>Prefer(n)))
    .union(INSTANCES.map(n=>Add(n))).union(INSTANCES.map(n=>Remove(n)))
  action step = {nondet event=EVENTS.oneOf();fire(event)}
  val allProps = selected==queryTarget and selected==streamTarget
    and (lastEvent==Start and selected==0 implies saved==beforeSaved)
    and (lastEvent==Start and preferred>0 implies selected==preferred)
}
