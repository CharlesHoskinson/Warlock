// launcher.qnt — model of the Files bar icon + explorer window lifecycle
//
// Code modelled:
//   ~/.config/omarchy/plugins/hoskinson.files/icon/FilesButton.qml  (click -> `omarchy-files <target>`)
//   ~/.local/bin/omarchy-files                                      (IPC open, else start qs; then summon)
//   explorer/Explorer.qml + shell.qml                               (FloatingWindow `visible`, openAt, onClosed)
//
// Three independent facts about the app can disagree, and that is the whole
// model:
//   procUp      the `qs -p omarchy-files` process is running
//   qmlVisible  the QML-side `visible` property of the FloatingWindow
//   mapped      Hyprland really has a "Files" client
// Quickshell maps a window only on a false -> true transition of `visible`;
// assigning `true` while it is already `true` is a no-op. That is exactly how a
// window closed by the user (mapped -> false, qmlVisible stays true) becomes
// impossible to reopen: the bug fixed on 2026-09-30 by `onClosed: visible = false`.
//
// `FIXED` selects the code: false = before the fix, true = after.
//
// The window's whereabouts are relative to the focused workspace, because
// `summon` only cares about "same workspace as focus or not":
//   Here      on the focused workspace
//   Elsewhere on another workspace (user switched workspace / moved it)
//   Scratch   minimized into the special:win-minimized scratchpad
//
// Not modelled (on purpose): focus, geometry, the 2 s summon poll (a cold start
// that takes > 2 s still ends with a mapped window, only un-summoned), the
// explorer's content, hover animation. `view` is the page openAt lands on.
module launcher {
  const FIXED: bool

  type Place = Here | Elsewhere | Scratch
  type Op = Boot | Click | UserClose | MoveAway | Minimize | Crash

  pure val HOME = "home"
  pure val RECENT = "coll:recent"
  pure val TARGETS = Set(HOME, RECENT)       // left click = Home, right click = Recent

  var procUp: bool
  var qmlVisible: bool
  var mapped: bool
  var place: Place
  var view: str

  // ghost: which action just ran, and with which target (for postconditions)
  var lastOp: Op
  var lastTarget: str

  // ------------------------------------------------------------ pure logic
  type Win = { procUp: bool, qmlVisible: bool, mapped: bool, place: Place, view: str }

  // `omarchy-files <target>`: IPC open if the process is up, else start it with
  // FILES_OPEN; then `summon` pulls a mapped window onto the focused workspace.
  pure def click(w: Win, target: str): Win = {
    if (not(w.procUp))
      // Shell.qml Component.onCompleted -> openAt: visible = true (false -> true, maps)
      { procUp: true, qmlVisible: true, mapped: true, place: Here, view: target }
    else {
      // IPC open -> openAt: view changes, visible = true
      val newlyMapped = not(w.qmlVisible)            // only false -> true maps a window
      val mapped2 = w.mapped or newlyMapped
      val place2 = if (newlyMapped) Here else w.place
      // summon: if a window exists, move it to the focused workspace
      { procUp: true, qmlVisible: true, mapped: mapped2,
        place: if (mapped2) Here else place2, view: target }
    }
  }

  // the user closes the window (X button / compositor close)
  pure def userClose(w: Win): Win =
    { ...w, mapped: false, qmlVisible: if (FIXED) false else w.qmlVisible }

  // ---------------------------------------------------------------- actions
  action init: bool = all {
    procUp' = false, qmlVisible' = false, mapped' = false, place' = Here, view' = HOME,
    lastOp' = Boot, lastTarget' = HOME,
  }

  def win: Win = { procUp: procUp, qmlVisible: qmlVisible, mapped: mapped, place: place, view: view }

  action setWin(w: Win): bool = all {
    procUp' = w.procUp, qmlVisible' = w.qmlVisible, mapped' = w.mapped,
    place' = w.place, view' = w.view,
  }

  action clickAction(target: str): bool = all {
    setWin(click(win, target)),
    lastOp' = Click, lastTarget' = target,
  }

  action closeAction: bool = all {
    mapped,
    setWin(userClose(win)),
    lastOp' = UserClose, lastTarget' = lastTarget,
  }

  action moveAwayAction: bool = all {
    mapped, place == Here,
    setWin({ ...win, place: Elsewhere }),
    lastOp' = MoveAway, lastTarget' = lastTarget,
  }

  action minimizeAction: bool = all {
    mapped, place != Scratch,
    setWin({ ...win, place: Scratch }),
    lastOp' = Minimize, lastTarget' = lastTarget,
  }

  // the process dies (kill, crash, session restart): window and flag go with it
  action crashAction: bool = all {
    procUp,
    setWin({ procUp: false, qmlVisible: false, mapped: false, place: Here, view: view }),
    lastOp' = Crash, lastTarget' = lastTarget,
  }

  action step: bool = {
    nondet t = TARGETS.oneOf()
    any {
      clickAction(t),
      closeAction,
      moveAwayAction,
      minimizeAction,
      crashAction,
    }
  }

  // ------------------------------------------------------------- invariants
  // (1) While the app runs, what QML believes matches what the compositor shows.
  val flagMatchesWindow: bool = procUp implies (qmlVisible == mapped)

  // (2) No process, no window.
  val noGhostWindow: bool = (not(procUp)) implies (not(mapped) and not(qmlVisible))

  // (3) THE user-facing property: after a click there is a Files window, on the
  //     focused workspace, showing the page that was asked for.
  val clickOpensWindow: bool =
    lastOp == Click implies (procUp and mapped and place == Here and view == lastTarget)

  val allInvariants: bool = flagMatchesWindow and noGhostWindow and clickOpensWindow

  // --------------------------------------------------------------- witnesses
  val wColdStart: bool = lastOp == Click and mapped and procUp and view == HOME
  val wRecent: bool = lastOp == Click and mapped and view == RECENT
  val wReopenAfterClose: bool = lastOp == Click and mapped and place == Here and qmlVisible
    and lastTarget == RECENT   // reached from any prior state incl. a closed window
  val wClosed: bool = lastOp == UserClose and procUp and not(mapped)
  val wSummonedFromScratch: bool = lastOp == Click and mapped and place == Here
  val wCrashed: bool = lastOp == Crash and not(procUp)
}

// Code before the fix (no onClosed handler) and code after it.
module launcherBuggy { import launcher(FIXED = false).* }
module launcherFixed { import launcher(FIXED = true).* }
