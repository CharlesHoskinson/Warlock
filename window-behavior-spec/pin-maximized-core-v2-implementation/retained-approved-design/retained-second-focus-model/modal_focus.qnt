module modal_focus {
 type Identity={session:int,root:int,child:int,nested:int,graph:int,other:int}
 type Guards={sessionUnlocked:bool,exclusiveLayerAllows:bool,seatGrabAllows:bool,rootFocusAllows:bool,leafFocusAllows:bool,
   visible:bool,fullscreenAllows:bool,graphValid:bool,otherFocusAllows:bool}
 type Event=Request(Identity)|UnrelatedRequest(Identity)|OtherReuse|OtherNoFocus|Resolve|Commit|FollowUp|GuardChange(int)|CloseLeaf|ReuseLeaf|GraphReplace|SessionReplace|HideNested|ClearNested|NoWarps|NoFollowMouse|Idle
 pure val identity={session:1,root:1,child:1,nested:1,graph:1,other:1}
 pure val allowed={sessionUnlocked:true,exclusiveLayerAllows:true,seatGrabAllows:true,rootFocusAllows:true,leafFocusAllows:true,
   visible:true,fullscreenAllows:true,graphValid:true,otherFocusAllows:true}
 type State={current:Identity,captured:Identity,g:Guards,before:Guards,phase:int,nestedLive:bool,nestedVisible:bool,
   requestOwner:int,leaf:int,focus:int,seat:int,cursor:int,forced:int,monitor:int,refused:bool,accepted:bool,warps:bool,follow:bool}
 var s:State
 def validFor(w:int):bool=all{s.g.sessionUnlocked,s.g.exclusiveLayerAllows,s.g.seatGrabAllows,s.g.visible,s.g.fullscreenAllows,
   if(w==5)s.g.otherFocusAllows else s.g.rootFocusAllows and s.g.leafFocusAllows and s.g.graphValid}
 val valid=validFor(s.requestOwner)
 val chosen=if(s.requestOwner==5)5 else if(s.nestedLive and s.nestedVisible)3 else 2
 val current=s.current==s.captured and s.g==s.before and valid and chosen==s.leaf
 action init=s'={current:identity,captured:identity,g:allowed,before:allowed,phase:0,nestedLive:true,nestedVisible:true,
   requestOwner:1,leaf:0,focus:5,seat:5,cursor:5,forced:0,monitor:5,refused:false,accepted:false,warps:true,follow:true}
 action fire(e:Event):bool={
   val refuse={...s,phase:0,refused:true,accepted:false}
   s'=match e {
    |Request(i)=>if(s.phase==0 and i==s.current and validFor(1)){...s,phase:1,requestOwner:1,captured:i,before:s.g,refused:false,accepted:false}else refuse
    |UnrelatedRequest(i)=>if(s.phase==0 and i==s.current and validFor(5)){...s,phase:1,requestOwner:5,captured:i,before:s.g,refused:false,accepted:false}else refuse
    |OtherReuse=>{...s,current:{...s.current,other:s.current.other+1},accepted:false}
    |OtherNoFocus=>{...s,g:{...s.g,otherFocusAllows:false},accepted:false}
    |Resolve=>if(s.phase==1 and s.captured==s.current and s.g==s.before and valid){...s,phase:2,leaf:chosen}else refuse
    |Commit=>if(s.phase==2 and current){...s,phase:3,focus:s.leaf,seat:s.leaf,accepted:true}else refuse
    |FollowUp=>if(s.phase==3 and current and s.accepted and s.focus==s.leaf and s.seat==s.leaf){...s,phase:0,
       cursor:if(s.warps)s.leaf else s.cursor,forced:if(s.follow)s.leaf else 0,monitor:s.leaf}else refuse
    |GuardChange(n)=>{...s,g:if(n==1){...s.g,sessionUnlocked:false}else if(n==2){...s.g,exclusiveLayerAllows:false}else if(n==3){...s.g,seatGrabAllows:false}
      else if(n==4){...s.g,rootFocusAllows:false}else if(n==5){...s.g,leafFocusAllows:false}else if(n==6){...s.g,visible:false}
      else if(n==7){...s.g,fullscreenAllows:false}else {...s.g,graphValid:false},accepted:false}
    |CloseLeaf=>{...s,nestedLive:false,accepted:false,current:{...s.current,nested:s.current.nested+1}}
    |ReuseLeaf=>{...s,nestedLive:true,accepted:false,current:{...s.current,nested:s.current.nested+1}}
    |GraphReplace=>{...s,accepted:false,current:{...s.current,graph:s.current.graph+1}}
    |SessionReplace=>{...s,accepted:false,current:{...s.current,session:s.current.session+1}}
    |HideNested=>{...s,nestedVisible:false,accepted:false}
    |ClearNested=>{...s,nestedLive:false,accepted:false}
    |NoWarps=>{...s,warps:false}
    |NoFollowMouse=>{...s,follow:false}
    |Idle=>s
   }
 }
 val allProps=all {s.accepted implies s.focus==s.leaf and s.seat==s.leaf and s.leaf!=1,
   s.cursor!=1,s.forced!=1,s.monitor!=1,s.focus!=1,s.seat!=1}
 action step={nondet n=1.to(8).oneOf();nondet e=Set(Request(s.current),Request(identity),UnrelatedRequest(s.current),OtherReuse,OtherNoFocus,Resolve,Commit,FollowUp,GuardChange(n),CloseLeaf,ReuseLeaf,GraphReplace,SessionReplace,HideNested,ClearNested,NoWarps,NoFollowMouse,Idle).oneOf();fire(e)}
 action check(p:bool):bool=all{assert(p),s'=s}
 action focusOwner=fire(Request(s.current)).then(fire(Resolve)).then(fire(Commit)).then(fire(FollowUp))
}
