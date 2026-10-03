module ancestor_policy {
 type Press={geometric:int,filtered:int,pointer:int,foreign:bool,region:bool,decoration:bool,guard:bool,x11:bool,resource:bool,scaleValid:bool}
 type Event=Click(Press)|Release|Modal(int)|Focus(int)
 var s:{depth:int,focus:int,consumed:bool,delivered:int,previousFocus:int,previousConsumed:bool,last:Event}
 pure def target(depth:int,owner:int):int = if(owner==1 and depth>0) (if(depth==2) 4 else 3) else if(owner==3 and depth==2) 4 else owner
 pure def recovery(depth:int,p:Press):bool = not(p.guard) and not(p.foreign) and (p.pointer==0 or p.pointer==p.filtered) and (p.decoration or (p.region and (not(p.x11) or (p.resource and p.scaleValid)))) and p.geometric!=0 and target(depth,p.geometric)!=p.geometric
 action init=s'={depth:1,focus:2,consumed:false,delivered:0,previousFocus:2,previousConsumed:false,last:Focus(2)}
 action fire(e:Event):bool=s'=match e {
 | Click(p)=>if(s.consumed or p.guard or p.foreign) {...s,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
   else if(recovery(s.depth,p)) {...s,focus:target(s.depth,p.geometric),consumed:true,delivered:0,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
   else {...s,focus:if(p.filtered==0) s.focus else target(s.depth,p.filtered),delivered:p.filtered,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
 | Release=>{...s,consumed:false,delivered:if(s.consumed) 0 else s.delivered,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
 | Modal(depth)=>{...s,depth:depth,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
 | Focus(id)=>{...s,focus:id,previousFocus:s.focus,previousConsumed:s.consumed,last:e}
 }
 action step={nondet geometric=0.to(4).oneOf();nondet filtered=0.to(4).oneOf();nondet pointer=0.to(4).oneOf();nondet foreign=Set(true,false).oneOf();nondet region=Set(true,false).oneOf();nondet decoration=Set(true,false).oneOf();nondet guard=Set(true,false).oneOf();nondet x11=Set(true,false).oneOf();nondet resource=Set(true,false).oneOf();nondet scaleValid=Set(true,false).oneOf();nondet e=Set(Click({geometric:geometric,filtered:filtered,pointer:pointer,foreign:foreign,region:region,decoration:decoration,guard:guard,x11:x11,resource:resource,scaleValid:scaleValid}),Release,Modal(0),Modal(1),Modal(2),Focus(1),Focus(2),Focus(3),Focus(4)).oneOf();fire(e)}
 val allProps=Set(1,2,3,4).contains(s.focus) and match s.last {
 | Click(p)=>if(p.guard or p.foreign or s.previousConsumed) s.focus==s.previousFocus else if(recovery(s.depth,p)) s.focus==target(s.depth,p.geometric) and s.consumed and s.delivered==0 else not(s.consumed)
 | Release=>not(s.consumed)
 | _=>true
 }
}
