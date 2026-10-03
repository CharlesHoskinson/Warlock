/** Caption press captures identity and geometry before the first movement.
 * A motion over another window or empty space cannot change the drag owner.
 * Restoring a snapped caption preserves the horizontal fractional press offset.
 */
module caption_drag {
  type Point = {x:int,y:int}
  type Box = {x:int,y:int,w:int,h:int}
  type Event = Press({id:int,dx:int}) | Motion({point:Point,hit:int}) | Focus(int) | Release | Cancel | Reload | Close(int) | Open(int) | Snap(int)
  var boxes:int -> Box
  var alive:Set[int]
  var owner:int
  var phase:int
  var held:bool
  var press:Point
  var point:Point
  var offset:Point
  var original:Box
  var focus:int
  var lastOwner:int
  var changed:Set[int]
  var last:Event
  pure val NORMAL:Box={x:26,y:30,w:60,h:35}
  pure val PEER:Box={x:102,y:40,w:38,h:30}
  pure val SNAP:Box={x:0,y:3,w:80,h:96}
  action init=all {boxes'=Map(1->NORMAL,2->PEER),alive'=Set(1,2),owner'=0,phase'=0,held'=false,press'={x:0,y:0},point'={x:0,y:0},offset'={x:0,y:0},original'=NORMAL,focus'=1,lastOwner'=0,changed'=Set(),last'=Focus(1)}
  def canFire(e:Event):bool=match e {
    | Press(p)=>alive.contains(p.id) and phase==0 and not(held)
    | Snap(id)=>alive.contains(id) and phase==0 and not(held)
    | _=>true
  }
  def start(e:Event):bool=match e {| Press(_)=>true | _=>false}
  def motion(e:Event):bool=match e {| Motion(_)=>phase!=0 | _=>false}
  def stopped(e:Event):bool=match e {| Release=>true | Cancel=>true | Reload=>true | Close(id)=>id==owner | _=>false}
  def pressed(e:Event):Point=match e {| Press(p)=>{x:boxes.get(p.id).x+p.dx,y:boxes.get(p.id).y-2} | _=>press}
  def pressOffset(e:Event):Point=match e {
    | Press(p)=>{x:if(boxes.get(p.id).w==80) p.dx*3/4 else p.dx,y:-2}
    | _=>offset
  }
  def moved(e:Event):Box=match e {| Motion(m)=>{x:m.point.x-offset.x,y:m.point.y-offset.y,w:if(original.w==80) 60 else original.w,h:if(original.w==80) 35 else original.h} | _=>boxes.get(1)}
  action fire(e:Event):bool=all {
    canFire(e),
    boxes'=match e {
      | Motion(_)=>if(phase!=0) boxes.put(owner,moved(e)) else boxes
      | Cancel=>if(phase!=0 and alive.contains(owner)) boxes.put(owner,original) else boxes
      | Reload=>if(phase!=0 and alive.contains(owner)) boxes.put(owner,original) else boxes
      | Snap(id)=>boxes.put(id,SNAP)
      | Open(id)=>if(alive.contains(id)) boxes else boxes.put(id,if(id==1) NORMAL else PEER)
      | _=>boxes
    },
    alive'=match e {| Close(id)=>alive.exclude(Set(id)) | Open(id)=>alive.union(Set(id)) | _=>alive},
    owner'=if(stopped(e)) 0 else match e {| Press(p)=>p.id | _=>owner},
    phase'=if(stopped(e)) 0 else if(start(e)) 1 else if(motion(e)) 2 else phase,
    held'=match e {| Press(_)=>true | Release=>false | _=>held},
    press'=pressed(e),
    point'=match e {| Motion(m)=>m.point | Press(_)=>pressed(e) | _=>point},
    offset'=pressOffset(e),
    original'=match e {| Press(p)=>boxes.get(p.id) | _=>original},
    focus'=match e {| Focus(id)=>id | _=>focus},
    lastOwner'=owner,
    changed'=match e {| Motion(_)=>if(phase!=0) Set(owner) else Set() | _=>Set()},
    last'=e,
  }
  pure val EVENTS=Set(Press({id:1,dx:20}),Press({id:2,dx:10}),Motion({point:{x:60,y:35},hit:1}),Motion({point:{x:120,y:50},hit:2}),Motion({point:{x:90,y:10},hit:0}),Focus(1),Focus(2),Release,Cancel,Reload,Close(1),Close(2),Open(1),Open(2),Snap(1))
  action step={nondet e=EVENTS.filter(canFire).oneOf();fire(e)}
  val allProps=phase>=0 and phase<=2 and (phase!=0 implies alive.contains(owner) and held)
    and (phase==2 implies boxes.get(owner)=={x:point.x-offset.x,y:point.y-offset.y,w:if(original.w==80) 60 else original.w,h:if(original.w==80) 35 else original.h})
    and (changed.size()>0 implies changed==Set(lastOwner))
}
