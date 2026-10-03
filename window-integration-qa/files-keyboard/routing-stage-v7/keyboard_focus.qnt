/** Required interaction contract, written independently of QML dispatch.
 * Paths are opaque sandbox identities; file operation semantics are unchanged.
 * Native widget lifetime and reader delivery need concrete replay evidence. */
module keyboard_focus {
  type Event = Tab(bool) | Arrow(int) | ShiftArrow(int) | Prompt | Cancel | Edit(str) | Layout(str)
    | Sidebar | Home | Unmap | MapWindow | Hide(int) | Disable(int) | Rebuild | Reload
    | DeferReload | Materialize | Focus(int) | KeyIntent | Rebind({node:int,path:int}) | Toggle({node:int, generation:int, path:int}) | Press({node:int, generation:int, path:int})
  var focus:int // 0 main,1 toolbar,2/8/9/10 independent files,3 sidebar,4 Home,5 input,6 Cancel,7 accept
  var rangeAnchor:int
  var rangeSelectionExpected:bool
  var expectedRange:Set[int]
  var selectionPath:int
  var selected:Set[int]
  var toggleAttempt:bool
  var previousSelected:Set[int]
  var arrowSelectionExpected:bool
  var navigationPath:int
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
  var savedFocus:int
  var savedPath:int
  var pendingFocus:bool
  var inputEpoch:int
  var savedInputEpoch:int
  var requestEpoch:int
  var savedRequestEpoch:int
  var materialized:bool
  var restoreAllowed:bool
  var reloaded:bool
  action init=all{focus'=0,cur'=0,rangeAnchor'=0,rangeSelectionExpected'=false,expectedRange'=Set(),selectionPath'=0,selected'=Set(),toggleAttempt'=false,previousSelected'=Set(),arrowSelectionExpected'=false,navigationPath'=0,layout'="list",editing'="none",prompt'=false,sidebar'=false,
    mapped'=true,nodePaths'=Map(0->0,1->1,2->0,3->3,4->4,5->5,6->6,7->7,8->1,9->2,10->3),epochs'=Map(0->0,1->0,2->0,3->0,4->0,5->0,6->0,7->0,8->0,9->0,10->0),promptPath'=0,hidden'=Set(),disabled'=Set(),generation'=0,pid'=667402,actions'=[],accepted'=false,
    wasAllowed'=false,previousActions'=0,previousFocus'=0,savedFocus'=0,savedPath'=0,pendingFocus'=false,inputEpoch'=0,savedInputEpoch'=0,requestEpoch'=0,savedRequestEpoch'=0,materialized'=false,restoreAllowed'=false,reloaded'=false}
  pure def clamp(n:int):int=if(n<0)0 else if(n>3)3 else n
  // Logical action identity is independent of the selected file for other scopes.
  pure def fileNode(index:int):int=if(index==0)2 else index+7
  def nodePath(n:int):int=if(n>=5 and n<=7)promptPath else nodePaths.get(n)
  val fieldsValid=focus>=0 and focus<=10 and cur>=0 and cur<=3 and pid==667402
  val modalTrap=prompt implies focus>=5 and focus<=7
  val refusedHasNoAction=(not(wasAllowed) implies actions.length()==previousActions)
  val reloadPreservesFocus=reloaded implies focus==previousFocus
  val delayedRestoreRespectsNewerIntent=(materialized and not(restoreAllowed)) implies focus==previousFocus
  val arrowSelectionAgrees=arrowSelectionExpected implies selected==Set(navigationPath) and nodePath(focus)==navigationPath
  val rangeSelectionAgrees=rangeSelectionExpected implies selected==expectedRange
  val refusedToggleKeepsSelection=toggleAttempt and not(wasAllowed) implies selected==previousSelected
  val allProps=refusedToggleKeepsSelection and rangeSelectionAgrees and arrowSelectionAgrees and fieldsValid and modalTrap and refusedHasNoAction and reloadPreservesFocus and delayedRestoreRespectsNewerIntent
  action fire(e:Event):bool={
    val allow=match e {|Press(p)=>mapped and p.node>=0 and p.node<=10 and (if(prompt)p.node>=5 and p.node<=7 else p.node<=4 or p.node>=8) and not(hidden.contains(p.node)) and not(disabled.contains(p.node)) and p.generation==epochs.get(p.node) and p.path==nodePath(p.node)|Toggle(p)=>mapped and not(prompt) and (p.node==2 or p.node>=8 and p.node<=10) and not(hidden.contains(p.node)) and not(disabled.contains(p.node)) and p.generation==epochs.get(p.node) and p.path==nodePath(p.node)|_=>false}
    // Reject incompatible commands in the transition, never rewrite generated events.
    val blocked=prompt and match e {|Sidebar=>true|Home=>true|Edit(_)=>true|Layout(_)=>true|Arrow(_)=>true|ShiftArrow(_)=>true|_=>false}
    val canRestore=mapped and (if(prompt)savedFocus>=5 and savedFocus<=7 else savedFocus<=4 or savedFocus>=8) and pendingFocus and inputEpoch==savedInputEpoch and requestEpoch==savedRequestEpoch and nodePath(savedFocus)==savedPath and not(hidden.contains(savedFocus)) and not(disabled.contains(savedFocus))
    val canFocus=match e{|Focus(n)=>mapped and n>=0 and n<=10 and (not(prompt) or n>=5 and n<=7) and not(hidden.contains(n)) and not(disabled.contains(n))|_=>false}
    val userIntent=match e{|Toggle(_)=>allow|Focus(_)=>canFocus|KeyIntent=>mapped|Tab(_)=>mapped|Arrow(_)=>mapped|ShiftArrow(_)=>mapped|Prompt=>mapped|Cancel=>mapped|Home=>mapped and not(blocked)|Sidebar=>mapped and not(blocked)|Edit(_)=>mapped and not(blocked)|_=>false}
    val nextFocus=if(blocked)focus else match e {
      |DeferReload=>if(prompt)5 else 0 |Materialize=>if(canRestore)savedFocus else focus |Focus(n)=>if(canFocus)n else focus
      |Prompt=>5 |Cancel=>0 |Edit(_)=>5 |Sidebar=>if(sidebar)0 else 3 |Home=>4
      |Tab(back)=>if(prompt){if(back){if(focus==5)7 else focus-1}else{if(focus==7)5 else focus+1}}else if(focus>=4)0 else focus+1
      |ShiftArrow(d)=>if(editing=="none" and not(prompt) and not(sidebar))fileNode(clamp(cur+d*(if(layout=="grid")2 else 1))) else focus
      |Toggle(_)=>if(allow)0 else focus
      |Arrow(d)=>if(editing=="none" and not(prompt) and not(sidebar))fileNode(clamp(cur+d*(if(layout=="grid")2 else 1))) else focus
      |_=>focus}
    val plainNavigation=match e{|Arrow(_)=>mapped and editing=="none" and not(prompt) and not(sidebar)|_=>false}
    val nextCur=match e{|ShiftArrow(d)=>clamp(cur+d*(if(layout=="grid")2 else 1))|Toggle(p)=>if(allow){if(p.node==2)0 else p.node-7}else cur|Arrow(d)=>clamp(cur+d*(if(layout=="grid")2 else 1))|Focus(n)=>if(canFocus and (n==2 or n>=8)){if(n==2)0 else n-7}else cur|_=>cur}
    val filterNavigation=match e{|Arrow(_)=>mapped and editing=="filter" and not(prompt) and not(sidebar)|ShiftArrow(_)=>mapped and editing=="filter" and not(prompt) and not(sidebar)|_=>false}
    val rangeNavigation=match e{|ShiftArrow(_)=>mapped and editing=="none" and not(prompt) and not(sidebar)|_=>false}
    val rangePaths=Set(0,1,2,3).filter(i=>i>=(if(rangeAnchor<nextCur)rangeAnchor else nextCur) and i<=(if(rangeAnchor>nextCur)rangeAnchor else nextCur)).map(i=>nodePath(fileNode(i)))
    val nextSelection=match e{|Toggle(p)=>if(allow){if(selected.contains(p.path))selected.exclude(Set(p.path))else selected.union(Set(p.path))}else selected|_=>if(rangeNavigation)rangePaths else if(plainNavigation or filterNavigation)Set(nodePath(fileNode(nextCur)))else selected}
    all{
      rangeAnchor'=if(plainNavigation or filterNavigation)nextCur else rangeAnchor,rangeSelectionExpected'=rangeNavigation,expectedRange'=rangePaths,
      selectionPath'=if(nextSelection.size()==1)nextSelection.fold(0,(out,path)=>path)else selectionPath,
      selected'=nextSelection,toggleAttempt'=match e{|Toggle(_)=>true|_=>false},previousSelected'=selected,arrowSelectionExpected'=plainNavigation,navigationPath'=nodePath(fileNode(nextCur)),
      focus'=nextFocus,
      cur'=match e {|ShiftArrow(_)=>if((editing=="none" or editing=="filter") and not(prompt) and not(sidebar))nextCur else cur|Toggle(_)=>nextCur|Arrow(_)=>if((editing=="none" or editing=="filter") and not(prompt) and not(sidebar))nextCur else cur|Focus(_)=>nextCur|_=>cur},
      layout'=if(blocked)layout else match e{|Layout(s)=>s|_=>layout},
      editing'=if(blocked)editing else match e{|Edit(s)=>s|Prompt=>"prompt"|Cancel=>"none"|Home=>"none"|_=>editing},
      prompt'=if(e==Prompt)true else if(e==Cancel)false else prompt,
      sidebar'=if(blocked)sidebar else if(e==Sidebar)not(sidebar)else if(e==Cancel or e==Home)false else sidebar,
      mapped'=if(e==Unmap)false else if(e==MapWindow)true else mapped,
      hidden'=match e{|Hide(n)=>hidden.union(Set(n))|_=>hidden},
      disabled'=match e{|Disable(n)=>disabled.union(Set(n))|_=>disabled},
      nodePaths'=match e {|Rebind(p)=>nodePaths.set(p.node,p.path)|_=>nodePaths},
      epochs'=match e {|Rebind(p)=>epochs.set(p.node,epochs.get(p.node)+1)|Rebuild=>epochs.keys().mapBy(n=>epochs.get(n)+1)|_=>epochs},
      promptPath'=if(e==Prompt and selected.size()==1)selectionPath else if(e==Prompt)nodePaths.get(fileNode(cur)) else promptPath,
      generation'=if(e==Rebuild)generation+1 else generation,
      pid'=pid,
      savedFocus'=if(e==DeferReload)focus else savedFocus,
      savedPath'=if(e==DeferReload)nodePath(focus)else savedPath,
      pendingFocus'=if(e==DeferReload)true else if(e==Materialize or e==Reload or userIntent)false else pendingFocus,
      inputEpoch'=if(userIntent)inputEpoch+1 else inputEpoch,
      savedInputEpoch'=if(e==DeferReload)inputEpoch else savedInputEpoch,
      requestEpoch'=if(e==Reload or e==DeferReload)requestEpoch+1 else requestEpoch,
      savedRequestEpoch'=if(e==DeferReload)requestEpoch+1 else savedRequestEpoch,
      materialized'=e==Materialize,restoreAllowed'=(e==Materialize and canRestore),
      actions'=match e{|Press(p)=>if(allow)actions.append(p.path)else actions|_=>actions},
      accepted'=allow,wasAllowed'=allow,previousActions'=actions.length(),previousFocus'=focus,reloaded'=e==Reload
    }
  }
  val EVENTS=Set(Tab(false),Tab(true),Arrow(1),Arrow(-1),ShiftArrow(1),ShiftArrow(-1),Prompt,Cancel,Edit("path"),Edit("filter"),Layout("list"),Layout("grid"),Sidebar,Home,Unmap,MapWindow,Rebuild,Reload,DeferReload,Materialize,KeyIntent)
    .union(Set(0,1,2,3,4,5,6,7,8,9,10).map(n=>Focus(n)))
    .union(Set(0,1,2,3,4,5,6,7,8,9,10).fold(Set(),(out,n)=>out.union(Set(Hide(n),Disable(n)))))
    .union(Set(0,1,2,3,4,8,9,10).fold(Set(),(out,n)=>out.union(Set(0,1,2,3,4,5,6,7).map(p=>Rebind({node:n,path:p})))))
    .union(Set(0,1,2,3,4,5,6,7,8,9,10).fold(Set(),(out,n)=>out.union(Set(0,epochs.get(n),if(epochs.get(n)>0)epochs.get(n)-1 else 0,epochs.get(n)+1).fold(Set(),(gs,g)=>gs.union(Set(0,1,2,3,4,5,6,7,nodePath(n)).fold(Set(),(out,p)=>out.union(Set(Press({node:n,generation:g,path:p}),Toggle({node:n,generation:g,path:p})))))))))
  action step={nondet e=EVENTS.oneOf();fire(e)}
}
