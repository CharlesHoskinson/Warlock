/** Intended Windows-like desktop navigation and focus contract.
 * This is model QA; platform wiring is audited separately in requirements.md.
 * Peek changes presentation. Show Desktop hides windows and restores focus.
 * Minimize batches never restore windows that were already minimized.
 * Alt+Tab commits on release, and a modal child owns its parent's focus.
 */
module navigation {
  type Event = Focus(int) | Minimize(int) | Restore(int) | MinimizeAll | Shake(int)
    | RestoreBatch | ToggleDesktop | Peek(bool) | BeginTab | NextTab | CommitTab | CancelTab
    | NewDesktop(int) | CloseDesktop | SwitchDesktop(int) | Move((int, int)) | ToggleModal | Scope(bool)
  pure val IDS = Set(1, 2, 3, 4)
  pure val DESKTOPS = Set(1, 2, 3, 4)
  pure def first(s: Set[int]): int = s.fold(99, (a, b) => if (a < b) a else b)
  var desktops: Set[int]
  var workspace: int -> int
  var minimized: Set[int]
  var batchByDesktop: int -> Set[int]
  var active: int
  var focused: int
  var shownDesktops: Set[int]
  var peekDesktops: Set[int]
  var savedFocusByDesktop: int -> int
  var tabbing: bool
  var candidate: int
  var modal: bool
  var lastEvent: Event
  var lastBatch: Set[int]
  var priorMinimized: Set[int]
  var tabScopeAll: bool

  val batch = batchByDesktop.get(active)
  val showDesktop = shownDesktops.contains(active)
  val peeking = peekDesktops.contains(active)
  val savedFocus = savedFocusByDesktop.get(active)
  def owner(id: int): int = if (modal and id == 1) 4 else id
  def family(id: int): Set[int] = if (modal and (id == 1 or id == 4)) Set(1, 4) else Set(id)
  val restoreFamilyBatch = batch.fold(Set(), (members, id) => members.union(family(id)))
  def windowExists(id: int): bool = IDS.contains(id) and (id != 4 or modal)
  def onDesktop(id: int): bool = windowExists(id) and workspace.get(id) == active
  def available(id: int): bool = onDesktop(id) and not(minimized.contains(id))
  val tabCandidates = IDS.filter(id => windowExists(id) and (tabScopeAll or onDesktop(id)) and (not(modal) or id != 1))

  action init = all {
    desktops' = Set(1, 2), workspace' = Map(1 -> 1, 2 -> 1, 3 -> 2, 4 -> 1),
    minimized' = Set(), batchByDesktop' = DESKTOPS.mapBy(id => Set()), active' = 1, focused' = 1,
    shownDesktops' = Set(), peekDesktops' = Set(), savedFocusByDesktop' = DESKTOPS.mapBy(id => if (id == 1) 1 else 0),
    tabbing' = false, candidate' = 0, modal' = false,
    lastEvent' = Focus(1), lastBatch' = Set(), priorMinimized' = Set(),
    tabScopeAll'=false,
  }
  def canFire(e: Event): bool = match e {
    | Focus(id) => onDesktop(id)
    | Minimize(id) => windowExists(id)
    | Restore(id) => windowExists(id)
    | MinimizeAll => true
    | Shake(id) => available(id)
    | RestoreBatch => true
    | ToggleDesktop => true
    | Peek(_) => true
    | BeginTab => not(tabbing) and tabCandidates.size() > 0
    | NextTab => tabbing
    | CommitTab => tabbing and tabCandidates.contains(candidate)
    | CancelTab => tabbing
    | NewDesktop(ws) => DESKTOPS.contains(ws) and not(desktops.contains(ws))
    | CloseDesktop => desktops.size() > 1
    | SwitchDesktop(ws) => desktops.contains(ws)
    | Move(pair) => windowExists(pair._1) and desktops.contains(pair._2)
    | ToggleModal => true
    | Scope(_) => not(tabbing)
  }
  def nextBatch(e: Event): Set[int] = match e {
    | MinimizeAll => IDS.filter(id => onDesktop(id) and not(minimized.contains(id)))
    | Shake(id) => IDS.filter(w => onDesktop(w) and owner(w) != owner(id) and not(minimized.contains(w)))
    | RestoreBatch => Set() | CloseDesktop => Set()
    | _ => batch
  }
  def nextMinimized(e: Event): Set[int] = match e {
    | Minimize(id) => minimized.union(family(id))
    | Restore(id) => minimized.exclude(family(id))
    | MinimizeAll => minimized.union(nextBatch(e))
    | Shake(_) => minimized.union(nextBatch(e))
    | RestoreBatch => minimized.exclude(restoreFamilyBatch)
    | Focus(id) => minimized.exclude(family(id))
    | CommitTab => minimized.exclude(family(candidate))
    | ToggleModal => if (not(modal) and minimized.contains(1)) minimized.union(Set(4)) else minimized.exclude(Set(4))
    | _ => minimized
  }
  def nextWorkspace(e: Event): int -> int = match e {
    | Move(pair) => workspace.put(pair._1, pair._2)
        .put(if (modal and (pair._1 == 1 or pair._1 == 4)) 1 else pair._1, pair._2)
        .put(if (modal and (pair._1 == 1 or pair._1 == 4)) 4 else pair._1, pair._2)
    | CloseDesktop => {
        val target = first(desktops.exclude(Set(active)))
        workspace.keys().mapBy(id => if (workspace.get(id) == active) target else workspace.get(id))
      }
    | ToggleModal => if (modal) workspace else workspace.put(4, workspace.get(1))
    | _ => workspace
  }
  def nextActive(e: Event): int = match e {
    | NewDesktop(ws) => ws | SwitchDesktop(ws) => ws
    | CloseDesktop => first(desktops.exclude(Set(active)))
    | Restore(id) => workspace.get(id)
    | CommitTab => workspace.get(owner(candidate))
    | _ => active
  }
  def nextShown(e: Event): Set[int] = match e {
    | ToggleDesktop => if (showDesktop) shownDesktops.exclude(Set(active)) else shownDesktops.union(Set(active))
    | Focus(_) => shownDesktops.exclude(Set(nextActive(e)))
    | Restore(_) => shownDesktops.exclude(Set(nextActive(e)))
    | CommitTab => shownDesktops.exclude(Set(nextActive(e)))
    | CloseDesktop => shownDesktops.exclude(Set(active))
    | _ => shownDesktops
  }
  def nextShowDesktop(e: Event): bool = nextShown(e).contains(nextActive(e))
  def nextFocus(e: Event): int = {
    val target = match e {
      | Focus(id) => owner(id) | Restore(id) => owner(id) | CommitTab => owner(candidate)
      | ToggleDesktop => if (showDesktop) owner(savedFocus) else 0
      | ToggleModal => if (modal and focused == 4) 1 else if (not(modal) and focused == 1) 4 else focused
      | _ => focused
    }
    val live = target != 0 and IDS.contains(target) and (target != 4 or (if (e == ToggleModal) not(modal) else modal))
    if (live and nextWorkspace(e).get(target) == nextActive(e) and not(nextMinimized(e).contains(target)) and not(nextShowDesktop(e))) target else 0
  }
  action fire(e: Event): bool = all {
    canFire(e), desktops' = match e {
      | NewDesktop(ws) => desktops.union(Set(ws)) | CloseDesktop => desktops.exclude(Set(active)) | _ => desktops
    },
    workspace' = nextWorkspace(e), active' = nextActive(e), minimized' = nextMinimized(e),
    batchByDesktop' = batchByDesktop.put(active, nextBatch(e)), focused' = nextFocus(e), shownDesktops' = nextShown(e),
    savedFocusByDesktop' = if (e == ToggleDesktop and not(showDesktop)) savedFocusByDesktop.put(active, focused)
      else if (e == CloseDesktop) savedFocusByDesktop.put(active, 0) else savedFocusByDesktop,
    peekDesktops' = match e {
      | Peek(value) => if (value) peekDesktops.union(Set(active)) else peekDesktops.exclude(Set(active))
      | CloseDesktop => peekDesktops.exclude(Set(active)) | _ => peekDesktops
    },
    tabbing' = match e { | BeginTab => true | NextTab => true | _ => false },
    candidate' = match e {
      | BeginTab => first(tabCandidates)
      | NextTab => { val later=tabCandidates.filter(id => id>candidate); if(later.size()>0) first(later) else first(tabCandidates) }
      | _ => 0
    },
    modal' = if (e == ToggleModal) not(modal) else modal,
    tabScopeAll' = match e { | Scope(value) => value | _ => tabScopeAll },
    lastEvent' = e, lastBatch' = restoreFamilyBatch, priorMinimized' = minimized,
  }
  pure val EVENTS = IDS.map(id => Focus(id)).union(IDS.map(id => Minimize(id)))
    .union(IDS.map(id => Restore(id))).union(IDS.map(id => Shake(id)))
    .union(DESKTOPS.map(ws => NewDesktop(ws))).union(DESKTOPS.map(ws => SwitchDesktop(ws)))
    .union(tuples(IDS, DESKTOPS).map(pair => Move(pair)))
    .union(Set(MinimizeAll, RestoreBatch, ToggleDesktop, Peek(true), Peek(false), BeginTab, NextTab, CommitTab, CancelTab, CloseDesktop, ToggleModal, Scope(true), Scope(false)))
  action step = { nondet e = EVENTS.filter(event => canFire(event)).oneOf(); fire(e) }
  val coherent = shownDesktops.subseteq(desktops) and peekDesktops.subseteq(desktops) and desktops.size() > 0 and desktops.subseteq(DESKTOPS) and desktops.contains(active) and
    workspace.keys().forall(id => desktops.contains(workspace.get(id))) and
    (focused == 0 or (available(focused) and not(showDesktop))) and
    (not(tabbing) implies candidate == 0) and (tabbing implies tabCandidates.contains(candidate)) and
    (modal implies workspace.get(4) == workspace.get(1) and focused != 1 and minimized.contains(1) == minimized.contains(4))
  val batchRestoration = lastEvent == RestoreBatch implies minimized == priorMinimized.exclude(lastBatch)
  val peekKeepsMinimize = match lastEvent { | Peek(_) => minimized == priorMinimized | _ => true }
  val allProps = coherent and batchRestoration and peekKeepsMinimize
}
