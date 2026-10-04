port module Probe exposing (main)
import Desktop
import Json.Encode as E
import Json.Decode as D
import Platform
import SurfaceController as C
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run _) _ ->
 let before=C.initial
     (after,effects)=C.update (C.Interaction (Desktop.PresentationOwner (Just {outputId=(UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero),providerId=(UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero)}))) before
     identity frame = D.decodeValue (D.map5 (\mode status bar popup lease -> E.object [("mode",E.string mode),("status",E.string status),("bar",bar),("popup",popup),("lease",E.string lease)])) (D.field "mode" D.string) (D.field "status" D.string) (D.field "bar" D.value) (D.field "popup" D.value) (D.field "lease" D.string)) frame |> Result.map (E.encode 0) |> Result.withDefault "invalid"
     publications=List.filterMap (\effect -> case effect of
          C.Publish frame -> Just frame
          _ -> Nothing) effects
 in ((),outgoing (E.object [("stateChanged",E.bool (C.desktop after/=C.desktop before)),("sameSurface",E.bool (identity (C.frame after)==identity (C.frame before))),("publishCount",E.int (List.length publications)),("before",C.frame before),("after",C.frame after)]))}
