module Scene exposing (Admitted, decode, focus, hit, paint)

import Json.Decode as D
import Set
import UInt64 exposing (Counter)


type Incarnation = Incarnation Counter
type Revision = Revision Counter

type alias Window =
    { id : Incarnation
    , owner : Maybe Incarnation
    , mapped : Bool
    , minimized : Bool
    , member : Bool
    , modal : Bool
    , inputAtProbe : Bool
    }

type alias Candidate =
    { revision : Revision
    , locked : Bool
    , windows : List Window
    , order : List Incarnation
    , focused : Maybe Incarnation
    }

-- Only successful admission constructs this value. No consumer receives partial
-- paint/input/focus results from a refused candidate.
type Admitted = Admitted Candidate

key : Incarnation -> String
key (Incarnation value) = UInt64.string value

strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder =
    D.keyValuePairs D.value
        |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort names then decoder else D.fail "Unexpected or missing scene field")

identity : D.Decoder Counter
identity = UInt64.decoder |> D.andThen (\value -> if value == UInt64.zero then D.fail "Zero identity" else D.succeed value)

incarnation : D.Decoder Incarnation
incarnation = D.map Incarnation identity

windowDecoder : D.Decoder Window
windowDecoder =
    strict [ "id", "owner", "mapped", "minimized", "member", "modal", "inputAtProbe" ]
        (D.map7 Window
            (D.field "id" incarnation)
            (D.field "owner" (D.nullable incarnation))
            (D.field "mapped" D.bool)
            (D.field "minimized" D.bool)
            (D.field "member" D.bool)
            (D.field "modal" D.bool)
            (D.field "inputAtProbe" D.bool))

find : Candidate -> Incarnation -> Maybe Window
find candidate id = List.filter (\window -> window.id == id) candidate.windows |> List.head

ancestry : Candidate -> List Incarnation -> Window -> Result String (List Incarnation)
ancestry candidate seen window =
    case window.owner of
        Nothing -> Ok []
        Just parent ->
            if List.length seen >= 32 then
                Err "Family depth bound exceeded"
            else if List.member parent (window.id :: seen) then
                Err "Cyclic family"
            else
                case find candidate parent of
                    Nothing -> Err "Unknown owner"
                    Just owner -> ancestry candidate (window.id :: seen) owner |> Result.map ((::) parent)

eligible : Candidate -> Window -> Bool
eligible candidate window =
    not candidate.locked && window.mapped && not window.minimized && window.member
        && (case window.owner of
                Nothing -> True
                Just parent -> True
           )

unique : List Incarnation -> Bool
unique ids = Set.size (Set.fromList (List.map key ids)) == List.length ids

index : Incarnation -> List Incarnation -> Int
index id order =
    List.indexedMap Tuple.pair order
        |> List.filter (\(_, entry) -> entry == id)
        |> List.head |> Maybe.map Tuple.first |> Maybe.withDefault -1

validate : Candidate -> Result String Admitted
validate candidate =
    let
        ids = List.map .id candidate.windows
        families = if List.length candidate.windows > 256 then [] else List.map (ancestry candidate []) candidate.windows
        familyError = List.filterMap (\result -> case result of
            Err message -> Just message
            Ok _ -> Nothing) families |> List.head
        live = if familyError /= Nothing || List.length candidate.windows > 256 then [] else List.filter (eligible candidate) candidate.windows
        sameMembers = List.sort (List.map key candidate.order) == List.sort (List.map (.id >> key) live)
        orderedFamily window = case window.owner of
            Nothing -> True
            Just parent -> index parent candidate.order < index window.id candidate.order
        focusEligible = case candidate.focused of
            Nothing -> True
            Just id -> List.any (\window -> window.id == id) live
        modalBlocksFocus = case candidate.focused of
            Nothing -> False
            Just id -> List.any (\window -> window.modal && (ancestry candidate [] window |> Result.map (List.member id) |> Result.withDefault False)) live
    in
    if List.length candidate.windows > 256 then
        Err "Scene bound exceeded"
    else if not (unique ids) then
        Err "Duplicate incarnation"
    else case familyError of
        Just message -> Err message
        Nothing ->
            if not (unique candidate.order) || not sameMembers then
                Err "Order does not equal live eligibility"
            else if not (List.all orderedFamily live) then
                Err "Child precedes owner"
            else if not focusEligible || modalBlocksFocus then
                Err "Ineligible or modal-blocked focus"
            else
                Ok (Admitted candidate)

decode : D.Value -> Result String Admitted
decode value =
    D.decodeValue
        (strict [ "revision", "locked", "windows", "order", "focused" ]
            (D.map5 Candidate
                (D.field "revision" (D.map Revision identity))
                (D.field "locked" D.bool)
                (D.field "windows" (D.list windowDecoder))
                (D.field "order" (D.list incarnation))
                (D.field "focused" (D.nullable incarnation)))) value
        |> Result.mapError D.errorToString |> Result.andThen validate

paint : Admitted -> List String
paint (Admitted candidate) = List.map key candidate.order

hit : Admitted -> Maybe String
hit (Admitted candidate) =
    List.reverse candidate.order
        |> List.filter (\id -> find candidate id |> Maybe.map .inputAtProbe |> Maybe.withDefault False)
        |> List.head |> Maybe.map key

focus : Admitted -> Maybe String
focus (Admitted candidate) = Maybe.map key candidate.focused
