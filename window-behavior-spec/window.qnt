/**
 * One-window Windows-like behavior contract. Coordinates are abstract screen units.
 * The model describes intended UI behavior, not Hyprland commands or configuration.
 * A drag is StartDrag, zero or more MoveTo events, then Release or cancellation.
 */
module window {
  type Mode = Normal | Snapped | Maximized | Minimized
  type Zone = Center | Left | Right | Top | TopLeft | TopRight | BottomLeft | BottomRight
    | ThirdLeft | ThirdCenter | ThirdRight | TwoThirdsLeft | TwoThirdsRight
  type Event = StartDrag | MoveTo(Zone) | Release | Place(Rect) | Maximize | Minimize | Restore
             | TogglePin | Focus | Blur | SwitchTo(int) | MoveWindowTo(int) | Choose(Zone) | ResizeMonitor(int)
  type Rect = { x: int, y: int, width: int, height: int }
  type Window = {
    mode: Mode,
    rect: Rect,
    normalRect: Rect,
    beforeMinimize: Mode,
    beforeMinimizeRect: Rect,
    snapZone: Zone,
    dragging: bool,
    candidate: Zone,
    focused: bool,
    pinned: bool,
    workspace: int,
  }

  pure val HOME: Rect = { x: 15, y: 15, width: 60, height: 60 }
  pure val OTHER: Rect = { x: 25, y: 20, width: 45, height: 55 }
  pure val FULL: Rect = { x: 0, y: 0, width: 100, height: 100 }
  pure def zoneRect(z: Zone): Rect = match z {
    | Left => { x: 0, y: 0, width: 50, height: 100 }
    | Right => { x: 50, y: 0, width: 50, height: 100 }
    | TopLeft => { x: 0, y: 0, width: 50, height: 50 }
    | TopRight => { x: 50, y: 0, width: 50, height: 50 }
    | BottomLeft => { x: 0, y: 50, width: 50, height: 50 }
    | BottomRight => { x: 50, y: 50, width: 50, height: 50 }
    | ThirdLeft => { x: 0, y: 0, width: 33, height: 100 }
    | ThirdCenter => { x: 33, y: 0, width: 33, height: 100 }
    | ThirdRight => { x: 66, y: 0, width: 34, height: 100 }
    | TwoThirdsLeft => { x: 0, y: 0, width: 66, height: 100 }
    | TwoThirdsRight => { x: 33, y: 0, width: 67, height: 100 }
    | Top => FULL
    | Center => HOME
  }
  pure def visible(win: Window, active: int): bool =
    win.mode != Minimized and (win.pinned or win.workspace == active)

  pure val BASE_ZONES = Set(Left, Right, TopLeft, TopRight, BottomLeft, BottomRight)
  pure val EXTENDED_ZONES = Set(ThirdLeft, ThirdCenter, ThirdRight, TwoThirdsLeft, TwoThirdsRight)
  /** Product contract: extended choices appear at >=1280 logical pixels.
   * This threshold specifies our implementation, not undocumented Windows internals. */
  pure def availableZones(width: int): Set[Zone] = BASE_ZONES.union(Set(Top)).union(
    if (width >= 1280) EXTENDED_ZONES else Set())
  /** Family IDs: halves, quarters, two mixed half/quarter layouts,
   * three thirds, and two asymmetric layouts. */
  pure def familyZones(family: int): Set[Zone] =
    if (family == 1) Set(Left, Right)
    else if (family == 2) Set(TopLeft, TopRight, BottomLeft, BottomRight)
    else if (family == 3) Set(Left, TopRight, BottomRight)
    else if (family == 4) Set(TopLeft, BottomLeft, Right)
    else if (family == 5) Set(ThirdLeft, ThirdCenter, ThirdRight)
    else if (family == 6) Set(TwoThirdsLeft, ThirdRight) else Set(ThirdLeft, TwoThirdsRight)
  pure def availableFamilies(width: int): Set[int] = Set(1, 2, 3, 4).union(
    if (width >= 1280) Set(5, 6, 7) else Set())
  pure def overlaps(a: Rect, b: Rect): bool =
    a.x < b.x + b.width and b.x < a.x + a.width and a.y < b.y + b.height and b.y < a.y + a.height
  var logicalWidth: int
  var w: Window
  var activeWorkspace: int
  var lastEvent: Event
  /** 0 or 1. This records the number of snap commands emitted by the last transition. */
  var snapsThisStep: int
  /** The candidate at the last Release, for a property about that transition. */
  var releasedCandidate: Zone

  action init = all {
    w' = {
      mode: Normal, rect: HOME, normalRect: HOME,
      beforeMinimize: Normal, beforeMinimizeRect: HOME,
      snapZone: Center, dragging: false, candidate: Center,
      focused: true, pinned: false, workspace: 1,
    },
    activeWorkspace' = 1, logicalWidth' = 1280,
    lastEvent' = Focus,
    snapsThisStep' = 0,
    releasedCandidate' = Center,
  }

  pure def canFire(win: Window, active: int, e: Event): bool = match e {
    | Choose(z) => z != Center and visible(win, active) and not(win.dragging)
    | ResizeMonitor(width) => width >= 800 and width <= 2560
    | StartDrag => win.focused and visible(win, active) and not(win.dragging)
    | MoveTo(_) => win.dragging
    | Release => win.dragging
    | Place(_) => win.mode == Normal and not(win.dragging)
    | Maximize => visible(win, active) and not(win.dragging)
    | Minimize => win.mode != Minimized
    | Restore => win.mode != Normal and not(win.dragging)
    | TogglePin => true
    | Focus => visible(win, active)
    | Blur => true
    | SwitchTo(n) => n >= 1 and n <= 3
    | MoveWindowTo(n) => n >= 1 and n <= 3
  }

  pure def apply(win: Window, active: int, e: Event): Window = match e {
    // A snapped/maximized window becomes normal at the saved position as soon
    // as the drag begins. Moving over an edge only changes the preview.
    | StartDrag => {
        ...win,
        mode: Normal,
        rect: if (win.mode == Normal) win.rect else win.normalRect,
        snapZone: Center,
        dragging: true,
        candidate: Center,
      }
    | Choose(z) => {
        ...win, mode: if (z == Top) Maximized else Snapped,
        normalRect: if (win.mode == Normal) win.rect else win.normalRect,
        rect: zoneRect(z), snapZone: z,
      }
    | ResizeMonitor(_) => win
    | MoveTo(z) => { ...win, candidate: z }
    | Release => {
        ...win,
        mode: if (win.candidate == Top) Maximized
              else if (win.candidate == Center) Normal else Snapped,
        rect: if (win.candidate == Center) win.rect else zoneRect(win.candidate),
        snapZone: win.candidate,
        dragging: false,
        candidate: Center,
      }
    | Place(r) => { ...win, rect: r, normalRect: r }
    | Maximize => {
        ...win,
        mode: Maximized,
        normalRect: if (win.mode == Normal) win.rect else win.normalRect,
        rect: FULL,
        snapZone: Top,
      }
    | Minimize => {
        ...win,
        mode: Minimized,
        beforeMinimize: win.mode,
        beforeMinimizeRect: win.rect,
        focused: false,
        dragging: false,
        candidate: Center,
      }
    | Restore =>
        if (win.mode == Minimized) {
          ...win,
          mode: win.beforeMinimize,
          rect: win.beforeMinimizeRect,
          focused: false,
        } else {
          ...win,
          mode: Normal,
          rect: win.normalRect,
          snapZone: Center,
        }
    | TogglePin => {
        ...win,
        pinned: not(win.pinned),
        focused: if (win.pinned and win.workspace != active) false else win.focused,
        dragging: if (win.pinned and win.workspace != active) false else win.dragging,
        candidate: if (win.pinned and win.workspace != active) Center else win.candidate,
      }
    | Focus => { ...win, focused: true, dragging: false, candidate: Center }
    | Blur => { ...win, focused: false, dragging: false, candidate: Center }
    | SwitchTo(n) => {
        ...win,
        focused: if (win.pinned or win.workspace == n) win.focused else false,
        dragging: false,
        candidate: Center,
      }
    | MoveWindowTo(n) => {
        ...win,
        workspace: n,
        focused: if (win.pinned or active == n) win.focused else false,
        dragging: false,
        candidate: Center,
      }
  }

  pure def canFireAt(win: Window, active: int, width: int, e: Event): bool =
    canFire(win, active, e) and match e {
      | Choose(z) => availableZones(width).contains(z) | _ => true
    }
  action fire(e: Event): bool = all {
    canFireAt(w, activeWorkspace, logicalWidth, e),
    logicalWidth' = match e { | ResizeMonitor(width) => width | _ => logicalWidth },
    w' = apply(w, activeWorkspace, e),
    activeWorkspace' = match e { | SwitchTo(n) => n | _ => activeWorkspace },
    lastEvent' = e,
    snapsThisStep' = match e {
      | Choose(_) => 1 | Release => if (w.candidate != Center) 1 else 0 | _ => 0
    },
    releasedCandidate' = match e { | Choose(z) => z | Release => w.candidate | _ => Center },
  }

  pure val EVENTS: Set[Event] = Set(
    Choose(Left), Choose(Right), Choose(Top), Choose(TopLeft), Choose(TopRight),
    Choose(BottomLeft), Choose(BottomRight), Choose(ThirdLeft), Choose(ThirdCenter), Choose(ThirdRight),
    Choose(TwoThirdsLeft), Choose(TwoThirdsRight),
    ResizeMonitor(800), ResizeMonitor(1279), ResizeMonitor(1280), ResizeMonitor(1600), ResizeMonitor(1920), ResizeMonitor(2560),
    StartDrag, MoveTo(Center), MoveTo(Left), MoveTo(Right), MoveTo(Top), Release,
    Place(HOME), Place(OTHER),
    Maximize, Minimize, Restore, TogglePin, Focus, Blur,
    SwitchTo(1), SwitchTo(2), SwitchTo(3),
    MoveWindowTo(1), MoveWindowTo(2), MoveWindowTo(3),
  )
  action step = {
    nondet e = EVENTS.filter(event => canFireAt(w, activeWorkspace, logicalWidth, event)).oneOf()
    fire(e)
  }

  val validState: bool =
    w.workspace >= 1 and w.workspace <= 3 and
    activeWorkspace >= 1 and activeWorkspace <= 3 and
    (w.mode == Normal implies w.snapZone == Center) and
    (w.mode == Snapped implies BASE_ZONES.union(EXTENDED_ZONES).contains(w.snapZone)) and
    (w.mode == Maximized implies w.snapZone == Top) and
    (w.mode == Normal implies w.rect == w.normalRect) and
    (w.mode == Minimized implies not(w.focused)) and
    (w.focused implies visible(w, activeWorkspace)) and
    (w.dragging implies w.mode == Normal and w.focused) and
    (not(w.dragging) implies w.candidate == Center)

  pure def isCommit(e: Event): bool = match e { | Choose(_) => true | Release => true | _ => false }
  /** The edge preview cannot apply a snap before Release; a chooser selection commits directly. */
  val noSnapBeforeRelease: bool =
    (not(isCommit(lastEvent)) implies snapsThisStep == 0) and
    (w.dragging implies w.mode == Normal and snapsThisStep == 0)

  /** An edge release issues exactly one snap; a center release issues none. */
  val oneSnapOnRelease: bool =
    (isCommit(lastEvent) implies
      snapsThisStep == (if (releasedCandidate == Center) 0 else 1)) and
    snapsThisStep >= 0 and snapsThisStep <= 1

  /** Saved normal size and position survive snap/maximize and dragging away. */
  val restoreGeometry: bool =
    ((w.mode == Snapped or w.mode == Maximized) implies w.rect == zoneRect(w.snapZone)) and
    (w.dragging implies w.rect == w.normalRect)

  pure def focusChange(e: Event): bool = match e {
    | Focus => true
    | Blur => true
    | SwitchTo(_) => true
    | MoveWindowTo(_) => true
    | _ => false
  }
  val noStaleDragAfterFocusChange: bool =
    ((focusChange(lastEvent) or not(w.focused)) implies not(w.dragging) and w.candidate == Center)

  val workspaceAndPin: bool =
    (w.focused implies w.pinned or w.workspace == activeWorkspace) and
    (w.pinned and w.mode != Minimized implies visible(w, activeWorkspace))

  val layoutSelection: bool = logicalWidth >= 800 and logicalWidth <= 2560 and
    match lastEvent { | Choose(z) => availableZones(logicalWidth).contains(z) | _ => true }
  val layoutFamilies: bool = availableFamilies(logicalWidth).forall(family => all {
    familyZones(family).subseteq(availableZones(logicalWidth)),
    familyZones(family).fold(0, (area, zone) => area + zoneRect(zone).width * zoneRect(zone).height) == FULL.width * FULL.height,
    familyZones(family).forall(a => familyZones(family).forall(b => a == b or not(overlaps(zoneRect(a), zoneRect(b)))))
  })
  val allProps: bool = layoutFamilies and layoutSelection and validState and noSnapBeforeRelease and oneSnapOnRelease and
                       restoreGeometry and noStaleDragAfterFocusChange and workspaceAndPin
}
