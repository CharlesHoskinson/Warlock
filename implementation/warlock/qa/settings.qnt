module Settings {
  var stored: int
  var applied: int
  var draft: int
  var revision: int
  var expected: int
  var phase: str
  var writes: int
  val valid = Set(100, 125, 150, 200)
  action init = all {stored'=100, applied'=100, draft'=100, revision'=1, expected'=1, phase'="idle", writes'=0}
  def editable(scale: int): bool = phase == "idle" and valid.contains(scale)
  val canSave = phase == "idle" and draft != stored
  action verify(condition: bool): bool = all {assert(condition),stored'=stored,applied'=applied,draft'=draft,revision'=revision,expected'=expected,phase'=phase,writes'=writes}
  action edit(scale: int): bool = all {
    editable(scale), draft'=scale,
    stored'=stored, applied'=applied, revision'=revision, expected'=expected, phase'=phase, writes'=writes
  }
  action save = all {
    canSave, expected'=revision, phase'="pending", writes'=writes+1,
    stored'=stored, applied'=applied, draft'=draft, revision'=revision
  }
  action delivered = all {
    phase == "pending", expected == revision, stored'=draft, applied'=draft, revision'=revision+1,
    phase'="idle", draft'=draft, expected'=expected, writes'=writes
  }
  action loseReceipt = all {
    phase == "pending", expected == revision, stored'=draft, revision'=revision+1, phase'="unknown",
    applied'=applied, draft'=draft, expected'=expected, writes'=writes
  }
  action refresh = all {
    phase != "pending", applied'=stored, draft'=stored, expected'=revision, phase'="idle",
    stored'=stored, revision'=revision, writes'=writes
  }
  action compete = all {
    phase == "pending", revision'=revision+1, stored'=200,
    applied'=applied, draft'=draft, expected'=expected, phase'=phase, writes'=writes
  }
  action refuseStale = all {
    phase == "pending", expected != revision, phase'="idle",
    stored'=stored, applied'=applied, draft'=draft, revision'=revision, expected'=expected, writes'=writes
  }
  action step = any {edit(100), edit(125), edit(150), edit(200), save, delivered, loseReceipt, refresh, compete, refuseStale}
  val safety = valid.contains(stored) and valid.contains(applied) and valid.contains(draft) and revision >= 1 and writes >= 0
  run draftDoesNotApplyTest = init.then(edit(150)).then(verify(applied == 100 and stored == 100))
  run exactSavePersistsTest = init.then(edit(150)).then(save).then(delivered).then(verify(applied == 150 and stored == 150 and revision == 2 and writes == 1))
  run lostReceiptNoReplayTest = init.then(edit(125)).then(save).then(loseReceipt).then(verify(phase == "unknown" and applied == 100 and stored == 125 and not(canSave)))
  run readReconcilesWithoutWriteTest = init.then(edit(150)).then(save).then(loseReceipt).then(refresh).then(verify(applied == 150 and stored == 150 and writes == 1))
  run staleCasCannotOverwriteTest = init.then(edit(150)).then(save).then(compete).then(refuseStale).then(verify(stored == 200 and applied == 100 and writes == 1))
  run invalidScaleCannotEditTest = init.then(verify(not(editable(77)) and applied == 100))
}
