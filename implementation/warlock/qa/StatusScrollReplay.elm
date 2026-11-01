port module StatusScrollReplay exposing (main)

-- Drives actual Bar.step and opaque StatusScroll; no synthetic state machine.
import Bar
import Json.Decode as D
import Json.Encode as E
import Platform
import Presentation
import StatusScroll
import SurfaceSnapshot
import SurfaceRenderer
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Input D.Value
encodeEffect effect = case effect of
    Bar.Dispatch raw -> E.object [("kind",E.string "dispatch"),("wire",raw)]
    Bar.ResetStatusViewport epoch target -> E.object [("kind",E.string "reset"),("epoch",E.string (StatusScroll.epochString epoch)),("target",E.string target)]
report model effects =
    let details=Presentation.current model.presentation |> Maybe.map SurfaceSnapshot.details
        nullable encode value = value |> Maybe.map encode |> Maybe.withDefault E.null
    in outgoing (E.object
        [ ("status",nullable E.string (details |> Maybe.map .status))
        , ("publication",nullable (UInt64.string >> E.string) (details |> Maybe.map .publication))
        , ("controlIds",E.list E.string (Presentation.current model.presentation |> Maybe.map (\snapshot -> let v=SurfaceSnapshot.details snapshot in List.map (.domId >> SurfaceRenderer.controlDomId snapshot) (v.bar ++ v.popup)) |> Maybe.withDefault []))
        , ("scrollStatus",nullable E.string (StatusScroll.currentStatus model.statusScroll))
        , ("epoch",nullable (StatusScroll.epochString >> E.string) (StatusScroll.epoch model.statusScroll))
        , ("domId",nullable E.string (Bar.statusDomId model))
        , ("exhausted",E.bool (StatusScroll.exhausted model.statusScroll))
        , ("effects",E.list encodeEffect effects)
        ])
update (Input raw) model =
    let kind=D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        value=D.decodeValue (D.field "value" D.value) raw |> Result.withDefault E.null
        floor=D.decodeValue (D.field "floor" UInt64.decoder) raw |> Result.withDefault UInt64.zero
        (next,effects)=case kind of
            "reset" -> (Bar.initialWithScroll (StatusScroll.fromFloor floor),[])
            "present" -> Bar.step (Bar.Present value) model
            "action" -> Bar.step (Bar.Action value) model
            "settled" -> Bar.step Bar.ViewportSettled model
            _ -> (model,[])
    in (next,report next effects)
main : Program () Bar.Model Msg
main = Platform.worker {init=\_ -> (Bar.initial,Cmd.none),update=update,subscriptions=\_ -> incoming Input}
