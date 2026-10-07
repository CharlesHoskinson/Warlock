module PreviewVisual exposing (Visual(..), State(..), LocalState(..), Fidelity(..), encode, decoder, view, inlineView)

import Html exposing (Html, img, span, text)
import Html.Attributes exposing (alt, attribute, class, src)
import Html.Keyed
import Json.Decode as D
import Json.Encode as E

-- Render data only. No job, native scope, demand, effect, lifecycle update or
-- native purpose ordinal can be reconstructed from this projection.
type State = Live | Historical | Loading | Unavailable
type LocalState = Capacity | Waiting | Expired | Conflict | Exhausted
type Fidelity = Client | Family
type Visual
    = Hidden
    | Fallback
    | Local LocalState String
    | Lifecycle { state : State, title : Maybe String, icon : Maybe String, frame : Maybe String, fidelity : Maybe Fidelity }

stateName : State -> String
stateName state = case state of
    Live -> "live"
    Historical -> "historical"
    Loading -> "loading"
    Unavailable -> "unavailable"

stateLabel : State -> String
stateLabel state = case state of
    Live -> "Live preview"
    Historical -> "Historical preview"
    Loading -> "Preview loading"
    Unavailable -> "Preview unavailable"

localName : LocalState -> String
localName state = case state of
    Capacity -> "capacity"
    Waiting -> "waiting"
    Expired -> "expired"
    Conflict -> "conflict"
    Exhausted -> "exhausted"

localLabel : LocalState -> String
localLabel state = case state of
    Capacity -> "Waiting for preview capacity"
    Waiting -> "Waiting for preview"
    Expired -> "Preview request expired"
    Conflict -> "Preview request changed"
    Exhausted -> "Preview unavailable"

encode : Visual -> E.Value
encode visual =
    let maybe f value = Maybe.map f value |> Maybe.withDefault E.null
    in case visual of
        Hidden -> E.object [("kind",E.string "hidden")]
        Fallback -> E.object [("kind",E.string "fallback")]
        Local state title -> E.object [("kind",E.string "local"),("state",E.string (localName state)),("title",E.string title)]
        Lifecycle data -> E.object [("kind",E.string "lifecycle"),("state",E.string (stateName data.state)),("title",maybe E.string data.title),("icon",maybe E.string data.icon),("frame",maybe E.string data.frame),("fidelity",maybe (\f -> E.string (if f==Family then "family" else "client")) data.fidelity)]

strict : List String -> D.Decoder a -> D.Decoder a
strict fields parser = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then parser else D.fail "Closed visual fields")

token : D.Decoder String
token = D.string |> D.andThen (\value -> if String.length value==64 && value/=String.repeat 64 "0" && String.all (\c -> (c>='0' && c<='9') || (c>='a' && c<='f')) value then D.succeed value else D.fail "Original opaque visual token")

titleDecoder : D.Decoder String
titleDecoder = D.string |> D.andThen (\value ->
    let bytes = String.foldl (\c total -> total + (if Char.toCode c<128 then 1 else if Char.toCode c<2048 then 2 else if Char.toCode c<65536 then 3 else 4)) 0 value
    in if bytes<=1024 && not (String.any (\c -> Char.toCode c<32 || (Char.toCode c>=127 && Char.toCode c<=159)) value) then D.succeed value else D.fail "Bounded visual title")

decoder : D.Decoder Visual
decoder = D.field "kind" D.string |> D.andThen (\kind -> case kind of
    "hidden" -> strict ["kind"] (D.succeed Hidden)
    "fallback" -> strict ["kind"] (D.succeed Fallback)
    "local" -> strict ["kind","state","title"] (D.map2 Local
        (D.field "state" D.string |> D.andThen (\state -> case state of
            "capacity" -> D.succeed Capacity
            "waiting" -> D.succeed Waiting
            "expired" -> D.succeed Expired
            "conflict" -> D.succeed Conflict
            "exhausted" -> D.succeed Exhausted
            _ -> D.fail "Closed local visual state")) (D.field "title" titleDecoder))
    "lifecycle" -> strict ["kind","state","title","icon","frame","fidelity"]
        (D.map5 (\state title icon frame fidelity -> {state=state,title=title,icon=icon,frame=frame,fidelity=fidelity})
            (D.field "state" D.string |> D.andThen (\state -> case state of
                "live" -> D.succeed Live
                "historical" -> D.succeed Historical
                "loading" -> D.succeed Loading
                "unavailable" -> D.succeed Unavailable
                _ -> D.fail "Closed lifecycle visual state"))
            (D.field "title" (D.nullable titleDecoder)) (D.field "icon" (D.nullable token))
            (D.field "frame" (D.nullable token))
            (D.field "fidelity" (D.nullable (D.string |> D.andThen (\value -> if value=="client" then D.succeed Client else if value=="family" then D.succeed Family else D.fail "Closed visual fidelity")))))
        |> D.andThen (\data ->
            if data.state==Live || data.state==Historical then
                if data.frame/=Nothing && data.fidelity/=Nothing && data.title==Nothing && data.icon==Nothing then D.succeed (Lifecycle data) else D.fail "Exact drawable visual shape"
            else if data.frame==Nothing && data.fidelity==Nothing && data.title/=Nothing then D.succeed (Lifecycle data) else D.fail "Exact fallback visual shape")
    _ -> D.fail "Closed visual union")

view : Visual -> Html msg
view = render "figure" "figcaption"

inlineView : Visual -> Html msg
inlineView = render "span" "span"

render : String -> String -> Visual -> Html msg
render root caption visual = case visual of
    Hidden -> text ""
    Fallback -> span [class "window-preview",attribute "data-preview-state" "unavailable"] [span [class "preview-title"] [text "Preview unavailable"],span [class "preview-state"] [text "Preview unavailable"]]
    Local state title -> span [class "window-preview",attribute "data-preview-state" (localName state)] [span [class "preview-title"] [text title],span [class "preview-state",attribute "role" "status",attribute "aria-live" "polite"] [text (localLabel state)]]
    Lifecycle data ->
        let contents = case data.frame of
                Just handle -> [("frame:" ++ handle,img [class "preview-image",src ("elm-shell://preview/" ++ handle),alt "",attribute "aria-hidden" "true"] [])]
                Nothing -> (data.icon |> Maybe.map (\handle -> [("icon:" ++ handle,img [class "preview-icon",src ("elm-shell://icon/" ++ handle),alt "",attribute "aria-hidden" "true"] [])]) |> Maybe.withDefault []) ++ [("title",span [class "preview-title"] [text (Maybe.withDefault "Preview unavailable" data.title)])]
            fidelity = data.fidelity |> Maybe.map (\f -> if f==Family then "Window family" else "Client content") |> Maybe.withDefault ""
        in Html.Keyed.node root [class "window-preview",attribute "data-preview-state" (stateName data.state)] (contents ++ [("status",Html.node caption [] [span [class "preview-state"] [text (stateLabel data.state)],span [class "preview-fidelity"] [text fidelity]])])
