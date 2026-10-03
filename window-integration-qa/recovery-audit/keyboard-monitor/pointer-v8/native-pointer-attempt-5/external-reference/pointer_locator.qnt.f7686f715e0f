module pointer_locator {
  type Event = Claim(int) | Disconnect((int,int)) | Query((int,int,bool))
    | Move((int,int)) | Hover((int,int,int)) | KeyboardFocus(int) | Retire
  pure val CLIENTS = Set(1,2,3)
  var owners: int -> int
  var registered: Set[int]
  var pending: Set[(int,int)]
  var sent: Set[(int,int)]
  var sentFrom: Set[(int,int)]
  var retired: bool
  var x: int
  var y: int
  var hover: int
  var originX: int
  var originY: int
  var keyboard: int
  var replyTarget: int
  var replyX: int
  var replyY: int
  var queryHover: int
  var queryX: int
  var queryY: int
  var queryOriginX: int
  var queryOriginY: int
  var replied: bool
  var denied: bool
  var replyError: str
  var lastEvent: Event

  def authorized(c:int, epoch:int):bool = not(retired)
    and registered.contains(c) and owners.get(c)==epoch
  action init = all {
    owners'=Map(1->0,2->0,3->0), registered'=Set(), pending'=Set(),
    sent'=Set(), sentFrom'=Set(), retired'=false, x'=0,y'=0,
    hover'=0,originX'=0,originY'=0,keyboard'=0,replyTarget'=0,
    replyX'=0,replyY'=0,queryHover'=0,queryX'=0,queryY'=0,
    queryOriginX'=0,queryOriginY'=0,replied'=false,denied'=false,replyError'="none",
    lastEvent'=Move((0,0))
  }
  action fire(e:Event):bool = {
    val ok = match e { | Query(q) => authorized(q._1,q._2) | _ => false }
    val motion = match e { | Move(p) => p._1!=x or p._2!=y | _ => false }
    all {
      owners'=match e { | Claim(c)=>owners.set(c,owners.get(c)+1) | _=>owners },
      registered'=match e { | Claim(c)=>if(retired)registered else registered.union(Set(c))
        | Disconnect(c)=>if(owners.get(c._1)==c._2)registered.exclude(Set(c._1))else registered | Retire=>Set() | _=>registered },
      pending'=match e {
        | Query(q)=>if(ok)pending.union(Set((q._1,q._2)))else pending
        | Claim(c)=>pending.filter(p=>p._1!=c)
        | Disconnect(c)=>if(owners.get(c._1)==c._2)pending.filter(p=>p._1!=c._1)else pending
        | Move(_)=>if(motion)Set()else pending
        | Retire=>Set() | _=>pending },
      sent'=if(motion and not(retired))pending else Set(),
      sentFrom'=pending,
      retired'=(retired or e==Retire),
      x'=match e { | Move(p)=>p._1 | _=>x },
      y'=match e { | Move(p)=>p._2 | _=>y },
      hover'=match e { | Hover(t)=>t._1 | _=>hover },
      originX'=match e { | Hover(t)=>t._2 | _=>originX },
      originY'=match e { | Hover(t)=>t._3 | _=>originY },
      keyboard'=match e { | KeyboardFocus(w)=>w | _=>keyboard },
      replyTarget'=if(ok)hover else replyTarget,
      replyX'=if(ok)x-originX else replyX,
      replyY'=if(ok)y-originY else replyY,
      queryHover'=if(ok)hover else queryHover,
      queryX'=if(ok)x else queryX,
      queryY'=if(ok)y else queryY,
      queryOriginX'=if(ok)originX else queryOriginX,
      queryOriginY'=if(ok)originY else queryOriginY,
      replied'=ok,
      denied'=match e { | Query(_)=>not(ok) | _=>false },
      replyError'=match e { | Query(q)=>if(not(ok))"AccessDenied" else if(q._3)"none" else "UnknownToplevel" | _=>replyError },
      lastEvent'=e
    }
  }
  val ownership = pending.forall(p=>registered.contains(p._1) and owners.get(p._1)==p._2)
  val directed = sent.subseteq(sentFrom)
  val retirement = retired implies pending==Set() and sent==Set()
  val querySnapshot = replied implies replyTarget==queryHover
    and replyX==queryX-queryOriginX and replyY==queryY-queryOriginY
  val allProps = ownership and directed and retirement and querySnapshot
  action step = {
    val controls = CLIENTS.fold(Set(Retire,Move((0,0)),Move((1,-1)),Move((-3,2)),
      Hover((0,0,0)),Hover((11,-2,1)),Hover((12,4,-3)),KeyboardFocus(11),KeyboardFocus(12)),
      (out,c)=>out.union(Set(Claim(c),Disconnect((c,owners.get(c))),Disconnect((c,owners.get(c)-1)),Query((c,owners.get(c),true)),
        Query((c,owners.get(c),false)),Query((c,owners.get(c)-1,true)))))
    nondet e=controls.oneOf()
    fire(e)
  }
}
