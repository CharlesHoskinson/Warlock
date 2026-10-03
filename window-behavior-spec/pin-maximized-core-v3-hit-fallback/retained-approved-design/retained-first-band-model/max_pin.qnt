module max_pin {
 type Rect={x:int,y:int,w:int,h:int}
 type Restore={known:bool,floating:bool,rect:Rect,layout:int,target:int,generation:int}
 type Win={live:bool,visible:bool,special:bool,floating:bool,pinned:bool,maxOrigin:bool,mode:int,client:int,
   rect:Rect,workspace:int,output:int,generation:int,restore:Restore}
 type Identity={owner:int,address:int,stable:int,pid:int,session:int,compositor:int,start:int,epoch:int,incarnation:int,generation:int,source:int}
 type Result={ok:bool,mutated:bool}
 type Event=Begin(Identity)|Pin(Result)|Raise(bool)|Finish|ExitMax(int)|EnterMax(int)|Exclusive(int)|UnknownMode(int)
  |Close(int)|Reuse(int)|Hide(int)|Show(int)|Transfer({owner:int,workspace:int,output:int})|Focus(int)|Reload|SourceReplace|CapabilityLoss
  |ForgetRestore(int)|GeometryChange(int)|RestoreChange(int)|ParentMove|ChildOwnPin|Reduce|Adopt|Idle
 pure val owners=Set(1,2,3,4,5)
 pure def rect(n:int):Rect={x:n*10,y:n*10,w:200+n,h:100+n}
 pure def maxRect(out:int):Rect={x:(out-1)*1000,y:20,w:980,h:680}
 pure def original(w:int):Restore={known:true,floating:w!=1,rect:rect(w),layout:w+10,target:w+100,generation:1}
 pure def win(w:int):Win={live:true,visible:true,special:false,floating:w!=1,pinned:false,maxOrigin:false,
   mode:if(w<=2)1 else 0,client:if(w<=2)1 else 0,rect:if(w<=2)maxRect(1)else rect(w),workspace:1,output:1,generation:1,restore:original(w)}
 pure val oldToken={owner:1,address:101,stable:1,pid:11,session:1,compositor:20,start:30,epoch:1,incarnation:1,generation:1,source:1}
 type State={windows:int->Win,roots:List[int],focus:int,epoch:int,incarnation:int,source:int,capability:bool,reduced:bool,
   phase:int,token:Identity,before:int->Win,beforeFocus:int,desired:bool,refused:bool,partial:bool,complete:bool,calls:int,
   lastNative:bool,lastBefore:int->Win,lastFocus:int,lastOwner:int}
 var s:State
 def token(w:int):Identity={...oldToken,owner:w,address:100+w,stable:w,pid:10+w,generation:s.windows.get(w).generation,
   epoch:s.epoch,incarnation:s.incarnation,source:s.source}
 def eligible(w:int):bool={val v=s.windows.get(w);v.live and v.visible and not(v.special) and v.restore.known and v.restore.generation==v.generation and v.restore.layout>0 and v.restore.target>0 and v.restore.rect.w>0 and v.restore.rect.h>0 and (v.mode==0 or v.mode==1) and (v.client==0 or v.client==1)}
 def supported(w:int):bool=eligible(w) and (s.windows.get(w).mode==1 or s.windows.get(w).maxOrigin)
 def exact(i:Identity):bool=owners.contains(i.owner) and i==token(i.owner)
 def guardedWindow(w:int):Win=if(s.phase>=2){...s.before.get(w),pinned:s.desired,maxOrigin:if(s.desired)true else false}else s.before.get(w)
 val current=s.phase>0 and exact(s.token) and s.capability and eligible(s.token.owner) and s.focus==s.beforeFocus and
   s.windows.get(s.token.owner)==guardedWindow(s.token.owner) and
   owners.exclude(Set(s.token.owner)).forall(w=>s.windows.get(w)==s.before.get(w))
 pure def family(w:int):List[int]=if(w==1)List(1,3,4)else List(w)
 def attached(w:int):bool={val v=s.windows.get(w); val p=s.windows.get(1); v.live and v.visible and not(v.special) and v.workspace==p.workspace and v.output==p.output}
 def effective(w:int):bool={val v=s.windows.get(w);v.live and v.visible and not(v.special) and
   (v.pinned or ((w==3 or w==4) and attached(w) and attached(3) and s.windows.get(1).pinned and attached(1)))}
 val visible=owners.filter(w=>{val v=s.windows.get(w);v.live and v.visible and not(v.special)})
 val familyOrder=s.roots.foldl(List(),(acc,r)=>acc.concat(family(r))).select(w=>visible.contains(w))
 val renderOrder=familyOrder.select(w=>not(effective(w))).concat(familyOrder.select(w=>effective(w)))
 val inputOrder=renderOrder.select(w=>not((w==1 and attached(3)) or (w==3 and attached(4))))
 val pinProjection=owners.forall(w=>s.windows.get(w)==(if(w==s.lastOwner){...s.lastBefore.get(w),pinned:s.windows.get(w).pinned,maxOrigin:s.windows.get(w).maxOrigin}else s.lastBefore.get(w)))
 action init=s'={windows:owners.mapBy(win),roots:List(5,2,1),focus:5,epoch:1,incarnation:1,source:1,capability:true,reduced:false,
   phase:0,token:oldToken,before:owners.mapBy(win),beforeFocus:5,desired:false,refused:false,partial:false,complete:false,calls:0,
   lastNative:false,lastBefore:owners.mapBy(win),lastFocus:5,lastOwner:1}
 action fire(e:Event):bool={
  val b={...s,lastNative:false,complete:false}
  val refusal={...b,phase:0,refused:true,partial:s.partial or s.calls>0}
  s'=match e {
   |Begin(i)=>if(s.phase==0 and exact(i) and supported(i.owner) and s.capability){...b,phase:1,token:i,before:s.windows,
      beforeFocus:s.focus,desired:not(s.windows.get(i.owner).pinned),refused:false,partial:false,calls:0}else {...b,refused:true}
   |Pin(r)=>if(current and s.phase==1){
     val v=s.windows.get(s.token.owner)
     val result=if(r.mutated){...v,pinned:s.desired,maxOrigin:s.desired}else v
     val ok=r.ok and result.pinned==s.desired
     {...b,windows:s.windows.put(s.token.owner,result),phase:if(ok)2 else 0,refused:not(ok),partial:not(ok),calls:s.calls+1,
       lastNative:true,lastBefore:s.windows,lastFocus:s.focus,lastOwner:s.token.owner}
    }else refusal
   |Raise(ok)=>if(current and s.phase==2 and s.desired and ok){...b,phase:3,roots:s.roots.select(w=>w!=s.token.owner).append(s.token.owner),
     calls:s.calls+1,lastNative:true,lastBefore:s.windows,lastFocus:s.focus,lastOwner:s.token.owner}else refusal
   |Finish=>if(current and (s.phase==3 or (s.phase==2 and not(s.desired)))){...b,phase:0,complete:true,partial:false,refused:false}else refusal
   |ExitMax(w)=>{val v=s.windows.get(w);if(v.live and v.mode==1 and v.restore.known){...b,windows:s.windows.put(w,{...v,mode:0,client:0,
       floating:v.restore.floating,rect:v.restore.rect})}else b}
   |EnterMax(w)=>{val v=s.windows.get(w);if(v.live and v.mode==0){...b,windows:s.windows.put(w,{...v,mode:1,client:1,rect:maxRect(v.output),
      restore:{known:true,floating:v.floating,rect:v.rect,layout:v.restore.layout,target:v.restore.target,generation:v.generation}})}else b}
   |Exclusive(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),mode:2,client:2})}
   |UnknownMode(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),mode:3})}
   |Close(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),live:false,visible:false,pinned:false,maxOrigin:false})}
   |Reuse(w)=>{...b,windows:s.windows.put(w,{...win(w),generation:s.windows.get(w).generation+1,restore:{...original(w),generation:s.windows.get(w).generation+1}})}
   |Hide(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),visible:false})}
   |Show(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),visible:true})}
   |Transfer(p)=>{val v=s.windows.get(p.owner);{...b,windows:s.windows.put(p.owner,{...v,workspace:p.workspace,output:p.output,
       rect:if(v.mode==1)maxRect(p.output)else v.rect})}}
   |Focus(w)=>{...b,focus:if(w==1 and attached(3)) {if(attached(4))4 else 3}else if(w==3 and attached(4))4 else w}
   |Reload=>{...b,epoch:s.epoch+1,incarnation:s.incarnation+1,phase:0}
   |SourceReplace=>{...b,source:s.source+1}
   |CapabilityLoss=>{...b,capability:false}
   |ForgetRestore(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),restore:{...s.windows.get(w).restore,known:false}})}
   |GeometryChange(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),rect:rect(w+10)})}
   |RestoreChange(w)=>{...b,windows:s.windows.put(w,{...s.windows.get(w),restore:{...s.windows.get(w).restore,target:999}})}
   |ParentMove=>{...b,windows:s.windows.put(3,{...s.windows.get(3),workspace:2})}
   |ChildOwnPin=>{...b,windows:s.windows.put(3,{...s.windows.get(3),pinned:not(s.windows.get(3).pinned)})}
   |Reduce=>{...b,reduced:true}
   |Adopt=>b
   |Idle=>b
  }
 }
 val allProps=all {
   s.lastNative implies pinProjection and s.focus==s.lastFocus,
   s.complete implies s.phase==0 and not(s.refused) and not(s.partial) and exact(s.token) and eligible(s.token.owner),
   s.complete implies s.windows.get(s.token.owner).pinned==s.desired,
   renderOrder.indices().map(i=>renderOrder.nth(i))==visible and renderOrder.length()==visible.size(),
   inputOrder.indices().map(i=>inputOrder.nth(i)).subseteq(visible),
   s.windows.get(1).pinned and attached(1) and attached(3) implies effective(3),
   s.windows.get(1).pinned and attached(1) and attached(3) and attached(4) implies effective(4),
   owners.forall(w=>s.windows.get(w).rect.w>0 and s.windows.get(w).rect.h>0)
 }
 action step={nondet w=owners.oneOf();nondet e=Set(Begin(token(w)),Begin({...token(w),generation:0}),Pin({ok:true,mutated:true}),Pin({ok:false,mutated:true}),Pin({ok:false,mutated:false}),
   Raise(true),Raise(false),Finish,ExitMax(w),EnterMax(w),Exclusive(w),UnknownMode(w),Close(w),Reuse(w),Hide(w),Show(w),Focus(w),Transfer({owner:w,workspace:2,output:2}),
   Reload,SourceReplace,CapabilityLoss,ForgetRestore(w),GeometryChange(w),RestoreChange(w),ParentMove,ChildOwnPin,Reduce,Adopt,Idle).oneOf();fire(e)}
 action check(p:bool):bool=all{assert(p),s'=s}
 action pin(w:int):bool=fire(Begin(token(w))).then(fire(Pin({ok:true,mutated:true}))).then(fire(Raise(true))).then(fire(Finish))
 action unpin(w:int):bool=fire(Begin(token(w))).then(fire(Pin({ok:true,mutated:true}))).then(fire(Finish))
 action validStep={nondet w=Set(1,2).oneOf();if(s.windows.get(w).mode==0)fire(EnterMax(w))else if(s.windows.get(w).pinned)unpin(w)else pin(w)}
}
