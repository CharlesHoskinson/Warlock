module picker {
 type State={scope:int,shown:int,generation:int,open:bool,pending:bool,queuedScope:int,queuedGeneration:int,focused:str,effects:int}
 var s:State
 action init=s'={scope:1,shown:1,generation:0,open:false,pending:false,queuedScope:0,queuedGeneration:0,focused:"opener",effects:0}
 action open=all{s.shown==s.scope,not(s.pending),s'={...s,generation:s.generation+1,open:true,queuedScope:s.scope,queuedGeneration:s.generation+1}}
 action focus=all{s.open,s.queuedScope==s.scope,s.queuedGeneration==s.generation,s'={...s,focused:"picker"}}
 action staleFocus=all{not(s.open) or s.queuedScope!=s.scope or s.queuedGeneration!=s.generation,s'=s}
 action close=all{s.open,s'={...s,open:false,focused:"opener"}}
 action change=s'={...s,scope:s.scope+1,open:false,focused:"native"}
 action reconcile=s'={...s,shown:s.scope}
 action choose=all{s.open,s.shown==s.scope,not(s.pending),s'={...s,open:false,pending:true,effects:s.effects+1,focused:"native"}}
 action oldSelection=all{not(s.open) or s.shown!=s.scope or s.pending,s'=s}
 action settle=s'={...s,pending:false}
 action oldQueue=s'={...s,queuedScope:s.scope-1,queuedGeneration:s.generation-1}
 action step=any{open,focus,staleFocus,close,change,reconcile,choose,oldSelection,settle,oldQueue}
 val safety=all{s.focused=="picker" implies s.open, s.pending implies not(s.open),s.generation>=0,s.effects>=0}
 run openFocusTest=init.then(open).then(focus).then(all{assert(s.focused=="picker"),s'=s})
 run escapeOpenerTest=init.then(open).then(focus).then(close).then(all{assert(s.focused=="opener" and s.effects==0),s'=s})
 run oldFocusAfterCloseTest=init.then(open).then(close).then(staleFocus).then(all{assert(s.focused=="opener"),s'=s})
 run oldFocusAfterReopenTest=init.then(open).then(close).then(open).then(oldQueue).then(staleFocus).then(all{assert(s.focused=="opener" and s.generation==2),s'=s})
 run nativeScopeChangeTest=init.then(open).then(change).then(staleFocus).then(all{assert(s.focused=="native"),s'=s})
 run selectionDoesNotRestoreOpenerTest=init.then(open).then(focus).then(choose).then(all{assert(s.focused=="native" and s.effects==1),s'=s})
 run duplicatePendingSelectionTest=init.then(open).then(choose).then(oldSelection).then(all{assert(s.effects==1),s'=s})
 run retiredPickerSelectionTest=init.then(open).then(close).then(oldSelection).then(all{assert(s.effects==0),s'=s})
}
