module ax_mapping {
  type Event = Native(int) | Apps(int) | Children(int) | Role(bool)
    | HoverChanged | OwnerChanged | Retire | Reply
  var nativeCount:int
  var appCount:int
  var childCount:int
  var roleValid:bool
  var sameTarget:bool
  var sameOwner:bool
  var retired:bool
  var success:bool
  val permitted=nativeCount==1 and appCount==1 and childCount==1 and roleValid
    and sameTarget and sameOwner and not(retired)
  action init=all {nativeCount'=0,appCount'=0,childCount'=0,roleValid'=false,
    sameTarget'=true,sameOwner'=true,retired'=false,success'=false}
  action fire(e:Event):bool=all {
    nativeCount'=match e { | Native(n)=>n | _=>nativeCount },
    appCount'=match e { | Apps(n)=>n | _=>appCount },
    childCount'=match e { | Children(n)=>n | _=>childCount },
    roleValid'=match e { | Role(b)=>b | _=>roleValid },
    sameTarget'=(sameTarget and e!=HoverChanged),
    sameOwner'=(sameOwner and e!=OwnerChanged),retired'=(retired or e==Retire),
    success'=(e==Reply and permitted)
  }
  pure val EVENTS=Set(Native(0),Native(1),Native(2),Apps(0),Apps(1),Apps(2),
    Children(0),Children(1),Children(2),Role(true),Role(false),HoverChanged,OwnerChanged,Retire,Reply)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=success implies permitted
}
