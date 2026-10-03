/** Multiple-window contract for the taskbar and Snap Groups.
 * Window IDs model compositor addresses; app IDs model normalized desktop IDs.
 * Launcher pinning and always-on-top window pinning are independent state.
 * Minimize retains zone/workspace/pin state. Close and geometry/workspace changes
 * dissolve affected groups. Recall restores every member and focuses its owner.
 */
module desktop {
  type Win = { app: int, workspace: int, minimized: bool, pinned: bool, zone: int }
  type Group = { members: Set[int], workspace: int }
  type Event = Open(int) | Close(int) | Focus(int) | Minimize(int) | Restore(int)
             | PinWindow(int) | PinApp(int) | Reorder((int, int)) | Switch(int) | Move((int, int))
             | Snap((int, int)) | CreateGroup((int, int)) | AddMember((int, int)) | Recall(int)
  pure val IDS = Set(1, 2, 3, 4)
  pure val APPS = Set(1, 2, 3)
  pure val WORKSPACES = Set(1, 2, 3)
  pure val ZONES = Set(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
  pure def appFor(id: int): int = if (id <= 2) 1 else id - 1
  /** Twelve cells (six columns, two rows) distinguish half/third overlaps. */
  pure def slots(zone: int): Set[int] =
    if (zone == 1) Set(0, 1, 2, 6, 7, 8) else if (zone == 2) Set(3, 4, 5, 9, 10, 11)
    else if (zone == 3) Set(0, 1, 2) else if (zone == 4) Set(3, 4, 5)
    else if (zone == 5) Set(6, 7, 8) else if (zone == 6) Set(9, 10, 11)
    else if (zone == 8) Set(0, 1, 6, 7) else if (zone == 9) Set(2, 3, 8, 9)
    else if (zone == 10) Set(4, 5, 10, 11) else if (zone == 11) Set(0, 1, 2, 3, 6, 7, 8, 9)
    else if (zone == 12) Set(2, 3, 4, 5, 8, 9, 10, 11) else Set(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
  pure def complement(a: int, b: int): bool =
    a >= 1 and a <= 12 and a != 7 and b >= 1 and b <= 12 and b != 7 and
    slots(a).intersect(slots(b)).size() == 0
  pure def visible(w: Win, workspace: int): bool =
    not(w.minimized) and (w.pinned or w.workspace == workspace)

  var windows: int -> Win
  var groups: int -> Group
  var pinnedApps: Set[int]
  var activeWorkspace: int
  var focused: int
  var lastEvent: Event
  var owner: int
  var launchRequests: int

  pure def withoutMember(gs: int -> Group, id: int): int -> Group =
    gs.keys().filter(g => not(gs.get(g).members.contains(id)))
      .mapBy(g => gs.get(g))
  def validGroup(a: int, b: int): bool =
    a != b and windows.keys().contains(a) and windows.keys().contains(b) and
    not(windows.get(a).minimized) and not(windows.get(b).minimized) and
    windows.get(a).workspace == windows.get(b).workspace and
    complement(windows.get(a).zone, windows.get(b).zone)
  def appWindows(app: int): Set[int] =
    windows.keys().filter(id => windows.get(id).app == app)
  val taskbarApps = pinnedApps.union(windows.keys().map(id => windows.get(id).app))
  val groupedTaskbar = taskbarApps.mapBy(app => appWindows(app))

  action init = all {
    windows' = Map(
      1 -> { app: 1, workspace: 1, minimized: false, pinned: false, zone: 0 },
      2 -> { app: 1, workspace: 1, minimized: false, pinned: false, zone: 0 },
      3 -> { app: 2, workspace: 1, minimized: false, pinned: false, zone: 0 }
    ),
    groups' = Map(), pinnedApps' = Set(), activeWorkspace' = 1, focused' = 1,
    lastEvent' = Focus(1), owner' = 1, launchRequests' = 0,
  }

  def canFire(e: Event): bool = match e {
    | Open(id) => IDS.contains(id) and not(windows.keys().contains(id))
    | Close(id) => windows.keys().contains(id)
    | Focus(id) => windows.keys().contains(id) and visible(windows.get(id), activeWorkspace)
    | Minimize(id) => windows.keys().contains(id) and not(windows.get(id).minimized)
    | Restore(id) => windows.keys().contains(id)
    | PinWindow(id) => windows.keys().contains(id)
    | PinApp(app) => APPS.contains(app)
    | Reorder(pair) => pair._1 != pair._2 and taskbarApps.contains(pair._1) and taskbarApps.contains(pair._2)
    | Switch(ws) => WORKSPACES.contains(ws)
    | Move(pair) => windows.keys().contains(pair._1) and not(windows.get(pair._1).minimized) and WORKSPACES.contains(pair._2)
    | Snap(pair) => windows.keys().contains(pair._1) and not(windows.get(pair._1).minimized) and ZONES.contains(pair._2)
    | CreateGroup(pair) => validGroup(pair._1, pair._2)
    | AddMember(pair) => groups.keys().contains(pair._1) and windows.keys().contains(pair._2) and
        not(windows.get(pair._2).minimized) and not(groups.get(pair._1).members.contains(pair._2)) and
        groups.get(pair._1).members.forall(id => validGroup(id, pair._2))
    | Recall(g) => groups.keys().contains(g)
  }

  def nextWindows(e: Event): int -> Win = match e {
    | Open(id) => windows.put(id, { app: appFor(id), workspace: activeWorkspace, minimized: false, pinned: false, zone: 0 })
    | Close(id) => windows.keys().exclude(Set(id)).mapBy(w => windows.get(w))
    | Minimize(id) => windows.put(id, { ...windows.get(id), minimized: true })
    | Restore(id) => windows.put(id, { ...windows.get(id), minimized: false })
    | PinWindow(id) => windows.put(id, { ...windows.get(id), pinned: not(windows.get(id).pinned) })
    | Move(pair) => windows.put(pair._1, { ...windows.get(pair._1), workspace: pair._2 })
    | Snap(pair) => windows.put(pair._1, { ...windows.get(pair._1), zone: pair._2 })
    | Recall(g) => windows.keys().mapBy(id =>
        if (groups.get(g).members.contains(id)) { ...windows.get(id), minimized: false }
        else windows.get(id))
    | _ => windows
  }
  def nextGroups(e: Event): int -> Group = match e {
    | Close(id) => withoutMember(groups, id)
    | Move(pair) => withoutMember(groups, pair._1)
    | Snap(pair) => withoutMember(groups, pair._1)
    | CreateGroup(pair) => withoutMember(withoutMember(groups, pair._1), pair._2)
        .put(pair._1, { members: Set(pair._1, pair._2), workspace: windows.get(pair._1).workspace })
    | AddMember(pair) => withoutMember(groups, pair._2).put(pair._1,
        { ...groups.get(pair._1), members: groups.get(pair._1).members.union(Set(pair._2)) })
    | _ => groups
  }
  def nextWorkspace(e: Event): int = match e {
    | Switch(ws) => ws
    | Restore(id) => windows.get(id).workspace
    | Recall(g) => groups.get(g).workspace
    | _ => activeWorkspace
  }
  pure def eventOwner(e: Event): int = match e {
    | Open(id) => id | Close(id) => id | Focus(id) => id | Minimize(id) => id
    | Restore(id) => id | PinWindow(id) => id | Move(pair) => pair._1 | Snap(pair) => pair._1
    | CreateGroup(pair) => pair._1 | AddMember(pair) => pair._1 | Recall(g) => g | _ => 0
  }
  def nextFocus(e: Event, ws: int -> Win, workspace: int): int = {
    val requested = match e {
      | Open(id) => id | Focus(id) => id | Restore(id) => id | Recall(g) => g
      | _ => focused
    }
    if (ws.keys().contains(requested) and visible(ws.get(requested), workspace)) requested else 0
  }

  action fire(e: Event): bool = all {
    canFire(e),
    windows' = nextWindows(e), groups' = nextGroups(e),
    pinnedApps' = match e {
      | PinApp(app) => if (pinnedApps.contains(app)) pinnedApps.exclude(Set(app)) else pinnedApps.union(Set(app))
      | _ => pinnedApps
    },
    activeWorkspace' = nextWorkspace(e),
    focused' = nextFocus(e, nextWindows(e), nextWorkspace(e)),
    lastEvent' = e, owner' = eventOwner(e), launchRequests' = 0,
  }

  pure val EVENTS = IDS.map(id => Open(id)).union(IDS.map(id => Close(id)))
    .union(IDS.map(id => Focus(id))).union(IDS.map(id => Minimize(id)))
    .union(IDS.map(id => Restore(id))).union(IDS.map(id => PinWindow(id)))
    .union(tuples(APPS, APPS).map(pair => Reorder(pair)))
    .union(APPS.map(app => PinApp(app))).union(WORKSPACES.map(ws => Switch(ws)))
    .union(tuples(IDS, WORKSPACES).map(pair => Move(pair)))
    .union(tuples(IDS, ZONES).map(pair => Snap(pair)))
    .union(tuples(IDS, IDS).map(pair => CreateGroup(pair)))
    .union(tuples(IDS, IDS).map(pair => AddMember(pair)))
    .union(IDS.map(g => Recall(g)))
  action step = {
    nondet e = EVENTS.filter(event => canFire(event)).oneOf()
    fire(e)
  }

  val validState = WORKSPACES.contains(activeWorkspace) and pinnedApps.subseteq(APPS) and
    windows.keys().subseteq(IDS) and windows.keys().forall(id => all {
      windows.get(id).app == appFor(id), WORKSPACES.contains(windows.get(id).workspace),
      ZONES.contains(windows.get(id).zone)
    }) and (focused == 0 or (windows.keys().contains(focused) and visible(windows.get(focused), activeWorkspace)))
  val noStaleGroups = groups.keys().forall(g => all {
    groups.get(g).members.size() >= 2,
    groups.get(g).members.contains(g),
    groups.get(g).members.subseteq(windows.keys()),
    groups.get(g).members.forall(id => windows.get(id).workspace == groups.get(g).workspace),
    groups.get(g).members.forall(a => groups.get(g).members.forall(b => a == b or complement(windows.get(a).zone, windows.get(b).zone)))
  })
  val uniqueMembership = windows.keys().forall(id => groups.keys().filter(g => groups.get(g).members.contains(id)).size() <= 1)
  val taskbarCoherent = taskbarApps.subseteq(APPS) and taskbarApps.forall(app =>
    groupedTaskbar.get(app) == appWindows(app) and (pinnedApps.contains(app) or appWindows(app).size() > 0)) and
    windows.keys().forall(id => taskbarApps.contains(windows.get(id).app))
  val targetedFocus = match lastEvent {
    | Focus(id) => focused == id | Restore(id) => focused == id
    | Recall(g) => focused == g and groups.get(g).members.forall(id => not(windows.get(id).minimized))
    | _ => true
  }
  val pinDoesNotLaunch = launchRequests == 0
  val allProps = validState and noStaleGroups and uniqueMembership and taskbarCoherent and targetedFocus and pinDoesNotLaunch
}
