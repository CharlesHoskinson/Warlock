module PreviewPaintGate exposing (Model, initial, hasPending, queue, painted)

import Dict exposing (Dict)
import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import UInt64 exposing (Counter)

-- Transport of commands already issued by the sole preview policy. A ticket
-- neither grants native permission nor creates/renews a job or its deadline.
type alias Pending = { identity : String, job : String, command : E.Value, realm : Maybe Realm.Domain }
type Model = Model Counter (Dict String Pending)

initial : Model
initial = Model UInt64.zero Dict.empty

hasPending : Model -> Bool
hasPending (Model _ pending) = not (Dict.isEmpty pending)

jobKey : E.Value -> Maybe String
jobKey command = D.decodeValue (D.field "job" D.value) command |> Result.toMaybe |> Maybe.map (E.encode 0)

row : String -> E.Value -> E.Value
row identity command = E.object [("identity",E.string identity),("commands",E.list identityValue [command])]

identityValue value = value

-- Preserve the policy-selected realm envelope through the existing paint
-- transport. This neither assigns a native ordinal nor admits a native effect.
encodeBatch : Maybe Realm.Domain -> List E.Value -> E.Value
encodeBatch realm entries =
    let rows = E.list identityValue entries
    in realm |> Maybe.map (\domain -> Realm.commands domain rows) |> Maybe.withDefault rows

batchDecoder : D.Decoder (Maybe Realm.Domain,List (String,List E.Value))
batchDecoder =
    let item = D.map2 Tuple.pair (D.field "identity" D.string) (D.field "commands" (D.list D.value))
        rows = D.list item
        scopedRows = D.list (D.keyValuePairs D.value |> D.andThen (\fields ->
            if List.sort (List.map Tuple.first fields)==["commands","identity"] then item
            else D.fail "Exact scoped proposal row"))
        scoped = D.keyValuePairs D.value |> D.andThen (\fields ->
            if List.sort (List.map Tuple.first fields) /= ["binding","entries","kind","previewProtocol","receiverEpoch"] then D.fail "Exact preview proposal fields"
            else D.map4 (\version kind domain entries -> {version=version,kind=kind,domain=domain,entries=entries})
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "entries" scopedRows)
                |> D.andThen (\packet ->
                    if packet.version==3 && packet.kind=="preview-proposals" then D.succeed (Just packet.domain,packet.entries)
                    else D.fail "Typed preview proposal envelope"))
    in D.oneOf [D.map (\entries -> (Nothing,entries)) rows,scoped]

queue : E.Value -> Model -> (Model,E.Value,E.Value)
queue raw initialModel =
    let (realm,entries)=D.decodeValue batchDecoder raw |> Result.withDefault (Nothing,[])
        step (identity,command) ((Model ordinal pending),immediate,tickets) =
            let kind=D.decodeValue (D.field "kind" D.string) command |> Result.withDefault ""
                job=jobKey command
            in case (kind,job) of
                ("acquire",Just key) ->
                    case UInt64.next ordinal of
                        Nothing -> (Model ordinal pending,immediate,tickets)
                        Just next ->
                            if Dict.values pending |> List.any (\held -> held.realm==realm && held.identity==identity && held.job==key) then (Model ordinal pending,immediate,tickets) else
                                let ticket=UInt64.string next
                                in (Model next (Dict.insert ticket {identity=identity,job=key,command=command,realm=realm} pending),immediate,tickets++[E.object [("ticket",E.string ticket)]])
                ("acquire",Nothing) -> (Model ordinal pending,immediate,tickets)
                _ ->
                    let retained=if kind=="cancel" then Dict.filter (\_ held -> not (held.realm==realm && held.identity==identity && Just held.job==job)) pending else pending
                    in (Model ordinal retained,immediate++[row identity command],tickets)
        commands=entries |> List.concatMap (\(identity,items) -> List.map (Tuple.pair identity) items)
        (updatedModel,commandsNow,paintRequests)=List.foldl step (initialModel,[],[]) commands
    in (updatedModel,encodeBatch realm commandsNow,E.list identityValue paintRequests)

painted : D.Value -> Model -> (Model,E.Value)
painted raw ((Model ordinal pending) as model) =
    let decoder=D.keyValuePairs D.value |> D.andThen (\fields -> if List.map Tuple.first fields==["ticket"] then D.field "ticket" UInt64.decoder else D.fail "Exact paint ticket")
    in case D.decodeValue decoder raw |> Result.toMaybe |> Maybe.map UInt64.string |> Maybe.andThen (\ticket -> Dict.get ticket pending |> Maybe.map (Tuple.pair ticket)) of
        Just (ticket,held) -> (Model ordinal (Dict.remove ticket pending),encodeBatch held.realm [row held.identity held.command])
        Nothing -> (model,E.list identityValue [])
