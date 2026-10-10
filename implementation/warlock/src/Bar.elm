port module Bar exposing (main)

import Browser
import Html exposing (div, text)
import Announcement
import Json.Decode as D
import Json.Encode as E
import Presentation
import SurfaceRenderer

port presentation : (D.Value -> msg) -> Sub msg
port announcements : (D.Value -> msg) -> Sub msg
port requestAction : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value | Announce D.Value
type alias Model = {presentation : Presentation.Model, announcements : Announcement.Model}

-- A display owns only a presentation cache. It cannot run Desktop.update.
main : Program () Model Msg
main = Browser.element
    { init=\_ -> ({presentation=Presentation.initial,announcements=Announcement.initial},Cmd.none)
    , subscriptions=\_ -> Sub.batch [presentation Present,requestAction Action,announcements Announce]
    , view=\model -> Presentation.current model.presentation |> Maybe.map (\snapshot -> div [] [SurfaceRenderer.view False Action snapshot,Announcement.view model.announcements]) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,Presentation.dispatch False value model.presentation |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Announce raw -> ({model | announcements=Announcement.receive False (Presentation.current model.presentation) raw model.announcements},Cmd.none)
        Present raw -> ({model | presentation=Presentation.accept raw model.presentation},Cmd.none)
    }
