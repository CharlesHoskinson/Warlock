/** Service lifecycle, separate from the frozen v5 key-routing contract.
 * Owned names authorize public requests; they never infer interception.
 * currentOwner/session epochs reject stale adoption and reconnect callbacks.
 * Virtual lock debt stands for raw/accepted Caps/Num divergence. */
module service_lifecycle {
  type Event = Owner(int) | Adopt((int,int)) | Request(int) | Capture
    | Release | DirtyLocks | ReconcileLocks | RemoveDevice | Prepare
    | Reload | Reconnect((int,int))
  var epoch:int
  var generation:int
  var currentOwner:int
  var adopted:int
  var subscriptions:Set[int]
  var retiring:bool
  var held:bool
  var debt:bool
  var ready:bool
  var denied:bool
  val quiescent=not(held) and not(debt)
  action init=all {epoch'=1,generation'=0,currentOwner'=0,adopted'=0,subscriptions'=Set(),
    retiring'=false,held'=false,debt'=false,ready'=false,denied'=false}
  action fire(e:Event):bool={
    val retirement= e==Prepare and quiescent
    val requested=match e { | Request(c1)=>c1 | Reconnect(t2)=>t2._2 | _=>0 }
    val permitted=requested!=0 and not(retiring) and adopted==requested and currentOwner==requested
      and (match e { | Reconnect(t3)=>t3._1==epoch | _=>true })
    all {
      epoch'=if(e==Reload and retiring) epoch+1 else epoch,
      generation'=match e { | Owner(c4)=>generation+1 | _=>generation },
      currentOwner'=match e { | Owner(c5)=>c5 | _=>currentOwner },
      adopted'=match e {
        | Owner(c6)=>0
        | Adopt(t7)=>if(t7._1==generation and t7._2==currentOwner) currentOwner else adopted
        | Reload=>if(retiring) 0 else adopted
        | _=>adopted },
      subscriptions'=if(retirement or (match e { | Owner(discard)=>true | Reload=>retiring | _=>false })) Set()
        else if(permitted) subscriptions.union(Set(requested)) else subscriptions,
      retiring'=(if(e==Reload and retiring) false else retiring or retirement),
      held'=match e { | Capture=>if(not(retiring) and subscriptions.size()>0) true else held
        | Release=>false | RemoveDevice=>false | _=>held },
      debt'=match e { | DirtyLocks=>if(not(retiring) and subscriptions.size()>0) true else debt
        | ReconcileLocks=>false | RemoveDevice=>false | _=>debt },
      ready'=retirement,
      denied'=(requested!=0 and not(permitted))
    }
  }
  pure val EVENTS=Set(Owner(0),Owner(1),Owner(2),Adopt((0,1)),Adopt((1,1)),Adopt((2,2)),
    Request(1),Request(2),Capture,Release,DirtyLocks,ReconcileLocks,RemoveDevice,Prepare,Reload,
    Reconnect((1,1)),Reconnect((2,1)),Reconnect((1,2)),Reconnect((2,2)))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=(retiring implies subscriptions.size()==0 and quiescent)
    and subscriptions.forall(c=>c==currentOwner and c==adopted)
    and (ready implies retiring)
}
