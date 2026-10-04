port module Probe exposing (main)
import Platform
import ReconciliationFrame as R
import Binding
import Effects
import Json.Decode as D
import Json.Encode as E
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let cases=D.decodeValue (D.field "cases" (D.list D.value)) raw |> Result.withDefault []
     result value = case D.decodeValue (D.field "expected" R.expectedDecoder) value of
       Err error -> E.object [("ok",E.bool False),("error",E.string (D.errorToString error))]
       Ok expected ->
        let frame=D.decodeValue (D.field "frame" D.value) value |> Result.withDefault E.null
            released=D.decodeValue (D.field "released" D.bool) value |> Result.withDefault True
            decoded=if released then R.decodeReleased expected frame else R.decodeUnknown expected.currentBinding frame
        in case decoded of
          Err error -> E.object [("ok",E.bool False),("error",E.string error)]
          Ok success -> case success of
            R.ReservationUnknown _ record -> E.object [("ok",E.bool True),("historicalStatus",E.string (Effects.statusName record.status)),("intent",Effects.encodeIntent record.intent)]
            R.ReservationReleased _ record release -> E.object [("ok",E.bool True),("historicalStatus",E.string (Effects.statusName record.status)),("intent",Effects.encodeIntent record.intent),("releaseId",E.string release.id)]
 in ((),outgoing (E.list result cases))}
