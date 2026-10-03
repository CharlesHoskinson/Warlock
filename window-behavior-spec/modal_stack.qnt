/** Owned modal surfaces remain above their owners, including pinned owners.
 * Pinning affects stacking priority, never a dialog's ability to receive input.
 */
module modal_stack {
  type Event = Raise(int) | Pin(bool) | Depth(int) | Click(int) | DesktopSwitch(int)
  var depth:int
  var pinned:bool
  var order:List[int]
  var focus:int
  var delivered:int
  var desktop:int
  var ownerDesktop:int
  var dialogDesktop:int
  pure def live(d:int):Set[int] = if(d==2) Set(1,2,3,4) else if(d==1) Set(1,2,3) else Set(1,2)
  pure def family(d:int):List[int] = if(d==2) List(1,3,4) else if(d==1) List(1,3) else List(1)
  pure def childTarget(d:int,id:int):int = if(d==2 and (id==1 or id==3)) 4 else if(d==1 and id==1) 3 else id
  pure def ids(o:List[int]):Set[int]=o.foldl(Set(),(members,id)=>members.union(Set(id)))
  pure def retain(o:List[int],keep:Set[int]):List[int]=o.foldl(List(),(members,id)=>if(keep.contains(id)) members.append(id) else members)
  pure def promote(o:List[int],members:List[int]):List[int] = retain(o,ids(o).exclude(ids(members))).concat(members)
  def raised(id:int):List[int] =
    if(id==1 or (id==2 and pinned)) promote(promote(order,List(id)),family(depth))
    else if(id==3 and depth==2) promote(order,List(3,4)) else promote(order,List(id))
  action init = all {depth'=1,pinned'=false,order'=List(1,2,3),focus'=3,delivered'=0,
    desktop'=1,ownerDesktop'=1,dialogDesktop'=1}
  def visible(id:int):bool=if(id==2)desktop==1 else desktop==ownerDesktop
  def canFire(e:Event):bool = match e {
    | Raise(id) => live(depth).contains(id)
    | Click(id) => live(depth).contains(id) and visible(id)
    | Depth(d) => d>=0 and d<=2
    | Pin(_) => true
    | DesktopSwitch(d) => d>=1 and d<=3
  }
  action fire(e:Event):bool = all {
    canFire(e),
    depth'=match e {| Depth(d)=>d | _=>depth},
    pinned'=match e {| Pin(value)=>value | _=>pinned},
    desktop'=match e {| DesktopSwitch(d)=>d | _=>desktop},
    ownerDesktop'=match e {| DesktopSwitch(d)=>if(pinned)d else ownerDesktop | Pin(value)=>if(value)desktop else ownerDesktop | _=>ownerDesktop},
    dialogDesktop'=match e {| DesktopSwitch(d)=>if(pinned)d else dialogDesktop | Pin(value)=>if(value)desktop else dialogDesktop | Depth(_)=>ownerDesktop | _=>dialogDesktop},
    order'=match e {
      | Raise(id)=>raised(id)
      | Click(id)=>raised(id)
      | Pin(value)=>if(value) promote(order,family(depth)) else order
      | Depth(d)=>{
        val retained=retain(order,live(d))
        retained.concat(retain(family(d),live(d).exclude(ids(retained))))
      }
      | DesktopSwitch(_)=>if(pinned)promote(order,family(depth)) else order
    },
    focus'=match e {| Click(id)=>childTarget(depth,id) | Depth(d)=>if(live(d).contains(focus)) childTarget(d,focus) else childTarget(d,1)
      | DesktopSwitch(d)=>if(pinned or d==ownerDesktop)childTarget(depth,1) else if(d==1)2 else 0 | _=>focus},
    delivered'=match e {| Click(id)=>if(childTarget(depth,id)==id) id else 0 | _=>0},
  }
  pure val EVENTS=Set(Raise(1),Raise(2),Raise(3),Raise(4),Pin(true),Pin(false),Depth(0),Depth(1),Depth(2),Click(1),Click(2),Click(3),Click(4),DesktopSwitch(1),DesktopSwitch(2),DesktopSwitch(3))
  action step = {nondet e=EVENTS.filter(canFire).oneOf();fire(e)}
  def rank(id:int):int=order.indices().fold(-1,(found,i)=>if(order.nth(i)==id) i else found)
  val allProps=order.foldl(Set(),(ids,id)=>ids.union(Set(id)))==live(depth) and order.length()==live(depth).size() and (focus==0 or live(depth).contains(focus))
    and (depth>=1 implies rank(3)>rank(1)) and (depth==2 implies rank(4)>rank(3))
    and (delivered!=0 implies childTarget(depth,delivered)==delivered)
    and ownerDesktop==dialogDesktop and (pinned implies ownerDesktop==desktop)
}
