module PreviewPresenter exposing (Model, initial, present, receive, image, observe, metadata, enrollment, feedback, enrollRealm, receiveRealm, realmStatus, closeRealm, quarantineRealm)

import Dict exposing (Dict)
import Html exposing (Html, span, text)
import Html.Attributes exposing (attribute, class)
import Set
import Json.Decode as D
import Json.Encode as E
import PreviewLifecycle as Preview
import NativePreviewSource
import NativeActorRetirement as Retirement
import NativePreviewRealm as Realm
import NativePreviewDetachment as Detachment
import SurfaceRenderer
import UInt64 exposing (Counter)

type alias Stamp = { publication : Counter, lease : Counter }
type LocalOutcome = Capacity | Waiting | Expired | Conflict | Exhausted
type alias LocalFeedback = { owner : String, subject : Counter, clock : Counter, stamp : Stamp, sequence : Counter, deadline : Counter, outcome : LocalOutcome }
type alias Entry = { model : Maybe Preview.Model, binding : String, source : Maybe NativePreviewSource.Source, stamp : Maybe Stamp, title : String, application : String, icon : Maybe Preview.IconHandle, iconKind : String, metadataRevision : Maybe Counter, minimized : Maybe Bool, local : Maybe LocalFeedback, feedbackFloor : Maybe Counter, retirement : Maybe Retirement.Observation, readySent : Bool, detachment : Maybe Detachment.Seed, detachReadySent : Bool }
type alias CatalogStamp = { binding : String, request : Counter, sequence : Counter, revision : Counter }
type alias Window = { subject : Counter, title : String, application : String, minimized : Bool }
type alias Scoped = { grant : Maybe Realm.Grant, closing : Bool, closed : Bool, processed : Counter, completed : Dict String (Counter,Detachment.Seed) }

emptyScoped : Scoped
emptyScoped = {grant=Nothing,closing=False,closed=False,processed=UInt64.zero,completed=Dict.empty}

type Model = Model (Dict String Entry) (Maybe CatalogStamp) Retirement.Ledger Scoped
type Input = Seed Stamp String Preview.Scope D.Value String String String (Maybe NativePreviewSource.Source) Bool (Maybe Counter) | Metadata String String Counter Counter String String (Maybe Preview.IconHandle) String | Event String Preview.Event D.Value | Catalog Stamp CatalogStamp (List Window) | Feedback String LocalFeedback | Retirement Retirement.Observation | Retired Retirement.Fact | RetirementChannel String | RetirementDelivery Retirement.Delivery | DetachSeed Detachment.Seed | Detached Detachment.Delivery
type alias Output = { identity : String, commands : List Preview.Command }

initial : Model
initial = Model Dict.empty Nothing Retirement.empty emptyScoped

enrollRealm : Realm.Grant -> Model -> Maybe Model
enrollRealm grant ((Model entries catalog ledger scoped) as prior) =
    case scoped.grant of
        Nothing ->
            if Dict.isEmpty entries && catalog == Nothing && ledger == Retirement.empty then
                Just (Model entries catalog {ledger | channel=Just (Realm.owner grant.domain)} {emptyScoped | grant=Just grant})
            else Nothing
        Just old ->
            if old == grant && not scoped.closed then Just prior
            else if scoped.closed && Dict.isEmpty entries && Realm.owner old.domain == Realm.owner grant.domain &&
                UInt64.compare grant.domain.receiverEpoch old.domain.receiverEpoch == GT then
                -- Permanent native facts keep their chronology. Only the
                -- completed old realm's delivery channel prefix is replaced.
                Just (Model entries catalog {ledger | channel=Just (Realm.owner grant.domain),processed=UInt64.zero} {emptyScoped | grant=Just grant})
            else Nothing

closeRealm : Realm.Domain -> Model -> Maybe Model
closeRealm domain (Model entries catalog ledger scoped) =
    if Dict.isEmpty entries && (scoped.grant |> Maybe.map (\grant -> Realm.same grant.domain domain) |> Maybe.withDefault False) then
        Just (Model entries catalog ledger {scoped | closed=True,closing=True})
    else Nothing

wrap : Scoped -> E.Value -> E.Value
wrap scoped entries =
    let row = D.map2 Tuple.pair (D.field "identity" D.string) (D.field "commands" (D.list D.value))
        canonical = D.decodeValue (D.list row) entries |> Result.map (\rows ->
            E.list (\value -> value) (List.concatMap (\(identity,commands) -> List.map (\command ->
                E.object [("identity",E.string (if D.decodeValue (D.field "kind" D.string) command == Ok "reconcile" then scoped.grant |> Maybe.map (\grant -> "binding:" ++ Realm.owner grant.domain) |> Maybe.withDefault identity else identity)),
                    ("commands",E.list (\value -> value) [command])]) commands) rows)) |> Result.withDefault entries
    in scoped.grant |> Maybe.map (\grant -> Realm.commands grant.domain canonical) |> Maybe.withDefault entries

receiveRealm : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receiveRealm snapshot raw ((Model _ _ _ scoped) as prior) =
    case (scoped.grant,D.decodeValue Realm.envelopeDecoder raw) of
        (Just grant,Ok envelope) ->
            case if scoped.closed then Nothing else Realm.unwrap grant.domain envelope of
                Nothing -> (prior,wrap scoped (encode []))
                Just event ->
                    let (next,emitted) = receiveOwned snapshot event prior
                    in (next,wrap scoped emitted)
        _ -> (prior,wrap scoped (encode []))

detachEntry : Entry -> (Entry,List Preview.Command)
detachEntry entry =
    case entry.model of
        Nothing -> ({entry | stamp=Nothing,local=Nothing},[])
        Just lifecycle ->
            let (next,emitted) = Preview.retire lifecycle
            in ({entry | model=Just next,stamp=Nothing,local=Nothing},emitted)

quarantineOwned : Model -> (Model,E.Value)
quarantineOwned ((Model entries catalog ledger scoped) as prior) =
    if scoped.closing then (prior,encode [])
    else
        let step identity entry (next,emitted) =
                let (closed,commands) = detachEntry entry
                in (Dict.insert identity closed next,emitted ++ [{identity=identity,commands=commands}])
            (retained,cleanup) = Dict.foldl step (Dict.empty,[]) entries
        in (Model retained catalog ledger {scoped | closing=True},encode cleanup)

quarantineRealm : Realm.Domain -> Model -> (Model,E.Value)
quarantineRealm domain ((Model _ _ _ scoped) as prior) =
    if scoped.closed || scoped.closing || not (scoped.grant |> Maybe.map (\grant -> Realm.same grant.domain domain) |> Maybe.withDefault False) then (prior,wrap scoped (encode []))
    else
        let (next,cleanup) = quarantineOwned prior
            original = E.object [("identity",E.string ("binding:" ++ Realm.owner domain)),("commands",E.list identity
                [E.object [("kind",E.string "reconcile"),("binding",Realm.bindingValue domain)]])]
            retained = D.decodeValue (D.list D.value) cleanup |> Result.withDefault []
        in (next,wrap scoped (E.list identity (original :: retained)))

floorMatches : Entry -> Detachment.Seed -> Bool
floorMatches entry seed =
    case entry.model of
        Nothing -> seed.requestFloor == UInt64.zero
        Just lifecycle ->
            D.decodeValue (D.field "nextRequest" (D.nullable UInt64.decoder)) (Preview.observe lifecycle)
                |> Result.map (\next -> next == UInt64.next seed.requestFloor)
                |> Result.withDefault False

realmStatus : Model -> E.Value
realmStatus (Model entries _ _ scoped) =
    E.object [("controlled",E.bool (scoped.grant /= Nothing)),("closing",E.bool scoped.closing),("closed",E.bool scoped.closed),
        ("processed",E.string (UInt64.string scoped.processed)),("retained",E.int (Dict.size entries)),
        ("completed",E.int (Dict.size scoped.completed)),("epoch",scoped.grant |> Maybe.map (\grant -> E.string (UInt64.string grant.domain.receiverEpoch)) |> Maybe.withDefault E.null)]

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Preview presenter fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Positive preview presentation identity")

bounded : D.Decoder String
bounded = D.string |> D.andThen (\value ->
    let size = String.foldl (\c bytes -> bytes + (if Char.toCode c < 128 then 1 else if Char.toCode c < 2048 then 2 else if Char.toCode c < 65536 then 3 else 4)) 0 value
        control c = Char.toCode c < 32 || (Char.toCode c >= 127 && Char.toCode c <= 159)
    in if size <= 1024 && not (String.any control value) then D.succeed value else D.fail "Preview label")

binding : D.Decoder String
binding = strict ["lifetime","session","frontend"] (D.map3 (\a b c -> String.join ":" (List.map UInt64.string [a,b,c])) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive))

windows : D.Decoder (List Window)
windows = D.list (strict ["incarnation","application","label","minimized"] (D.map4 Window (D.field "incarnation" positive) (D.field "label" bounded) (D.field "application" bounded) (D.field "minimized" D.bool)))
    |> D.andThen (\rows -> if List.length rows <= 256 && Set.size (Set.fromList (List.map (.subject >> UInt64.string) rows)) == List.length rows then D.succeed rows else D.fail "Unique bounded catalog")

closeEntry : Entry -> (Entry,List Preview.Command)
closeEntry entry =
    case entry.model of
        Nothing -> ({entry | stamp=Nothing,local=Nothing},[])
        Just lifecycle ->
            let (closed,commands) = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "close")]) |> Result.map (\event -> Preview.update event lifecycle) |> Result.withDefault (lifecycle,[])
            in ({entry | model=Just closed,stamp=Nothing,local=Nothing},commands)

retireEntry : Entry -> (Entry,List Preview.Command)
retireEntry entry =
    case entry.model of
        Nothing -> ({entry | stamp=Nothing,local=Nothing},[])
        Just lifecycle ->
            let (retiring,commands) = Preview.retire lifecycle
            in ({entry | model=Just retiring,stamp=Nothing,local=Nothing},commands)

outcomeDecoder : D.Decoder LocalOutcome
outcomeDecoder = D.string |> D.andThen (\value -> case value of
    "capacity" -> D.succeed Capacity
    "waiting" -> D.succeed Waiting
    "expired" -> D.succeed Expired
    "conflict" -> D.succeed Conflict
    "exhausted" -> D.succeed Exhausted
    _ -> D.fail "Typed local preview outcome")

advanceFloor : Maybe Counter -> Maybe Counter -> Maybe Counter
advanceFloor old incoming = case (old,incoming) of
    (Just previous,Just next) -> Just (if UInt64.compare next previous == GT then next else previous)
    (_,Just next) -> Just next
    _ -> old

input : D.Decoder Input
input = D.field "kind" D.string |> D.andThen (\kind -> case kind of
    "native-preview-detach-seed" -> D.map DetachSeed Detachment.seedDecoder
    "native-preview-binding-detach-delivery" -> D.map Detached Detachment.deliveryDecoder
    "native-incarnation-retirement" -> D.map Retirement Retirement.observationDecoder
    "native-actor-retired" -> D.map Retired Retirement.actorDecoder
    "native-actor-retirement-channel" -> D.map RetirementChannel Retirement.channelDecoder
    "native-actor-retirement-delivery" -> D.map RetirementDelivery Retirement.deliveryDecoder
    "demand-feedback" -> strict ["kind","identity","binding","subject","clock","publication","lease","sequence","deadline","outcome"]
        (D.map3 (\identity stamp value -> Feedback identity {value | stamp=stamp}) (D.field "identity" bounded)
            (D.map2 Stamp (D.field "publication" positive) (D.field "lease" positive))
            (D.map6 (\owner subject clock sequence deadline outcome -> {owner=owner,subject=subject,clock=clock,stamp={publication=UInt64.zero,lease=UInt64.zero},sequence=sequence,deadline=deadline,outcome=outcome})
                (D.field "binding" binding) (D.field "subject" positive) (D.field "clock" positive) (D.field "sequence" positive) (D.field "deadline" positive) (D.field "outcome" outcomeDecoder)))
    "catalog" -> strict ["protocolVersion","kind","publication","lease","binding","requestId","sequence","revision","windows"]
        (D.map8 (\protocol publication lease owner request sequence revision rows -> (protocol,Catalog {publication=publication,lease=lease} {binding=owner,request=request,sequence=sequence,revision=revision} rows))
            (D.field "protocolVersion" D.int) (D.field "publication" positive) (D.field "lease" positive) (D.field "binding" binding) (D.field "requestId" positive) (D.field "sequence" positive) (D.field "revision" positive) (D.field "windows" windows)
            |> D.andThen (\(protocol,result) -> if protocol == 3 then D.succeed result else D.fail "Native catalog protocol"))
    "seed" -> strict ["kind","publication","lease","identity","scope","title","application"]
        (D.map7 (\publication lease identity raw title application owner -> {publication=publication,lease=lease,identity=identity,raw=raw,title=title,application=application,owner=owner})
            (D.field "publication" positive) (D.field "lease" positive) (D.field "identity" bounded) (D.field "scope" D.value) (D.field "title" bounded) (D.field "application" bounded) (D.at ["scope","binding"] binding)
            |> D.andThen (\seed ->
                case (D.decodeValue Preview.scopeDecoder seed.raw,D.decodeValue (D.at ["context","incarnation"] positive) seed.raw) of
                    (Ok scope,Ok incarnation) -> if seed.identity == "family:" ++ UInt64.string incarnation then D.succeed (Seed {publication=seed.publication,lease=seed.lease} seed.identity scope seed.raw seed.title seed.application seed.owner Nothing False Nothing) else D.fail "Preview control incarnation mismatch"
                    _ -> D.fail "Native preview scope"))
    sourceSeedKind -> if List.member sourceSeedKind ["source-seed","demand-seed"] then strict ["kind","publication","lease","identity","source","title","application"]
        (D.map6 (\publication lease identity raw title application -> {publication=publication,lease=lease,identity=identity,raw=raw,title=title,application=application})
            (D.field "publication" positive) (D.field "lease" positive) (D.field "identity" bounded) (D.field "source" D.value) (D.field "title" bounded) (D.field "application" bounded)
            |> D.andThen (\seed ->
                case (D.decodeValue NativePreviewSource.decoder seed.raw,D.decodeValue (D.map3 (\native incarnation owner -> (native,incarnation,owner)) (D.field "scope" D.value) (D.at ["scope","context","incarnation"] positive) (D.at ["scope","binding"] binding)) seed.raw) of
                    (Ok observation,Ok (native,incarnation,owner)) ->
                        if seed.identity == "family:" ++ UInt64.string incarnation then
                            D.succeed (Seed {publication=seed.publication,lease=seed.lease} seed.identity (NativePreviewSource.scope observation) native seed.title seed.application owner (Just (NativePreviewSource.source observation)) (sourceSeedKind == "demand-seed") (D.decodeValue (D.field "requestId" positive) seed.raw |> Result.toMaybe))
                        else D.fail "Typed source control incarnation mismatch"
                    _ -> D.fail "Typed native preview source"))
      else case sourceSeedKind of
        "metadata" -> strict ["kind","identity","binding","subject","revision","title","application","icon","iconKind"]
            (D.map8 Metadata (D.field "identity" bounded) (D.field "binding" binding) (D.field "subject" positive) (D.field "revision" positive) (D.field "title" bounded) (D.field "application" bounded) (D.field "icon" (D.nullable Preview.iconDecoder)) (D.field "iconKind" (D.string |> D.andThen (\resolution -> if List.member resolution ["application","generic","unavailable"] then D.succeed resolution else D.fail "Native icon resolution"))))
        "event" -> strict ["kind","identity","event"] (D.map3 Event (D.field "identity" bounded) (D.field "event" Preview.eventDecoder) (D.field "event" D.value))
        _ -> D.fail "Preview presenter kind")

-- Observe/Attach may retarget a standalone lifecycle. A picker entry has a
-- fixed native incarnation and may never inherit another control's subject.
eventOwns : String -> D.Value -> Bool
eventOwns identity wire =
    case D.decodeValue (D.field "kind" D.string) wire of
        Ok "observe" -> D.decodeValue (D.at ["scope","context","incarnation"] positive) wire |> Result.map (\incarnation -> identity == "family:" ++ UInt64.string incarnation) |> Result.withDefault False
        Ok "attach" -> D.decodeValue (D.at ["scope","context","incarnation"] positive) wire |> Result.map (\incarnation -> identity == "family:" ++ UInt64.string incarnation) |> Result.withDefault False
        _ -> True

familyFrameOwns : Maybe NativePreviewSource.Source -> D.Value -> Bool
familyFrameOwns sourceKind wire =
    if not (case sourceKind of
        Just NativePreviewSource.StyleCroppedFamily -> True
        Just (NativePreviewSource.GeneratedBackdropFamily _) -> True
        _ -> False) then True
    else
        let shape = D.map2 (\fidelity coverage -> fidelity == "family" && List.sort coverage == [ "client", "decoration", "modal", "popup" ]) (D.field "fidelity" D.string) (D.field "coverage" (D.list D.string))
            admit path = D.decodeValue (D.at path shape) wire |> Result.withDefault False
        in case D.decodeValue (D.field "kind" D.string) wire of
            Ok "offer" -> admit [ "frame" ]
            Ok "fence" -> admit [ "frame" ]
            Ok "expired" -> admit [ "frame" ]
            Ok "receipt" -> case D.decodeValue (D.at [ "event", "kind" ] D.string) wire of
                Ok "released" -> admit [ "event", "frame" ]
                _ -> True
            _ -> True

-- Current native color is a source fact. It does not alter the identity of an
-- already owned historical image or authorize switching between capture planes.
sameSourcePlane : Maybe NativePreviewSource.Source -> Maybe NativePreviewSource.Source -> Bool
sameSourcePlane old current =
    case (old,current) of
        (Just (NativePreviewSource.GeneratedBackdropFamily _),Just (NativePreviewSource.GeneratedBackdropFamily _)) -> True
        _ -> old == current

same : Stamp -> SurfaceRenderer.Snapshot -> Bool
same stamp snapshot = stamp.publication == SurfaceRenderer.publication snapshot && stamp.lease == SurfaceRenderer.lease snapshot && SurfaceRenderer.mode snapshot == "picker"

encode : List Output -> E.Value
encode outputs = E.list (\out -> E.object [("identity",E.string out.identity),("commands",Preview.encodeCommands out.commands)]) (List.filter (\out -> not (List.isEmpty out.commands)) outputs)

-- Closing the UI cancels demand but keeps every lifecycle, request counter and
-- pending receipt. Late cleanup events continue to reach the retained owner.
present : Maybe SurfaceRenderer.Snapshot -> Model -> (Model,E.Value)
present snapshot (Model entries catalog ledger scoped) =
    let advance identity entry (next,outputs) =
            let current = entry.stamp |> Maybe.map (\stamp -> snapshot |> Maybe.map (\shown -> same stamp shown && SurfaceRenderer.enabled True identity shown) |> Maybe.withDefault False) |> Maybe.withDefault False
            in if current || entry.stamp == Nothing then (Dict.insert identity entry next,outputs)
               else
                let (closed,commands) = closeEntry entry
                in (if (not scoped.closing && closed.model == Nothing && closed.retirement == Nothing && closed.detachment == Nothing) then Dict.remove identity next else Dict.insert identity closed next,outputs ++ [{identity=identity,commands=commands}])
        (collected,emissions) = Dict.foldl advance (Dict.empty,[]) entries
    in (Model collected catalog ledger scoped,wrap scoped (encode emissions))

-- Readiness shares the same output port as cleanup and exact terminal ACK.
-- It is appended after those controls, with no Cmd.batch ordering assumption.
receive : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receive snapshot raw ((Model _ _ _ scoped) as prior) =
    if scoped.grant /= Nothing then (prior,encode []) else receiveOwned snapshot raw prior

receiveOwned : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receiveOwned snapshot raw prior =
    let
        (Model entries catalog ledger scoped,emitted) = receiveInput snapshot raw prior
        settled entry = entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True
        advance identity entry (next,ready) =
            case entry.retirement of
                Just observation ->
                    if not entry.readySent && settled entry then
                        (Dict.insert identity {entry | readySent=True} next,
                            ready ++ [E.object [("identity",E.string identity),("commands",E.list (\command -> command) [Retirement.readyCommand observation])]])
                    else (Dict.insert identity entry next,ready)
                Nothing ->
                    case entry.detachment of
                        Just seed ->
                            if not entry.detachReadySent && settled entry && floorMatches entry seed then
                                (Dict.insert identity {entry | detachReadySent=True} next,
                                    ready ++ [E.object [("identity",E.string identity),("commands",E.list (\value -> value) [Detachment.ready seed])]])
                            else (Dict.insert identity entry next,ready)
                        Nothing -> (Dict.insert identity entry next,ready)
        (retained,barriers) = Dict.foldl advance (Dict.empty,[]) entries
        cleanup = D.decodeValue (D.list D.value) emitted |> Result.withDefault []
    in (Model retained catalog ledger scoped,E.list identity (cleanup ++ barriers))

receiveInput : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receiveInput snapshot raw ((Model entries previousCatalog ledger scoped) as prior) =
    case D.decodeValue input raw of
        Err _ -> (prior,encode [])
        Ok (DetachSeed seed) ->
            let identity = "family:" ++ UInt64.string seed.subject
                own = scoped.grant |> Maybe.map (\grant -> Realm.same grant.domain seed.domain) |> Maybe.withDefault False
            in if not own || scoped.closed then (prior,encode [])
               else case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if entry.binding /= Realm.owner seed.domain || entry.retirement /= Nothing || not (floorMatches entry seed) ||
                        (entry.detachment /= Nothing && entry.detachment /= Just seed) then (prior,encode [])
                    else
                        let (Model retained catalog held nextScoped,cleanup) = quarantineOwned prior
                            updated = Dict.update identity (Maybe.map (\row -> {row | detachment=Just seed})) retained
                        in (Model updated catalog held nextScoped,cleanup)
        Ok (Detached delivery) ->
            let seed = delivery.seed
                identity = "family:" ++ UInt64.string seed.subject
                own = scoped.grant |> Maybe.map (\grant -> Realm.same grant.domain seed.domain) |> Maybe.withDefault False
                ack = E.list (\value -> value) [E.object [("identity",E.string identity),("commands",E.list (\value -> value) [Detachment.acknowledgment delivery])]]
            in if not own || scoped.closed then (prior,encode [])
               else if UInt64.compare delivery.ordinal scoped.processed /= GT then
                if Dict.get identity scoped.completed == Just (delivery.ordinal,seed) then (prior,encode []) else (prior,encode [])
               else if UInt64.next scoped.processed /= Just delivery.ordinal then (prior,encode [])
               else case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if entry.retirement /= Nothing || not entry.detachReadySent || entry.detachment /= Just seed || not (floorMatches entry seed) ||
                        not (entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True) || Dict.size scoped.completed >= 256 then (prior,encode [])
                    else (Model (Dict.remove identity entries) previousCatalog ledger
                        {scoped | processed=delivery.ordinal,completed=Dict.insert identity (delivery.ordinal,seed) scoped.completed},ack)
        Ok (RetirementChannel owner) ->
            let known = (not (Dict.isEmpty entries) || (previousCatalog |> Maybe.map (\catalog -> catalog.binding == owner) |> Maybe.withDefault False)) &&
                    List.all (\entry -> entry.binding == owner) (Dict.values entries)
            in if ledger.channel == Just owner then (prior,encode [])
               else if ledger.channel /= Nothing || ledger.observed /= Nothing || ledger.settled /= Nothing || not known then (prior,encode [])
               else (Model entries previousCatalog {ledger | channel=Just owner} scoped,encode [])
        Ok (RetirementDelivery delivery) ->
            let fact = delivery.fact
                identity = "family:" ++ UInt64.string fact.native.subject
                acknowledge = E.list (\value -> value) [E.object [("identity",E.string identity),
                    ("commands",E.list (\value -> value) [Retirement.deliveryAcknowledgment delivery])]]
            in if ledger.channel /= Just (Retirement.owner fact.native) then (prior,encode [])
               else if UInt64.compare delivery.ordinal ledger.processed /= GT then (prior,acknowledge)
               else if UInt64.next ledger.processed /= Just delivery.ordinal then (prior,encode [])
               else case Dict.get identity entries of
                   Nothing -> (prior,encode [])
                   Just entry ->
                       let settled = entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True
                           exact = entry.retirement |> Maybe.map (\pending -> Retirement.settles pending fact) |> Maybe.withDefault False
                       in if not entry.readySent || not settled || not exact || not (Retirement.coherentFrontier ledger fact) then (prior,encode [])
                          else
                              let confirmed = Retirement.confirm ledger fact
                              in (Model (Dict.remove identity entries) previousCatalog {confirmed | processed=delivery.ordinal} scoped,acknowledge)
        Ok (Retirement observation) ->
            let identity = "family:" ++ UInt64.string observation.subject
            in case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if (ledger.channel /= Nothing && ledger.channel /= Just (Retirement.owner observation)) || entry.binding /= Retirement.owner observation || entry.retirement /= Nothing || entry.detachment /= Nothing ||
                        not (entry.model |> Maybe.map (\lifecycle -> D.decodeValue (D.field "scope" D.value) (Preview.observe lifecycle) |> Result.map (Retirement.scopeBefore observation) |> Result.withDefault False) |> Maybe.withDefault True) then (prior,encode [])
                    else
                        let (closed,commands) = retireEntry entry
                            pending = {closed | retirement=Just observation,readySent=False}
                        in (Model (Dict.insert identity pending entries) previousCatalog (Retirement.remember ledger observation) scoped,
                            encode [{identity=identity,commands=commands}])
        Ok (Retired fact) ->
            let identity = "family:" ++ UInt64.string fact.native.subject
            in case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    let settled = entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True
                        exact = entry.retirement |> Maybe.map (\pending -> Retirement.settles pending fact) |> Maybe.withDefault False
                        frontier = Retirement.coherentFrontier ledger fact
                    in if ledger.channel /= Nothing || not entry.readySent || not settled || not exact || not frontier then (prior,encode [])
                       else (Model (Dict.remove identity entries) previousCatalog (Retirement.confirm ledger fact) scoped,encode [])
        Ok (Catalog stamp current rows) ->
            let allowed = snapshot |> Maybe.map (same stamp) |> Maybe.withDefault False
                monotonic = previousCatalog |> Maybe.map (\previous -> current.binding == previous.binding && UInt64.compare current.request previous.request == GT && UInt64.compare current.sequence previous.sequence == GT && UInt64.compare current.revision previous.revision /= LT) |> Maybe.withDefault True
                admitted = rows |> List.filter (\row -> snapshot |> Maybe.map (SurfaceRenderer.enabled True ("family:" ++ UInt64.string row.subject)) |> Maybe.withDefault False)
                identities = Set.fromList (List.map (.subject >> UInt64.string >> (++) "family:") admitted)
                ownersMatch = List.all (\entry -> entry.binding == current.binding) (Dict.values entries)
                prune identity entry (next,outputs) =
                    if Set.member identity identities then (Dict.insert identity entry next,outputs)
                    else
                        let (closed,commands) = closeEntry entry
                        in (if (not scoped.closing && closed.model == Nothing && closed.retirement == Nothing && closed.detachment == Nothing) then next else Dict.insert identity closed next,outputs ++ [{identity=identity,commands=commands}])
                (retained,cleanup) = Dict.foldl prune (Dict.empty,[]) entries
                enroll row next =
                    let identity = "family:" ++ UInt64.string row.subject
                    in case Dict.get identity next of
                        Just entry ->
                            -- Existing jobs and scopes have their own source/metadata
                            -- authority. Inventory neither reopens demand nor updates them.
                            if scoped.closing || Dict.member identity scoped.completed || entry.model /= Nothing || entry.retirement /= Nothing || entry.detachment /= Nothing then next
                            else Dict.insert identity {entry | stamp=Just stamp,title=row.title,application=row.application,metadataRevision=Just current.request,minimized=Just row.minimized} next
                        Nothing -> if scoped.closing || Dict.member identity scoped.completed then next else Dict.insert identity {model=Nothing,binding=current.binding,source=Nothing,stamp=Just stamp,title=row.title,application=row.application,icon=Nothing,iconKind="unavailable",metadataRevision=Just current.request,minimized=Just row.minimized,local=Nothing,feedbackFloor=Nothing,retirement=Nothing,readySent=False,detachment=Nothing,detachReadySent=False} next
                enrolled = List.foldl enroll retained admitted
            in if not allowed || not monotonic || not ownersMatch || (ledger.settled |> Maybe.map (\final -> UInt64.compare current.request final.native.request /= GT) |> Maybe.withDefault False) || Dict.size enrolled > 2051 then (prior,encode [])
               else (Model enrolled (Just current) ledger scoped,encode cleanup)
        Ok (Metadata identity owner subject revision title application icon iconKind) ->
            case Dict.get identity entries of
                Just entry ->
                    if scoped.closing || identity /= "family:" ++ UInt64.string subject || entry.binding /= owner || entry.retirement /= Nothing || entry.detachment /= Nothing || (icon == Nothing) /= (iconKind == "unavailable") || (entry.metadataRevision |> Maybe.map (\previous -> UInt64.compare revision previous /= GT) |> Maybe.withDefault False) then (prior,encode [])
                    else (Model (Dict.insert identity {entry | title=title,application=application,icon=icon,iconKind=iconKind,metadataRevision=Just revision} entries) previousCatalog ledger scoped,encode [])
                Nothing -> (prior,encode [])
        Ok (Feedback identity local) ->
            case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    let current = snapshot |> Maybe.map (\shown -> same local.stamp shown && SurfaceRenderer.enabled True identity shown) |> Maybe.withDefault False
                        scopeMatches = entry.model |> Maybe.map (\lifecycle -> Preview.idle lifecycle && (D.decodeValue (D.at ["scope","clock"] positive) (Preview.observe lifecycle) == Ok local.clock)) |> Maybe.withDefault False
                        newer = entry.feedbackFloor |> Maybe.map (\floor -> UInt64.compare local.sequence floor == GT) |> Maybe.withDefault True
                    in if scoped.closing || not current || not scopeMatches || not newer || entry.retirement /= Nothing || entry.detachment /= Nothing || entry.binding /= local.owner || identity /= "family:" ++ UInt64.string local.subject then (prior,encode [])
                       else (Model (Dict.insert identity {entry | stamp=Just local.stamp,local=Just local,feedbackFloor=Just local.sequence} entries) previousCatalog ledger scoped,encode [])
        Ok (Event identity event wire) ->
            case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if entry.readySent || not (eventOwns identity wire && familyFrameOwns entry.source wire) || ((scoped.closing || entry.retirement /= Nothing || entry.detachment /= Nothing) && (D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> List.member kind ["open","request","attach","observe"]) |> Result.withDefault True)) then (prior,encode [])
                    else case entry.model of
                        Nothing -> (prior,encode [])
                        Just lifecycle ->
                            let (next,commands) = Preview.update event lifecycle
                                owner = D.decodeValue (D.at ["scope","binding"] binding) (Preview.observe next) |> Result.withDefault entry.binding
                                updated = if owner == entry.binding then {entry | model=Just next,local=if Preview.idle next then entry.local else Nothing} else {entry | model=Just next,binding=owner,title="Preview unavailable",application="",icon=Nothing,iconKind="unavailable",metadataRevision=Nothing,local=Nothing,feedbackFloor=Nothing}
                            in (Model (Dict.insert identity updated entries) previousCatalog ledger scoped,encode [{identity=identity,commands=commands}])
        Ok (Seed stamp identity scope native title application owner sourceKind unissued sequence) ->
            let allowed = snapshot |> Maybe.map (\shown -> same stamp shown && SurfaceRenderer.enabled True identity shown) |> Maybe.withDefault False
                old = Dict.get identity entries
                matching = old |> Maybe.map (\entry -> not scoped.closing && entry.binding == owner && entry.retirement == Nothing && entry.detachment == Nothing && (entry.model == Nothing || (sameSourcePlane entry.source sourceKind && (not unissued || (entry.model |> Maybe.map Preview.idle |> Maybe.withDefault True))))) |> Maybe.withDefault True
                observeEvent = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "observe"),("scope",native)])
                openEvent = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "open")])
            in if scoped.closing || not allowed || not matching || (old == Nothing && not (Retirement.admittedAfter ledger owner native)) || (old == Nothing && Dict.size entries >= 2051) then (prior,encode [])
               else
                let base = old |> Maybe.andThen .model |> Maybe.withDefault (Preview.init scope)
                    (observed,first) = observeEvent |> Result.map (\event -> Preview.update event base) |> Result.withDefault (base,[])
                    (opened,second) = if unissued then (observed,[]) else openEvent |> Result.map (\event -> Preview.update event observed) |> Result.withDefault (observed,[])
                    floor = old |> Maybe.andThen .feedbackFloor
                    entry = {model=Just opened,binding=owner,source=sourceKind,stamp=Just stamp,title=old |> Maybe.map .title |> Maybe.withDefault title,application=old |> Maybe.map .application |> Maybe.withDefault application,icon=old |> Maybe.andThen .icon,iconKind=old |> Maybe.map .iconKind |> Maybe.withDefault "unavailable",metadataRevision=old |> Maybe.andThen .metadataRevision,minimized=old |> Maybe.andThen .minimized,local=if unissued then old |> Maybe.andThen .local else Nothing,feedbackFloor=if unissued then floor else advanceFloor floor sequence,retirement=Nothing,readySent=False,detachment=Nothing,detachReadySent=False}
                in (Model (Dict.insert identity entry entries) previousCatalog ledger scoped,encode [{identity=identity,commands=first ++ second}])

image : SurfaceRenderer.Snapshot -> String -> Model -> Html msg
image snapshot identity (Model entries _ _ _) =
    Dict.get identity entries |> Maybe.andThen (\entry -> entry.stamp |> Maybe.andThen (\stamp -> if same stamp snapshot && SurfaceRenderer.enabled True identity snapshot then Just (case entry.local of
        Just local -> if entry.model |> Maybe.map Preview.idle |> Maybe.withDefault False then span [class "window-preview",attribute "data-preview-state" (outcomeName local.outcome)] [span [class "preview-title"] [text entry.title],span [class "preview-state",attribute "role" "status",attribute "aria-live" "polite"] [text (outcomeLabel local.outcome)]] else entryView entry
        Nothing -> entryView entry) else Nothing)) |> Maybe.withDefault (text "")

entryView : Entry -> Html msg
entryView entry = entry.model |> Maybe.map (Preview.inlineView {title=entry.title,application=entry.application,icon=entry.icon}) |> Maybe.withDefault (span [class "window-preview",attribute "data-preview-state" "unavailable"] [span [class "preview-title"] [text "Preview unavailable"],span [class "preview-state"] [text "Preview unavailable"]])

outcomeName : LocalOutcome -> String
outcomeName outcome = case outcome of
    Capacity -> "capacity"
    Waiting -> "waiting"
    Expired -> "expired"
    Conflict -> "conflict"
    Exhausted -> "exhausted"

outcomeLabel : LocalOutcome -> String
outcomeLabel outcome = case outcome of
    Capacity -> "Waiting for preview capacity"
    Waiting -> "Waiting for preview"
    Expired -> "Preview request expired"
    Conflict -> "Preview request changed"
    Exhausted -> "Preview unavailable"

feedback : Model -> E.Value
feedback (Model entries _ _ _) = E.list (\(identity,entry) -> E.object [("identity",E.string identity),("floor",entry.feedbackFloor |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("outcome",entry.local |> Maybe.map (.outcome >> outcomeName >> E.string) |> Maybe.withDefault E.null),("label",entry.local |> Maybe.map (.outcome >> outcomeLabel >> E.string) |> Maybe.withDefault E.null),("deadline",entry.local |> Maybe.map (.deadline >> UInt64.string >> E.string) |> Maybe.withDefault E.null)]) (Dict.toList entries)

observe : Model -> E.Value
observe (Model entries _ _ _) = E.list (\(identity,entry) -> E.object [("identity",E.string identity),("active",E.bool (entry.stamp /= Nothing)),("model",entry.model |> Maybe.map Preview.observe |> Maybe.withDefault E.null)]) (Dict.toList entries)

metadata : Model -> E.Value
metadata (Model entries _ _ _) = E.list (\(identity,entry) -> E.object [("identity",E.string identity),("title",E.string entry.title),("application",E.string entry.application),("revision",entry.metadataRevision |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("iconKind",E.string entry.iconKind),("hasIcon",E.bool (entry.icon /= Nothing)),("visible",E.bool (entry.model |> Maybe.map Preview.metadataVisible |> Maybe.withDefault False))]) (Dict.toList entries)

-- Metadata-only inventory is observable without fabricating a capture Scope.
enrollment : Model -> E.Value
enrollment (Model entries _ _ _) = E.list (\(identity,entry) -> E.object [("identity",E.string identity),("nativeScoped",E.bool (entry.model /= Nothing)),("minimized",entry.minimized |> Maybe.map E.bool |> Maybe.withDefault E.null)]) (Dict.toList entries)
