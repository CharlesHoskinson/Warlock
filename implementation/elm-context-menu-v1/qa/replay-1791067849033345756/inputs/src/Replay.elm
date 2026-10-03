port module Replay exposing (main)

import Binding
import Json.Decode as D
import Json.Encode as E
import Menu
import Platform
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value

type alias State =
    { model : Menu.Model, menus : List Menu.MenuId, intents : List Menu.IntentId, results : List E.Value }

main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , subscriptions = \_ -> incoming Run
        , update = \(Run value) _ -> ( (), outgoing (run value) )
        }

success : E.Value -> E.Value
success value = E.object [ ( "passed", E.bool True ), ( "value", value ) ]

failure : String -> E.Value
failure error = E.object [ ( "passed", E.bool False ), ( "error", E.string error ) ]

run : D.Value -> E.Value
run value =
    case D.decodeValue (D.field "kind" D.string) value of
        Err error -> failure (D.errorToString error)
        Ok kind ->
            case kind of
                "counter" ->
                    case D.decodeValue (D.field "value" UInt64.decoder) value of
                        Ok counter -> success (E.string (UInt64.string counter))
                        Err error -> failure (D.errorToString error)
                "binding" ->
                    case D.decodeValue (D.field "value" Binding.decoder) value of
                        Ok binding -> success (Binding.encode binding)
                        Err error -> failure (D.errorToString error)
                "trace" ->
                    case D.decodeValue (D.field "steps" (D.list D.value)) value of
                        Err error -> failure (D.errorToString error)
                        Ok steps ->
                            case List.foldl step (Ok { model = Menu.init, menus = [], intents = [], results = [] }) steps of
                                Err error -> failure error
                                Ok state -> E.object [ ( "passed", E.bool True ), ( "steps", E.list identity state.results ) ]
                _ -> failure "Unknown replay request"

positive : D.Decoder String
positive = UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed (UInt64.string n) else D.fail "Nonzero identity required")

bindingDecoder : D.Decoder Menu.Binding
bindingDecoder =
    D.map6 (\authority revision output generation window incarnation ->
        Menu.binding { authority = authority, revision = revision, output = Menu.outputId output,
            outputGeneration = generation, target = Menu.Window (Menu.windowId window incarnation) })
        (D.field "authority" positive) (D.field "revision" positive) (D.field "output" D.string)
        (D.field "outputGeneration" positive) (D.field "window" D.string) (D.field "incarnation" positive)

actionDecoder : D.Decoder Menu.Action
actionDecoder =
    D.string |> D.andThen (\action -> case action of
        "restore" -> D.succeed Menu.Restore
        "move" -> D.succeed Menu.Move
        "close" -> D.succeed Menu.Close
        _ -> D.fail "Unknown fixture action")

itemDecoder : D.Decoder Menu.Item
itemDecoder = D.map2 (\action enabled -> { action = action, enabled = enabled, label = "Fixture label" })
    (D.field "action" actionDecoder) (D.field "enabled" D.bool)

lookup : String -> Int -> List a -> D.Decoder a
lookup label index values =
    if index < 0 then D.fail ("Negative " ++ label)
    else case List.head (List.drop index values) of
        Just value -> D.succeed value
        Nothing -> D.fail ("Absent " ++ label)

menuDecoder : State -> D.Decoder Menu.MenuId
menuDecoder state = D.field "menu" D.int |> D.andThen (\index -> lookup "menu" index state.menus)

navigationDecoder : D.Decoder Menu.Navigation
navigationDecoder = D.string |> D.andThen (\value -> case value of
    "up" -> D.succeed Menu.Up
    "down" -> D.succeed Menu.Down
    "home" -> D.succeed Menu.Home
    "end" -> D.succeed Menu.End
    _ -> D.fail "Unknown navigation")

outcomeDecoder : D.Decoder Menu.Outcome
outcomeDecoder = D.string |> D.andThen (\value -> case value of
    "committed" -> D.succeed Menu.Committed
    "refused" -> D.succeed (Menu.Refusal "Authority refused fixture action")
    "cancelled" -> D.succeed Menu.Cancellation
    "uncertain" -> D.succeed Menu.Uncertain
    _ -> D.fail "Unknown outcome")

messageDecoder : State -> D.Decoder Menu.Msg
messageDecoder state =
    D.field "op" D.string |> D.andThen (\op -> case op of
        "open" -> D.map2 Menu.Open (D.field "binding" bindingDecoder) (D.field "items" (D.list itemDecoder))
        "select" -> D.map3 Menu.Select (menuDecoder state) (D.field "binding" bindingDecoder) (D.field "index" D.int)
        "activate" -> D.map3 Menu.Activate (menuDecoder state) (D.field "binding" bindingDecoder) (D.field "index" D.int)
        "navigate" -> D.map2 Menu.Navigate (menuDecoder state) (D.field "navigation" navigationDecoder)
        "dismiss" -> D.map Menu.Dismiss (menuDecoder state)
        "invalidate" -> D.map Menu.Invalidate (D.field "binding" bindingDecoder)
        "outputRetired" -> D.map2 (\output generation -> Menu.OutputRetired (Menu.outputId output) generation)
            (D.field "output" D.string) (D.field "generation" positive)
        "receive" -> D.map2 Menu.Receive
            (D.field "intent" D.int |> D.andThen (\index -> lookup "intent" index state.intents))
            (D.field "outcome" outcomeDecoder)
        _ -> D.fail "Unknown fixture operation")

step : D.Value -> Result String State -> Result String State
step value previous =
    previous |> Result.andThen (\state ->
        D.decodeValue (messageDecoder state) value |> Result.mapError D.errorToString |> Result.map (\message ->
            let
                ( model, effects ) = Menu.update message state.model
                snapshot = Menu.snapshot model
                menus = case snapshot.menu of
                    Just menu -> if List.member menu.id state.menus then state.menus else state.menus ++ [ menu.id ]
                    Nothing -> state.menus
                intents = state.intents ++ List.map (\(Menu.Dispatch intent _ _) -> intent) effects
            in
            { model = model, menus = menus, intents = intents,
              results = state.results ++ [ encodeStep snapshot effects ] }))

statusName : Menu.Status -> String
statusName status = case status of
    Menu.Ready -> "ready"
    Menu.Pending _ -> "pending"
    Menu.Refused _ -> "refused"
    Menu.Cancelled -> "cancelled"
    Menu.Unknown _ -> "unknown"

actionName : Menu.Action -> String
actionName action = case action of
    Menu.Restore -> "restore"
    Menu.Move -> "move"
    Menu.Close -> "close"
    _ -> "other"

encodeStep : Menu.Snapshot -> List Menu.Effect -> E.Value
encodeStep snapshot effects =
    E.object
        [ ( "menu", case snapshot.menu of
            Nothing -> E.null
            Just menu -> E.object
                [ ( "id", E.int (Menu.menuNumber menu.id) )
                , ( "selected", Maybe.map E.int menu.selected |> Maybe.withDefault E.null )
                , ( "status", E.string (statusName menu.status) )
                ])
        , ( "effects", E.list (\(Menu.Dispatch intent _ action) ->
            E.object [ ( "intent", E.int (Menu.intentNumber intent) ), ( "action", E.string (actionName action) ) ]) effects )
        , ( "outstanding", E.int snapshot.outstanding )
        ]
