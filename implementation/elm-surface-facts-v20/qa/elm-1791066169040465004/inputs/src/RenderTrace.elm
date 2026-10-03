module RenderTrace exposing (decode, encodeSummary)

import Binding exposing (Binding)
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

-- Diagnostic draw dispatch, deliberately separate from Scene.Admitted.
type Trace = Trace Binding Counter Counter Bool (List Frame)
type alias Frame = { monitor : Counter, serial : Counter, complete : Bool, overflow : Bool, committed : Bool, draws : List Draw, output : Output }
type alias Draw = { incarnation : Maybe Counter, authority : Maybe Counter, retired : Bool, unbound : Bool, main : Bool, popup : Bool, facts : Facts }
type alias Facts = { surface : Counter, box : List Float, alpha : Float, input : List (List Float) }
type alias Output = { configuration : List Float, transform : Int, generation : Counter }
finite = D.float |> D.andThen (\v -> if isNaN v || isInfinite v then D.fail "Nonfinite geometry" else D.succeed v)
rectangle = D.list finite |> D.andThen (\r -> if List.length r == 4 && (r |> List.drop 2 |> List.all (\v -> v > 0)) then D.succeed r else D.fail "Invalid rectangle")
configuration = D.list finite |> D.andThen (\r -> if List.length r == 5 && (r |> List.drop 2 |> List.all (\v -> v > 0)) then D.succeed r else D.fail "Invalid output configuration")
strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected trace fields")
nonzero : D.Decoder Counter
nonzero = UInt64.decoder |> D.andThen (\n -> if n == UInt64.zero then D.fail "Zero identity" else D.succeed n)
drawDecoder : D.Decoder Draw
drawDecoder = strict ["incarnation","authority","retired","unbound","main","popup","surface","box","alpha","input"] (D.map7 Draw (D.field "incarnation" (D.nullable nonzero)) (D.field "authority" (D.nullable nonzero)) (D.field "retired" D.bool) (D.field "unbound" D.bool) (D.field "main" D.bool) (D.field "popup" D.bool) (D.map4 Facts (D.field "surface" nonzero) (D.field "box" rectangle) (D.field "alpha" finite) (D.field "input" (D.list rectangle |> D.andThen (\r -> if List.length r <= 64 then D.succeed r else D.fail "Input bound")))))
    |> D.andThen (\draw -> if (draw.incarnation == Nothing) /= (draw.authority == Nothing) || (draw.retired && draw.incarnation == Nothing) || (draw.unbound && draw.incarnation /= Nothing) then D.fail "Incoherent captured draw identity" else D.succeed draw)
frameDecoder : D.Decoder Frame
frameDecoder = strict ["monitor","frame","complete","overflow","committed","draws","outputConfiguration","outputTransform","configurationGeneration"] (D.map7 Frame (D.field "monitor" UInt64.decoder) (D.field "frame" nonzero) (D.field "complete" D.bool) (D.field "overflow" D.bool) (D.field "committed" D.bool) (D.field "draws" (D.list drawDecoder)) (D.map3 Output (D.field "outputConfiguration" configuration) (D.field "outputTransform" (D.int |> D.andThen (\v -> if v >= 0 && v <= 7 then D.succeed v else D.fail "Transform"))) (D.field "configurationGeneration" nonzero)))
    |> D.andThen (\frame -> if List.length frame.draws > 1024 || (frame.overflow && frame.complete) then D.fail "Incoherent trace bound/completeness" else D.succeed frame)
decode : D.Value -> Result String Trace
decode value =
    let version = D.field "protocolVersion" D.int |> D.andThen (\v -> if v == 3 then D.succeed () else D.fail "Trace version")
        kind = D.field "kind" D.string |> D.andThen (\v -> if v == "render-trace" then D.succeed () else D.fail "Trace kind")
        body = D.map5 Trace (D.field "binding" Binding.decoder) (D.field "requestId" nonzero) (D.field "outputGeneration" nonzero) (D.field "retained" D.bool) (D.field "frames" (D.list frameDecoder))
    in D.decodeValue (strict ["protocolVersion","kind","traceProtocol","retained","binding","requestId","outputGeneration","frames"] (D.map4 (\_ _ _ trace -> trace) version kind (D.field "traceProtocol" D.int |> D.andThen (\v -> if v == 3 then D.succeed () else D.fail "Trace protocol")) body)) value
        |> Result.mapError D.errorToString
        |> Result.andThen (\((Trace _ _ _ _ frames) as trace) ->
            let monitors = List.map .monitor frames
                unique = List.foldl (\m seen -> if List.member m seen then seen else m :: seen) [] monitors
            in if List.length frames > 32 || List.length monitors /= List.length unique then Err "Monitor trace bound/duplication" else Ok trace)
encodeSummary : Trace -> E.Value
encodeSummary (Trace binding request output retained frames) = E.object [("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("outputGeneration",E.string (UInt64.string output)),("canonicalScene",E.bool False),("frames",E.list (\frame -> E.object [("monitor",E.string (UInt64.string frame.monitor)),("frame",E.string (UInt64.string frame.serial)),("usableDispatchTrace",E.bool (not retained && frame.complete && frame.committed && not frame.overflow && not (List.any (\d -> d.retired || d.unbound || (d.authority |> Maybe.map (\a -> not (Binding.matchesLifetime a binding)) |> Maybe.withDefault False)) frame.draws))),("drawCount",E.int (List.length frame.draws))]) frames)]
