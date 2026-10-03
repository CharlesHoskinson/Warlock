/** Required interaction contract, written independently of QML dispatch.
 * Paths are opaque sandbox identities; file operation semantics are unchanged.
 * Native widget lifetime and reader delivery need concrete replay evidence. */
module keyboard_focus {
  type Event = Tab(bool) | Arrow(int) | Prompt | Cancel | Edit(str) | Layout(str)
    | Sidebar | Home | Hide(int) | Disable(int) | Rebuild | Reload
    | Press({node:int, generation:int, path:int})
  var focus:int // 0 main,1 toolbar,2 file,3 sidebar,4 Home,5 input,6 Cancel,7 accept
  var cur:int
  var layout:str
  var editing:str
  var prompt:bool
  var sidebar:bool
  var mapped:bool
  var hidden:Set[int]
  var disabled:Set[int]
  var generation:int
  var pid:int
  var actions:List[int]
  var accepted:bool
  var wasAllowed:bool
  var previousActions:int
  var previousFocus:int
  var reloaded:bool
  action init=all{focus'=0,cur'=0,layout'="list",editing'="none",prompt'=false,sidebar'=false,
    mapped'=true,hidden'=Set(),disabled'=Set(),generation'=0,pid'=667402,actions'=[],accepted'=false,
    wasAllowed'=false,previousActions'=0,previousFocus'=0,reloaded'=false}
  pure def clamp(n:int):int=if(n<0)0 else if(n>3)3 else n
  val fieldsValid=focus>=0 and focus<=7 and cur>=0 and cur<=3 and pid==667402
  val modalTrap=prompt implies focus>=5 and focus<=7
  val refusedHasNoAction=(not(wasAllowed) implies actions.length()==previousActions)
  val reloadPreservesFocus=reloaded implies focus==previousFocus
  val allProps=fieldsValid and modalTrap and refusedHasNoAction and reloadPreservesFocus
  action fire(e:Event):bool={
    val allow=match e {|Press(p)=>mapped and (not(prompt) or p.node>=5) and not(hidden.contains(p.node)) and not(disabled.contains(p.node)) and p.generation==generation and p.path==cur|_=>false}
    val nextFocus=match e {
      |Prompt=>5 |Cancel=>0 |Edit(_)=>5 |Sidebar=>if(sidebar)0 else 3 |Home=>4
      |Tab(back)=>if(prompt){if(back){if(focus==5)7 else focus-1}else{if(focus==7)5 else focus+1}}else if(focus>=4)0 else focus+1
      |Arrow(_)=>if(editing=="none" and not(prompt) and not(sidebar))2 else focus
      |_=>focus}
    all{
      focus'=nextFocus,
      cur'=match e {|Arrow(d)=>if((editing=="none" or editing=="filter") and not(prompt) and not(sidebar))clamp(cur+d*(if(layout=="grid")2 else 1))else cur|_=>cur},
      layout'=match e{|Layout(s)=>s|_=>layout},
      editing'=match e{|Edit(s)=>s|Prompt=>"prompt"|Cancel=>"none"|Home=>"none"|_=>editing},
      prompt'=if(e==Prompt)true else if(e==Cancel)false else prompt,
      sidebar'=if(e==Sidebar)not(sidebar)else if(e==Cancel or e==Home)false else sidebar,
      mapped'=mapped,
      hidden'=match e{|Hide(n)=>hidden.union(Set(n))|_=>hidden},
      disabled'=match e{|Disable(n)=>disabled.union(Set(n))|_=>disabled},
      generation'=if(e==Rebuild)generation+1 else generation,
      pid'=pid,
      actions'=match e{|Press(p)=>if(allow)actions.append(p.path)else actions|_=>actions},
      accepted'=allow,wasAllowed'=allow,previousActions'=actions.length(),previousFocus'=focus,reloaded'=e==Reload
    }
  }
  val EVENTS=Set(Tab(false),Tab(true),Arrow(1),Arrow(-1),Prompt,Cancel,Edit("path"),Edit("filter"),Layout("list"),Layout("grid"),Sidebar,Home,Rebuild,Reload)
    .union(Set(0,1,2,3,4).fold(Set(),(out,n)=>out.union(Set(Hide(n),Disable(n)))))
    .union(Set(0,1,2,3,4).fold(Set(),(out,n)=>out.union(Set(0,1,2).fold(Set(),(gs,g)=>gs.union(Set(0,1,2,3).map(p=>Press({node:n,generation:g,path:p})))))))
  action step={nondet e=EVENTS.oneOf();if(prompt)fire(if(e==Reload or e==Cancel or e==Tab(true) or e==Tab(false))e else Tab(false))else fire(e)}
}
