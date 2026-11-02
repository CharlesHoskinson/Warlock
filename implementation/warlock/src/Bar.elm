port module Bar exposing (main, Model, Msg(..), Effect(..), Subscription(..), initial, initialWithScroll, step, transition, localEffect, statusDomId, subscriptionPlan, subscriptions, view)

import Announcement
import Browser
import Browser.Dom
import Html exposing (div, text)
import Html.Attributes exposing (attribute)
import Json.Decode as D
import Json.Encode as E
import Presentation
import StatusScroll
import SurfaceRenderer
import SurfaceTheme
import Task

port presentation : (D.Value -> msg) -> Sub msg
port announcements : (D.Value -> msg) -> Sub msg
port requestAction : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg
    = Present D.Value
    | Action E.Value
    | Announce D.Value
    | ViewportSettled

-- Pure effect descriptions shared by port Bar, HttpBar, and StatusScrollReplay.
type Effect
    = Dispatch E.Value
    | ResetStatusViewport StatusScroll.Epoch String

type Subscription
    = PresentationChannel
    | RequestActionChannel
    | AnnouncementsChannel

type alias Model =
    { presentation : Presentation.Model
    , announcements : Announcement.Model
    , statusScroll : StatusScroll.Model
    }

initial : Model
initial =
    initialWithScroll StatusScroll.initial

initialWithScroll : StatusScroll.Model -> Model
initialWithScroll scrollState =
    { presentation = Presentation.initial
    , announcements = Announcement.initial
    , statusScroll = scrollState
    }

step : Msg -> Model -> ( Model, List Effect )
step message model =
    case message of
        Action value ->
            ( model
            , Presentation.dispatch False value model.presentation
                |> Maybe.map (\wire -> [ Dispatch wire ])
                |> Maybe.withDefault []
            )

        Announce raw ->
            ( { model | announcements = Announcement.receive False (Presentation.current model.presentation) raw model.announcements }
            , []
            )

        Present raw ->
            let
                priorPublication =
                    Presentation.current model.presentation |> Maybe.map SurfaceRenderer.publication

                nextPresentation =
                    Presentation.accept raw model.presentation

                acceptedSnapshot =
                    case Presentation.current nextPresentation of
                        Nothing ->
                            Nothing

                        Just snapshot ->
                            if Just (SurfaceRenderer.publication snapshot) == priorPublication then
                                Nothing

                            else
                                Just snapshot

                ( nextScroll, scrollEffects ) =
                    case acceptedSnapshot of
                        Nothing ->
                            ( model.statusScroll, [] )

                        Just snapshot ->
                            let
                                ( updatedScroll, maybeReset ) =
                                    StatusScroll.observeSnapshot snapshot model.statusScroll
                            in
                            ( updatedScroll
                            , maybeReset
                                |> Maybe.map (\( targetEpoch, targetDomId ) -> [ ResetStatusViewport targetEpoch targetDomId ])
                                |> Maybe.withDefault []
                            )
            in
            ( { model | presentation = nextPresentation, statusScroll = nextScroll }, scrollEffects )

        ViewportSettled ->
            ( model, [] )

transition : Msg -> Model -> ( Model, Maybe E.Value )
transition message model =
    let
        ( nextModel, effects ) =
            step message model

        pickAction effect found =
            case ( found, effect ) of
                ( Just _, _ ) ->
                    found

                ( Nothing, Dispatch wire ) ->
                    Just wire

                ( Nothing, ResetStatusViewport _ _ ) ->
                    Nothing
    in
    ( nextModel, List.foldl pickAction Nothing effects )

localEffect : (Msg -> msg) -> Effect -> Maybe (Cmd msg)
localEffect lift effect =
    case effect of
        Dispatch _ ->
            Nothing

        ResetStatusViewport _ targetDomId ->
            Just (Browser.Dom.setViewportOf targetDomId 0 0 |> Task.attempt (\_ -> lift ViewportSettled))

statusDomId : Model -> Maybe String
statusDomId model =
    Presentation.current model.presentation
        |> Maybe.andThen (\snapshot -> StatusScroll.domIdForSnapshot snapshot model.statusScroll)

subscriptionPlan : Model -> List Subscription
subscriptionPlan model =
    if Presentation.current model.presentation /= Nothing then
        [ PresentationChannel, RequestActionChannel, AnnouncementsChannel ]

    else
        [ PresentationChannel ]

subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch
        (List.map
            (\channel ->
                case channel of
                    PresentationChannel ->
                        presentation Present

                    RequestActionChannel ->
                        requestAction Action

                    AnnouncementsChannel ->
                        announcements Announce
            )
            (subscriptionPlan model)
        )

waitingView : Html.Html Msg
waitingView =
    div
        ([ attribute "data-bar-state" "waiting"
         , attribute "role" "status"
         , attribute "aria-live" "polite"
         , attribute "aria-atomic" "true"
         ]
            ++ SurfaceTheme.preFrameBarStyles
        )
        [ text "Waiting for desktop state…" ]

view : Model -> Html.Html Msg
view model =
    Presentation.current model.presentation
        |> Maybe.map
            (\snapshot ->
                div []
                    [ SurfaceRenderer.viewBarWithStatusScroll (StatusScroll.domIdForSnapshot snapshot model.statusScroll) Action snapshot
                    , Announcement.view model.announcements
                    ]
            )
        |> Maybe.withDefault waitingView

-- A display owns only a presentation cache and local viewport state. It cannot run Desktop.update.
main : Program () Model Msg
main =
    Browser.element
        { init = \_ -> ( initial, Cmd.none )
        , subscriptions = subscriptions
        , view = view
        , update =
            \message model ->
                let
                    ( nextModel, effects ) =
                        step message model

                    interpret effect =
                        case effect of
                            Dispatch wire ->
                                actions wire

                            ResetStatusViewport _ _ ->
                                localEffect identity effect |> Maybe.withDefault Cmd.none
                in
                ( nextModel, Cmd.batch (List.map interpret effects) )
        }
