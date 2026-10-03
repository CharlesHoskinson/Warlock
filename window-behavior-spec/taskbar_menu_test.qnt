module taskbar_menu_test {
  import taskbar_menu.* from "./taskbar_menu"
  run keyboardWheelTest = init.then(fire(Open(true))).then(fire(Wheel(1)))
    .then(all {assert(menu.keyboard and menu.scroll==1),fire(Close)})
    .then(all {assert(not(menu.open) and not(menu.keyboard)),fire(Open(false))})
  run mouseWheelTest = init.then(fire(Open(false))).then(fire(Wheel(1)))
    .then(all {assert(menu.open and not(menu.keyboard) and menu.scroll==1),fire(Close)})
  run rapidReopenTest = init.then(fire(Open(true))).then(fire(Move(-1)))
    .then(all {assert(menu.selected==5 and menu.scroll==4),fire(Close)})
    .then(fire(Open(true)))
    .then(all {assert(menu.open and menu.keyboard and menu.scroll==0 and menu.selected==0),fire(Close)})
  run closedInputTest = init.then(fire(Wheel(1))).then(fire(Move(-1)))
    .then(all {assert(not(menu.open) and not(menu.keyboard) and menu.scroll==0),fire(Open(true))})
}
