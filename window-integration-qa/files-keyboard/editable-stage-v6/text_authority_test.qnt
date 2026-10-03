module text_authority_test {
 import text_authority.* from "./text_authority"
 run nativeVisibleContentTest=init.then(fire(Mutate({node:0,epoch:0,kind:"insert"}))).then(all{assert(allowed and content.get(0)==1),fire(MapWindow(mapped))})
 run nativeVisibleSelectionTest=init.then(fire(Mutate({node:2,epoch:0,kind:"selection"}))).then(all{assert(allowed and selection.get(2)==1),fire(MapWindow(mapped))})
 run hiddenWindowRefusesMutationTest=init.then(fire(MapWindow(false))).then(fire(Mutate({node:0,epoch:0,kind:"delete"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run hiddenAncestorRefusesSelectionTest=init.then(fire(Show({node:2,value:false}))).then(fire(Mutate({node:2,epoch:0,kind:"selection"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run disabledRefusesCursorTest=init.then(fire(Enable({node:0,value:false}))).then(fire(Mutate({node:0,epoch:0,kind:"cursor"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run modalBackgroundRefusesValueTest=init.then(fire(Modal(true))).then(fire(Mutate({node:0,epoch:0,kind:"setValue"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run modalOwnerNativeEditingTest=init.then(fire(Modal(true))).then(fire(Mutate({node:1,epoch:0,kind:"replace"}))).then(all{assert(allowed and content.get(1)==1),fire(MapWindow(mapped))})
 run cachedReadonlyEditableRefusedTest=init.then(fire(ReadOnly({node:0,value:true}))).then(fire(Mutate({node:0,epoch:0,kind:"delete"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run readonlyNativeSelectionStillAllowedTest=init.then(fire(ReadOnly({node:2,value:true}))).then(fire(Mutate({node:2,epoch:0,kind:"addSelection"}))).then(all{assert(allowed and selection.get(2)==1 and content.get(2)==0),fire(MapWindow(mapped))})
 run retiredPeerRefusesTest=init.then(fire(Retire(0))).then(fire(Mutate({node:0,epoch:0,kind:"insert"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run rebuiltPeerOldEpochRefusesTest=init.then(fire(Retire(2))).then(fire(Recreate(2))).then(fire(Mutate({node:2,epoch:0,kind:"setValue"}))).then(all{assert(not(allowed) and allProps),fire(MapWindow(mapped))})
 run rebuiltCurrentPeerStillEditableTest=init.then(fire(Retire(2))).then(fire(Recreate(2))).then(fire(Mutate({node:2,epoch:2,kind:"replace"}))).then(all{assert(allowed and content.get(2)==1),fire(MapWindow(mapped))})
}
