module layerAppearanceTests {
  import layerAppearance.* from "./layer-appearance"
  action verify(ok:bool):bool=all {assert(ok),s'=s}
  run draftDoesNotApplyTest=init.then(edit(3)).then(verify(s.applied==0 and s.stored==0 and s.writes==0))
  run bothFlagsCommitTest=init.then(edit(3)).then(save).then(delivered).then(verify(bothCommitted and s.stored==3 and s.writes==1))
  run unknownKeepsOldAppearanceTest=init.then(edit(1)).then(save).then(lost).then(staleReceipt).then(verify(unknownHeld and s.writes==1))
  run readReconcilesWithoutReplayTest=init.then(edit(2)).then(save).then(lost).then(refresh).then(verify(s.applied==2 and s.writes==1))
  run staleSaveCannotOverwriteTest=init.then(edit(1)).then(save).then(compete).then(refuse).then(verify(staleRefused and s.stored==3 and s.applied==0 and s.writes==1))
}
