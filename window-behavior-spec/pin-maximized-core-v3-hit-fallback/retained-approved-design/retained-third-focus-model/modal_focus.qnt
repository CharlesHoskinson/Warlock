module modal_focus {
 type Identity={session:int,root:int,child:int,nested:int,graph:int,other:int}
 type Guards={sessionUnlocked:bool,exclusiveLayerAllows:bool,seatGrabAllows:bool,rootFocusAllows:bool,leafFocusAllows:bool,
   visible:bool,fullscreenAllows:bool,graphValid:bool,otherFocusAllows:bool}
 type Result={core:bool,seat:bool,ok:bool}
 type Event=Request(Identity)|UnrelatedRequest(Identity)|OtherReuse|OtherNoFocus|Resolve|Commit(Result)|FollowUp|GuardChange(int)|CloseLeaf|ReuseLeaf|GraphReplace|SessionReplace|HideNested|ClearNested|ClearChild|HideChild|KeyboardLoss|NoWarps|NoFollowMouse|Idle
 pure val identity={session:1,root:1,child:1,nested:1,graph:1,other:1}
 pure val allowed={sessionUnlocked:true,exclusiveLayerAllows:true,seatGrabAllows:true,rootFocusAllows:true,leafFocusAllows:true,
   visible:true,fullscreenAllows:true,graphValid:true,otherFocusAllows:true}
 type State={current:Identity,captured:Identity,g:Guards,before:Guards,phase:int,nestedLive:bool,nestedVisible:bool,childLive:bool,childVisible:bool,keyboard:bool,partial:bool,lastFollowUp:bool,
   requestOwner:int,leaf:int,focus:int,seat:int,cursor:int,forced:int,monitor:int,refused:bool,accepted:bool,warps:bool,follow:bool}
 var s:State
 def validFor(w:int):bool=all{s.g.sessionUnlocked,s.g.exclusiveLayerAllows,s.g.seatGrabAllows,s.g.visible,s.g.fullscreenAllows,
   if(w==5)s.g.otherFocusAllows else s.g.rootFocusAllows and s.g.leafFocusAllows and s.g.graphValid}
 val valid=validFor(s.requestOwner)
 val chosen=if(s.requestOwner==5)5 else if(not(s.childLive) or not(s.childVisible))1 else if(s.nestedLive and s.nestedVisible)3 else 2
 val current=s.current==s.captured and s.g==s.before and valid and chosen==s.leaf
 action init=s'={current:identity,captured:identity,g:allowed,before:allowed,phase:0,nestedLive:true,nestedVisible:true,childLive:true,childVisible:true,keyboard:true,partial:false,lastFollowUp:false,
   requestOwner:1,leaf:0,focus:5,seat:5,cursor:5,forced:0,monitor:5,refused:false,accepted:false,warps:true,follow:true}
 action fire(e:Event):bool={
   val b={...s,lastFollowUp:false}
   val refuse={...b,phase:0,refused:true,accepted:false}
   s'=match e {
    |Request(i)=>if(s.phase==0 and i==s.current and validFor(1)){...b,phase:1,requestOwner:1,captured:i,before:s.g,refused:false,accepted:false,partial:false}else refuse
    |UnrelatedRequest(i)=>if(s.phase==0 and i==s.current and validFor(5)){...b,phase:1,requestOwner:5,captured:i,before:s.g,refused:false,accepted:false,partial:false}else refuse
    |OtherReuse=>{...b,current:{...s.current,other:s.current.other+1},accepted:false}
    |OtherNoFocus=>{...b,g:{...s.g,otherFocusAllows:false},accepted:false}
    |Resolve=>if(s.phase==1 and s.captured==s.current and s.g==s.before and valid){...b,phase:2,leaf:chosen}else refuse
    |Commit(r)=>if(s.phase==2 and current){
      val core=if(r.core)s.leaf else s.focus
      val seat=if(r.seat and s.keyboard)s.leaf else s.seat
      val accepted=r.ok and r.core and r.seat and s.keyboard and core==s.leaf and seat==s.leaf
      {...b,phase:if(accepted)3 else 0,focus:core,seat:seat,accepted:accepted,refused:not(accepted),partial:not(accepted)}
     }else refuse
    |FollowUp=>if(s.phase==3 and current and s.keyboard and s.accepted and s.focus==s.leaf and s.seat==s.leaf){...b,phase:0,lastFollowUp:true,
       cursor:if(s.warps)s.leaf else s.cursor,forced:if(s.follow)s.leaf else 0,monitor:s.leaf}else refuse
    |GuardChange(n)=>{...b,g:if(n==1){...s.g,sessionUnlocked:false}else if(n==2){...s.g,exclusiveLayerAllows:false}else if(n==3){...s.g,seatGrabAllows:false}
      else if(n==4){...s.g,rootFocusAllows:false}else if(n==5){...s.g,leafFocusAllows:false}else if(n==6){...s.g,visible:false}
      else if(n==7){...s.g,fullscreenAllows:false}else {...s.g,graphValid:false},accepted:false}
    |CloseLeaf=>{...b,nestedLive:false,accepted:false,current:{...s.current,nested:s.current.nested+1}}
    |ReuseLeaf=>{...b,nestedLive:true,accepted:false,current:{...s.current,nested:s.current.nested+1}}
    |GraphReplace=>{...b,accepted:false,current:{...s.current,graph:s.current.graph+1}}
    |SessionReplace=>{...b,accepted:false,current:{...s.current,session:s.current.session+1}}
    |HideNested=>{...b,nestedVisible:false,accepted:false}
    |ClearNested=>{...b,nestedLive:false,accepted:false}
    |ClearChild=>{...b,childLive:false,accepted:false,current:{...s.current,child:s.current.child+1}}
    |HideChild=>{...b,childVisible:false,accepted:false}
    |KeyboardLoss=>{...b,keyboard:false,accepted:false}
    |NoWarps=>{...b,warps:false}
    |NoFollowMouse=>{...b,follow:false}
    |Idle=>b
   }
 }
 val allProps=all {s.accepted implies s.focus==s.leaf and s.seat==s.leaf and s.keyboard and current,
   s.accepted implies not(s.partial) and not(s.refused),
   s.lastFollowUp implies s.accepted and s.keyboard and current and s.focus==s.leaf and s.seat==s.leaf and s.monitor==s.leaf,
   s.partial implies not(s.accepted)}
 action step={nondet n=1.to(8).oneOf();nondet e=Set(Request(s.current),Request(identity),UnrelatedRequest(s.current),OtherReuse,OtherNoFocus,Resolve,Commit({core:true,seat:true,ok:true}),Commit({core:true,seat:false,ok:true}),Commit({core:false,seat:true,ok:false}),FollowUp,GuardChange(n),CloseLeaf,ReuseLeaf,GraphReplace,SessionReplace,HideNested,ClearNested,ClearChild,HideChild,KeyboardLoss,NoWarps,NoFollowMouse,Idle).oneOf();fire(e)}
 action check(p:bool):bool=all{assert(p),s'=s}
 action focusOwner=fire(Request(s.current)).then(fire(Resolve)).then(fire(Commit({core:true,seat:true,ok:true}))).then(fire(FollowUp))
}
