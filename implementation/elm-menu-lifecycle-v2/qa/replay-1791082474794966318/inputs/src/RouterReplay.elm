port module RouterReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import Menu
import Platform
import Provider
import ReceiptRouter

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
type alias Attempt = { effect : Menu.Effect, provider : Provider.Snapshot }
type alias State = { menu : Menu.Model, router : ReceiptRouter.Model, provider : Maybe Provider.Snapshot, last : Maybe Attempt, commands : Int }
initial : State
initial = { menu=Menu.init, router=ReceiptRouter.empty, provider=Nothing, last=Nothing, commands=0 }

status : Menu.Status -> String
status value = case value of
    Menu.Ready -> "ready"
    Menu.Pending _ -> "pending"
    Menu.Unknown _ -> "unknown"
    Menu.Refused _ -> "refused"
    Menu.Cancelled -> "cancelled"

encode : State -> Maybe String -> E.Value
encode state error =
    let snapshot=Menu.snapshot state.menu
        menu = case snapshot.menu of
            Nothing -> E.null
            Just current -> E.object [("id",E.int (Menu.menuNumber current.id)),("status",E.string (status current.status)),("selected",current.selected |> Maybe.map E.int |> Maybe.withDefault E.null)]
    in E.object [("menu",menu),("outstanding",E.int snapshot.outstanding),("registry",E.int (ReceiptRouter.count state.router)),("commands",E.int state.commands),("observed",E.null),("error",error |> Maybe.map E.string |> Maybe.withDefault E.null)]

step : D.Value -> State -> (State,Maybe String)
step value state =
    case D.decodeValue (D.field "op" D.string) value of
        Err error -> (state,Just (D.errorToString error))
        Ok "open" ->
            case D.decodeValue (D.field "provider" D.value) value |> Result.mapError D.errorToString |> Result.andThen Provider.decode of
                Err error -> (state,Just error)
                Ok provider ->
                    let (menu,_)=Menu.update (Provider.toOpen provider) state.menu
                        admitted = (Menu.snapshot menu).menu |> Maybe.map (\current ->
                            current.binding==Provider.getBinding provider
                                && ((Menu.snapshot state.menu).menu |> Maybe.map (\old -> old.id/=current.id) |> Maybe.withDefault True)) |> Maybe.withDefault False
                    in if admitted then ({state | menu=menu,provider=Just provider},Nothing)
                       else ({state | menu=menu},Just "Provider context was not admitted")
        Ok "dismiss" ->
            case (Menu.snapshot state.menu).menu of
                Nothing -> (state,Nothing)
                Just current ->
                    let (menu,_)=Menu.update (Menu.Dismiss current.id) state.menu
                    in ({state | menu=menu},Nothing)
        Ok "activate" ->
            case ((Menu.snapshot state.menu).menu,state.provider,D.decodeValue (D.field "index" D.int) value) of
                (Just current,Just provider,Ok index) ->
                    let (menu,effects)=Menu.update (Menu.Activate current.id current.binding index) state.menu
                    in case effects of
                        [((Menu.Dispatch local binding _) as effect)] ->
                            case D.decodeValue (D.field "command" D.value) value |> Result.mapError D.errorToString |> Result.andThen (\command -> ReceiptRouter.register effect provider command state.router) of
                                Ok router -> ({state | menu=menu,router=router,last=Just {effect=effect,provider=provider},commands=state.commands+1},Nothing)
                                Err error ->
                                    let (refused,_)=Menu.update (Menu.ReceiveFor local binding (Menu.Refusal error)) menu
                                    in ({state | menu=refused},Just error)
                        _ -> ({state | menu=menu},Nothing)
                _ -> (state,Just "Activation context unavailable")
        Ok "duplicate" ->
            case state.last of
                Nothing -> (state,Just "No registered command")
                Just last ->
                    case D.decodeValue (D.field "command" D.value) value |> Result.mapError D.errorToString |> Result.andThen (\command -> ReceiptRouter.register last.effect last.provider command state.router) of
                        Err error -> (state,Just error)
                        Ok router -> ({state | router=router},Nothing)
        Ok "local_receipt" ->
            -- Adversarial unit setup only: intentionally desynchronize the two
            -- ledgers to reach the registry's independent capacity guard.
            case state.last of
                Just {effect} ->
                    case effect of
                        Menu.Dispatch local binding _ ->
                            let (menu,_)=Menu.update (Menu.ReceiveFor local binding Menu.Committed) state.menu
                            in ({state | menu=menu},Nothing)
                Nothing -> (state,Just "No local unit-test operation")
        Ok "receipt" ->
            case D.decodeValue (D.field "frame" D.string) value of
                Err error -> (state,Just (D.errorToString error))
                Ok raw ->
                    let (router,message,error)=ReceiptRouter.accept raw state.router
                        menu=message |> Maybe.map (\incomingMessage -> Menu.update incomingMessage state.menu |> Tuple.first) |> Maybe.withDefault state.menu
                    in ({state | router=router,menu=menu},error)
        _ -> (state,Just "Unknown router fixture operation")

run : D.Value -> E.Value
run value =
    case D.decodeValue (D.field "steps" (D.list D.value)) value of
        Err error -> E.object [("passed",E.bool False),("error",E.string (D.errorToString error))]
        Ok steps ->
            let (_,results)=List.foldl (\event (state,prior) -> let (next,error)=step event state in (next,encode next error::prior)) (initial,[]) steps
            in E.object [("passed",E.bool True),("steps",E.list identity (List.reverse results))]

main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),update=\(Run value) _ -> ((),outgoing (run value)),subscriptions=\_ -> incoming Run}
