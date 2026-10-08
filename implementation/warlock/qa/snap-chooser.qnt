module SnapChooser {
  var state: { output: int, revision: int, choiceOutput: int, choiceRevision: int, open: bool, region: int, waiting: bool, issued: bool, sealed: bool, request: int, admittedOutput: int, admittedRevision: int }
  action init = state' = { output: 1, revision: 1, choiceOutput: 0, choiceRevision: 0, open: false, region: 0, waiting: false, issued: false, sealed: false, request: 0, admittedOutput: 0, admittedRevision: 0 }
  action open = all {
    not(state.waiting) and not(state.issued) and not(state.sealed),
    state' = { ...state, choiceOutput: state.output, choiceRevision: state.revision, open: true, region: 0 }
  }
  action chooseRegion = {
    nondet region = 0.to(5).oneOf()
    all { state.open and state.choiceOutput == state.output and state.choiceRevision == state.revision, state' = { ...state, region: region } }
  }
  action apply = all { state.open, state' = { ...state, open: false, waiting: true } }
  action authorize = all {
    state.waiting and not(state.sealed) and state.choiceOutput == state.output and state.choiceRevision == state.revision,
    state' = { ...state, waiting: false, issued: true, request: state.request + 1, admittedOutput: state.output, admittedRevision: state.revision }
  }
  action refuseStale = all {
    state.waiting and (state.choiceOutput != state.output or state.choiceRevision != state.revision),
    state' = { ...state, waiting: false }
  }
  action definitive = all { state.issued and not(state.sealed), state' = { ...state, issued: false } }
  action uncertain = all { state.issued, state' = { ...state, sealed: true } }
  action retrySealed = all { state.sealed, state' = state }
  action outputChanged = state' = { ...state, output: state.output + 1, revision: state.revision + 1, open: false, sealed: state.sealed or state.issued }
  action workAreaChanged = state' = { ...state, revision: state.revision + 1, open: false, sealed: state.sealed or state.issued }
  action close = state' = { ...state, open: false }
  action step = any { open, chooseRegion, apply, authorize, refuseStale, definitive, uncertain, retrySealed, outputChanged, workAreaChanged, close }
  val safety = all {
    not(state.open) or (state.choiceOutput == state.output and state.choiceRevision == state.revision and not(state.waiting) and not(state.issued) and not(state.sealed)),
    not(state.issued) or (not(state.open) and not(state.waiting) and (state.sealed or (state.admittedOutput == state.output and state.admittedRevision == state.revision))),
    state.region >= 0 and state.region <= 5 and state.request >= 0
  }
  run outputRetiresPreviewTest = init.then(open).then(outputChanged).then(all { assert(not(state.open)), state' = state })
  run areaRetiresPreviewTest = init.then(open).then(workAreaChanged).then(all { assert(not(state.open)), state' = state })
  run reopenUsesCurrentGenerationTest = init.then(open).then(outputChanged).then(open).then(all { assert(safety and state.choiceOutput == 2), state' = state })
  run outputChangeBeforeCommitRefusesTest = init.then(open).then(apply).then(outputChanged).then(refuseStale).then(all { assert(state.request == 0 and not(state.waiting)), state' = state })
  run areaChangeBeforeCommitRefusesTest = init.then(open).then(apply).then(workAreaChanged).then(refuseStale).then(all { assert(state.request == 0), state' = state })
  run unknownCannotReplayTest = init.then(open).then(apply).then(authorize).then(uncertain).then(retrySealed).then(all { assert(state.request == 1 and state.sealed), state' = state })
  run changedAfterIssueCannotCommitTest = init.then(open).then(apply).then(authorize).then(outputChanged).then(all { assert(state.sealed and state.issued and safety), state' = state })
}
