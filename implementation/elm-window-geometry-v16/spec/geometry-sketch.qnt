// Proposed authority types only; no logic before explicit sketch approval.
// One serialized compositor authority owns shared window/placement/journal state.
// Requests are API inputs, not additional independently scheduled model actors.
// Dispatch, native mutation/readback and later client/presentation observations
// remain separate facts. This sketch does not model browser transport or GPU code.
module geometry_sketch {
  type Identity = { lifetime: int, incarnation: int }
  type Rect = { x: int, y: int, width: int, height: int }
  type Geometry = { logical: Rect, visual: Rect }
  type Output = { identity: int, generation: int, workArea: Rect, workAreaRevision: int, live: bool }
  type NativeMode = Ordinary | Maximized | Fullscreen
  type WindowClass = Floating | Tiled | Grouped | Transient
  type Focus = NoWindow | WindowFocus(Identity)
  type PlacementOrigin = Recorded(Geometry) | NativeFallback
  type Window = {
    identity: Identity, root: Identity, live: bool, mapped: bool,
    windowClass: WindowClass, workspace: int, output: int,
    outputGeneration: int, workAreaRevision: int, dependencyRevision: int,
    geometry: Geometry, internalMode: NativeMode, clientMode: NativeMode,
    configuredClientMode: NativeMode, configureSerial: int, ackedConfigureSerial: int,
    minimized: bool, pinned: bool, resizable: bool, eligible: bool
  }
  type Placement = {
    target: Identity, workspace: int, output: int,
    outputGeneration: int, workAreaRevision: int, origin: PlacementOrigin
  }
  // RestoreMinimized preserves native mode; RestoreGeometry changes maximized
  // geometry; ExitFullscreen is a separate explicitly supported operation.
  type Operation = Maximize | RestoreGeometry | RestoreMinimized | Minimize | Activate | ExitFullscreen
  type Binding = {
    target: Identity, root: Identity, frontendEpoch: int,
    outputGeneration: int, dependencyRevision: int,
    capabilityRevision: int, request: int, generation: int, deadline: int
  }
  type Phase = Admitted | NativeAttempted | ReadBack | AwaitingPresentation
  type Outcome = Pending | Unknown | Committed | Refused | Cancelled
  type Receipt = {
    binding: Binding, operation: Operation, outcome: Outcome,
    sceneRevision: int, configureSerial: int, configured: bool, presented: bool
  }
  type Transaction = {
    binding: Binding, operation: Operation, phase: Phase,
    affected: Set[Identity], before: Identity -> Window,
    mutationCount: int, receipt: Receipt
  }
  type Journal = {
    frontendEpoch: int, request: int, generation: int,
    transaction: Transaction
  }
  type State = {
    lifetime: int, windows: Identity -> Window, outputs: int -> Output,
    placements: Identity -> Placement,
    knownPlacements: Set[Identity], journals: List[Journal],
    focused: Focus, keyboardRecipient: Focus,
    sceneRevision: int, outputGeneration: int, capabilityRevision: int,
    locked: bool, exclusiveInput: bool, protectedGrab: bool,
    tick: int, exhausted: bool
  }
  var state: State
}
