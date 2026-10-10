module modal_eligibility_test {
  import modal_eligibility.* from "modal-eligibility"
  run singletonTest = init.then(focusFamily).then(all { assert(s.focus==0), s' = s })
  run singleModalTest = init.then(shape(1)).then(commit).then(focusFamily).then(all { assert(s.focus==1), s' = s })
  run nestedModalTest = init.then(shape(2)).then(commit).then(focusFamily).then(all { assert(s.focus==2), s' = s })
  run blockedModalTest = init.then(shape(1)).then(block).then(commit).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run blockedNestedTest = init.then(shape(2)).then(block).then(commit).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run noFocusModalTest = init.then(shape(1)).then(noFocus).then(commit).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run ambiguousTest = init.then(shape(3)).then(commit).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run cyclicTest = init.then(shape(4)).then(commit).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run staleTest = init.then(shape(1)).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run protectedTest = init.then(shape(1)).then(commit).then(protect).then(focusFamily).then(all { assert(s.focus==9 and s.refusals==1), s' = s })
  run draftAndOtherTest = init.then(shape(1)).then(commit).then(focusFamily).then(clickUnrelated).then(all { assert(s.focus==9 and s.draft=="unsaved modal draft" and s.topology==1), s' = s })
}
