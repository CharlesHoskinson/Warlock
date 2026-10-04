module OwnPopupPreparation exposing (Action(..), Snapshot, Host, Native, Proof, Model, Decision(..), initial, authenticate, retain, select, closed, reply, cancel, expire, prepared)

import Binding
import UInt64 exposing (Counter)

type Action = Maximize | RestoreGeometry

type alias Snapshot =
    { binding : Binding.Binding, incarnation : Counter, output : Counter, workArea : Counter
    , legacyRevision : Counter, geometryRevision : Counter, legacyRead : Counter, geometryRead : Counter, structure : String, action : Action, eligible : Bool, allowed : Bool }

type alias Host =
    { pid : Int, started : Counter, surface : Int, view : Counter, generation : Counter
    , topology : Counter, publication : Counter, lease : Counter, menu : Counter }

-- Integration boundary: these are authenticated observations from different
-- owners, not web content. This module does not manufacture their authenticity.
type alias Native =
    { host : Host, binding : Binding.Binding, exclusiveOwnGrab : Bool
    , sessionLocked : Bool, exclusiveLayer : Bool, dragging : Bool, modal : Bool }

type Proof = Proof Host Snapshot

type Phase = AwaitClose | AwaitReads Counter Counter (Maybe Snapshot) (Maybe Snapshot)

type alias Slot = { token : Counter, proof : Proof, deadline : Int, phase : Phase }

type Model = Model { highest : Counter, slot : Maybe Slot, retired : List Host }

type Decision = None | ClosePopup Counter Host | Observe Counter Counter Counter | DispatchFresh Counter Snapshot | Refused String

initial : Model
initial = Model { highest = UInt64.zero, slot = Nothing, retired = [] }

positive : Counter -> Bool
positive n = n /= UInt64.zero

validHost : Host -> Bool
validHost h = h.pid > 1 && h.pid < 2147483648 && h.surface > 0 && h.surface < 2147483648 && List.all positive [h.started,h.view,h.generation,h.topology,h.publication,h.lease,h.menu]

sameStructure : Snapshot -> Snapshot -> Bool
sameStructure before after = before.binding == after.binding && before.incarnation == after.incarnation && before.output == after.output && before.workArea == after.workArea && before.structure == after.structure && before.action == after.action

stable : Snapshot -> Snapshot -> Bool
stable before after = sameStructure before after && UInt64.compare after.legacyRevision before.legacyRevision /= LT && UInt64.compare after.geometryRevision before.geometryRevision /= LT

authenticate : Host -> Native -> Snapshot -> Snapshot -> Maybe Proof
authenticate host native original blocked =
    if validHost host && native.host == host && native.binding == original.binding && not (native.sessionLocked || native.exclusiveLayer || native.dragging || native.modal) && original.eligible && original.allowed && not blocked.eligible && stable original blocked && List.all positive [original.incarnation,original.output,original.workArea,original.legacyRevision,original.geometryRevision,original.legacyRead,original.geometryRead] && String.length original.structure > 0 && String.length original.structure <= 16384 then
        Just (Proof host original)
    else Nothing

retain : Host -> Native -> Snapshot -> Snapshot -> Bool
retain host native original current = authenticate host native original current /= Nothing

prepared : Model -> Maybe Counter
prepared (Model m) = m.slot |> Maybe.map .token

sameMenu : Host -> Host -> Bool
sameMenu a b = a.pid==b.pid && a.started==b.started && a.surface==b.surface && a.view==b.view && a.generation==b.generation && a.topology==b.topology && a.lease==b.lease && a.menu==b.menu

select : Int -> Int -> Proof -> Model -> (Model, Decision)
select now deadline proof ((Model m) as model) =
    let (Proof host _) = proof
    in if now < 0 || deadline <= now || deadline - now > 6000 || m.slot /= Nothing || List.length m.retired>=64 || List.any (sameMenu host) m.retired then (model,Refused "Selection unavailable or expired") else
    case UInt64.next m.highest of
        Nothing -> (model,Refused "Prepared counter exhausted")
        Just token ->
            (Model {highest=token,retired=host::m.retired,slot=Just {token=token,proof=proof,deadline=deadline,phase=AwaitClose}},ClosePopup token host)

closed : Int -> Counter -> Host -> Bool -> Counter -> Counter -> Model -> (Model, Decision)
closed now token host nativeFence legacy geometry ((Model m) as model) =
    case m.slot of
        Nothing -> (model,None)
        Just slot ->
            let (Proof expected original) = slot.proof
            in if token /= slot.token then (model,None) else
               if now < 0 || now >= slot.deadline then cancel token model else
               case slot.phase of
                   AwaitReads _ _ _ _ -> (model,None)
                   AwaitClose ->
                       if host /= expected || not nativeFence || not (positive legacy && positive geometry) || legacy == geometry || UInt64.compare legacy original.legacyRead/=GT || UInt64.compare geometry original.geometryRead/=GT then cancel token model else
                       (Model {m|slot=Just {slot|phase=AwaitReads legacy geometry Nothing Nothing}},Observe token legacy geometry)

reply : Int -> Counter -> Bool -> Counter -> Snapshot -> Model -> (Model, Decision)
reply now token geometry request fresh ((Model m) as model) =
    case m.slot of
        Nothing -> (model,None)
        Just slot ->
            let (Proof _ original) = slot.proof
            in if token /= slot.token then (model,None) else
               if now < 0 || now >= slot.deadline then cancel token model else
               case slot.phase of
                   AwaitClose -> (model,None)
                   AwaitReads legacyId geometryId legacyResult geometryResult ->
                       if request /= (if geometry then geometryId else legacyId) then (model,None) else
                       if not fresh.eligible || not fresh.allowed || (if geometry then fresh.geometryRead else fresh.legacyRead)/=request || not (stable original fresh) then cancel token model else
                       if (if geometry then geometryResult else legacyResult) /= Nothing then (model,None) else
                       let l=if geometry then legacyResult else Just fresh
                           g=if geometry then Just fresh else geometryResult
                       in case (l,g) of
                           (Just legacy,Just geom) ->
                               if not (sameStructure legacy geom) then cancel token model else
                               (Model {m|slot=Nothing},DispatchFresh token {geom|legacyRevision=legacy.legacyRevision,legacyRead=legacy.legacyRead})
                           _ -> (Model {m|slot=Just {slot|phase=AwaitReads legacyId geometryId l g}},None)

cancel : Counter -> Model -> (Model, Decision)
cancel token ((Model m) as model) =
    if (m.slot |> Maybe.map .token) == Just token then (Model {m|slot=Nothing},Refused "Selection canceled; no effect issued") else (model,None)

expire : Int -> Counter -> Model -> (Model, Decision)
expire now token ((Model m) as model) =
    case m.slot of
        Just slot -> if slot.token == token && now >= slot.deadline then cancel token model else (model,None)
        Nothing -> (model,None)
