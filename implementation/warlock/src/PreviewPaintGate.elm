module PreviewPaintGate exposing (Model, initial, queue, painted)

import Dict exposing (Dict)
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

-- Transport of commands already issued by the sole preview policy. A ticket
-- neither grants native permission nor creates/renews a job or its deadline.
type alias Pending = { identity : String, job : String, command : E.Value }
type Model = Model Counter (Dict String Pending)

initial : Model
initial = Model UInt64.zero Dict.empty

jobKey : E.Value -> Maybe String
jobKey command = D.decodeValue (D.field "job" D.value) command |> Result.toMaybe |> Maybe.map (E.encode 0)

row : String -> E.Value -> E.Value
row identity command = E.object [("identity",E.string identity),("commands",E.list identityValue [command])]

identityValue value = value

queue : E.Value -> Model -> (Model,E.Value,E.Value)
queue raw initialModel =
    let entries=D.decodeValue (D.list (D.map2 Tuple.pair (D.field "identity" D.string) (D.field "commands" (D.list D.value)))) raw |> Result.withDefault []
        step (identity,command) ((Model ordinal pending),immediate,tickets) =
            let kind=D.decodeValue (D.field "kind" D.string) command |> Result.withDefault ""
                job=jobKey command
            in case (kind,job,UInt64.next ordinal) of
                ("acquire",Just key,Just next) ->
                    if Dict.values pending |> List.any (\held -> held.identity==identity && held.job==key) then (Model ordinal pending,immediate,tickets) else
                        let ticket=UInt64.string next
                        in (Model next (Dict.insert ticket {identity=identity,job=key,command=command} pending),immediate,tickets++[E.object [("ticket",E.string ticket)]])
                _ ->
                    let retained=if kind=="cancel" then Dict.filter (\_ held -> not (held.identity==identity && Just held.job==job)) pending else pending
                    in (Model ordinal retained,immediate++[row identity command],tickets)
        commands=entries |> List.concatMap (\(identity,items) -> List.map (Tuple.pair identity) items)
        (updatedModel,commandsNow,paintRequests)=List.foldl step (initialModel,[],[]) commands
    in (updatedModel,E.list identityValue commandsNow,E.list identityValue paintRequests)

painted : D.Value -> Model -> (Model,E.Value)
painted raw ((Model ordinal pending) as model) =
    let decoder=D.keyValuePairs D.value |> D.andThen (\fields -> if List.map Tuple.first fields==["ticket"] then D.field "ticket" UInt64.decoder else D.fail "Exact paint ticket")
    in case D.decodeValue decoder raw |> Result.toMaybe |> Maybe.map UInt64.string |> Maybe.andThen (\ticket -> Dict.get ticket pending |> Maybe.map (Tuple.pair ticket)) of
        Just (ticket,held) -> (Model ordinal (Dict.remove ticket pending),E.list identityValue [row held.identity held.command])
        Nothing -> (model,E.list identityValue [])
