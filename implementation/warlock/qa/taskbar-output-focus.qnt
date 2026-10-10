// ELM-UI-004 taskbar-inactive/taskbar-active. Native desktop focus is distinct
// from keyboard custody held by a bar/popup. Single validated native snapshot;
// no transport authentication, modal succession, pixels, AT or liveness proof.
module taskbar_output_focus {
 var s:{phase:int,rawFocus:bool,visible:bool,hidden:bool,minimized:bool,seat:str,workspace:int,draft:int,effects:int}
 action init=s'={phase:0,rawFocus:true,visible:true,hidden:false,minimized:false,seat:"app",workspace:2,draft:1,effects:0}
 pure def eligible(visible:bool,hidden:bool,minimized:bool,ordinaryWorkspace:bool):bool=visible and not(hidden) and not(minimized) and ordinaryWorkspace
 pure def focusProjection(rawFocus:bool,visible:bool,hidden:bool,minimized:bool,ordinaryWorkspace:bool):bool=rawFocus and eligible(visible,hidden,minimized,ordinaryWorkspace)
 val projectedFocus=focusProjection(s.rawFocus,s.visible,s.hidden,s.minimized,s.workspace>0)
 val offer=if(s.minimized) "restore" else if(projectedFocus) "minimize" else "activate"
 action retire=all{s.phase==0,s'={...s,phase:1,visible:false,seat:"shell"}}
 action activate=all{s.phase==1,offer=="activate",s'={...s,phase:2,visible:true,rawFocus:true,seat:"app",effects:s.effects+1}}
 action holdBar=all{s.phase==2,s'={...s,phase:3,seat:"bar"}}
 action holdPopup=all{s.phase==2,s'={...s,phase:4,seat:"popup"}}
 action minimize=all{Set(2,3,4).contains(s.phase),offer=="minimize",s'={...s,phase:5,minimized:true,rawFocus:false,seat:"desktop",effects:s.effects+1}}
 action restore=all{s.phase==5,offer=="restore",s'={...s,phase:6,minimized:false,rawFocus:true,seat:"app",effects:s.effects+1}}
 action idle=s'=s
 action step=any{retire,activate,holdBar,holdPopup,minimize,restore,idle}
 val ghostSuppressed=s.phase==1 and s.rawFocus and not(projectedFocus) and offer=="activate"
 val activated=s.phase==2 and projectedFocus
 val minimized=s.phase==5 and not(projectedFocus) and offer=="restore"
 val restored=s.phase==6 and projectedFocus
 val barCustody=s.phase==3 and s.seat=="bar" and projectedFocus and offer=="minimize"
 val popupCustody=s.phase==4 and s.seat=="popup" and projectedFocus and offer=="minimize"
 val safety=all{s.workspace==2,s.draft==1,s.minimized==(s.phase==5),
  s.effects==(if(s.phase<=1) 0 else if(s.phase<=4) 1 else if(s.phase==5) 2 else 3),
  not(projectedFocus) or eligible(s.visible,s.hidden,s.minimized,s.workspace>0),
  s.phase!=1 or (s.rawFocus and offer=="activate")}
}
