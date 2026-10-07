module NativePreviewReceiver exposing (Model, init, receive, view, action, inspect)

import Html exposing (Html, text)
import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import NativePreviewVisual as Visual
import UInt64 exposing (Counter)

-- Presentation custody only. No window/lifecycle policy or native effects.
type alias Grant = { domain : Realm.Domain, lease : Counter, floor : Counter }
type Model = Inert | Receiver Grant Counter (Maybe Visual.Projection) Bool

strict : List String -> D.Decoder a -> D.Decoder a
strict fields parser = D.keyValuePairs D.value |> D.andThen (\pairs ->
    if List.sort (List.map Tuple.first pairs)==List.sort fields then parser else D.fail "Closed visual channel fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\n -> if n==UInt64.zero then D.fail "Positive native renderer lease/sequence" else D.succeed n)

grantDecoder : D.Decoder Grant
grantDecoder = strict ["channelProtocol","kind","binding","receiverEpoch","rendererLease","sequenceFloor"]
    (D.map5 (\protocol kind domain lease floor -> (protocol,kind,Grant domain lease floor))
        (D.field "channelProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder
        (D.field "rendererLease" positive) (D.field "sequenceFloor" UInt64.decoder))
    |> D.andThen (\(protocol,kind,grant) -> if protocol==1 && kind=="native-preview-renderer-grant" then D.succeed grant else D.fail "Native renderer grant required")

init : D.Value -> Model
init flags = case D.decodeValue grantDecoder flags of
    Ok grant -> Receiver grant grant.floor Nothing False
    Err _ -> Inert

type alias Packet = { domain : Realm.Domain, lease : Counter, sequence : Counter, raw : D.Value }

packetDecoder : D.Decoder Packet
packetDecoder = strict ["channelProtocol","kind","binding","receiverEpoch","rendererLease","visualSequence","visual"]
    (D.map6 (\protocol kind domain lease sequence raw -> (protocol,kind,Packet domain lease sequence raw))
        (D.field "channelProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder
        (D.field "rendererLease" positive) (D.field "visualSequence" positive) (D.field "visual" D.value))
    |> D.andThen (\(protocol,kind,packet) -> if protocol==1 && kind=="native-preview-projection" then D.succeed packet else D.fail "Native projection packet required")

receipt : Grant -> Counter -> E.Value
receipt grant sequence = E.object [("channelProtocol",E.int 1),("kind",E.string "native-preview-projection-accepted"),
    ("binding",Realm.bindingValue grant.domain),("receiverEpoch",E.string (UInt64.string grant.domain.receiverEpoch)),
    ("rendererLease",E.string (UInt64.string grant.lease)),("visualSequence",E.string (UInt64.string sequence))]

receive : D.Value -> Model -> (Model,Maybe E.Value)
receive raw model = case model of
    Inert -> (model,Nothing)
    Receiver grant last shown poisoned ->
        if poisoned then (model,Nothing)
        else case D.decodeValue packetDecoder raw of
            Err _ -> (Receiver grant last Nothing True,Nothing)
            Ok packet ->
                if not (Realm.same packet.domain grant.domain) || packet.lease/=grant.lease then (model,Nothing)
                else if UInt64.compare packet.sequence grant.floor/=GT || UInt64.compare packet.sequence last==LT then (model,Nothing)
                else case D.decodeValue (Visual.decoder grant.domain) packet.raw of
                    Err _ -> (Receiver grant last Nothing True,Nothing)
                    Ok visual ->
                        if packet.sequence==last then
                            if shown |> Maybe.map (\prior -> E.encode 0 (Visual.encode prior)==E.encode 0 (Visual.encode visual)) |> Maybe.withDefault False then
                                (model,Just (receipt grant last))
                            else (Receiver grant last Nothing True,Nothing)
                        else (Receiver grant packet.sequence (Just visual) False,Just (receipt grant packet.sequence))

view : (E.Value -> msg) -> Model -> Html msg
view send model = case model of
    Receiver _ _ (Just projection) False -> Visual.view send projection
    _ -> text ""

action : String -> Model -> Maybe E.Value
action identity model = case model of
    Receiver _ _ (Just projection) False -> Visual.action identity projection
    _ -> Nothing

inspect : Model -> E.Value
inspect model = case model of
    Inert -> E.object [("inert",E.bool True),("concealed",E.bool True)]
    Receiver grant last shown poisoned -> E.object [("inert",E.bool False),("poisoned",E.bool poisoned),
        ("rendererLease",E.string (UInt64.string grant.lease)),("sequence",E.string (UInt64.string last)),
        ("concealed",E.bool (shown==Nothing)),("visual",shown |> Maybe.map Visual.encode |> Maybe.withDefault E.null)]
