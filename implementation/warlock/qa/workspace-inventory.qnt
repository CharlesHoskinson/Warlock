module workspaceInventory {
  type State={binding:int,geometry:int,expected:int,inventory:int,owner:int,listed:Set[int],active:int,selected:int,open:bool,effects:int}
  var s:State
  action init = s'={binding:1,geometry:0,expected:0,inventory:0,owner:0,listed:Set(),active:0,selected:0,open:false,effects:0}
  action request=all{s.binding==1,s.expected==0,s.geometry<2,s'={...s,expected:s.geometry+1}}
  action current=all{s.binding==1,s.expected>0,s'={...s,geometry:s.expected,inventory:s.expected,owner:s.binding,listed:if(s.expected==1) Set(1,2) else Set(1),active:if(s.expected==1) 2 else 1,selected:if(s.expected==2) 0 else s.selected,expected:0}}
  action foreign=all{s.expected>0,s'=s}
  action malformed=all{s.expected>0,s'=s}
  action show=all{s.inventory==s.geometry,s.owner==s.binding,s.inventory>0,s'={...s,open:true}}
  action browseEmpty=all{s.open,s.listed.contains(2),s'={...s,selected:2}}
  action dismiss=all{s.open,s'={...s,open:false,selected:0}}
  action replace=all{s.binding==1,s'={...s,binding:2,geometry:0,expected:0,inventory:0,owner:0,listed:Set(),active:0,selected:0,open:false}}
  action step=any{request,current,foreign,malformed,show,browseEmpty,dismiss,replace}
  val safety=s.effects==0 and (s.inventory>0 implies s.owner==s.binding and s.inventory==s.geometry and s.listed.contains(s.active)) and (s.selected>0 implies s.open and s.listed.contains(s.selected))
  val emptyWitness=s.open and s.selected==2
  val activeEmptyWitness=s.active==2
  val retiredWitness=s.geometry==2 and not(s.listed.contains(2))
  val replacementWitness=s.binding==2 and s.inventory==0
}
