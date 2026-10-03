module Observation exposing (Binding, Event(..), Incarnation, Revision, Sequence, Window, bindingDecoder, decode, encodeBinding, incarnationString, replacesBinding, revisionCounter, revisionString, sequenceCounter, sequenceString)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)


type Lifetime = Lifetime Counter
type Session = Session Counter
type FrontendEpoch = FrontendEpoch Counter
type Sequence = Sequence Counter
type Revision = Revision Counter
type Incarnation = Incarnation Counter


type alias Binding =
    { lifetime : Lifetime, session : Session, frontend : FrontendEpoch }


type alias Window =
    { incarnation : Incarnation, label : String, minimized : Bool }


-- Delta payloads are a complete replacement of this bounded window projection.
-- This observation-only schema does not carry control events or effect outcomes.
type Event
    = Snapshot Binding Counter Sequence Revision (List Window)
    | Delta Binding Sequence Revision (List Window)


sequenceCounter : Sequence -> Counter
sequenceCounter (Sequence value) = value

sequenceString : Sequence -> String
sequenceString = sequenceCounter >> UInt64.string

revisionCounter : Revision -> Counter
revisionCounter (Revision value) = value

revisionString : Revision -> String
revisionString = revisionCounter >> UInt64.string

incarnationString : Incarnation -> String
incarnationString (Incarnation value) = UInt64.string value


strict : List String -> D.Decoder a -> D.Decoder a
strict fields payload =
    D.keyValuePairs D.value
        |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then payload else D.fail "Unexpected or missing field")


nonzero : D.Decoder Counter
nonzero =
    UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed n else D.fail "Zero identity")


bindingDecoder : D.Decoder Binding
bindingDecoder =
    strict [ "lifetime", "session", "frontend" ]
        (D.map3 Binding (D.field "lifetime" (D.map Lifetime nonzero)) (D.field "session" (D.map Session nonzero)) (D.field "frontend" (D.map FrontendEpoch nonzero)))


replacesBinding : Binding -> Binding -> Bool
replacesBinding incoming current =
    let
        (FrontendEpoch nextEpoch) = incoming.frontend
        (FrontendEpoch oldEpoch) = current.frontend
    in
    incoming.lifetime /= current.lifetime || incoming.session /= current.session || UInt64.compare nextEpoch oldEpoch == GT


encodeBinding : Binding -> E.Value
encodeBinding binding =
    let
        (Lifetime lifetime) = binding.lifetime
        (Session session) = binding.session
        (FrontendEpoch frontend) = binding.frontend
    in
    E.object [ ( "lifetime", E.string (UInt64.string lifetime) ), ( "session", E.string (UInt64.string session) ), ( "frontend", E.string (UInt64.string frontend) ) ]


labelDecoder : D.Decoder String
labelDecoder =
    D.string |> D.andThen (\label -> if String.length label <= 256 && not (String.any (\c -> Char.toCode c < 32) label) then D.succeed label else D.fail "Label bound or control character")


windowsDecoder : D.Decoder (List Window)
windowsDecoder =
    D.list (strict [ "incarnation", "label", "minimized" ] (D.map3 Window (D.field "incarnation" (D.map Incarnation nonzero)) (D.field "label" labelDecoder) (D.field "minimized" D.bool)))
        |> D.andThen
            (\windows ->
                let
                    unique = List.foldl (\window seen -> if List.member window.incarnation seen then seen else window.incarnation :: seen) [] windows
                in
                if List.length windows <= 256 && List.length unique == List.length windows then D.succeed windows else D.fail "Duplicate or oversized projection"
            )


decoder : D.Decoder Event
decoder =
    D.field "protocolVersion" D.int
        |> D.andThen
            (\version ->
                if version /= 2 then D.fail "Unsupported experimental protocol" else
                    D.field "kind" D.string |> D.andThen
                        (\kind ->
                            let
                                fields = [ "protocolVersion", "kind", "binding", "sequence", "revision", "windows" ]
                                binding = D.field "binding" bindingDecoder
                                sequence = D.field "sequence" (D.map Sequence UInt64.decoder)
                                revision = D.field "revision" (D.map Revision UInt64.decoder)
                                windows = D.field "windows" windowsDecoder
                            in
                            case kind of
                                "snapshot" -> strict ("requestId" :: fields) (D.map5 Snapshot binding (D.field "requestId" nonzero) sequence revision windows)
                                "delta" -> strict fields (D.map4 Delta binding sequence revision windows)
                                _ -> D.fail "Unsupported event"
                        )
            )


decode : D.Value -> Result D.Error Event
decode = D.decodeValue decoder
