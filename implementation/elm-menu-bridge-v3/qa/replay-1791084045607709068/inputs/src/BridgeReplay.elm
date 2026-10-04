port module BridgeReplay exposing (main)

import ActionProjection
import Binding
import Effects
import Json.Decode as D
import Json.Encode as E
import Menu
import MenuBridge
import NativeProvider
import Platform
import Provider
import Shell
import TaskbarShell
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value

type alias State =
    { model : TaskbarShell.Model, sent : List E.Value, results : List E.Value, ids : List Menu.MenuId, intents : List Menu.IntentId }

initial : State
initial = { model = TaskbarShell.initial, sent = [], results = [], ids = [], intents = [] }

scopeDecoder : D.Decoder NativeProvider.Scope
scopeDecoder = D.map3 NativeProvider.Scope (D.field "outputId" UInt64.decoder)
    (D.field "providerId" UInt64.decoder) (D.field "capabilityGeneration" UInt64.decoder)

status : Menu.Status -> String
status value = case value of
    Menu.Ready -> "ready"
    Menu.Pending _ -> "pending"
    Menu.Refused _ -> "refused"
    Menu.Cancelled -> "cancelled"
    Menu.Unknown _ -> "unknown"

commandKind : E.Value -> String
commandKind value = D.decodeValue (D.field "kind" D.string) value |> Result.withDefault "invalid"

observed : Shell.Model -> E.Value
observed shell = case shell.effects.observed of
    Nothing -> E.null
    Just snapshot -> E.object
        [ ( "context", E.object
            [ ( "lifetime", E.string (UInt64.string snapshot.context.lifetime) )
            , ( "epoch", E.string (UInt64.string snapshot.context.epoch) )
            , ( "output", E.string (UInt64.string snapshot.context.output) )
            , ( "revision", E.string (UInt64.string snapshot.context.revision) ) ])
        , ( "windows", E.list (\window -> E.object
            [ ( "incarnation", E.string (UInt64.string window.incarnation) )
            , ( "minimized", E.bool window.minimized )
            , ( "available", E.bool window.available ) ]) (ActionProjection.windows snapshot.scene) ) ]

encode : State -> Maybe String -> Maybe Provider.Snapshot -> Maybe Provider.Snapshot -> E.Value
encode state error produced expected =
    let
        snapshot = MenuBridge.menuSnapshot state.model.menus
        menu = case snapshot.menu of
            Nothing -> E.null
            Just current -> E.object
                [ ( "id", E.int (Menu.menuNumber current.id) )
                , ( "selected", current.selected |> Maybe.map E.int |> Maybe.withDefault E.null )
                , ( "status", E.string (status current.status) ) ]
        windowCommands = List.filter (commandKind >> (==) "window-effect") state.sent
        producer = case produced of
            Nothing -> E.null
            Just provider -> E.object
                [ ( "incarnation", E.string (UInt64.string (Provider.incarnation provider)) )
                , ( "title", E.string (Provider.title provider) )
                , ( "enabled", E.list (\item -> E.bool item.enabled) (Provider.getItems provider) )
                , ( "output", E.string (UInt64.string (Provider.nativeContext provider).output) )
                , ( "nativeBinding", Binding.encode (Provider.nativeBinding provider) )
                , ( "matchesExpectedBinding", expected |> Maybe.map (\reference -> E.bool (Provider.getBinding reference == Provider.getBinding provider)) |> Maybe.withDefault E.null ) ]
    in E.object
        [ ( "shell", Shell.encode state.model.shell )
        , ( "menu", menu )
        , ( "outstanding", E.int snapshot.outstanding )
        , ( "registry", E.int (MenuBridge.receiptCount state.model.menus) )
        , ( "picker", state.model.picker |> Maybe.map (\picker -> E.object
            [ ( "key", E.string picker.key ), ( "generation", E.string (UInt64.string picker.generation) ) ]) |> Maybe.withDefault E.null )
        , ( "observed", observed state.model.shell )
        , ( "commands", E.list identity windowCommands )
        , ( "sent", E.list identity state.sent )
        , ( "error", error |> Maybe.map E.string |> Maybe.withDefault E.null )
        , ( "produced", producer ) ]

transition : TaskbarShell.Msg -> State -> State
transition message state =
    let
        ( model, effects ) = TaskbarShell.update message state.model
        sent = state.sent ++ List.filterMap (\effect -> case effect of
            Shell.Send value -> Just value
            Shell.RestartBackend -> Nothing) effects
        snapshot = MenuBridge.menuSnapshot model.menus
        ids = case snapshot.menu of
            Nothing -> state.ids
            Just current -> if List.member current.id state.ids then state.ids else state.ids ++ [ current.id ]
        intents = case snapshot.lastOutcome of
            Nothing -> state.intents
            Just ( intent, _ ) -> if List.member intent state.intents then state.intents else state.intents ++ [ intent ]
    in { state | model = model, sent = sent, ids = ids, intents = intents }

step : D.Value -> State -> State
step value state =
    let
        op = D.decodeValue (D.field "op" D.string) value
        expected = D.decodeValue (D.field "expectedProvider" D.value) value
            |> Result.mapError (\_ -> "No expected provider") |> Result.andThen Provider.decode |> Result.toMaybe
        finish next error producer = { next | results = state.results ++ [ encode next error producer expected ] }
        refuse error = finish state (Just error) Nothing
        current = (MenuBridge.menuSnapshot state.model.menus).menu
        dispatch event = finish (transition event state) Nothing Nothing
        production = D.decodeValue (D.map2 Tuple.pair (D.field "scope" scopeDecoder) (D.field "incarnation" UInt64.decoder)) value
            |> Result.mapError (\_ -> "Invalid producer fixture")
            |> Result.andThen (\(scope, incarnation) -> NativeProvider.fromShell scope incarnation state.model.shell)
    in case op of
        Ok "frame" -> case D.decodeValue (D.field "frame" D.value) value of
            Ok frame -> dispatch (TaskbarShell.Native (Shell.Incoming frame))
            Err _ -> refuse "Missing frame"
        Ok "reconnect" -> dispatch (TaskbarShell.Native Shell.Reconnect)
        Ok "refresh" -> dispatch (TaskbarShell.Native Shell.Refresh)
        Ok "open" -> case D.decodeValue (D.field "provider" D.value) value |> Result.mapError (\_ -> "Missing provider") |> Result.andThen Provider.decode of
            Ok provider -> dispatch (TaskbarShell.OpenMenu provider)
            Err error -> refuse error
        Ok "produce" -> case production of
            Ok provider -> finish state Nothing (Just provider)
            Err error -> refuse error
        Ok "produceOpen" -> case production of
            Ok provider -> finish (transition (TaskbarShell.OpenMenu provider) state) Nothing (Just provider)
            Err error -> refuse error
        Ok "activate" -> case ( current, D.decodeValue (D.field "index" D.int) value ) of
            ( Just menu, Ok index ) -> dispatch (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))
            _ -> refuse "No activation menu"
        Ok "staleDismiss" -> case D.decodeValue (D.field "menu" D.int) value |> Result.toMaybe |> Maybe.andThen (\index -> List.drop index state.ids |> List.head) of
            Just id -> dispatch (TaskbarShell.MenuEvent (Menu.Dismiss id))
            Nothing -> refuse "Missing historical menu"
        Ok "forgedReceipt" -> case ( List.head state.intents, MenuBridge.currentProvider state.model.menus ) of
            ( Just intent, Just provider ) -> dispatch (TaskbarShell.MenuEvent (Menu.ReceiveFor intent (Provider.getBinding provider) Menu.Committed))
            _ -> refuse "Missing forged-receipt fixture context"
        Ok "dismiss" -> case current of
            Just menu -> dispatch (TaskbarShell.MenuEvent (Menu.Dismiss menu.id))
            Nothing -> finish state Nothing Nothing
        Ok "taskbar" -> case ( Shell.capture state.model.shell, D.decodeValue (D.map2 Tuple.pair
            (D.field "operation" Effects.operationDecoder) (D.field "incarnation" UInt64.decoder)) value ) of
            ( Just stamp, Ok (operation, incarnation) ) -> dispatch (TaskbarShell.Native (Shell.Act stamp operation incarnation))
            _ -> refuse "No taskbar scope"
        Ok "primary" -> case ( Shell.capture state.model.shell, D.decodeValue (D.field "key" D.string) value ) of
            ( Just stamp, Ok key ) -> dispatch (TaskbarShell.Primary stamp key)
            _ -> refuse "No taskbar primary scope"
        _ -> refuse "Unknown bridge fixture operation"

run : D.Value -> E.Value
run value = case D.decodeValue (D.field "steps" (D.list D.value)) value of
    Err _ -> E.object [ ( "passed", E.bool False ), ( "error", E.string "Missing steps" ) ]
    Ok steps ->
        let state = List.foldl step initial steps
        in E.object [ ( "passed", E.bool True ), ( "steps", E.list identity state.results ) ]

main : Program () () Msg
main = Platform.worker { init=\_ -> ((),Cmd.none), update=\(Run value) _ -> ((),outgoing (run value)), subscriptions=\_ -> incoming Run }
