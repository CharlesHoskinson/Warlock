module SnapChooser {
  var state: { output: int, revision: int, choiceOutput: int, choiceRevision: int, open: bool, region: int }
  action init = state' = { output: 1, revision: 1, choiceOutput: 0, choiceRevision: 0, open: false, region: 0 }
  action open = state' = { ...state, choiceOutput: state.output, choiceRevision: state.revision, open: true, region: 0 }
  action chooseRegion = {
    nondet region = 0.to(5).oneOf()
    all {
      state.open and state.choiceOutput == state.output and state.choiceRevision == state.revision,
      state' = { ...state, region: region }
    }
  }
  action outputChanged = state' = { ...state, output: state.output + 1, revision: state.revision + 1, open: false }
  action workAreaChanged = state' = { ...state, revision: state.revision + 1, open: false }
  action close = state' = { ...state, open: false }
  action step = any { open, chooseRegion, outputChanged, workAreaChanged, close }
  val safety = not(state.open) or (state.choiceOutput == state.output and state.choiceRevision == state.revision and state.region >= 0 and state.region <= 5)
  run outputRetiresPreviewTest = init.then(open).then(outputChanged).then(all { assert(not(state.open)), state' = state })
  run areaRetiresPreviewTest = init.then(open).then(workAreaChanged).then(all { assert(not(state.open)), state' = state })
  run reopenUsesCurrentGenerationTest = init.then(open).then(outputChanged).then(open).then(all { assert(safety and state.choiceOutput == 2), state' = state })
}
