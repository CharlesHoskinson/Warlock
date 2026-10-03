module drag_hover_test {
  import drag_hover.* from "./drag_hover"
  run minimizedSingleDwellTest=init.then(fire(App(1))).then(all{assert(s.activated==0),fire(Dwell)}).then(all{assert(s.offered and s.activated==0),fire(Dwell)}).then(all{assert(s.activated==1),fire(Dwell)}).then(all{assert(s.activated==0),fire(Leave)})
  run earlyLeaveCancelsTest=init.then(fire(App(1))).then(fire(Dwell)).then(fire(Leave)).then(fire(Dwell)).then(all{assert(s.activated==0),fire(Drop)})
  run groupedChooserTest=init.then(fire(App(0))).then(fire(Dwell)).then(fire(Dwell)).then(all{assert(s.offered and s.activated==0),fire(Preview(2))}).then(fire(Dwell)).then(all{assert(s.activated==2),fire(Leave)})
  run reusedWindowCannotActivateTest=init.then(fire(App(1))).then(fire(Dwell)).then(fire(Close(1))).then(fire(Reuse(1))).then(fire(Dwell)).then(all{assert(s.activated==0),fire(Leave)})
  run droppedFileNeverConsumedTest=init.then(fire(Preview(2))).then(fire(Drop)).then(fire(Dwell)).then(all{assert(not(s.consumed) and s.activated==0),fire(Leave)})
  run emptyPinnedLauncherCannotActivateTest=init.then(fire(App(-1))).then(fire(Dwell)).then(fire(Dwell)).then(all{assert(not(s.offered) and s.activated==0),fire(Drop)})
}
