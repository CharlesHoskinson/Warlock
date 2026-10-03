module family_order {
 type State={parents:int->int,paint:int->int,order:List[int],valid:bool}
 var s:State
 pure val nodes=Set(0,1,2,3)
 pure def listHas(xs:List[int],n:int):bool=xs.indices().exists(i=>xs.nth(i)==n)
 pure def followParent(p:int->int,n:int):int=if(n==-1) -1 else p.get(n)
 pure def ancestors(p:int->int,n:int):Set[int]={
  val p1=followParent(p,n);val p2=followParent(p,p1);val p3=followParent(p,p2);val p4=followParent(p,p3)
  Set(p1,p2,p3,p4).exclude(Set(-1))
 }
 pure def valid(p:int->int):bool={
  val root=nodes.filter(n=>p.get(n)==-1)
  root.size()==1 and nodes.forall(n=>p.get(n)==-1 or nodes.contains(p.get(n))) and nodes.forall(n=>not(ancestors(p,n).contains(n)))
 }
 action begin(p:int->int,paint:int->int):bool=s'={parents:p,paint:paint,order:List(),valid:valid(p)}
 action init=begin(Map(0->-1,1->0,2->1,3->0),Map(0->0,1->3,2->2,3->1))
 val eligible=nodes.filter(n=>not(listHas(s.order,n)) and (s.parents.get(n)==-1 or listHas(s.order,s.parents.get(n))))
 action draw={
  nondet n=eligible.oneOf()
  all{s.valid,eligible.forall(other=>s.paint.get(n)<=s.paint.get(other)),s'={...s,order:s.order.append(n)}}
 }
 val ancestorBeforeDescendant=s.order.indices().forall(i=>ancestors(s.parents,s.order.nth(i)).forall(a=>s.order.indices().exists(j=>j<i and s.order.nth(j)==a)))
 val siblingPaintOrder=s.order.indices().forall(i=>s.order.indices().forall(j=>{
  val a=s.order.nth(i);val b=s.order.nth(j)
  if(s.parents.get(a)==s.parents.get(b) and s.paint.get(a)<s.paint.get(b)) i<j else true
 }))
 val rejectedGraphHasNoDraw=if(not(s.valid)) s.order.length()==0 else true
 val exactNoDuplicate=s.order.indices().forall(i=>s.order.indices().forall(j=>i==j or s.order.nth(i)!=s.order.nth(j)))
 val allProps=ancestorBeforeDescendant and siblingPaintOrder and rejectedGraphHasNoDraw and exactNoDuplicate
 action step={
  nondet mode=0.to(3).oneOf();nondet rotation=0.to(3).oneOf();nondet flip=Set(0,1).oneOf()
  val p=if(mode==0) Map(0->-1,1->0,2->1,3->0) else if(mode==1) Map(0->-1,1->0,2->0,3->2) else if(mode==2) Map(0->-1,1->2,2->1,3->0) else Map(0->-1,1->-1,2->1,3->0)
  val paint=nodes.mapBy(n=>if(flip==0) (n+rotation)%4 else 3-((n+rotation)%4))
  any{begin(p,paint),draw}
 }
}
