module gesture_end_test {
  import gesture_end.* from "./gesture-end"
  run moveCancelRestoresTest=init.then(fire(BeginMove)).then(fire(Motion)).then(fire(EscapePress)).then(all {assert(cancelRestores and s.geom==10 and safety),s'=s})
  run crossOutputCancelRestoresSpaceTest=init.then(fire(BeginMove)).then(fire(Motion)).then(all {assert(s.space==2),s'=s}).then(fire(EscapePress)).then(all {assert(crossedCancel and s.space==1 and safety),s'=s})
  run resizeCancelRestoresTest=init.then(fire(BeginResize)).then(fire(Motion)).then(fire(EscapePress)).then(all {assert(cancelRestores and s.geom==10 and safety),s'=s})
  run releaseCommitsTest=init.then(fire(BeginMove)).then(fire(Motion)).then(fire(Release)).then(all {assert(releaseCommits and s.geom==13 and safety),s'=s})
  run cancellationEndsOnceTest=init.then(fire(BeginMove)).then(fire(Motion)).then(fire(EscapePress)).then(fire(Release)).then(fire(EscapePress)).then(all {assert(duplicateEndIgnored and s.ends==1 and s.drops==0 and s.geom==10 and safety),s'=s})
  run ownerRetirementCannotDropTest=init.then(fire(BeginMove)).then(fire(Motion)).then(fire(CloseOwner)).then(all {assert(retireWithoutDrop and s.owner==0 and s.ends==1 and safety),s'=s})
  run unrelatedCloseKeepsOwnerTest=init.then(fire(BeginResize)).then(fire(ClosePeer)).then(all {assert(peerKeepsOwner and s.mode=="resize" and safety),s'=s})
  run replacementCannotReceiveOldEndTest=init.then(fire(BeginMove)).then(fire(Motion)).then(fire(CloseOwner)).then(fire(Reopen)).then(fire(EscapePress)).then(fire(Release)).then(all {assert(s.geom==99 and s.current==2 and s.ends==1 and s.drops==0 and safety),s'=s})
  run escapeReleaseCannotEndNewGestureTest=init.then(fire(BeginMove)).then(fire(EscapePress)).then(fire(Release)).then(fire(BeginResize)).then(fire(EscapeRelease)).then(all {assert(s.owner==1 and s.mode=="resize" and s.ends==1 and safety),s'=s})
}
