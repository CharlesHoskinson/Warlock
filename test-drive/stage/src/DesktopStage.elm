port module DesktopStage exposing (main)
import Browser
import Html exposing (Html, button, div, h2, p, pre, text)
import Html.Attributes exposing (attribute, class, style, type_)
import Html.Events exposing (onClick, on, preventDefaultOn)
import Json.Decode as D exposing (Decoder, Value)
import Json.Encode as E
port observe : (Value -> msg) -> Sub msg
port input : E.Value -> Cmd msg
port watch : E.Value -> Cmd msg
port completed : (Int -> msg) -> Sub msg

type alias Window = { id : String, incarnation : String, title : String, workspace : String, minimized : Bool, focused : Bool, active : Bool, x : Float, y : Float, width : Float, height : Float, stack : Int, placement : String, pinned : Bool }
type alias Snapshot = { windows : List Window, workspace : String, epoch : Int, now : Int, tier : String }
type alias Effect = { window : Window, phase : String, cycle : Int, tier : String }
type alias Model = { snapshot : Maybe Snapshot, effect : Maybe Effect, cycle : Int, lastStart : Int }
type Msg = Observed Value | Operation String String String | Context String String Float Float String | Completed Int
main : Program () Model Msg
main = Browser.element { init = \_ -> ( Model Nothing Nothing 0 -10000, Cmd.none ), update = update, subscriptions = \_ -> Sub.batch [ observe Observed, completed Completed ], view = view }
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Operation id incarnation action -> ( model, input (E.object [ ( "kind", E.string "window" ), ( "action", E.string action ), ( "windowId", E.string id ), ( "incarnation", E.string incarnation ) ]) )
        Context id incarnation x y trigger -> ( model, input (E.object [ ( "kind", E.string "window" ), ( "action", E.string "window-menu" ), ( "windowId", E.string id ), ( "incarnation", E.string incarnation ), ( "anchor", E.object [ ( "x", E.float x ), ( "y", E.float y ) ] ), ( "trigger", E.string trigger ) ]) )
        Completed cycle -> ( if Maybe.map .cycle model.effect == Just cycle then { model | effect = Nothing } else model, Cmd.none )
        Observed value ->
            case D.decodeValue snapshot value of
                Err _ -> ( model, Cmd.none )
                Ok next ->
                    case model.snapshot of
                        Nothing -> ( { model | snapshot = Just next }, Cmd.none )
                        Just old ->
                            let
                                changedEpoch = old.epoch /= next.epoch
                                same w other = w.id == other.id && w.incarnation == other.incarnation
                                added = List.filter (\w -> not (List.any (same w) old.windows) && w.workspace == next.workspace && not w.minimized) next.windows
                                removed = List.filter (\w -> not (List.any (same w) next.windows) && w.workspace == old.workspace && not w.minimized) old.windows
                                candidate = case ( added, removed ) of
                                    ( [ w ], [] ) -> Just ( w, "open" )
                                    ( [], [ w ] ) -> Just ( w, "close" )
                                    _ -> Nothing
                                effectInvalid = case model.effect of
                                    Just effect -> effect.phase == "open" && not (List.any (same effect.window) next.windows)
                                    Nothing -> False
                                eligible = not effectInvalid && not changedEpoch && old.workspace == next.workspace && next.tier /= "off" && model.effect == Nothing && next.now - model.lastStart >= 1000
                            in
                            case ( eligible, candidate ) of
                                ( True, Just ( w, phase ) ) ->
                                    let
                                        cycle = model.cycle + 1
                                        effect = Effect w phase cycle next.tier
                                    in
                                    ( { model | snapshot = Just next, effect = Just effect, cycle = cycle, lastStart = next.now }, watch (E.object [ ( "cycle", E.int cycle ), ( "phase", E.string phase ), ( "tier", E.string next.tier ) ]) )
                                _ -> ( { model | snapshot = Just next, effect = if effectInvalid || changedEpoch || old.tier /= next.tier || old.workspace /= next.workspace then Nothing else model.effect }, Cmd.none )
snapshot : Decoder Snapshot
snapshot = D.map5 Snapshot (D.field "windows" (D.list window)) (D.field "activeWorkspace" D.string) (D.field "epoch" D.int) (D.field "_now" D.int) (D.field "_tier" D.string)
window : Decoder Window
window =
    D.map5 (\make active stack placement pinned -> make active stack placement pinned)
        (D.map8 (\id incarnation title workspace minimized focused x rest active -> Window id incarnation title workspace minimized focused active x (Tuple.first rest) (Tuple.first (Tuple.second rest)) (Tuple.second (Tuple.second rest)))
        (D.field "id" D.string) (D.oneOf [ D.field "incarnation" D.string, D.field "generation" D.string, D.field "id" D.string ]) (D.oneOf [ D.field "title" D.string, D.succeed "Application" ]) (D.field "workspace" D.string) (D.field "minimized" D.bool) (D.field "focused" D.bool) (D.at [ "geometry", "x" ] D.float) (D.map2 Tuple.pair (D.at [ "geometry", "y" ] D.float) (D.map2 Tuple.pair (D.at [ "geometry", "width" ] D.float) (D.at [ "geometry", "height" ] D.float))))
        (D.oneOf [ D.field "activeApplication" D.bool, D.field "active" D.bool, D.succeed False ])
        (D.oneOf [ D.field "_stack" D.int, D.succeed 0 ])
        (D.oneOf [ D.field "_placement" D.string, D.succeed "unknown" ])
        (D.oneOf [ D.field "pinned" D.bool, D.succeed False ])
view : Model -> Html Msg
view model =
    div [ class "stage-windows" ] (case model.snapshot of
        Nothing -> []
        Just s -> List.map viewWindow (List.filter (\w -> (w.workspace == s.workspace || w.pinned) && not w.minimized) s.windows) ++ (case model.effect of
            Nothing -> []
            Just effect -> [ div (geometry effect.window ++ [ class "wl-effect-portal stage-effect", attribute "aria-hidden" "true", attribute "data-portal-phase" effect.phase, attribute "data-effect-cycle" (String.fromInt effect.cycle), attribute "data-effects-tier" effect.tier ]) [] ]))
geometry : Window -> List (Html.Attribute msg)
geometry w = [ style "left" (px w.x), style "top" ("calc(" ++ px w.y ++ " - var(--desktop-bar-height))"), style "width" (px w.width), style "height" (px w.height) ]
viewWindow : Window -> Html Msg
viewWindow w =
    div (geometry w ++ [ class ("stage-window" ++ (if w.focused then " is-focused" else "") ++ (if w.active then " is-active-application" else "")), attribute "data-window-id" w.id, attribute "data-placement" w.placement, attribute "data-pinned" (if w.pinned then "true" else "false"), style "z-index" (String.fromInt w.stack) ])
        [ div [ class "stage-titlebar", preventDefaultOn "contextmenu" (D.map3 (\x y button -> ( Context w.id w.incarnation x y (if button == 2 then "pointer" else "keyboard"), True )) (D.field "clientX" D.float) (D.field "clientY" D.float) (D.field "button" D.int)) ]
            [ button [ type_ "button", onClick (Operation w.id w.incarnation "focus"), on "dblclick" (D.succeed (Operation w.id w.incarnation "maximize-toggle")), class "stage-title" ] [ text w.title ]
            , button [ type_ "button", onClick (Operation w.id w.incarnation "minimize"), attribute "aria-label" ("Minimize " ++ w.title) ] [ text "−" ]
            , button [ type_ "button", onClick (Operation w.id w.incarnation "maximize-toggle"), on "mouseenter" (D.succeed (Operation w.id w.incarnation "snap-hover")), attribute "aria-label" ((if w.placement == "maximized" then "Restore " else "Maximize ") ++ w.title), attribute "title" "Maximize or restore; hover for snap layouts" ] [ text "□" ]
            , button [ type_ "button", onClick (Operation w.id w.incarnation "window-menu"), attribute "aria-label" ("Window menu for " ++ w.title) ] [ text "⋮" ]
            , button [ type_ "button", onClick (Operation w.id w.incarnation "close"), attribute "aria-label" ("Close " ++ w.title) ] [ text "×" ] ]
        , div [ class "stage-client", onClick (Operation w.id w.incarnation "focus") ]
            [ p [ class "fixture-label" ] [ text "SIMULATED CLIENT" ], h2 [] [ text w.title ]
            , if String.contains "terminal" (String.toLower w.title) then pre [] [ text "$ warlock\nDesktop session ready.\n$ _" ] else if String.contains "browser" (String.toLower w.title) then div [] [ p [] [ text "Local document preview" ], h2 [] [ text "A clear workspace" ], p [] [ text "Arrange windows, keep your place, and move between tasks." ] ] else div [] [ p [] [ text "workspace / notes.md" ], pre [] [ text "# Working notes\n\nKeep the next step visible.\nArrange the workspace around the task." ] ] ] ]
px : Float -> String
px n = String.fromFloat n ++ "px"
