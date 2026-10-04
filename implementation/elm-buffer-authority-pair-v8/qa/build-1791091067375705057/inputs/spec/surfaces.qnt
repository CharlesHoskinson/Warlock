module surfaces {
 type State={grab:bool,foreign:bool,focused:bool,lock:bool,exclusive:bool,operation:int,minimized:bool,keyboard:int,oldKeyboard:int,focus:int,oldFocus:int,grabToken:int,oldGrab:int,committed:bool}
 var s:State
 action init=s'={grab:true,foreign:true,focused:false,lock:false,exclusive:false,operation:0,minimized:false,keyboard:9,oldKeyboard:9,focus:1,oldFocus:1,grabToken:4,oldGrab:4,committed:false}
 val allowed=not(s.lock) and not(s.exclusive) and (not(s.grab) or (s.operation==0 and not(s.focused) and s.foreign))
 action execute=s'=if(allowed) {...s,minimized:s.operation==0,committed:true} else {...s,committed:false}
 action ownGrab=s'={...s,foreign:false,committed:false}
 action focusedTarget=s'={...s,focused:true,committed:false}
 action restore=s'={...s,operation:1,committed:false}
 action activate=s'={...s,operation:2,committed:false}
 action lock=s'={...s,lock:true,committed:false}
 action exclusive=s'={...s,exclusive:true,committed:false}
 action step=any{execute,ownGrab,focusedTarget,restore,activate,lock,exclusive}
 val safety=s.committed implies allowed and s.keyboard==s.oldKeyboard and s.focus==s.oldFocus and s.grabToken==s.oldGrab
 run foreignBackgroundTest=init.then(execute).then(all{assert(s.committed and s.minimized),s'=s})
 run ownGrabTest=init.then(ownGrab).then(execute).then(all{assert(not(s.committed)),s'=s})
 run focusedTargetTest=init.then(focusedTarget).then(execute).then(all{assert(not(s.committed)),s'=s})
 run restoreTest=init.then(restore).then(execute).then(all{assert(not(s.committed)),s'=s})
 run activateTest=init.then(activate).then(execute).then(all{assert(not(s.committed)),s'=s})
 run lockedTest=init.then(lock).then(execute).then(all{assert(not(s.committed)),s'=s})
 run exclusiveTest=init.then(exclusive).then(execute).then(all{assert(not(s.committed)),s'=s})
}
