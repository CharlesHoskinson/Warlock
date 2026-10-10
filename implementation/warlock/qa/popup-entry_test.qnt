module popup_entry_test {
  import popup_entry.* from "./popup-entry"
  run pointerReturnTest = init.then(open(false)).then(commitClose).then(all {assert(not(s.parentKeyboard)),s'=s}).then(endGrab).then(all {assert(applicationReturned and safety),s'=s})
  run keyboardReturnTest = init.then(open(true)).then(commitClose).then(all {assert(s.parentKeyboard),s'=s}).then(endGrab).then(all {assert(barReturned and safety),s'=s})
  run nestedPointerTest = init.then(open(false)).then(nest).then(dismissNested).then(all {assert(nestedParentReturned and s.parentKeyboard),s'=s})
  run nestedKeyboardTest = init.then(open(true)).then(nest).then(dismissNested).then(commitClose).then(endGrab).then(all {assert(barReturned),s'=s})
  run staleOpenerTest = init.then(open(false)).then(retire).then(commitClose).then(endGrab).then(all {assert(staleOpenerRefused),s'=s})
  run lockSupersedesTest = init.then(open(false)).then(lock).then(commitClose).then(endGrab).then(all {assert(s.focus==3 and not(s.parentKeyboard)),s'=s})
}
