port module UiHttpFailureReplay exposing (main)

{-| Proposed unexecuted source-bound QA for actual UiHttp.update/enqueue/stop.
Commands are deliberately not interpreted here: real HTTP cancellation, FIFO,
no replay and native accessibility remain separate protected harness obligations.
-}

import Http
import Json.Encode as E
import Platform
import UiHttp

port outgoing : E.Value -> Cmd msg

initial : UiHttp.Model
initial = Tuple.first UiHttp.renderer

lost : Maybe UiHttp.Event -> Maybe String
lost event =
    case event of
        Just (UiHttp.Lost reason) -> Just reason
        _ -> Nothing

isIncoming : Maybe UiHttp.Event -> Bool
isIncoming event =
    case event of
        Just (UiHttp.Incoming raw) -> E.encode 0 raw == "{\"bridgeProtocol\":1,\"kind\":\"presentation\",\"payload\":{}}"
        _ -> False

isNothing : Maybe a -> Bool
isNothing value =
    case value of
        Nothing -> True
        Just _ -> False

step : UiHttp.Msg -> UiHttp.Model -> ( UiHttp.Model, Maybe UiHttp.Event )
step message state =
    let (next,_,event) = UiHttp.update message state
    in (next,event)

queue : E.Value -> UiHttp.Model -> ( UiHttp.Model, Maybe UiHttp.Event )
queue value state =
    let (next,_,event) = UiHttp.enqueue value state
    in (next,event)

stop : String -> UiHttp.Model -> ( UiHttp.Model, Maybe UiHttp.Event )
stop reason state =
    let (next,_,event) = UiHttp.stop reason state
    in (next,event)

checkFailure : UiHttp.Model -> UiHttp.Msg -> String -> Bool
checkFailure source message expected =
    let (failed,event) = step message source
        (again,second) = step (UiHttp.Polled (Err Http.NetworkError)) failed
        (queued,third) = queue (E.string "must-not-retry") again
    in UiHttp.problem failed == Just expected
        && lost event == Just expected
        && UiHttp.problem again == Just expected
        && isNothing second
        && UiHttp.problem queued == Just expected
        && isNothing third

checks : List ( String, Bool )
checks =
    let
        (emptyPoll,emptyEvent) = step (UiHttp.Polled (Ok "")) initial
        (incoming,incomingEvent) = step (UiHttp.Polled (Ok "{\"bridgeProtocol\":1,\"kind\":\"presentation\",\"payload\":{}}")) emptyPoll
        (sent,sentEvent) = queue (E.string "request") initial
        (delivered,deliveredEvent) = step (UiHttp.Posted (Ok "")) sent
        (stopped,stopEvent) = stop "Explicit fixture stop" initial
        (restopped,restopEvent) = stop "later stop must not replace first" stopped
        (emptyStop,emptyStopEvent) = stop "" initial
        (afterEmpty,emptyLaterEvent) = stop "later" emptyStop
        push _ state = Tuple.first (queue (E.string "x") state)
        full = List.foldl push initial (List.range 1 16)
        (overflow,overflowEvent) = queue (E.string "seventeenth") full
        (large,largeEvent) = queue (E.string (String.repeat 8192 "x")) initial
        (eventTooLarge,eventTooLargeEvent) = step (UiHttp.Polled (Ok (String.repeat 1048705 "x"))) initial
    in
    [ ("initial-no-problem", UiHttp.problem initial == Nothing)
    , ("empty-poll-then-valid-presentation", UiHttp.problem incoming == Nothing && isNothing emptyEvent && isIncoming incomingEvent)
    , ("successful-post-does-not-fail", UiHttp.problem delivered == Nothing && isNothing sentEvent && isNothing deliveredEvent)
    , ("poll-timeout-first-failure", checkFailure initial (UiHttp.Polled (Err Http.Timeout)) "UI event transport unavailable. Actions were not retried.")
    , ("post-timeout-unconfirmed", checkFailure sent (UiHttp.Posted (Err Http.Timeout)) "UI delivery is unconfirmed. The action will not be repeated.")
    , ("malformed-json", checkFailure initial (UiHttp.Polled (Ok "{")) "UI event is not valid JSON.")
    , ("malformed-gateway", checkFailure initial (UiHttp.Polled (Ok "{}")) "UI event does not match the recorded gateway.")
    , ("wrong-renderer-kind", checkFailure initial (UiHttp.Polled (Ok "{\"bridgeProtocol\":1,\"kind\":\"native-event\",\"payload\":{}}")) "UI event source is not allowed for this role.")
    , ("unexpected-post-body", checkFailure sent (UiHttp.Posted (Ok "not-empty")) "Unexpected UI delivery response.")
    , ("event-bound", UiHttp.problem eventTooLarge == Just "UI event exceeds the bounded profile." && lost eventTooLargeEvent == Just "UI event exceeds the bounded profile.")
    , ("queue-17-capacity", UiHttp.problem full == Nothing && UiHttp.problem overflow == Just "UI transport capacity exceeded. No action was retried." && lost overflowEvent == Just "UI transport capacity exceeded. No action was retried.")
    , ("encoded-action-byte-bound", UiHttp.problem large == Just "UI transport capacity exceeded. No action was retried." && lost largeEvent == Just "UI transport capacity exceeded. No action was retried.")
    , ("explicit-stop-first-reason", UiHttp.problem stopped == Just "Explicit fixture stop" && lost stopEvent == Just "Explicit fixture stop" && UiHttp.problem restopped == Just "Explicit fixture stop" && isNothing restopEvent)
    , ("empty-explicit-stop-remains-stopped", UiHttp.problem emptyStop == Just "" && lost emptyStopEvent == Just "" && UiHttp.problem afterEmpty == Just "" && isNothing emptyLaterEvent)
    ]

main : Program () () Never
main =
    Platform.worker
        { init = \_ -> ( (), outgoing (E.object [ ( "checks", E.list (\(name,ok) -> E.object [ ( "name", E.string name ), ( "passed", E.bool ok ) ]) checks ) ]) )
        , update = \_ model -> ( model, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }
