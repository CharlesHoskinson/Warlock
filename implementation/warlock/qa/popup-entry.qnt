module popup_entry {
  // UX-024/UI-011: Desktop popup origin -> frame keyboard parent policy ->
  // shared_keyboard_parent commit BEFORE popup_hide/native grab teardown.
  // Actual native opener identity, locks, Wayland delivery, timing and AT are
  // separate. Native owns opener eligibility; no window command is added.
  type State = { keyboardEntry: bool, live: bool, protected: bool, depth: int,
    closing: bool, parentKeyboard: bool, focus: int, savedFocus: int,
    policyCommitted: bool, completed: bool, nestedReturn: bool }
  var s: State
  action init = s' = { keyboardEntry:false,live:true,protected:false,depth:0,
    closing:false,parentKeyboard:false,focus:0,savedFocus:0,
    policyCommitted:false,completed:false,nestedReturn:false }
  action open(keyboard: bool): bool = all {s.live and s.depth==0 and not(s.closing),
    s' = {...s,keyboardEntry:keyboard,depth:1,parentKeyboard:true,focus:2,
      savedFocus:s.focus,completed:false,policyCommitted:false,nestedReturn:false}}
  action nest = all {s.depth==1 and not(s.closing),s'={...s,depth:2}}
  action dismissNested = all {s.depth==2 and not(s.closing),
    s'={...s,depth:1,focus:2,parentKeyboard:true,nestedReturn:true}}
  action commitClose = all {s.depth==1 and not(s.closing),
    s'={...s,closing:true,parentKeyboard:s.keyboardEntry and s.live and not(s.protected),policyCommitted:true}}
  action endGrab = all {s.closing and s.policyCommitted,
    s'={...s,closing:false,depth:0,completed:true,
      focus:if(not(s.live) or s.protected) 3 else if(s.parentKeyboard) 1 else s.savedFocus}}
  action retire = s'={...s,live:false}
  action lock = s'={...s,protected:true}
  action step = any {open(false),open(true),nest,dismissNested,commitClose,endGrab,retire,lock}
  val safety = (not(s.closing) or s.policyCommitted)
    and (not(s.completed) or not(s.live) or s.protected or
      (if(s.keyboardEntry) s.focus==1 else s.focus==s.savedFocus))
  val applicationReturned = s.completed and not(s.keyboardEntry) and s.focus==0
  val barReturned = s.completed and s.keyboardEntry and s.focus==1
  val nestedParentReturned = s.nestedReturn and s.depth==1 and s.focus==2
  val staleOpenerRefused = s.completed and not(s.live) and s.focus==3
}
