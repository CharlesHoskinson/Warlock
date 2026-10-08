module SurfaceRenderer exposing (enabled, Snapshot, decode, encode, controlIdentities, publication, lease, mode, view, viewWithPreview, action, queryValue, pendingQuery)

import Html exposing (Html, button, div, h1, input, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id, title, type_, value, placeholder)
import Html.Events exposing (on)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Set
import Settings
import UInt64 exposing (Counter)

type alias Control = { identity : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool }
type Snapshot = Snapshot { publication : Counter, lease : Counter, mode : String, status : String, appearance : Settings.Values, bar : List Control, popup : List Control }

strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Presentation fields")

bounded : Int -> D.Decoder String
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Presentation text")

controls : Int -> D.Decoder (List Control)
controls maximum =
    D.list D.value |> D.andThen (\values -> if List.length values>maximum then D.fail "Presentation capacity" else
        D.list (strict ["id","domId","label","ariaLabel","detail","enabled"] (D.map6 Control (D.field "id" (bounded 512)) (D.field "domId" (bounded 1024)) (D.field "label" (bounded 1024)) (D.field "ariaLabel" (bounded 1024)) (D.field "detail" (bounded 128)) (D.field "enabled" D.bool))))

decode : D.Value -> Result String Snapshot
decode raw =
    let legacy = D.decodeValue (D.field "appearance" D.value) raw |> Result.toMaybe |> (==) Nothing
        decoder = strict (["surfaceProtocol","publication","lease","mode","status","bar","popup"] ++ (if legacy then [] else ["appearance"]))
            (D.map8 (\version shown scoped current notice bar popup appearance -> {version=version,shown=shown,scoped=scoped,current=current,notice=notice,bar=bar,popup=popup,appearance=appearance})
                (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "mode" (bounded 16)) (D.field "status" (bounded 1024)) (D.field "bar" (controls 300)) (D.field "popup" (controls 2150)) (if legacy then D.succeed Settings.defaults else D.field "appearance" Settings.valuesDecoder))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\record ->
        let all = record.bar ++ record.popup
            identities = List.map .identity all
            unique names = List.length names == Set.size (Set.fromList names)
        in if record.version/=2 || record.shown==UInt64.zero || not (List.member record.current ["closed","picker","applications","menu","overview","switcher","snap","settings","notifications","system"]) || (record.current/="closed" && record.scoped==UInt64.zero) || (record.current=="closed" && not (List.isEmpty record.popup)) || not (unique identities) || not (unique (List.map .domId all)) || List.any (\control -> String.isEmpty control.identity || String.isEmpty control.domId) all then Err "Invalid presentation scope/identities"
        else Ok (Snapshot {publication=record.shown,lease=record.scoped,mode=record.current,status=record.notice,appearance=record.appearance,bar=record.bar,popup=record.popup}))

publication : Snapshot -> Counter
publication (Snapshot snapshot) = snapshot.publication

encode : Snapshot -> E.Value
encode (Snapshot snapshot) =
    let control row = E.object [("id",E.string row.identity),("domId",E.string row.domId),("label",E.string row.label),("ariaLabel",E.string row.ariaLabel),("detail",E.string row.detail),("enabled",E.bool row.enabled)]
    in E.object [("surfaceProtocol",E.int 2),("appearance",Settings.encodeValues snapshot.appearance),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("mode",E.string snapshot.mode),("status",E.string snapshot.status),("bar",E.list control snapshot.bar),("popup",E.list control snapshot.popup)]

controlIdentities : Bool -> Snapshot -> List String
controlIdentities popup (Snapshot snapshot) = List.map .identity (if popup then snapshot.popup else snapshot.bar)

lease : Snapshot -> Counter
lease (Snapshot snapshot) = snapshot.lease

mode : Snapshot -> String
mode (Snapshot snapshot) = snapshot.mode

queryValue : Snapshot -> Maybe String
queryValue (Snapshot snapshot) = snapshot.popup |> List.filter (\item -> item.identity=="control:search") |> List.head |> Maybe.map .label

pendingQuery : String -> Snapshot -> Snapshot
pendingQuery query (Snapshot snapshot) = Snapshot {snapshot | popup=List.map (\item -> if item.identity=="control:search" then {item | label=query} else if String.startsWith "entry:" item.identity then {item | enabled=False} else item) snapshot.popup}

enabled : Bool -> String -> Snapshot -> Bool
enabled popup identity (Snapshot snapshot) = List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar)

action : Bool -> String -> Snapshot -> Maybe E.Value
action popup identity (Snapshot snapshot) =
    if List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar) then
        Just (E.object [("surface",E.string (if popup then "popup" else "bar")),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string identity)])
    else Nothing

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send current = viewWithPreview (\_ -> text "") popup send current

viewWithPreview : (String -> Html msg) -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreview preview popup send ((Snapshot snapshot) as current) =
    let control item =
            let kind = if String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity then "control-group" else if item.identity=="bar:recovery-refresh" then "control-recovery" else "control-utility"
            in if popup && snapshot.mode=="notifications" && (String.endsWith ":summary" item.identity || String.endsWith ":body" item.identity) then
                p [class "notification-text",id item.domId,attribute "data-notification-content" item.identity] [span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
            else if popup && snapshot.mode=="system" && String.endsWith ":state" item.identity then
                p [class "notification-text",id item.domId,attribute "data-system-content" item.identity] [span [class "control-label"] [text item.label]]
            else if popup && snapshot.mode=="applications" && item.identity=="control:search" then
                let event = D.map2 (\query composing -> (query,composing)) (D.at ["target","value"] D.string) (D.oneOf [D.field "isComposing" D.bool,D.succeed False]) |> D.andThen (\(query,composing) -> D.succeed (send (E.object [("surfaceProtocol",E.int 2),("kind",E.string (if composing then "surface-preedit" else "surface-query")),("surface",E.string "popup"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string item.identity),("query",E.string query)])))
                in input [class "launcher-search",id item.domId,type_ "search",placeholder "Search applications",value item.label,attribute "aria-label" item.ariaLabel,attribute "data-surface-field" item.identity,attribute "autocomplete" "off",disabled (not item.enabled),on "input" event,on "compositionend" event] []
            else button [class kind,id item.domId,attribute "aria-label" item.ariaLabel,disabled (not item.enabled),attribute "data-surface-control" item.identity,attribute "role" (if popup && snapshot.mode=="menu" then "menuitem" else "button"),attribute "aria-current" (if popup && List.member snapshot.mode ["menu","switcher","snap","settings","notifications","system"] && item.detail=="Selected" then "true" else "false")] [preview item.identity,span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
        familyPrefix rows = case rows of
            first :: rest -> if String.startsWith "overview:family:" first.identity then first :: familyPrefix rest else []
            [] -> []
        overviewRows rows =
            case rows of
                [] -> []
                first :: rest ->
                    if String.startsWith "overview:workspace:" first.identity then
                        let members = familyPrefix rest
                        in div [class "overview-workspace",attribute "role" "group",attribute "aria-labelledby" first.domId] (List.map control (first::members)) :: overviewRows (List.drop (List.length members) rest)
                    else control first :: overviewRows rest
    in if popup then div [attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),class "surface-popup",attribute "data-mode" snapshot.mode,attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] [h1 [] [text (if snapshot.mode=="applications" then "Applications" else if snapshot.mode=="overview" then "Task View" else if snapshot.mode=="switcher" then "Switch windows" else if snapshot.mode=="snap" then "Snap window" else if snapshot.mode=="system" then "System" else if snapshot.mode=="notifications" then "Notifications" else if snapshot.mode=="settings" then "Settings" else if snapshot.mode=="menu" then "Window actions" else "Choose a window")],p [attribute "role" "status",attribute "aria-live" "polite"] [text snapshot.status],(if snapshot.mode=="overview" then div [class "surface-controls",attribute "role" "group"] (overviewRows snapshot.popup) else Keyed.node "div" [class "surface-controls",attribute "role" (if snapshot.mode=="menu" then "menu" else "group")] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.popup))]
       else Keyed.node "div" [attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),class "surface-bar",attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)]
            [("actions",Keyed.node "div" [class "surface-actions"] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.bar))
            ,("status",span [class (if String.isEmpty snapshot.status || snapshot.status=="Ready" then "surface-status surface-status-idle" else "surface-status"),attribute "role" "status",attribute "aria-live" "polite",attribute "aria-atomic" "true",attribute "aria-label" snapshot.status,title snapshot.status] [text snapshot.status])]
