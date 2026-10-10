module caption_gesture_test {
  import caption_gesture.* from "./caption-gesture"
  run captionMoveTest=init.then(press).then(fire(Move)).then(all {assert(acceptedMove and safety),s'=s}).then(fire(Release)).then(all {assert(releaseIdle and safety),s'=s})
  run edgeResizeTest=init.then(press).then(fire(Resize)).then(all {assert(acceptedResize and safety),s'=s})
  run noFocusAfterPressTest=init.then(press).then(fire(NoFocus)).then(fire(Move)).then(all {assert(noFocusRefused and safety),s'=s})
  run modalAfterPressTest=init.then(press).then(fire(Modal)).then(fire(Move)).then(all {assert(modalRefused and safety),s'=s})
  run protectedInputTest=init.then(press).then(fire(Protect)).then(fire(Resize)).then(all {assert(protectedRefused and safety),s'=s})
  run replacementCannotReceiveGestureTest=init.then(press).then(fire(Close)).then(fire(Reopen)).then(fire(Move)).then(all {assert(staleOwnerRefused and safety),s'=s})
  run refusedPressCannotReplayTest=init.then(press).then(fire(NoFocus)).then(fire(Move)).then(fire(Eligible)).then(fire(Move)).then(all {assert(consumedPressRefused and s.active==0 and safety),s'=s})
}
