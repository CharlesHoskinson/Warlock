module mouse_review {
  type Event = Enable(bool) | Toggle | Refresh((int,bool)) | Activate | Disable
    | Signal((int,int)) | Process(int)
  var requested:bool
  var capable:bool
  var device:int
  var active:bool
  var handlers:int
  var epoch:int
  var queue:Set[int]
  var currentItem:int
  action init=all {requested'=false,capable'=true,device'=1,active'=false,
    handlers'=0,epoch'=0,queue'=Set(),currentItem'=0}
  action fire(e:Event):bool={
    val refresh=match e { | Refresh(r)=>true | _=>false }
    val wanted=match e { | Enable(b)=>if(capable) b else requested
      | Toggle=>if(capable) not(active) else requested | _=>requested }
    val newCap=match e { | Refresh(r)=>r._2 and r._1!=0 | _=>capable }
    val nextActive=match e { | Enable(b)=>if(capable) b else active
      | Toggle=>if(capable) not(active) else active
      | Refresh(r)=>wanted and newCap | Activate=>newCap | Disable=>false | _=>active }
    val cleared=refresh or (active and not(nextActive)) or e==Disable
    all {
      requested'=wanted,capable'=newCap,
      device'=match e { | Refresh(r)=>r._1 | _=>device },
      active'=nextActive,handlers'=if(nextActive) 1 else 0,
      epoch'=if(cleared) epoch+1 else epoch,
      queue'=if(cleared) Set() else match e {
        | Signal(s)=>if(active and s._1==device and s._2==epoch) Set(epoch) else queue
        | Process(t)=>if(t==epoch) Set() else queue | _=>queue },
      currentItem'=if(cleared) 0 else match e {
        | Process(t)=>if(active and t==epoch and queue.contains(t)) device else currentItem
        | _=>currentItem }
    }
  }
  pure val EVENTS=Set(Enable(true),Enable(false),Toggle,Refresh((0,false)),
    Refresh((1,true)),Refresh((2,true)),Refresh((2,false)),Activate,Disable,
    Signal((1,0)),Signal((2,0)),Signal((1,1)),Signal((2,1)),
    Process(0),Process(1),Process(2))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=(active implies capable and device!=0 and handlers==1)
    and (not(active) implies handlers==0)
    and (currentItem!=0 implies active and currentItem==device)
}
