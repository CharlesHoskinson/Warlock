module pin_popup_refined {
 val Roles=Set(1,2,3,4,5,6,7) // menu,row,popup,attached,proxy content,window,native root
 val NativeRoles=Set(4,5,6,7)
 val Limit=40
 type Witness={available:bool,g:int->int,epoch:int,nonce:int,owner:int,layout:int,nc:int->int}
 type State={live:Set[int],g:int->int,next:int,epoch:int,nonce:int,owner:int,layout:int,open:bool,visible:bool,enabled:bool,source:bool,refused:bool,context:bool,lexical:bool,popupOwner:bool,existingAttached:bool,attachedPopup:bool,attachedContent:bool,baseContent:bool,rowAncestry:bool,windowMatch:bool,nativeRoot:bool,nativeInput:bool,aliasContent:bool,nc:int->int,ncGood:Set[int],w:Witness,accepted:bool,pinWrites:int}
 type Event=Ready|Capture|Confirm|Destroy(int)|Recreate(int)|OldDestroyed({r:int,g:int})|AliasContent|Epoch|NewMenu|Cancel|OwnerChange|LayoutChange|Disable|Hide|SourceFault|ThreadFault|LoaderReset|ContextFault|LexicalFault|PopupOwnerFault|MissingAttached|AttachedPopupFault|AttachedContentFault|BaseAliasOnly|RowAncestryFault|WindowFault|NativeRootFault|NativeInputFault|CallerNonce|NativeContextPresent(int)|NativeContextAbsent(int)|NativeContextForeign(int)|NativeContextConflict(int)
 var s:State
 val empty={available:false,g:Roles.mapBy(r=>0),epoch:0,nonce:0,owner:0,layout:0,nc:NativeRoles.mapBy(r=>0)}
 action init=s'={live:Set(),g:Roles.mapBy(r=>0),next:1,epoch:1,nonce:1,owner:1,layout:1,open:false,visible:false,enabled:false,source:true,refused:false,context:true,lexical:true,popupOwner:true,existingAttached:true,attachedPopup:true,attachedContent:true,baseContent:true,rowAncestry:true,windowMatch:true,nativeRoot:true,nativeInput:true,aliasContent:false,nc:NativeRoles.mapBy(r=>0),ncGood:NativeRoles,w:empty,accepted:false,pinWrites:0}
 pure def eligible(a:State):bool=all{a.live==Roles,a.open,a.visible,a.enabled,a.source,not(a.refused),a.context,a.lexical,a.popupOwner,a.existingAttached,a.attachedPopup,a.attachedContent,a.baseContent,a.rowAncestry,a.windowMatch,a.nativeRoot,a.nativeInput,a.ncGood==NativeRoles}
 pure def matches(a:State,w:Witness):bool=all{w.available,eligible(a),w.g==a.g,w.epoch==a.epoch,w.nonce==a.nonce,w.owner==a.owner,w.layout==a.layout,w.nc==a.nc}
 pure def nativeContext(a:State,r:int,n:int):int->int=if(a.aliasContent and (r==5 or r==7))a.nc.set(5,n).set(7,n)else a.nc.set(r,n)
 pure def nativeBad(a:State,r:int):Set[int]=if(a.aliasContent and (r==5 or r==7))a.ncGood.exclude(Set(5,7))else a.ncGood.exclude(Set(r))
 action fire(e:Event):bool={
  val b={...s,accepted:false}
  s'=match e {
  |Ready=>if(not(s.refused) and s.next+7<Limit){...b,live:Roles,g:Roles.mapBy(r=>s.next+r-1),next:s.next+7,open:true,visible:true,enabled:true,aliasContent:false,nc:NativeRoles.mapBy(r=>0),ncGood:NativeRoles}else {...b,refused:true}
  |Capture=>{...b,w:{available:eligible(s),g:s.g,epoch:s.epoch,nonce:s.nonce,owner:s.owner,layout:s.layout,nc:s.nc}}
  |Confirm=>{...b,accepted:matches(s,s.w)}
  |Destroy(r)=>if(s.aliasContent and (r==5 or r==7)){...b,live:s.live.exclude(Set(5,7))}else {...b,live:s.live.exclude(Set(r))}
  |Recreate(r)=>if(s.next>=Limit){...b,refused:true}else if(not(s.live.contains(r))){...b,live:s.live.union(Set(r)),g:s.g.set(r,s.next),next:s.next+1,aliasContent:false}else b
  |OldDestroyed(v)=>if(s.g.get(v.r)==v.g){if(s.aliasContent and (v.r==5 or v.r==7)){...b,live:s.live.exclude(Set(5,7))}else {...b,live:s.live.exclude(Set(v.r))}}else b
  |AliasContent=>{...b,g:s.g.set(7,s.g.get(5)),aliasContent:true,nc:s.nc.set(7,s.nc.get(5)),ncGood:if(s.ncGood.contains(5))s.ncGood.union(Set(7))else s.ncGood.exclude(Set(7))}
  |Epoch=>{...b,epoch:s.epoch+1}
  |NewMenu=>{...b,nonce:s.nonce+1}
  |Cancel=>{...b,open:false}
  |OwnerChange=>{...b,owner:s.owner+1}
  |LayoutChange=>{...b,layout:s.layout+1}
  |Disable=>{...b,enabled:false}
  |Hide=>{...b,visible:false}
  |SourceFault=>{...b,source:false,refused:true}
  |ThreadFault=>{...b,refused:true}
  |LoaderReset=>{...b,refused:true}
  |ContextFault=>{...b,context:false}
  |LexicalFault=>{...b,lexical:false}
  |PopupOwnerFault=>{...b,popupOwner:false}
  |MissingAttached=>{...b,existingAttached:false}
  |AttachedPopupFault=>{...b,attachedPopup:false}
  |AttachedContentFault=>{...b,attachedContent:false}
  |BaseAliasOnly=>{...b,baseContent:false}
  |RowAncestryFault=>{...b,rowAncestry:false}
  |WindowFault=>{...b,windowMatch:false}
  |NativeRootFault=>{...b,nativeRoot:false}
  |NativeInputFault=>{...b,nativeInput:false}
  |NativeContextPresent(r)=>if(s.next>=Limit){...b,refused:true}else {...b,nc:nativeContext(s,r,s.next),next:s.next+1}
  |NativeContextAbsent(r)=>{...b,nc:nativeContext(s,r,0)}
  |NativeContextForeign(r)=>{...b,ncGood:nativeBad(s,r)}
  |NativeContextConflict(r)=>{...b,ncGood:nativeBad(s,r)}
  |CallerNonce=>b
  }
 }
 val acceptedExact=not(s.accepted)or matches(s,s.w)
 val readonly=s.pinWrites==0
 val safeCounters=s.next>0 and s.next<=Limit
 val aliasExact=not(s.aliasContent and s.live.contains(5) and s.live.contains(7))or s.g.get(5)==s.g.get(7)
 val nativeAliasExact=not(s.aliasContent and s.live.contains(5) and s.live.contains(7))or s.nc.get(5)==s.nc.get(7)
 val allProps=acceptedExact and readonly and safeCounters and aliasExact and nativeAliasExact
 action step=nondet e=Set(Ready,Capture,Confirm,Destroy(1),Destroy(2),Destroy(3),Destroy(4),Destroy(5),Destroy(6),Destroy(7),Recreate(1),Recreate(2),Recreate(3),Recreate(4),Recreate(5),Recreate(6),Recreate(7),OldDestroyed({r:2,g:2}),AliasContent,Epoch,NewMenu,Cancel,OwnerChange,LayoutChange,Disable,Hide,SourceFault,ThreadFault,LoaderReset,ContextFault,LexicalFault,PopupOwnerFault,MissingAttached,AttachedPopupFault,AttachedContentFault,BaseAliasOnly,RowAncestryFault,WindowFault,NativeRootFault,NativeInputFault,CallerNonce,NativeContextPresent(4),NativeContextPresent(5),NativeContextPresent(6),NativeContextPresent(7),NativeContextAbsent(4),NativeContextAbsent(5),NativeContextAbsent(6),NativeContextAbsent(7),NativeContextForeign(4),NativeContextForeign(5),NativeContextForeign(6),NativeContextForeign(7),NativeContextConflict(4)).oneOf();fire(e)
 action check(ok:bool):bool=all{assert(ok),s'=s}
 action ready=fire(Ready)
 action capture=fire(Capture)
 action confirm=fire(Confirm)
 action refused=check(not(s.accepted))
 run exactPopupTest=init.then(ready).then(capture).then(confirm).then(check(s.accepted))
 run separateMenuVisualParentUnneededTest=init.then(ready).then(capture).then(confirm).then(check(s.accepted and s.lexical and s.rowAncestry))
 run sameContentNativeRootAllowedTest=init.then(ready).then(fire(AliasContent)).then(capture).then(confirm).then(check(s.accepted and s.g.get(5)==s.g.get(7)))
 run menuDeathTest=init.then(ready).then(capture).then(fire(Destroy(1))).then(confirm).then(refused)
 run rowDeathTest=init.then(ready).then(capture).then(fire(Destroy(2))).then(confirm).then(refused)
 run popupDeathTest=init.then(ready).then(capture).then(fire(Destroy(3))).then(confirm).then(refused)
 run attachedDeathTest=init.then(ready).then(capture).then(fire(Destroy(4))).then(confirm).then(refused)
 run contentDeathTest=init.then(ready).then(capture).then(fire(Destroy(5))).then(confirm).then(refused)
 run windowDeathTest=init.then(ready).then(capture).then(fire(Destroy(6))).then(confirm).then(refused)
 run nativeRootDeathTest=init.then(ready).then(capture).then(fire(Destroy(7))).then(confirm).then(refused)
 run rowReuseTest=init.then(ready).then(capture).then(fire(Destroy(2))).then(fire(Recreate(2))).then(confirm).then(refused)
 run windowReuseTest=init.then(ready).then(capture).then(fire(Destroy(6))).then(fire(Recreate(6))).then(confirm).then(refused)
 run staleCallbackTest=init.then(ready).then(fire(Destroy(2))).then(fire(Recreate(2))).then(capture).then(fire(OldDestroyed({r:2,g:2}))).then(confirm).then(check(s.accepted))
 run reloadTest=init.then(ready).then(capture).then(fire(Epoch)).then(confirm).then(refused)
 run newMenuTest=init.then(ready).then(capture).then(fire(NewMenu)).then(confirm).then(refused)
 run cancelTest=init.then(ready).then(capture).then(fire(Cancel)).then(confirm).then(refused)
 run otherOwnerTest=init.then(ready).then(capture).then(fire(OwnerChange)).then(confirm).then(refused)
 run layoutTest=init.then(ready).then(capture).then(fire(LayoutChange)).then(confirm).then(refused)
 run disabledTest=init.then(ready).then(capture).then(fire(Disable)).then(confirm).then(refused)
 run hiddenTest=init.then(ready).then(capture).then(fire(Hide)).then(confirm).then(refused)
 run missingAttachedTest=init.then(ready).then(fire(MissingAttached)).then(capture).then(confirm).then(refused)
 run differentAttachedPopupTest=init.then(ready).then(fire(AttachedPopupFault)).then(capture).then(confirm).then(refused)
 run differentAttachedContentTest=init.then(ready).then(fire(AttachedContentFault)).then(capture).then(confirm).then(refused)
 run shadowedContentAliasNotAuthorityTest=init.then(ready).then(fire(BaseAliasOnly)).then(capture).then(confirm).then(refused)
 run falseRowAncestryTest=init.then(ready).then(fire(RowAncestryFault)).then(capture).then(confirm).then(refused)
 run wrongWindowTest=init.then(ready).then(fire(WindowFault)).then(capture).then(confirm).then(refused)
 run wrongNativeRootTest=init.then(ready).then(fire(NativeRootFault)).then(capture).then(confirm).then(refused)
 run missingNativeInputTest=init.then(ready).then(capture).then(fire(NativeInputFault)).then(confirm).then(refused)
 run sourceFaultTest=init.then(ready).then(capture).then(fire(SourceFault)).then(ready).then(confirm).then(refused)
 run contextFaultTest=init.then(ready).then(capture).then(fire(ContextFault)).then(confirm).then(refused)
 run wrongThreadTest=init.then(ready).then(capture).then(fire(ThreadFault)).then(ready).then(confirm).then(refused)
 run loaderResetTest=init.then(ready).then(capture).then(fire(LoaderReset)).then(ready).then(confirm).then(refused)
 run callerNonceCannotGrantTest=init.then(fire(CallerNonce)).then(capture).then(confirm).then(refused)
 run lexicalFaultTest=init.then(ready).then(fire(LexicalFault)).then(capture).then(confirm).then(refused)
 run wrongPopupOwnerTest=init.then(ready).then(fire(PopupOwnerFault)).then(capture).then(confirm).then(refused)
 run nativeAbsentIsExplicitTest=init.then(ready).then(capture).then(confirm).then(check(s.accepted and s.w.nc==NativeRoles.mapBy(r=>0)))
 run genuinePresentNativeContextTest=init.then(ready).then(fire(NativeContextPresent(4))).then(capture).then(confirm).then(check(s.accepted and s.w.nc.get(4)>0))
 run nativeContextAppearsBetweenReadsTest=init.then(ready).then(capture).then(fire(NativeContextPresent(5))).then(confirm).then(refused)
 run nativeContextDisappearsBetweenReadsTest=init.then(ready).then(fire(NativeContextPresent(6))).then(capture).then(fire(NativeContextAbsent(6))).then(confirm).then(refused)
 run nativeContextReplacementBetweenReadsTest=init.then(ready).then(fire(NativeContextPresent(7))).then(capture).then(fire(NativeContextPresent(7))).then(confirm).then(refused)
 run foreignNativeContextTest=init.then(ready).then(fire(NativeContextForeign(4))).then(capture).then(confirm).then(refused)
 run absentContextConflictingEngineTest=init.then(ready).then(fire(NativeContextConflict(5))).then(capture).then(confirm).then(refused)
 run aliasedContentHasSameContextTest=init.then(ready).then(fire(AliasContent)).then(fire(NativeContextPresent(5))).then(capture).then(confirm).then(check(s.accepted and s.nc.get(5)==s.nc.get(7)))
 run aliasedNativeContextRetirementTest=init.then(ready).then(fire(AliasContent)).then(fire(NativeContextPresent(7))).then(capture).then(fire(NativeContextAbsent(5))).then(confirm).then(refused)
}
