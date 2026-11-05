port module PreviewConsumptionReplay exposing (main)

import Desktop
import Presentation
import Surface
import SurfaceRenderer
import UInt64
import Json.Decode as D
import Json.Encode as E
import Platform
import NativePreviewProposalIngress as Ingress
import NativePreviewRealm as Realm
import Popup
import RetainedPreviewPresenter as Preview

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value
type alias Model = { popup : Popup.Model, saved : List Ingress.AcceptedTicket }

main : Program () Model Msg
main = Platform.worker { init = \_ -> ( { popup = Popup.initial, saved = [] }, Cmd.none ), subscriptions = \_ -> incoming Run, update = update }

update : Msg -> Model -> ( Model, Cmd Msg )
update (Run raw) model =
    let
        kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        value = D.decodeValue (D.field "value" D.value) raw |> Result.withDefault E.null
        index = D.decodeValue (D.field "index" D.int) raw |> Result.withDefault -1
        sequence = D.decodeValue (D.field "sequence" D.int) raw |> Result.withDefault -1
        selected = Popup.pendingConfirmations model.popup |> List.drop (max 0 index) |> List.head
        saved = model.saved |> List.drop (max 0 index) |> List.head
        message = case kind of
            "presentClosed" ->
                let one = D.decodeValue UInt64.decoder (E.string "1") |> Result.withDefault UInt64.zero
                    base = Desktop.initial
                in Just (Popup.Present (Surface.packet one one { base | open = False, filesOpen = False }))
            "grant" -> Just (Popup.NativeGrant value)
            "quarantine" -> Just (Popup.NativeQuarantine value)
            "issued" -> Just (Popup.NativeIssued value)
            "closed" -> Just (Popup.NativeClosed value)
            "retry" -> Just (Popup.NativeRetry value)
            "complete" -> if index < 0 then Nothing else Maybe.map Popup.ConfirmationTransportCompleted selected
            "completeSaved" -> if index < 0 then Nothing else Maybe.map Popup.ConfirmationTransportCompleted saved
            _ -> Nothing
        (next,effects) = message |> Maybe.map (\msg -> Popup.transition msg model.popup) |> Maybe.withDefault (model.popup,[])
        accepted = List.filterMap (\effect -> case effect of
            Popup.TicketConsumed ticket -> Just (Popup.encodeConsumed ticket)
            _ -> Nothing) effects
        tickets = List.filterMap (\effect -> case effect of
            Popup.TicketConsumed ticket -> Just ticket
            _ -> Nothing) effects
        ingressTicket =
            let grant = D.decodeValue (D.field "grant" Realm.grantDecoder) value |> Result.toMaybe
                proposal = D.decodeValue (D.field "proposal" D.value) value |> Result.toMaybe
                ticket = D.decodeValue (D.field "ticket" D.value) value |> Result.toMaybe
            in case (grant,proposal,ticket) of
                (Just g,Just offered,Just fact) ->
                    Ingress.decode g offered |> Maybe.andThen (\intents -> Ingress.enqueue intents (Ingress.empty g))
                        |> Maybe.andThen (Ingress.issuedWithConfirmation fact)
                        |> Maybe.map Tuple.second
                _ -> Nothing
        effectNames = List.map (\effect -> case effect of
            Popup.Dispatch _ -> "Dispatch"
            Popup.PreviewCommand _ -> "PreviewCommand"
            Popup.PaintRequest _ -> "PaintRequest"
            Popup.TicketConsumed _ -> "TicketConsumed") effects
        result = E.object
            [ ("sequence", E.int sequence)
            , ("ingress", ingressTicket |> Maybe.map Ingress.encodeConsumed |> Maybe.withDefault E.null)
            , ("wholePopupUnchanged", E.bool (next == model.popup))
            , ("effectCount", E.int (List.length effects))
            , ("effectTypes", E.list E.string effectNames)
            , ("outbox", E.list Popup.encodeConsumed (Popup.pendingConfirmations next))
            , ("accepted", E.list identity accepted)
            , ("realm", Preview.realmStatus next.previews)
            , ("mode", next.presentation |> Presentation.current |> Maybe.map (SurfaceRenderer.mode >> E.string) |> Maybe.withDefault E.null)
            , ("subscription", E.bool (List.member Popup.RequestActionChannel (Popup.subscriptionPlan next)))
            ]
    in ({ popup = next, saved = model.saved ++ tickets ++ (ingressTicket |> Maybe.map List.singleton |> Maybe.withDefault []) },outgoing result)
