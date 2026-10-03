/** Required interaction contract, written independently of QML dispatch.
 * Paths are opaque sandbox identities; file operation semantics are unchanged.
 * Native widget lifetime and reader delivery need concrete replay evidence. */
module keyboard_focus {
  type Event = Tab(bool) | Arrow(int) | Prompt | Cancel | Edit(str) | Layout(str)
    | Sidebar | Home | Unmap | MapWindow | Hide(int) | Disable(int) | Rebuild | Reload
    | Rebind({node:int,path:int}) | Press({node:int, generation:int, path:int})
  var focus:int // 0 main,1 toolbar,2/8/9/10 independent files,3 sidebar,4 Home,5 input,6 Cancel,7 accept
  var cur:int
  var layout:str
  var editing:str
  var prompt:bool
  var sidebar:bool
  var mapped:bool
  var hidden:Set[int]
  var disabled:Set[int]
  var nodePaths:int -> int
  var epochs:int -> int
  var promptPath:int
  var generation:int
  var pid:int
  var actions:List[int]
  var accepted:bool
  var wasAllowed:bool
  var previousActions:int
  var previousFocus:int
  var reloaded:bool
  action init=all{focus'=0,cur'=0,layout'="list",editing'="none",prompt'=false,sidebar'=false,
    mapped'=true,nodePaths'=Map(0->0,1->1,2->0,3->3,4->4,5->5,6->6,7->7,8->1,9->2,10->3),epochs'=Map(0->0,1->0,2->0,3->0,4->0,5->0,6->0,7->0,8->0,9->0,10->0),promptPath'=0,hidden'=Set(),disabled'=Set(),generation'=0,pid'=667402,actions'=[],accepted'=false,
    wasAllowed'=false,previousActions'=0,previousFocus'=0,reloaded'=false}
  pure def clamp(n:int):int=if(n<0)0 else if(n>3)3 else n
  // Logical action identity is independent of the selected file for other scopes.
  pure def fileNode(index:int):int=if(index==0)2 else index+7
  def nodePath(n:int):int=if(n>=5 and n<=7)promptPath else nodePaths.get(n)
  val fieldsValid=focus>=0 and focus<=10 and cur>=0 and cur<=3 and pid==667402
  val modalTrap=prompt implies focus>=5 and focus<=7
  val refusedHasNoAction=(not(wasAllowed) implies actions.length()==previousActions)
  val reloadPreservesFocus=reloaded implies focus==previousFocus
  val allProps=fieldsValid and modalTrap and refusedHasNoAction and reloadPreservesFocus
  action fire(e:Event):bool={
    val allow=match e {|Press(p)=>mapped and p.node>=0 and p.node<=10 and (if(prompt)p.node>=5 and p.node<=7 else p.node<=4 or p.node>=8) and not(hidden.contains(p.node)) and not(disabled.contains(p.node)) and p.generation==epochs.get(p.node) and p.path==nodePath(p.node)|_=>false}
    // Reject incompatible commands in the transition, never rewrite generated events.
    val blocked=prompt and match e {|Sidebar=>true|Home=>true|Edit(_)=>true|Layout(_)=>true|Arrow(_)=>true|_=>false}
    val nextFocus=if(blocked)focus else match e {
      |Prompt=>5 |Cancel=>0 |Edit(_)=>5 |Sidebar=>if(sidebar)0 else 3 |Home=>4
      |Tab(back)=>if(prompt){if(back){if(focus==5)7 else focus-1}else{if(focus==7)5 else focus+1}}else if(focus>=4)0 else focus+1
      |Arrow(d)=>if(editing=="none" and not(prompt) and not(sidebar))fileNode(clamp(cur+d*(if(layout=="grid")2 else 1))) else focus
      |_=>focus}
    all{
      focus'=nextFocus,
      cur'=match e {|Arrow(d)=>if((editing=="none" or editing=="filter") and not(prompt) and not(sidebar))clamp(cur+d*(if(layout=="grid")2 else 1))else cur|_=>cur},
      layout'=if(blocked)layout else match e{|Layout(s)=>s|_=>layout},
      editing'=if(blocked)editing else match e{|Edit(s)=>s|Prompt=>"prompt"|Cancel=>"none"|Home=>"none"|_=>editing},
      prompt'=if(e==Prompt)true else if(e==Cancel)false else prompt,
      sidebar'=if(blocked)sidebar else if(e==Sidebar)not(sidebar)else if(e==Cancel or e==Home)false else sidebar,
      mapped'=if(e==Unmap)false else if(e==MapWindow)true else mapped,
      hidden'=match e{|Hide(n)=>hidden.union(Set(n))|_=>hidden},
      disabled'=match e{|Disable(n)=>disabled.union(Set(n))|_=>disabled},
      nodePaths'=match e {|Rebind(p)=>nodePaths.set(p.node,p.path)|_=>nodePaths},
      epochs'=match e {|Rebind(p)=>epochs.set(p.node,epochs.get(p.node)+1)|Rebuild=>epochs.keys().mapBy(n=>epochs.get(n)+1)|_=>epochs},
      promptPath'=if(e==Prompt)nodePaths.get(fileNode(cur)) else promptPath,
      generation'=if(e==Rebuild)generation+1 else generation,
      pid'=pid,
      actions'=match e{|Press(p)=>if(allow)actions.append(p.path)else actions|_=>actions},
      accepted'=allow,wasAllowed'=allow,previousActions'=actions.length(),previousFocus'=focus,reloaded'=e==Reload
    }
  }
  val EVENTS=Set(Tab(false),Tab(true),Arrow(1),Arrow(-1),Prompt,Cancel,Edit("path"),Edit("filter"),Layout("list"),Layout("grid"),Sidebar,Home,Unmap,MapWindow,Rebuild,Reload)
    .union(Set(0,1,2,3,4,5,6,7,8,9,10).fold(Set(),(out,n)=>out.union(Set(Hide(n),Disable(n)))))
    .union(Set(0,1,2,3,4,8,9,10).fold(Set(),(out,n)=>out.union(Set(0,1,2,3,4,5,6,7).map(p=>Rebind({node:n,path:p})))))
    .union(Set(0,1,2,3,4,5,6,7,8,9,10).fold(Set(),(out,n)=>out.union(Set(0,epochs.get(n),if(epochs.get(n)>0)epochs.get(n)-1 else 0,epochs.get(n)+1).fold(Set(),(gs,g)=>gs.union(Set(0,1,2,3,4,5,6,7,nodePath(n)).map(p=>Press({node:n,generation:g,path:p})))))))
  action step={nondet e=EVENTS.oneOf();fire(e)}
}
