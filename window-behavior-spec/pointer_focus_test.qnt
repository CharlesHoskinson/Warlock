module pointer_focus_test {
  import pointer_focus.* from "./pointer_focus"
  run inactiveScrollPreservesTypingTest = init.then(fire(Hover(2))).then(fire(Wheel))
    .then(all {assert(s.keyboard==1 and s.wheel==2),fire(Key)})
    .then(all {assert(s.key==1),fire(Click)})
    .then(all {assert(s.keyboard==2),fire(Key)})
  run noWindowDoesNotStealFocusTest = init.then(fire(Hover(0))).then(fire(Wheel))
    .then(all {assert(s.wheel==0 and s.keyboard==1),fire(Click)})
    .then(all {assert(s.keyboard==1),fire(Key)})
}
