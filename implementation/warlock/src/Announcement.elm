module Announcement exposing (Model, Message, initial, receive, view, encodeMessage)

import Html exposing (Html, text)
import Html.Attributes exposing (attribute, class)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import SurfaceRenderer
import UInt64 exposing (Counter)

type alias Message = { sequence : Counter, correlation : String, text : String }
type Model = Model { last : Counter, active : Bool, message : Maybe Message }
initial : Model
initial = Model {last=UInt64.zero,active=False,message=Nothing}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Closed announcement fields")
positive = UInt64.decoder |> D.andThen (\n -> if n/=UInt64.zero then D.succeed n else D.fail "Positive announcement identity")
bounded limit = D.string |> D.andThen (\value -> if not (String.isEmpty value) && String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Bounded announcement text")
scope = strict ["id","generation"] (D.map2 Tuple.pair (D.field "id" positive) (D.field "generation" positive))
route = strict ["scope","surface"] (D.map2 Tuple.pair (D.field "scope" scope) (D.field "surface" (D.string |> D.andThen (\value -> if List.member value ["bar","popup"] then D.succeed value else D.fail "Announcement surface"))))
messageDecoder = strict ["sequence","correlation","text"] (D.map3 Message (D.field "sequence" positive) (D.field "correlation" (bounded 2048)) (D.field "text" (bounded 1024)))
encodeMessage message = E.object [("sequence",E.string (UInt64.string message.sequence)),("correlation",E.string message.correlation),("text",E.string message.text)]

-- Scoped presentation facts only: no action, focus command, receipt policy or
-- announcement queue lives in a view. Native delivery is not proof of speech.
receive : Bool -> Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> Model
receive popup snapshot raw ((Model model) as prior) =
    let decoder = strict ["announcementProtocol","kind","recipient","announcer","publication","lease","message","deliver"]
            (D.map8 (\version kind recipient owner publication lease message deliver -> {version=version,kind=kind,recipient=recipient,owner=owner,publication=publication,lease=lease,message=message,deliver=deliver})
                (D.field "announcementProtocol" D.int) (D.field "kind" D.string) (D.field "recipient" route) (D.field "announcer" (D.nullable route)) (D.field "publication" positive) (D.field "lease" UInt64.decoder) (D.field "message" (D.nullable messageDecoder)) (D.field "deliver" D.bool))
    in case (snapshot,D.decodeValue decoder raw) of
        (Just current,Ok packet) ->
            if packet.version/=1 || packet.kind/="announcement-projection" || Tuple.second packet.recipient/=(if popup then "popup" else "bar") || packet.publication/=SurfaceRenderer.publication current || packet.lease/=SurfaceRenderer.lease current then prior
            else if packet.owner/=Just packet.recipient then Model {model | active=False,message=Nothing}
            else case packet.message of
                Just message ->
                    if packet.deliver && UInt64.compare message.sequence model.last==GT then Model {last=message.sequence,active=True,message=Just message}
                    else if model.active && model.message==Just message then prior
                    else Model {model | active=True,message=Nothing}
                Nothing -> Model {model | active=True,message=Nothing}
        _ -> prior

view : Model -> Html msg
view (Model model) =
    if not model.active then text "" else
        Keyed.node "span" [class "shell-announcement",attribute "role" "status",attribute "aria-live" "polite",attribute "aria-atomic" "true"]
            (model.message |> Maybe.map (\message -> [(UInt64.string message.sequence,Html.span [attribute "data-announcement-sequence" (UInt64.string message.sequence),attribute "data-announcement-correlation" message.correlation] [text message.text])]) |> Maybe.withDefault [])
