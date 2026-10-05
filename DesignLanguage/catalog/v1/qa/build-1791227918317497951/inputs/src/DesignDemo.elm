port module DesignDemo exposing (main)

import Browser
import CapturedAction
import Effects
import Html exposing (Html, div, p, text)
import Html.Attributes exposing (attribute, class)
import Json.Decode as D
import Json.Encode as E
import Menu
import PreviewLifecycle as Preview
import SurfaceRenderer
import Taskbar
import UInt64

-- This isolated documentation program runs shipped pure modules. Its messages
-- and effects are fixtures; it never connects to a compositor or issues effects.
port fixtureInput : (D.Value -> msg) -> Sub msg
port fixtureObserved : E.Value -> Cmd msg

type alias Model =
    { topic : String, publication : Int, menu : Menu.Model
    , intent : Maybe ( Menu.IntentId, Menu.Binding ), preview : Maybe Preview.Model
    , effects : E.Value, profile : String, error : String }

type Msg = Input D.Value

fixtureBinding : Menu.Binding
fixtureBinding = Menu.binding {authority="fixture-authority",revision="1",output=Menu.outputId "fixture-output",outputGeneration="1",target=Menu.Window (Menu.windowId "fixture-lifetime" "fixture-window")}

items : List Menu.Item
items =
    [ {label="Restore",enabled=True,action=Menu.Restore}
    , {label="Restore geometry",enabled=True,action=Menu.RestoreGeometry}
    , {label="Move",enabled=True,action=Menu.Move}
    , {label="Size",enabled=False,action=Menu.Size}
    , {label="Minimize",enabled=True,action=Menu.Minimize}
    , {label="Maximize",enabled=True,action=Menu.Maximize}
    , {label="Close window",enabled=True,action=Menu.Close}
    , {label="Exit fullscreen",enabled=True,action=Menu.ExitFullscreen}
    , {label="Always on top",enabled=True,action=Menu.AlwaysOnTop True}
    , {label="Pin to taskbar",enabled=True,action=Menu.PinToTaskbar True}
    , {label="Launch declared application",enabled=True,action=Menu.Launch (Menu.declaredActionId "fixture-application")}
    , {label="Declared provider action",enabled=True,action=Menu.ProviderCommand (Menu.declaredActionId "fixture-action")}
    ]

nativeBinding : E.Value
nativeBinding = E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string "3")]

context : E.Value
context = E.object (List.map (\(key,value) -> (key,E.string value)) [("lifetime","1"),("incarnation","4"),("output","5"),("privacy","6"),("rendering","7"),("scene","8"),("content","9")])

scope : Bool -> Bool -> E.Value
scope live locked = E.object [("binding",nativeBinding),("context",context),("observation",E.string (if live && not locked then "1" else "2")),("clock",E.string "10"),("now",E.string "11"),("present",E.bool True),("sourceLive",E.bool live),("locked",E.bool locked),("gpuReady",E.bool True)]

initialPreview : Maybe Preview.Model
initialPreview = D.decodeValue Preview.scopeDecoder (scope True False) |> Result.toMaybe |> Maybe.map Preview.init

initial : String -> Model
initial topic =
    {topic=topic,publication=1,menu=Tuple.first (Menu.update (Menu.Open fixtureBinding items) Menu.init),intent=Nothing,preview=initialPreview,effects=E.list identity [],profile="inactive",error=""}

notice : Model -> String
notice model =
    case (Menu.snapshot model.menu).menu of
        Nothing -> "Menu closed. Outstanding requests: " ++ String.fromInt (Menu.snapshot model.menu).outstanding
        Just menu -> case menu.status of
            Menu.Ready -> "Ready"
            Menu.Pending _ -> "Applying window change…"
            Menu.Unknown _ -> "Outcome unconfirmed. Reconcile before repeating."
            Menu.Refused reason -> reason
            Menu.Cancelled -> "Cancelled"

blocked : Model -> Bool
blocked model =
    case (Menu.snapshot model.menu).menu |> Maybe.map .status of
        Just (Menu.Pending _) -> True
        Just (Menu.Unknown _) -> True
        _ -> False

control : String -> String -> String -> Bool -> E.Value
control identity label detail enabled = E.object [("id",E.string identity),("domId",E.string ("fixture-" ++ identity)),("label",E.string label),("ariaLabel",E.string label),("detail",E.string detail),("enabled",E.bool enabled)]

projection : Model -> Result String SurfaceRenderer.Snapshot
projection model =
    let
        menu = (Menu.snapshot model.menu).menu
        mode = if model.topic=="menu" then (if menu==Nothing then "closed" else "menu") else if model.topic=="applications" then "applications" else if model.topic=="picker" then "picker" else "closed"
        popup = if mode=="menu" then
                items |> List.indexedMap (\index item -> control ("demo-menu:" ++ String.fromInt index) item.label (if not item.enabled then "Unavailable in this fixture" else if blocked model then "Awaiting confirmation" else if menu |> Maybe.andThen .selected |> (==) (Just index) then "Selected" else "") (item.enabled && not (blocked model)))
            else if mode=="applications" then [control "demo-app:editor" "Text editor" "Declared application" True,control "demo-app:terminal" "Terminal" "Declared application" True]
            else if mode=="picker" then [control "demo-picker:document" "Restore design notes" "Text editor" True,control "demo-picker:terminal" "Activate build session" "Terminal" True]
            else []
        bar = if model.topic=="bar" || model.topic=="status" then [control "bar:applications" "Applications" "" True,control "bar:group:terminal" "Terminal" (decision model.profile) (model.profile/="unavailable"),control "bar:recovery-refresh" "Refresh windows" "" True] else []
    in SurfaceRenderer.decode (E.object [("surfaceProtocol",E.int 2),("publication",E.string (String.fromInt model.publication)),("lease",E.string "1"),("mode",E.string mode),("status",E.string (if model.topic=="menu" then notice model else "Simulated fixture; no native effect")),("bar",E.list identity bar),("popup",E.list identity popup)])

family : String -> Taskbar.Family
family profile = {root=D.decodeValue UInt64.decoder (E.string "4") |> Result.withDefault UInt64.zero,label="Terminal",application="fixture-terminal",minimized=profile=="minimized",available=profile/="unavailable",active=profile=="active"}

decision : String -> String
decision profile =
    let families = if profile=="empty" then [] else if profile=="multiple" then [family "active",family "inactive"] else [family profile]
    in case Taskbar.primary False families of
        Taskbar.Launch -> "Launch (function-level; not reached by this call)"
        Taskbar.Picker -> "Open window picker"
        Taskbar.Unavailable -> "Unavailable"
        Taskbar.Apply operation _ -> case operation of
            Effects.Restore -> "Request restore"
            Effects.Minimize -> "Request minimize"
            Effects.Activate -> "Request activate"

menuUpdate : Menu.Msg -> Model -> Model
menuUpdate message model =
    let
        (next,effects) = Menu.update message model.menu
        pending = List.head effects |> Maybe.map (\effect -> case effect of Menu.Dispatch intent binding _ -> (intent,binding))
    in {model | menu=next,intent=if pending==Nothing then model.intent else pending,effects=E.object [("dispatches",E.int (List.length effects))]}

previewUpdate : E.Value -> Model -> Model
previewUpdate raw model =
    case (model.preview,D.decodeValue Preview.eventDecoder raw) of
        (Just before,Ok event) -> let (after,effects)=Preview.update event before in {model | preview=Just after,effects=Preview.encodeCommands effects}
        _ -> {model | error="Fixture event was rejected by the shipped preview decoder."}

previewAction : String -> Model -> Model
previewAction action model =
    case action of
        "load" -> model |> previewUpdate (E.object [("kind",E.string "open")]) |> previewUpdate (E.object [("kind",E.string "request"),("trigger",E.object [("binding",nativeBinding),("context",context),("origin",E.string "12"),("clock",E.string "10"),("deadline",E.string "80")])])
        "frame" ->
            case model.preview |> Maybe.andThen (Preview.observe >> D.decodeValue (D.field "job" D.value) >> Result.toMaybe) of
                Just job -> previewUpdate (E.object [("kind",E.string "offer"),("frame",E.object [("job",job),("handle",E.string (String.repeat 64 "1")),("owned",E.bool True),("signaled",E.bool True),("fidelity",E.string "family"),("coverage",E.list E.string ["client","decoration","modal","popup"]),("expires",E.string "90")])]) model
                Nothing -> model
        "historical" -> previewUpdate (E.object [("kind",E.string "observe"),("scope",scope False False)]) model
        "lock" -> previewUpdate (E.object [("kind",E.string "observe"),("scope",scope True True)]) model
        "expire" -> previewUpdate (E.object [("kind",E.string "clock"),("binding",nativeBinding),("clock",E.string "10"),("now",E.string "100")]) model
        "close" -> previewUpdate (E.object [("kind",E.string "close")]) model
        _ -> model

apply : D.Value -> Model -> Model
apply raw model =
    case D.decodeValue (D.field "kind" D.string) raw of
        Ok "reset" -> initial model.topic
        Ok "profile" -> case D.decodeValue (D.field "value" D.string) raw of
            Ok value -> if List.member value ["empty","inactive","active","minimized","unavailable","multiple"] then {model | profile=value} else model
            Err _ -> model
        Ok "preview" -> D.decodeValue (D.field "action" D.string) raw |> Result.map (\action -> previewAction action model) |> Result.withDefault model
        Ok "dismiss" -> case (Menu.snapshot model.menu).menu of Just menu -> menuUpdate (Menu.Dismiss menu.id) model
                                                                   Nothing -> model
        Ok "navigate" ->
            case ((Menu.snapshot model.menu).menu,D.decodeValue (D.field "key" D.string) raw) of
                (Just menu,Ok key) -> case key of
                    "ArrowUp" -> menuUpdate (Menu.Navigate menu.id Menu.Up) model
                    "ArrowDown" -> menuUpdate (Menu.Navigate menu.id Menu.Down) model
                    "Home" -> menuUpdate (Menu.Navigate menu.id Menu.Home) model
                    "End" -> menuUpdate (Menu.Navigate menu.id Menu.End) model
                    _ -> model
                _ -> model
        Ok "authority" ->
            case (model.intent,D.decodeValue (D.field "outcome" D.string) raw) of
                (Just (intent,binding),Ok outcome) -> case outcome of
                    "committed" -> menuUpdate (Menu.ReceiveFor intent binding Menu.Committed) model
                    "refused" -> menuUpdate (Menu.ReceiveFor intent binding (Menu.Refusal "Change refused by simulated authority.")) model
                    "cancelled" -> menuUpdate (Menu.ReceiveFor intent binding Menu.Cancellation) model
                    "unknown" -> menuUpdate (Menu.ReceiveFor intent binding Menu.Uncertain) model
                    _ -> model
                _ -> model
        Ok "surface-action" ->
            case (projection model,CapturedAction.decode raw,(Menu.snapshot model.menu).menu) of
                (Ok shown,Ok captured,Just menu) ->
                    if CapturedAction.publication captured/=SurfaceRenderer.publication shown || CapturedAction.lease captured/=SurfaceRenderer.lease shown || CapturedAction.surface captured/="popup" || not (SurfaceRenderer.enabled True (CapturedAction.identity captured) shown) then model
                    else case String.dropLeft 10 (CapturedAction.identity captured) |> String.toInt of
                        Just index -> menuUpdate (Menu.Activate menu.id menu.binding index) model
                        Nothing -> model
                _ -> model
        _ -> model

observe : Model -> E.Value
observe model = E.object [("topic",E.string model.topic),("menuStatus",E.string (notice model)),("outstanding",E.int (Menu.snapshot model.menu).outstanding),("effects",model.effects),("decision",E.string (decision model.profile)),("preview",model.preview |> Maybe.map Preview.observe |> Maybe.withDefault E.null),("error",E.string model.error)]

update : Msg -> Model -> (Model,Cmd Msg)
update (Input raw) model = let result=apply raw model
                              next={result | publication=model.publication+1}
                          in (next,fixtureObserved (observe next))

view : Model -> Html Msg
view model =
    if model.topic=="preview" then model.preview |> Maybe.map (Preview.view {title="Design notes",application="Text editor",icon=Nothing}) |> Maybe.withDefault (text "Preview fixture unavailable")
    else case projection model of
        Ok shown -> div [class "elm-specimen",attribute "data-fixture-publication" (String.fromInt model.publication)] [SurfaceRenderer.view (model.topic/="bar" && model.topic/="status") (\_ -> Input E.null) shown,p [class "fixture-summary"] [text (if model.topic=="menu" then notice model else if model.topic=="bar" then decision model.profile else "Read-only presentation fixture. No native action is issued.")]]
        Err error -> text error

main : Program D.Value Model Msg
main = Browser.element {init=\flags -> let model=initial (D.decodeValue (D.field "topic" D.string) flags |> Result.withDefault "menu") in (model,fixtureObserved (observe model)),update=update,view=view,subscriptions=\_ -> fixtureInput Input}
