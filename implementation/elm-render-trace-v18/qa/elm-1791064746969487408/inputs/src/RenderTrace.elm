module RenderTrace exposing (decode, encodeSummary)

import Binding exposing (Binding)
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

-- Diagnostic draw dispatch, deliberately separate from Scene.Admitted.
type Trace = Trace Binding Counter Counter (List Frame)
type alias Frame = { monitor : Counter, serial : Counter, complete : Bool, overflow : Bool, committed : Bool, draws : List Draw }
type alias Draw = { incarnation : Maybe Counter, retired : Bool, main : Bool, popup : Bool }
strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected trace fields")
nonzero : D.Decoder Counter
nonzero = UInt64.decoder |> D.andThen (\n -> if n == UInt64.zero then D.fail "Zero identity" else D.succeed n)
drawDecoder : D.Decoder Draw
drawDecoder = strict ["incarnation","retired","main","popup"] (D.map4 Draw (D.field "incarnation" (D.nullable nonzero)) (D.field "retired" D.bool) (D.field "main" D.bool) (D.field "popup" D.bool))
    |> D.andThen (\draw -> if draw.retired && draw.incarnation /= Nothing then D.fail "Retired draw with live identity" else D.succeed draw)
frameDecoder : D.Decoder Frame
frameDecoder = strict ["monitor","frame","complete","overflow","committed","draws"] (D.map6 Frame (D.field "monitor" UInt64.decoder) (D.field "frame" nonzero) (D.field "complete" D.bool) (D.field "overflow" D.bool) (D.field "committed" D.bool) (D.field "draws" (D.list drawDecoder)))
    |> D.andThen (\frame -> if List.length frame.draws > 1024 || (frame.overflow && frame.complete) then D.fail "Incoherent trace bound/completeness" else D.succeed frame)
decode : D.Value -> Result String Trace
decode value =
    let version = D.field "protocolVersion" D.int |> D.andThen (\v -> if v == 3 then D.succeed () else D.fail "Trace version")
        kind = D.field "kind" D.string |> D.andThen (\v -> if v == "render-trace" then D.succeed () else D.fail "Trace kind")
        body = D.map4 Trace (D.field "binding" Binding.decoder) (D.field "requestId" nonzero) (D.field "outputGeneration" nonzero) (D.field "frames" (D.list frameDecoder))
    in D.decodeValue (strict ["protocolVersion","kind","binding","requestId","outputGeneration","frames"] (D.map3 (\_ _ trace -> trace) version kind body)) value
        |> Result.mapError D.errorToString
        |> Result.andThen (\((Trace _ _ _ frames) as trace) ->
            let monitors = List.map .monitor frames
                unique = List.foldl (\m seen -> if List.member m seen then seen else m :: seen) [] monitors
            in if List.length frames > 32 || List.length monitors /= List.length unique then Err "Monitor trace bound/duplication" else Ok trace)
encodeSummary : Trace -> E.Value
encodeSummary (Trace binding request output frames) = E.object [("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("outputGeneration",E.string (UInt64.string output)),("canonicalScene",E.bool False),("frames",E.list (\frame -> E.object [("monitor",E.string (UInt64.string frame.monitor)),("frame",E.string (UInt64.string frame.serial)),("usableDispatchTrace",E.bool (frame.complete && frame.committed && not frame.overflow && not (List.any .retired frame.draws))),("drawCount",E.int (List.length frame.draws))]) frames)]
