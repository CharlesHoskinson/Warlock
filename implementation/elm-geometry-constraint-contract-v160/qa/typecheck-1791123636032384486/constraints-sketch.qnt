// Revised declarations only; no functional or transition logic before approval.
// One serialized native authority with separately observed callback/client steps.
module constraints_sketch {
  type Identity = { lifetime: int, incarnation: int }
  type Rational = { numerator: int, denominator: int }
  type Size = { width: int, height: int }
  type Point = { x: Rational, y: Rational }
  type Rect = { x: Rational, y: Rational, width: Rational, height: Rational }
  type Upper = Unbounded | Bounded(int)
  type LayoutUpper = LayoutUnbounded | LayoutBounded(Rational)
  type ClientLimits = { minimum: Size, maximumWidth: Upper, maximumHeight: Upper }
  type LayoutLimits = { minimumWidth: Rational, minimumHeight: Rational,
                        maximumWidth: LayoutUpper, maximumHeight: LayoutUpper }
  // Valid optional absence/unboundedness is distinct from failed measurement.
  type ClientObservation = ClientUnavailable | ClientInvalid | ClientBounds(ClientLimits)
  type LayoutObservation = LayoutUnavailable | LayoutInvalid | LayoutBounds(LayoutLimits)
  type RuleObservation = RulesNotSupplied | RulesUnavailable | RulesInvalid | RuleBounds(LayoutLimits)
  type Constraints = {
    client: ClientObservation, layout: LayoutObservation,
    rules: RuleObservation, revision: int
  }
  type Mode = Ordinary | Maximized | Fullscreen
  type Operation = Maximize | RestoreGeometry
  type Scope = {
    workspace: int, workspaceGeneration: int, output: int,
    outputOwnershipGeneration: int, outputGeneration: int, workAreaRevision: int
  }
  // These observations stay in their native box conventions until projection.
  type Conversion = {
    windowGeometryOrigin: Point, reservedTopLeft: Point,
    reservedBottomRight: Point, revision: int
  }
  type ConversionObservation = ConversionUnavailable | ConversionInvalid | ValidConversion(Conversion)
  type CoordinateState = {
    ordinary: ConversionObservation, maximized: ConversionObservation,
    revision: int, monitorScale: Rational
  }
  type Prospective = {
    operation: Operation, logicalTarget: Rect, visualTarget: Rect,
    realClientBox: Rect, configureSize: Size, conversionRevision: int
  }
  type Projection = ProjectionUnavailable | ProjectionInvalid | ValidProjection(Prospective)
  type Window = {
    identity: Identity, live: bool, baseEligible: bool,
    constraints: Constraints, coordinates: CoordinateState,
    logical: Rect, visual: Rect, realClientBox: Rect, configureSize: Size,
    nativeMode: Mode, clientMode: Mode, scope: Scope, dependencyRevision: int
  }
  type Placement = {
    target: Identity, logical: Rect, visual: Rect, realClientBox: Rect,
    configureSize: Size, scope: Scope, coordinateRevision: int
  }
  type Output = { live: bool, scope: Scope, workArea: Rect }
  type RequestKey = {
    target: Identity, frontend: int, session: int,
    request: int, generation: int, operation: Operation
  }
  type Dependency = {
    constraintRevision: int, coordinateRevision: int,
    sceneRevision: int, scope: Scope
  }
  type Phase = Admitted | NativeAttempted | ReadBack | AwaitingClient
  type Outcome = Pending | Unknown | Committed | Refused
  type Transaction = {
    key: RequestKey, dependency: Dependency, projection: Projection,
    phase: Phase, outcome: Outcome, mutations: int,
    before: Window, peersBefore: Identity -> Window,
    configureSerial: int, acknowledgedSerial: int, presented: bool
  }
  type Focus = NoWindow | WindowFocus(Identity)
  type State = {
    lifetime: int, windows: Identity -> Window, outputs: int -> Output,
    placements: Identity -> Placement, knownPlacements: Set[Identity],
    transactions: RequestKey -> Transaction, unresolved: Set[Identity],
    focused: Focus, keyboardRecipient: Focus, pointerRecipient: Focus,
    sceneRevision: int, locked: bool, exclusiveInput: bool,
    protectedGrab: bool, dragging: bool, exhausted: bool
  }
  var state: State
}
