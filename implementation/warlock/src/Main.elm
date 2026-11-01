port module Main exposing (main)

import Browser
import DesktopPolicy as Policy
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Process
import Task

port incoming : (D.Value -> msg) -> Sub msg
port surfaceCommits : E.Value -> Cmd msg

-- The port root and HTTP root interpret the same pure policy description.
interpret : Policy.Effect -> Cmd Policy.Msg
interpret effect =
    case effect of
        Policy.Publish packet -> surfaceCommits packet
        Policy.Delay duration message -> Process.sleep duration |> Task.perform (\_ -> Policy.Deadline message)

main : Program () Policy.Model Policy.Msg
main = Browser.element
    { init=\_ -> (Policy.initial,Cmd.none)
    , update=\message model ->
        let (next,effects)=Policy.update message model
        in (next,Cmd.batch (List.map interpret effects))
    , view=\_ -> text ""
    , subscriptions=\_ -> incoming Policy.Incoming
    }
