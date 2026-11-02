port module NativePreviewRenderer exposing (main, Msg(..), Subscription(..), subscriptionPlan, subscriptions)

import Browser
import Json.Decode as D
import Json.Encode as E
import NativePreviewReceiver as Receiver

port visualSnapshots : (D.Value -> msg) -> Sub msg
port acceptedSnapshots : E.Value -> Cmd msg
-- These remain ordinary surface actions. Actual native callback routing must
-- independently bind the current renderer/context and original surface gates.
port surfaceActions : E.Value -> Cmd msg
type Msg = Snapshot D.Value | Action E.Value
type Subscription = VisualSnapshotsChannel

subscriptionPlan : Receiver.Model -> List Subscription
subscriptionPlan model =
    if Receiver.acceptsSnapshots model then
        [ VisualSnapshotsChannel ]
    else
        []

subscriptions : Receiver.Model -> Sub Msg
subscriptions model =
    Sub.batch
        (List.map
            (\channel ->
                case channel of
                    VisualSnapshotsChannel ->
                        visualSnapshots Snapshot
            )
            (subscriptionPlan model)
        )

main : Program D.Value Receiver.Model Msg
main = Browser.element
    { init=\flags -> (Receiver.init flags,Cmd.none)
    , subscriptions=subscriptions
    , view=Receiver.view Action
    , update=\message model -> case message of
        Snapshot raw -> let (next,receipt)=Receiver.receive raw model in (next,receipt |> Maybe.map acceptedSnapshots |> Maybe.withDefault Cmd.none)
        Action value -> (model,surfaceActions value)
    }
