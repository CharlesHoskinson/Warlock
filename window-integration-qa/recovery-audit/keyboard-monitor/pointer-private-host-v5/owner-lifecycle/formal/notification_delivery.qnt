module notification_delivery {
  type Event = Query | Motion | OwnerLoss | Reclaim | Drain | Deliver | Retire | BusLoss | Overflow | LegacyDirect
  var wireOwner:int
  var cachedOwner:int
  var nextEpoch:int
  var owners:List[int]
  var pending:int
  var notes:List[int]
  var retired:bool
  var point:int
  var replyPoint:int
  var signals:List[int]
  var emissionEpochs:List[(int,int)]
  var stale:bool
  var refused:bool
  action init=all {wireOwner'=1,cachedOwner'=1,nextEpoch'=1,owners'=List(),pending'=0,
    notes'=List(),retired'=false,point'=0,replyPoint'=0,signals'=List(),emissionEpochs'=List(),stale'=false,refused'=false}
  action fire(e:Event):bool={
    val stop=e==Retire or e==BusLoss or e==Overflow
    val lose=e==OwnerLoss and wireOwner!=0 and owners.length()<2 and not(retired)
    val claim=e==Reclaim and wireOwner==0 and nextEpoch<3 and owners.length()<2 and not(retired)
    val drain=e==Drain and owners.length()>0 and not(retired)
    val ready=not(retired) and owners.length()==0 and wireOwner!=0 and wireOwner==cachedOwner
    val query=e==Query and ready and notes.length()<2
    val move=e==Motion and not(retired)
    val capture=move and pending!=0 and 1-point!=replyPoint and notes.length()<2
    val delivery=e==Deliver and owners.length()==0 and notes.length()>0 and not(retired)
    val valid=delivery and ready and notes.head()==cachedOwner
    val legacy=e==LegacyDirect and not(retired) and pending!=0 and cachedOwner!=0
    all {
      wireOwner'=if(lose) 0 else if(claim) nextEpoch+1 else if(stop) 0 else wireOwner,
      cachedOwner'=if(stop) 0 else if(drain) owners.head() else cachedOwner,
      nextEpoch'=if(claim) nextEpoch+1 else nextEpoch,
      owners'=if(stop) List() else if(lose) owners.append(0) else if(claim) owners.append(nextEpoch+1) else if(drain) owners.tail() else owners,
      pending'=if(stop or (drain and owners.head()!=pending) or capture or legacy) 0 else if(query) cachedOwner else pending,
      notes'=if(stop) List() else if(capture) notes.append(pending) else if(delivery) notes.tail() else notes,
      retired'=(retired or stop),
      point'=if(move) 1-point else point,
      replyPoint'=if(query) point else replyPoint,
      signals'=if(valid) signals.append(notes.head()) else if(legacy) signals.append(pending) else signals,
      emissionEpochs'=if(valid) emissionEpochs.append((notes.head(),wireOwner)) else if(legacy) emissionEpochs.append((pending,wireOwner)) else emissionEpochs,
      stale'=(stale or (legacy and pending!=wireOwner)),
      refused'=(e==Query and not(query))
    }
  }
  pure val EVENTS=Set(Query,Motion,OwnerLoss,Reclaim,Drain,Deliver,Retire,BusLoss,Overflow)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=not(stale) and emissionEpochs.foldl(true,(ok,p)=>ok and p._1==p._2) and signals.length()==emissionEpochs.length() and notes.length()<=2 and owners.length()<=2
    and (retired implies pending==0 and notes.length()==0 and cachedOwner==0)
}
