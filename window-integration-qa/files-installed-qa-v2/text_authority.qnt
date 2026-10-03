/** Independent mutation authority specification, before formal/native acceptance.
 * Content versions stand for text changes; concrete byte/selection results are
 * replayed separately against actual Qt interfaces. */
module text_authority {
 type Event=MapWindow(bool)|Modal(bool)|Show({node:int,value:bool})|Enable({node:int,value:bool})|ReadOnly({node:int,value:bool})|Retire(int)|Recreate(int)|Mutate({node:int,epoch:int,kind:str})
 var mapped:bool
 var modal:bool
 var visible:Set[int]
 var enabledNodes:Set[int]
 var alive:Set[int]
 var readonly:Set[int]
 var epochs:int->int
 var content:int->int
 var selection:int->int
 var cursor:int->int
 var beforeContent:int->int
 var beforeSelection:int->int
 var beforeCursor:int->int
 var attempted:bool
 var allowed:bool
 var attemptedContent:bool
 var targetReadonly:bool
 var pid:int
 action init=all{mapped'=true,modal'=false,visible'=Set(0,1,2),enabledNodes'=Set(0,1,2),alive'=Set(0,1,2),readonly'=Set(),epochs'=Map(0->0,1->0,2->0),content'=Map(0->0,1->0,2->0),selection'=Map(0->0,1->0,2->0),cursor'=Map(0->0,1->0,2->0),beforeContent'=Map(0->0,1->0,2->0),beforeSelection'=Map(0->0,1->0,2->0),beforeCursor'=Map(0->0,1->0,2->0),attempted'=false,allowed'=false,attemptedContent'=false,targetReadonly'=false,pid'=667402}
 pure val NODES=Set(0,1,2) // 0 actual path input,1 own prompt input,2 diagnostic native text edit
 pure val CONTENT=Set("delete","insert","replace","setValue")
 pure val SELECTION=Set("selection","addSelection","removeSelection","cursor")
 val mutationRefusal=attempted and not(allowed) implies content==beforeContent and selection==beforeSelection and cursor==beforeCursor
 val readOnlyContentRefusal=attempted and attemptedContent and targetReadonly implies content==beforeContent
 val allProps=mutationRefusal and readOnlyContentRefusal and pid==667402
 action fire(e:Event):bool={
  val contentAttempt=match e{|Mutate(p)=>CONTENT.contains(p.kind)|_=>false}
  val permitted=match e{|Mutate(p)=>NODES.contains(p.node) and p.epoch==epochs.get(p.node) and alive.contains(p.node) and mapped and visible.contains(p.node) and enabledNodes.contains(p.node) and (if(modal)p.node==1 else p.node!=1) and (not(contentAttempt) or not(readonly.contains(p.node)))|_=>false}
  all{
   mapped'=match e{|MapWindow(b)=>b|_=>mapped},modal'=match e{|Modal(b)=>b|_=>modal},
   visible'=match e{|Show(p)=>if(p.value)visible.union(Set(p.node))else visible.exclude(Set(p.node))|_=>visible},
   enabledNodes'=match e{|Enable(p)=>if(p.value)enabledNodes.union(Set(p.node))else enabledNodes.exclude(Set(p.node))|_=>enabledNodes},
   readonly'=match e{|ReadOnly(p)=>if(p.value)readonly.union(Set(p.node))else readonly.exclude(Set(p.node))|_=>readonly},
   alive'=match e{|Retire(n)=>alive.exclude(Set(n))|Recreate(n)=>alive.union(Set(n))|_=>alive},
   epochs'=match e{|Retire(n)=>epochs.set(n,epochs.get(n)+1)|Recreate(n)=>epochs.set(n,epochs.get(n)+1)|_=>epochs},
   content'=match e{|Mutate(p)=>if(permitted and contentAttempt)content.set(p.node,content.get(p.node)+1)else content|_=>content},
   selection'=match e{|Mutate(p)=>if(permitted and p.kind!="cursor" and not(contentAttempt))selection.set(p.node,selection.get(p.node)+1)else selection|_=>selection},
   cursor'=match e{|Mutate(p)=>if(permitted and p.kind=="cursor")cursor.set(p.node,cursor.get(p.node)+1)else cursor|_=>cursor},
   beforeContent'=content,beforeSelection'=selection,beforeCursor'=cursor,
   attempted'=match e{|Mutate(_)=>true|_=>false},allowed'=permitted,attemptedContent'=contentAttempt,
   targetReadonly'=match e{|Mutate(p)=>readonly.contains(p.node)|_=>false},pid'=pid
  }
 }
 val EVENTS=Set(MapWindow(true),MapWindow(false),Modal(true),Modal(false))
  .union(NODES.fold(Set(),(es,n)=>es.union(Set(Retire(n),Recreate(n),Show({node:n,value:true}),Show({node:n,value:false}),Enable({node:n,value:true}),Enable({node:n,value:false}),ReadOnly({node:n,value:true}),ReadOnly({node:n,value:false})))))
  .union(NODES.fold(Set(),(es,n)=>es.union(Set(epochs.get(n),epochs.get(n)+1,if(epochs.get(n)>0)epochs.get(n)-1 else 0).fold(Set(),(gs,g)=>gs.union(CONTENT.union(SELECTION).map(k=>Mutate({node:n,epoch:g,kind:k})))))))
 action step={nondet e=EVENTS.oneOf();fire(e)}
}
