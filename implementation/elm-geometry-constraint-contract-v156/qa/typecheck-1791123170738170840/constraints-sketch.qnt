// Types only: awaiting explicit sketch approval before functional/transition logic.
// One serialized native authority owns state. Native callbacks are distinct
// environment observations; browser transport stays in the existing models.
module constraints_sketch {
  type Identity = { lifetime: int, incarnation: int }
  type Size = { width: int, height: int }
  type Rect = { x: int, y: int, width: int, height: int }
  type Upper = Unbounded | Bounded(int)
  type Limits = { minimum: Size, maximumWidth: Upper, maximumHeight: Upper }
  // Limits are normalized to the native logical target coordinate space.
  // Invalid/nonfinite/unconvertible source measurements are explicit failure.
  type BoundObservation = MissingBounds | InvalidBounds | ObservedBounds(Limits)
  type Constraints = {
    client: BoundObservation, layout: BoundObservation, revision: int
  }
  type Mode = Ordinary | Maximized | Fullscreen
  type Window = {
    identity: Identity, live: bool, baseEligible: bool,
    constraints: Constraints, logical: Rect, visual: Rect,
    nativeMode: Mode, clientMode: Mode, workspace: int, output: int,
    outputGeneration: int, workAreaRevision: int, dependencyRevision: int
  }
  type Placement = {
    target: Identity, logical: Rect, visual: Rect,
    workspace: int, output: int, outputGeneration: int, workAreaRevision: int
  }
  type Output = {
    live: bool, generation: int, workAreaRevision: int, workArea: Rect
  }
  type Operation = Maximize | RestoreGeometry
  type RequestKey = {
    target: Identity, frontend: int, session: int,
    request: int, generation: int, operation: Operation
  }
  type Dependency = {
    constraintRevision: int, sceneRevision: int,
    outputGeneration: int, workAreaRevision: int
  }
  type Phase = Admitted | NativeAttempted | ReadBack | AwaitingClient
  type Outcome = Pending | Unknown | Committed | Refused
  type Transaction = {
    key: RequestKey, dependency: Dependency, desired: Rect,
    phase: Phase, outcome: Outcome, mutations: int,
    before: Window, peersBefore: Identity -> Window,
    configureSerial: int, acknowledgedSerial: int, presented: bool
  }
  type State = {
    lifetime: int, windows: Identity -> Window, outputs: int -> Output,
    placements: Identity -> Placement, knownPlacements: Set[Identity],
    transactions: RequestKey -> Transaction, unresolved: Set[Identity],
    focused: Identity, keyboardRecipient: Identity, pointerRecipient: Identity,
    sceneRevision: int, locked: bool, exclusiveInput: bool,
    protectedGrab: bool, dragging: bool, exhausted: bool
  }
  var state: State
}
