module PreviewLifecycle exposing (Model, Event, Command, Scope, IconHandle, eventDecoder, scopeDecoder, iconDecoder, init, update, observe, encodeCommands, view, inlineView, metadataVisible, idle)

import Html exposing (Html, figcaption, img, span, text)
import Html.Attributes exposing (alt, attribute, class, src)
import Html.Keyed
import Json.Decode as D
import Json.Encode as E
import PreviewIdentity as I
import Set exposing (Set)

type alias Binding = { lifetime : I.Identity I.Lifetime, session : I.Identity I.Session, frontend : I.Identity I.Frontend }
type alias Context = { lifetime : I.Identity I.Lifetime, incarnation : I.Identity I.Incarnation, output : I.Identity I.Output, privacy : I.Identity I.Privacy, rendering : I.Identity I.Rendering, scene : I.Identity I.Scene, content : I.Identity I.Content }
type alias NativeScope = { binding : Binding, context : Context, observation : I.Identity I.Observation, clock : I.Identity I.Clock, now : I.Identity I.MonotonicTime, present : Bool, sourceLive : Bool, locked : Bool, gpuReady : Bool }
type Scope = Scope NativeScope
type alias Trigger = { binding : Binding, context : Context, origin : I.Identity I.Origin, clock : I.Identity I.Clock, deadline : I.Identity I.MonotonicTime }
type alias Job = { binding : Binding, context : Context, request : I.Identity I.Request, origin : I.Identity I.Origin, clock : I.Identity I.Clock, deadline : I.Identity I.MonotonicTime }
type LeaseHandle = LeaseHandle String
type IconHandle = IconHandle String
type Fidelity = ClientContent | ComposedFamily
type alias Packet = { job : Job, handle : LeaseHandle, owned : Bool, signaled : Bool, fidelity : Fidelity, coverage : Set String, expires : I.Identity I.MonotonicTime }
type Candidate = Candidate Packet
type Accepted = Accepted Packet
type Capture = Idle | Capturing Job | WaitingFence Candidate
type Connection = Connected | SourceSuspended | NeedsReconciliation
type Status = Live Accepted | Historical Accepted | Loading | Unavailable
type alias State = { metadataHidden : Bool, scope : NativeScope, demand : Bool, connection : Connection, nextRequest : Maybe (I.Identity I.Request), capture : Capture, accepted : Maybe Accepted, known : List Job, cancelling : List Job, retiring : List Packet, lastTerminal : Maybe ( Job, I.Identity I.Receipt ) }
type Model = Model State
type Command = Acquire Job | Cancel Job | Release Packet | Reconcile Binding | Acknowledge Job (I.Identity I.Receipt)
type Event = Open | Close | Request Trigger | Offer Packet | Fence Packet | Observe NativeScope | SourceDenied Job String | Attach Binding NativeScope | Clock Binding (I.Identity I.Clock) (I.Identity I.MonotonicTime) | Cancelled Job | Released Packet | Expired Packet | Exhausted Binding | Refused Job | Receipt (I.Identity I.Receipt) Event
type alias Work = { state : State, effects : List Command }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Preview lifecycle fields")

bindingDecoder : D.Decoder Binding
bindingDecoder = strict [ "lifetime", "session", "frontend" ] (D.map3 Binding (D.field "lifetime" I.positive) (D.field "session" I.positive) (D.field "frontend" I.positive))

contextDecoder : D.Decoder Context
contextDecoder = strict [ "lifetime", "incarnation", "output", "privacy", "rendering", "scene", "content" ] (D.map7 Context (D.field "lifetime" I.positive) (D.field "incarnation" I.positive) (D.field "output" I.positive) (D.field "privacy" I.positive) (D.field "rendering" I.positive) (D.field "scene" I.positive) (D.field "content" I.positive))

nativeScopeDecoder : D.Decoder NativeScope
nativeScopeDecoder = strict [ "binding", "context", "observation", "clock", "now", "present", "sourceLive", "locked", "gpuReady" ]
    (D.map2 (\constructor gpu -> constructor gpu)
        (D.map8 NativeScope (D.field "binding" bindingDecoder) (D.field "context" contextDecoder) (D.field "observation" I.positive) (D.field "clock" I.positive) (D.field "now" I.positive) (D.field "present" D.bool) (D.field "sourceLive" D.bool) (D.field "locked" D.bool))
        (D.field "gpuReady" D.bool))

scopeDecoder : D.Decoder Scope
scopeDecoder = nativeScopeDecoder |> D.andThen (\scope -> if scope.context.lifetime == scope.binding.lifetime then D.succeed (Scope scope) else D.fail "Scope lifetime does not match binding")

triggerDecoder : D.Decoder Trigger
triggerDecoder = strict [ "binding", "context", "origin", "clock", "deadline" ] (D.map5 Trigger (D.field "binding" bindingDecoder) (D.field "context" contextDecoder) (D.field "origin" I.positive) (D.field "clock" I.positive) (D.field "deadline" I.positive))

jobDecoder : D.Decoder Job
jobDecoder = strict [ "binding", "context", "request", "origin", "clock", "deadline" ] (D.map6 Job (D.field "binding" bindingDecoder) (D.field "context" contextDecoder) (D.field "request" I.positive) (D.field "origin" I.positive) (D.field "clock" I.positive) (D.field "deadline" I.positive))

opaqueDecoder : D.Decoder String
opaqueDecoder = D.string |> D.andThen (\value -> if String.length value == 64 && value /= String.repeat 64 "0" && String.all (\c -> (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) value then D.succeed value else D.fail "Opaque native resource token")

iconDecoder : D.Decoder IconHandle
iconDecoder = D.map IconHandle opaqueDecoder

packetDecoder : D.Decoder Packet
packetDecoder =
    let
        fidelity = D.string |> D.andThen (\value -> case value of
            "client" -> D.succeed ClientContent
            "family" -> D.succeed ComposedFamily
            _ -> D.fail "Preview fidelity")
        coverage = D.list D.string |> D.andThen (\values ->
            let unique = Set.fromList values in
            if List.length values <= 4 && List.length values == Set.size unique && Set.isEmpty (Set.diff unique (Set.fromList [ "client", "decoration", "modal", "popup" ])) then D.succeed unique else D.fail "Preview coverage")
    in strict [ "job", "handle", "owned", "signaled", "fidelity", "coverage", "expires" ]
        (D.map7 Packet (D.field "job" jobDecoder) (D.field "handle" (D.map LeaseHandle opaqueDecoder)) (D.field "owned" D.bool) (D.field "signaled" D.bool) (D.field "fidelity" fidelity) (D.field "coverage" coverage) (D.field "expires" I.positive))

basicDecoder : D.Decoder Event
basicDecoder = D.field "kind" D.string |> D.andThen (\kind -> case kind of
    "open" -> strict [ "kind" ] (D.succeed Open)
    "close" -> strict [ "kind" ] (D.succeed Close)
    "request" -> strict [ "kind", "trigger" ] (D.map Request (D.field "trigger" triggerDecoder))
    "offer" -> strict [ "kind", "frame" ] (D.map Offer (D.field "frame" packetDecoder))
    "fence" -> strict [ "kind", "frame" ] (D.map Fence (D.field "frame" packetDecoder))
    "observe" -> strict [ "kind", "scope" ] (D.map Observe (D.field "scope" nativeScopeDecoder))
    "source-denied" -> strict [ "kind", "job", "reason" ] (D.map2 SourceDenied (D.field "job" jobDecoder) (D.field "reason" (D.string |> D.andThen (\reason -> if List.member reason [ "locked", "source-unavailable", "output-unavailable", "layout-unsupported" ] then D.succeed reason else D.fail "Typed native source denial"))))
    "attach" -> strict [ "kind", "previous", "scope" ] (D.map2 Attach (D.field "previous" bindingDecoder) (D.field "scope" nativeScopeDecoder))
    "clock" -> strict [ "kind", "binding", "clock", "now" ] (D.map3 Clock (D.field "binding" bindingDecoder) (D.field "clock" I.positive) (D.field "now" I.positive))
    "cancelled" -> strict [ "kind", "job" ] (D.map Cancelled (D.field "job" jobDecoder))
    "released" -> strict [ "kind", "frame" ] (D.map Released (D.field "frame" packetDecoder))
    "expired" -> strict [ "kind", "frame" ] (D.map Expired (D.field "frame" packetDecoder))
    "exhausted" -> strict [ "kind", "binding" ] (D.map Exhausted (D.field "binding" bindingDecoder))
    "refused" -> strict [ "kind", "job" ] (D.map Refused (D.field "job" jobDecoder))
    _ -> D.fail "Preview lifecycle event")

-- Only terminal cleanup events carry stable native receipt identities. The
-- authenticated native channel is responsible for their provenance; JSON
-- alone never grants the right to retire a native resource.
terminalJob : Event -> Maybe Job
terminalJob event = case event of
    Cancelled job -> Just job
    Released frame -> Just frame.job
    Refused job -> Just job
    _ -> Nothing

eventDecoder : D.Decoder Event
eventDecoder = D.field "kind" D.string |> D.andThen (\kind ->
    if kind == "receipt" then
        let terminal = basicDecoder |> D.andThen (\event ->
                if terminalJob event /= Nothing then D.succeed event else D.fail "Terminal native receipt body")
        in strict [ "kind", "sequence", "event" ] (D.map2 Receipt (D.field "sequence" I.positive) (D.field "event" terminal))
    else basicDecoder |> D.andThen (\event ->
        if terminalJob event == Nothing then D.succeed event else D.fail "Native cleanup receipt identity required"))

init : Scope -> Model
init (Scope scope) = Model { metadataHidden = scope.locked, scope = scope, demand = False, connection = Connected, nextRequest = I.nextRequest I.zeroRequest, capture = Idle, accepted = Nothing, known = [], cancelling = [], retiring = [], lastTerminal = Nothing }

notAfter : I.Identity domain -> I.Identity domain -> Bool
notAfter a b = I.compare a b /= GT

before : I.Identity domain -> I.Identity domain -> Bool
before a b = I.compare a b == LT

generationMatches : Context -> Context -> Bool
generationMatches a b = a.lifetime == b.lifetime && a.incarnation == b.incarnation && a.output == b.output && a.privacy == b.privacy && a.rendering == b.rendering

sameLease : Packet -> Packet -> Bool
sameLease a b = a.job == b.job && a.handle == b.handle

candidate : State -> Maybe Packet
candidate st = case st.capture of
    WaitingFence (Candidate frame) -> Just frame
    _ -> Nothing

acceptedPacket : State -> Maybe Packet
acceptedPacket st = st.accepted |> Maybe.map (\(Accepted packet) -> packet)

authorized : State -> Packet -> Bool
authorized st frame = st.connection == Connected && st.scope.present && not st.scope.locked && st.scope.gpuReady && frame.owned && frame.job.binding == st.scope.binding && frame.job.clock == st.scope.clock && generationMatches st.scope.context frame.job.context && notAfter frame.job.context.scene st.scope.context.scene && notAfter frame.job.context.content st.scope.context.content && before st.scope.now frame.expires && Set.member "client" frame.coverage && (frame.fidelity == ClientContent || frame.coverage == Set.fromList [ "client", "decoration", "modal", "popup" ])

status : State -> Status
status st =
    case st.accepted of
        Just ((Accepted frame) as lease) ->
            if st.demand && authorized st frame then
                if st.scope.sourceLive && frame.job.context.scene == st.scope.context.scene && frame.job.context.content == st.scope.context.content then Live lease else Historical lease
            else loadingStatus st
        Nothing -> loadingStatus st

loadingStatus : State -> Status
loadingStatus st = if st.demand && st.capture /= Idle then Loading else Unavailable

mapState : (State -> State) -> Work -> Work
mapState f work = { work | state = f work.state }

emit : Command -> Work -> Work
emit command work = { work | effects = work.effects ++ [ command ] }

retirePacket : Packet -> Work -> Work
retirePacket frame work =
    if List.any (sameLease frame) work.state.retiring then work
    else work |> mapState (\st -> { st | retiring = frame :: st.retiring }) |> emit (Release frame)

cancelCurrent : Work -> Work
cancelCurrent work =
    case work.state.capture of
        Capturing job ->
            let cleared = mapState (\st -> { st | capture = Idle }) work in
            if List.member job work.state.cancelling then cleared
            else cleared |> mapState (\st -> { st | cancelling = job :: st.cancelling }) |> emit (Cancel job)
        _ -> work

retireCandidate : Work -> Work
retireCandidate work = case candidate work.state of
    Just frame -> work |> mapState (\st -> { st | capture = Idle }) |> retirePacket frame
    Nothing -> work

retireAccepted : Work -> Work
retireAccepted work = case acceptedPacket work.state of
    Just frame -> work |> mapState (\st -> { st | accepted = Nothing }) |> retirePacket frame
    Nothing -> work

revoke : Work -> Work
revoke = cancelCurrent >> retireCandidate >> retireAccepted

reconcile : Work -> Work
reconcile work = work |> revoke |> mapState (\st -> { st | connection = NeedsReconciliation }) |> emit (Reconcile work.state.scope.binding)

finishKnown : Job -> Work -> Work
finishKnown job work =
    let
        st = work.state
        captureMatches = case st.capture of
            Capturing current -> current == job
            WaitingFence (Candidate current) -> current.job == job
            Idle -> False
        stillHeld = captureMatches || (acceptedPacket st |> Maybe.map (\f -> f.job == job) |> Maybe.withDefault False) || List.member job st.cancelling || List.any (\f -> f.job == job) st.retiring
    in if stillHeld then work else mapState (\state -> { state | known = List.filter ((/=) job) state.known }) work

heldHandle : State -> LeaseHandle -> Bool
heldHandle st handle = List.any (\packet -> packet.handle == handle) (List.filterMap identity [ candidate st, acceptedPacket st ] ++ st.retiring)

offer : Packet -> Work -> Work
offer frame work =
    let
        st = work.state
        matches = case st.capture of
            Capturing job -> st.demand && job == frame.job && authorized st frame && before st.scope.now frame.job.deadline && not (heldHandle st frame.handle)
            _ -> False
    in if matches then
        if frame.signaled then work |> retireAccepted |> mapState (\state -> { state | capture = Idle, accepted = Just (Accepted frame) })
        else mapState (\state -> { state | capture = WaitingFence (Candidate frame) }) work
    else if List.member frame.job st.known && frame.owned && not (heldHandle st frame.handle) then
        let cleanup = retirePacket frame work in
        case cleanup.state.capture of
            Capturing job -> if job == frame.job then cancelCurrent cleanup else cleanup
            _ -> cleanup
    else work

advanceClock : I.Identity I.MonotonicTime -> Work -> Work
advanceClock now work =
    let
        timed = mapState (\st -> let sc = st.scope in { st | scope = { sc | now = now } }) work
        jobTimed = case timed.state.capture of
            Capturing job -> if notAfter job.deadline now then cancelCurrent timed else timed
            _ -> timed
        candidateTimed = case candidate jobTimed.state of
            Just frame -> if notAfter frame.job.deadline now || notAfter frame.expires now then retireCandidate jobTimed else jobTimed
            Nothing -> jobTimed
    in case acceptedPacket candidateTimed.state of
        Just frame -> if notAfter frame.expires now then retireAccepted candidateTimed else candidateTimed
        Nothing -> candidateTimed

scopeValid : NativeScope -> NativeScope -> Bool
scopeValid previous incoming = incoming.binding == previous.binding && incoming.clock == previous.clock && incoming.context.lifetime == incoming.binding.lifetime && notAfter previous.now incoming.now && before previous.observation incoming.observation

scopeCoherent : NativeScope -> NativeScope -> Bool
scopeCoherent previous incoming = notAfter previous.context.output incoming.context.output && notAfter previous.context.privacy incoming.context.privacy && notAfter previous.context.rendering incoming.context.rendering && (incoming.context.incarnation /= previous.context.incarnation || (notAfter previous.context.scene incoming.context.scene && notAfter previous.context.content incoming.context.content && (incoming.sourceLive == previous.sourceLive || before previous.context.scene incoming.context.scene)))

update : Event -> Model -> ( Model, List Command )
update event model =
    case event of
        Receipt sequence terminal ->
            case terminalJob terminal of
                Just job ->
                    let
                        (Model initial) = model
                        correlated = List.member job initial.known || initial.lastTerminal == Just ( job, sequence )
                    in
                    if not correlated then ( model, [] )
                    else
                        let
                            ( next, commands ) = updatePlain terminal model
                            (Model state) = next
                        in
                        if List.member job state.known then ( next, commands )
                        else ( Model { state | lastTerminal = Just ( job, sequence ) }, commands ++ [ Acknowledge job sequence ] )
                Nothing -> updatePlain terminal model
        _ -> updatePlain event model

updatePlain : Event -> Model -> ( Model, List Command )
updatePlain event (Model initial) =
    let
        base = { state = initial, effects = [] }
        final = case event of
            Open -> mapState (\st -> { st | demand = True }) base
            Close -> base |> cancelCurrent |> retireCandidate |> mapState (\st -> { st | demand = False })
            Request trigger ->
                if initial.connection == Connected && initial.demand && initial.scope.present && initial.scope.sourceLive && not initial.scope.locked && initial.scope.gpuReady && initial.capture == Idle && List.isEmpty initial.cancelling && List.isEmpty initial.retiring && trigger.binding == initial.scope.binding && trigger.context == initial.scope.context && trigger.clock == initial.scope.clock && before initial.scope.now trigger.deadline then
                    case initial.nextRequest of
                        Just request ->
                            let job = { binding = initial.scope.binding, context = initial.scope.context, request = request, origin = trigger.origin, clock = initial.scope.clock, deadline = trigger.deadline } in
                            base |> mapState (\st -> { st | nextRequest = I.nextRequest request, capture = Capturing job, known = job :: st.known }) |> emit (Acquire job)
                        Nothing -> base
                else base
            Offer frame -> offer frame base
            Fence incoming ->
                case candidate initial of
                    Just frame ->
                        if sameLease frame incoming && initial.demand && authorized initial frame && before initial.scope.now frame.job.deadline then
                            base |> retireAccepted |> mapState (\st -> { st | capture = Idle, accepted = Just (Accepted { frame | signaled = True }) })
                        else base
                    Nothing -> base
            Observe incoming ->
                if not (scopeValid initial.scope incoming) then base
                else if not (scopeCoherent initial.scope incoming) then reconcile base
                else
                    let changed = if not (generationMatches initial.scope.context incoming.context) || not incoming.present || incoming.locked || not incoming.gpuReady then revoke base else base in
                    changed |> mapState (\st -> { st | scope = incoming, metadataHidden = incoming.locked, connection = if st.connection == SourceSuspended && incoming.present && not incoming.locked && incoming.gpuReady then Connected else st.connection }) |> advanceClock incoming.now
            SourceDenied job reason ->
                let current = case initial.capture of
                        Capturing active -> active == job
                        WaitingFence (Candidate frame) -> frame.job == job
                        Idle -> False
                    accepted = initial.capture == Idle && (acceptedPacket initial |> Maybe.map (\frame -> frame.job == job) |> Maybe.withDefault False)
                in if job.binding == initial.scope.binding && List.member job initial.known && (current || accepted) then
                    base |> revoke |> mapState (\st -> { st | metadataHidden = st.metadataHidden || reason == "locked", connection = if st.connection == NeedsReconciliation then NeedsReconciliation else SourceSuspended })
                   else base
            Attach previous incoming ->
                if previous == initial.scope.binding && incoming.binding /= previous && incoming.context.lifetime == incoming.binding.lifetime then
                    base |> revoke |> mapState (\st -> { st | scope = incoming, metadataHidden = incoming.locked, connection = Connected, nextRequest = I.nextRequest I.zeroRequest })
                else base
            Clock binding clock now ->
                if binding == initial.scope.binding && clock == initial.scope.clock && before initial.scope.now now then advanceClock now base else base
            Cancelled job ->
                if List.member job initial.cancelling then
                    base |> mapState (\st -> { st | cancelling = List.filter ((/=) job) st.cancelling, retiring = List.filter (\f -> f.job /= job) st.retiring }) |> finishKnown job
                else base
            Released frame ->
                if List.any (sameLease frame) initial.retiring then
                    base |> mapState (\st -> { st | retiring = List.filter (sameLease frame >> not) st.retiring }) |> finishKnown frame.job
                else base
            Expired frame ->
                if candidate initial |> Maybe.map (sameLease frame) |> Maybe.withDefault False then retireCandidate base
                else if acceptedPacket initial |> Maybe.map (sameLease frame) |> Maybe.withDefault False then retireAccepted base
                else base
            Exhausted binding -> if binding == initial.scope.binding then reconcile base else base
            Receipt _ _ -> base
            Refused job ->
                case initial.capture of
                    Capturing current -> if current == job then base |> mapState (\st -> { st | capture = Idle }) |> finishKnown job else base
                    _ -> base
    in ( Model final.state, final.effects )

encodeBinding : Binding -> E.Value
encodeBinding binding = E.object [ ( "lifetime", I.encode binding.lifetime ), ( "session", I.encode binding.session ), ( "frontend", I.encode binding.frontend ) ]

encodeContext : Context -> E.Value
encodeContext context = E.object [ ( "lifetime", I.encode context.lifetime ), ( "incarnation", I.encode context.incarnation ), ( "output", I.encode context.output ), ( "privacy", I.encode context.privacy ), ( "rendering", I.encode context.rendering ), ( "scene", I.encode context.scene ), ( "content", I.encode context.content ) ]

encodeScope : NativeScope -> E.Value
encodeScope scope = E.object [ ( "binding", encodeBinding scope.binding ), ( "context", encodeContext scope.context ), ( "observation", I.encode scope.observation ), ( "clock", I.encode scope.clock ), ( "now", I.encode scope.now ), ( "present", E.bool scope.present ), ( "sourceLive", E.bool scope.sourceLive ), ( "locked", E.bool scope.locked ), ( "gpuReady", E.bool scope.gpuReady ) ]

encodeJob : Job -> E.Value
encodeJob job = E.object [ ( "binding", encodeBinding job.binding ), ( "context", encodeContext job.context ), ( "request", I.encode job.request ), ( "origin", I.encode job.origin ), ( "clock", I.encode job.clock ), ( "deadline", I.encode job.deadline ) ]

handleString : LeaseHandle -> String
handleString (LeaseHandle value) = value

encodePacket : Packet -> E.Value
encodePacket packet = E.object [ ( "job", encodeJob packet.job ), ( "handle", E.string (handleString packet.handle) ), ( "owned", E.bool packet.owned ), ( "signaled", E.bool packet.signaled ), ( "fidelity", E.string (if packet.fidelity == ClientContent then "client" else "family") ), ( "coverage", E.list E.string (Set.toList packet.coverage) ), ( "expires", I.encode packet.expires ) ]

encodeCommands : List Command -> E.Value
encodeCommands commands = E.list (\command -> case command of
    Acknowledge job sequence -> E.object [ ( "kind", E.string "acknowledge" ), ( "job", encodeJob job ), ( "sequence", I.encode sequence ) ]
    Acquire job -> E.object [ ( "kind", E.string "acquire" ), ( "job", encodeJob job ) ]
    Cancel job -> E.object [ ( "kind", E.string "cancel" ), ( "job", encodeJob job ) ]
    Release packet -> E.object [ ( "kind", E.string "release" ), ( "frame", encodePacket packet ) ]
    Reconcile binding -> E.object [ ( "kind", E.string "reconcile" ), ( "binding", encodeBinding binding ) ]) commands

statusName : Status -> String
statusName current = case current of
    Live _ -> "live"
    Historical _ -> "historical"
    Loading -> "loading"
    Unavailable -> "unavailable"

drawablePacket : Status -> Maybe Packet
drawablePacket current = case current of
    Live (Accepted packet) -> Just packet
    Historical (Accepted packet) -> Just packet
    _ -> Nothing

observe : Model -> E.Value
observe (Model st) =
    let
        maybe encode value = Maybe.map encode value |> Maybe.withDefault E.null
        job = case st.capture of
            Capturing active -> Just active
            _ -> Nothing
        current = status st
    in E.object [ ( "scope", encodeScope st.scope ), ( "demand", E.bool st.demand ), ( "ready", E.bool (st.connection == Connected) ), ( "nextRequest", maybe I.encode st.nextRequest ), ( "job", maybe encodeJob job ), ( "candidate", maybe encodePacket (candidate st) ), ( "accepted", maybe encodePacket (acceptedPacket st) ), ( "known", E.list encodeJob st.known ), ( "cancelling", E.list encodeJob st.cancelling ), ( "retiring", E.list encodePacket st.retiring ), ( "state", E.string (statusName current) ), ( "image", maybe (.handle >> handleString >> (++) "elm-shell://preview/" >> E.string) (drawablePacket current) ) ]

view : { title : String, application : String, icon : Maybe IconHandle } -> Model -> Html msg
view = render "figure" "figcaption"

inlineView : { title : String, application : String, icon : Maybe IconHandle } -> Model -> Html msg
inlineView = render "span" "span"

render : String -> String -> { title : String, application : String, icon : Maybe IconHandle } -> Model -> Html msg
render root caption info (Model st) =
    let
        current = status st
        label = case current of
            Live _ -> "Live preview"
            Historical _ -> "Historical preview"
            Loading -> "Preview loading"
            Unavailable -> "Preview unavailable"
        title = if st.metadataHidden || st.scope.locked then "Preview unavailable" else info.title
        contents = case drawablePacket current of
            Just packet -> [ ( "frame:" ++ handleString packet.handle, img [ class "preview-image", src ("elm-shell://preview/" ++ handleString packet.handle), alt "", attribute "aria-hidden" "true" ] [] ) ]
            Nothing ->
                (if st.metadataHidden || st.scope.locked then [] else info.icon |> Maybe.map (\(IconHandle token) -> [ ( "icon:" ++ token, img [ class "preview-icon", src ("elm-shell://icon/" ++ token), alt "", attribute "aria-hidden" "true" ] [] ) ]) |> Maybe.withDefault []) ++ [ ( "title", span [ class "preview-title" ] [ text title ] ) ]
        fidelity = drawablePacket current |> Maybe.map (\packet -> if packet.fidelity == ComposedFamily then "Window family" else "Client content") |> Maybe.withDefault ""
    in Html.Keyed.node root [ class "window-preview", attribute "data-preview-state" (statusName current) ] (contents ++ [ ( "status", Html.node caption [] [ span [ class "preview-state" ] [ text label ], span [ class "preview-fidelity" ] [ text fidelity ] ] ) ])

metadataVisible : Model -> Bool
metadataVisible (Model st) = not st.scope.locked && not st.metadataHidden

-- Local admission status cannot replace any owned or unsettled lifecycle work.
idle : Model -> Bool
idle (Model st) = st.connection == Connected && st.scope.present && st.scope.sourceLive && not st.scope.locked && st.scope.gpuReady && not st.metadataHidden && st.capture == Idle && st.accepted == Nothing && List.isEmpty st.known && List.isEmpty st.cancelling && List.isEmpty st.retiring
