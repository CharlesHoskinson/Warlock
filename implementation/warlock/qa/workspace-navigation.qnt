module workspaceNavigation {
  // Bounded authority schedule; not a native refinement or pixel verdict.
  var s: { active: int, member: int, focused: int, live: bool, issued: bool, unknown: bool, refused: bool, restored: bool, activations: int }
  action init = s'={active:1,member:2,focused:1,live:true,issued:false,unknown:false,refused:false,restored:false,activations:0}
  action navigate = all {s.live,not(s.issued),s'={...s,active:2,issued:true}}
  action refuseBefore = s'=s
  action commit = all {s.issued,s.live,s.active==2,not(s.unknown),not(s.refused),not(s.restored),s'={...s,focused:2,restored:true,activations:s.activations+1}}
  action retire = s'={...s,live:false}
  action refuseAfter = all {s.issued,not(s.restored),not(s.unknown),not(s.refused),s'={...s,active:1,focused:1,refused:true}}
  action uncertain = all {s.issued,not(s.restored),not(s.refused),s'={...s,unknown:true}}
  action duplicate = s'=s
  action step = any {navigate,refuseBefore,commit,retire,refuseAfter,uncertain,duplicate}
  val safety = s.member==2 and s.activations<=1 and (s.focused!=2 or (s.restored and s.active==2)) and (not(s.refused) or (not(s.restored) and s.activations==0))
  run restorePreservesWorkspaceTest = init.then(navigate).then(commit).then(duplicate).then(all {assert(s.member==2 and s.active==2 and s.focused==2 and s.activations==1),s'=s})
  run preflightRefusalPreservesFocusTest = init.then(refuseBefore).then(all {assert(s.active==1 and s.focused==1 and not(s.restored)),s'=s})
  run navigationRefusalCompensatesTest = init.then(navigate).then(refuseAfter).then(all {assert(s.active==1 and s.focused==1 and s.member==2),s'=s})
  run retiredIdentityNeverActivatesTest = init.then(navigate).then(retire).then(refuseAfter).then(all {assert(s.focused==1 and s.activations==0),s'=s})
  run unknownNeverReplaysTest = init.then(navigate).then(uncertain).then(duplicate).then(all {assert(s.unknown and s.activations==0 and not(s.restored)),s'=s})
}
