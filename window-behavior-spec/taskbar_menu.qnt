/** Taskbar menu lifecycle and bounded viewport. Input shares one surface. */
module taskbar_menu {
  type Event = Open(bool) | Close | Move(int) | Wheel(int)
  var menu: {open: bool, keyboard: bool, selected: int, scroll: int}
  pure val ROWS = 6
  pure val VIEWPORT = 2
  pure def clamp(x: int): int = if (x < 0) 0 else if (x > ROWS - VIEWPORT) ROWS - VIEWPORT else x
  pure def reveal(selected: int, scroll: int): int =
    if (selected < scroll) selected
    else if (selected >= scroll + VIEWPORT) selected - VIEWPORT + 1
    else scroll
  action init = menu' = {open:false, keyboard:false, selected:0, scroll:0}
  action fire(event: Event): bool = menu' = match event {
    | Open(keyboard) => {open:true, keyboard:keyboard, selected:0, scroll:0}
    | Close => {...menu, open:false, keyboard:false}
    | Move(step) => if (menu.open and menu.keyboard) {
        val selected = (menu.selected + step + ROWS) % ROWS
        {...menu, selected:selected, scroll:reveal(selected,menu.scroll)}
      } else menu
    | Wheel(step) => if (menu.open) {...menu,scroll:clamp(menu.scroll+step)} else menu
  }
  pure val EVENTS = Set(Open(true),Open(false),Close,Move(1),Move(-1),Wheel(1),Wheel(-1))
  action step = { nondet event = EVENTS.oneOf(); fire(event) }
  val allProps = (menu.keyboard implies menu.open)
    and menu.selected >= 0 and menu.selected < ROWS
    and menu.scroll >= 0 and menu.scroll <= ROWS - VIEWPORT
}
