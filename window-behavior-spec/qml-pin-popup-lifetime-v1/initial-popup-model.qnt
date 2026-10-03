module pin_popup {
 val Roles=Set(1,2,3,4,5,6,7) // menu,row,popup,attached,proxy content,window,native root
 val Limit=40
 type Witness={available:bool,g:int->int,epoch:int,nonce:int,owner:int,layout:int}
 type State={live:Set[int],g:int->int,next:int,epoch:int,nonce:int,owner:int,layout:int,open:bool,visible:bool,enabled:bool,source:bool,refused:bool,context:bool,lexical:bool,popupOwner:bool,existingAttached:bool,attachedPopup:bool,attachedContent:bool,baseContent:bool,rowAncestry:bool,windowMatch:bool,nativeRoot:bool,nativeInput:bool,aliasContent:bool,w:Witness,accepted:bool,pinWrites:int}
 type Event=Ready|Capture|Confirm|Destroy(int)|Recreate(int)|OldDestroyed({r:int,g:int})|AliasContent|Epoch|NewMenu|Cancel|OwnerChange|LayoutChange|Disable|Hide|SourceFault|ThreadFault|LoaderReset|ContextFault|LexicalFault|PopupOwnerFault|MissingAttached|AttachedPopupFault|AttachedContentFault|BaseAliasOnly|RowAncestryFault|WindowFault|NativeRootFault|NativeInputFault|CallerNonce
 var s:State
 val empty={available:false,g:Roles.mapBy(r=>0),epoch:0,nonce:0,owner:0,layout:0}
 action init=s'={live:Set(),g:Roles.mapBy(r=>0),next:1,epoch:1,nonce:1,owner:1,layout:1,open:false,visible:false,enabled:false,source:true,refused:false,context:true,lexical:true,popupOwner:true,existingAttached:true,attachedPopup:true,attachedContent:true,baseContent:true,rowAncestry:true,windowMatch:true,nativeRoot:true,nativeInput:true,aliasContent:false,w:empty,accepted:false,pinWrites:0}
 pure def eligible(a:State):bool=all{a.live==Roles,a.open,a.visible,a.enabled,a.source,not(a.refused),a.context,a.lexical,a.popupOwner,a.existingAttached,a.attachedPopup,a.attachedContent,a.baseContent,a.rowAncestry,a.windowMatch,a.nativeRoot,a.nativeInput}
 pure def matches(a:State,w:Witness):bool=all{w.available,eligible(a),w.g==a.g,w.epoch==a.epoch,w.nonce==a.nonce,w.owner==a.owner,w.layout==a.layout}
 action fire(e:Event):bool={
  val b={...s,accepted:false}
  s'=match e {
  |Ready=>if(not(s.refused) and s.next+7<Limit){...b,live:Roles,g:Roles.mapBy(r=>s.next+r-1),next:s.next+7,open:true,visible:true,enabled:true}else {...b,refused:true}
  |Capture=>{...b,w:{available:eligible(s),g:s.g,epoch:s.epoch,nonce:s.nonce,owner:s.owner,layout:s.layout}}
  |Confirm=>{...b,accepted:matches(s,s.w)}
  |Destroy(r)=>if(s.aliasContent and (r==5 or r==7)){...b,live:s.live.exclude(Set(5,7))}else {...b,live:s.live.exclude(Set(r))}
  |Recreate(r)=>if(s.next>=Limit){...b,refused:true}else if(not(s.live.contains(r))){...b,live:s.live.union(Set(r)),g:s.g.set(r,s.next),next:s.next+1,aliasContent:false}else b
  |OldDestroyed(v)=>if(s.g.get(v.r)==v.g){...b,live:s.live.exclude(Set(v.r))}else b
  |AliasContent=>{...b,g:s.g.set(7,s.g.get(5)),aliasContent:true}
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
  |CallerNonce=>b
  }
 }
 val acceptedExact=not(s.accepted)or matches(s,s.w)
 val readonly=s.pinWrites==0
 val safeCounters=s.next>0 and s.next<=Limit
 val allProps=acceptedExact and readonly and safeCounters
 action step=nondet e=Set(Ready,Capture,Confirm,Destroy(1),Destroy(2),Destroy(3),Destroy(4),Destroy(5),Destroy(6),Destroy(7),Recreate(1),Recreate(2),Recreate(3),Recreate(4),Recreate(5),Recreate(6),Recreate(7),OldDestroyed({r:2,g:2}),AliasContent,Epoch,NewMenu,Cancel,OwnerChange,LayoutChange,Disable,Hide,SourceFault,ThreadFault,LoaderReset,ContextFault,LexicalFault,PopupOwnerFault,MissingAttached,AttachedPopupFault,AttachedContentFault,BaseAliasOnly,RowAncestryFault,WindowFault,NativeRootFault,NativeInputFault,CallerNonce).oneOf();fire(e)
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
}
