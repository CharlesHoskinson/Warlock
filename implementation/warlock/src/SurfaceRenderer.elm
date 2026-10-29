module SurfaceRenderer exposing (enabled, Snapshot, decode, encode, controlIdentities, publication, lease, mode, view, viewWithPreview, action, queryValue, pendingQuery, fieldIdentity)

import Html exposing (Html, button, div, h1, input, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, hidden, id, title, type_, value, placeholder)
import Html.Events exposing (on)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Set
import Settings
import PreviewVisual as Preview
import UInt64 exposing (Counter)
import SurfaceSnapshot

type alias Snapshot = SurfaceSnapshot.Snapshot

enabled : Bool -> String -> Snapshot -> Bool
enabled = SurfaceSnapshot.enabled

decode : D.Value -> Result String Snapshot
decode = SurfaceSnapshot.decode

encode : Snapshot -> E.Value
encode = SurfaceSnapshot.encode

controlIdentities : Bool -> Snapshot -> List String
controlIdentities = SurfaceSnapshot.controlIdentities

publication : Snapshot -> Counter
publication = SurfaceSnapshot.publication

lease : Snapshot -> Counter
lease = SurfaceSnapshot.lease

mode : Snapshot -> String
mode = SurfaceSnapshot.mode

action : Bool -> String -> Snapshot -> Maybe E.Value
action = SurfaceSnapshot.action

queryValue : Snapshot -> Maybe String
queryValue = SurfaceSnapshot.queryValue

pendingQuery : String -> Snapshot -> Snapshot
pendingQuery = SurfaceSnapshot.pendingQuery

fieldIdentity : Snapshot -> String
fieldIdentity = SurfaceSnapshot.fieldIdentity

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send current = viewWithPreview (\_ -> Preview.Hidden) popup send current

viewWithPreview : (String -> Preview.Visual) -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreview preview popup send current =
    let snapshot = SurfaceSnapshot.details current
        -- A description ID is stable across state changes and cannot collide
        -- with any control ID supplied by the current closed projection.
        domIds = Set.fromList (List.map .domId (snapshot.bar ++ snapshot.popup))
        prefix candidate = if List.any (\item -> Set.member (candidate ++ item.domId) domIds) (snapshot.bar ++ snapshot.popup) then prefix (candidate ++ "-") else candidate
        descriptionPrefix = prefix "preview-description-"
        control item =
            let visual = preview item.identity
                description = Preview.description visual
                descriptionId = descriptionPrefix ++ item.domId
                settingsToggle = popup && ((snapshot.mode=="settings" && List.member item.identity ["settings:effects-off","settings:reduced-transparency"]) || (snapshot.mode=="notifications" && List.member item.identity ["notifications:dnd","notifications:critical-interrupt"]))
                switcherOption = popup && snapshot.mode=="switcher" && String.startsWith "switcher:family:" item.identity
                overviewFilter = popup && snapshot.mode=="overview" && (item.identity=="overview:all" || String.startsWith "overview:workspace:" item.identity)
                active = not popup && (String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity) && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)
                kind = if String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity then "control-group" else if item.identity=="bar:recovery-refresh" then "control-recovery" else "control-utility"
            in if popup && snapshot.mode=="settings" && (String.startsWith "settings:help:text:" item.identity || (String.startsWith "settings:shortcuts:" item.identity && String.endsWith ":state" item.identity)) then
                p [class "notification-text",id item.domId,attribute (if String.startsWith "settings:help:text:" item.identity then "data-settings-help" else "data-shortcut-state") item.identity] [span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
            else if popup && snapshot.mode=="notifications" && (String.endsWith ":summary" item.identity || String.endsWith ":body" item.identity) then
                p [class "notification-text",id item.domId,attribute "data-notification-content" item.identity] [span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
            else if popup && List.member snapshot.mode ["system","files","jump"] && String.endsWith ":state" item.identity then
                p [class "notification-text",id item.domId,attribute (if snapshot.mode=="jump" then "data-jump-content" else if snapshot.mode=="files" then "data-files-content" else "data-system-content") item.identity] [span [class "control-label"] [text item.label]]
            else if popup && List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then
                let packet inputKind query = send (E.object [("surfaceProtocol",E.int 2),("kind",E.string inputKind),("surface",E.string "popup"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string item.identity),("query",E.string query)])
                    edit = D.map2 (\query composing -> packet (if composing then "surface-preedit" else "surface-query") query) (D.at ["target","value"] D.string) (D.oneOf [D.field "isComposing" D.bool,D.succeed False])
                    composition inputKind = D.map (packet inputKind) (D.at ["target","value"] D.string)
                in input [class "launcher-search",id item.domId,type_ (if snapshot.mode=="files" then "text" else "search"),placeholder (if snapshot.mode=="files" then "/path/to/folder or ~/Documents" else "Search applications"),value item.label,attribute "aria-label" item.ariaLabel,attribute "data-surface-field" item.identity,attribute "autocomplete" "off",disabled (not item.enabled),on "input" edit,on "compositionstart" (composition "surface-composition-start"),on "compositionend" (composition "surface-composition-end")] []
            else button ([class kind,id item.domId,attribute "data-window-state" (if kind/="control-group" then "none" else if String.contains "Attention; " item.detail then "attention" else if String.contains "Active" item.detail then "active" else if String.contains "Minimized" item.detail then "minimized" else "open"),attribute "aria-label" item.ariaLabel,disabled (not item.enabled && not item.focusOnly),attribute "aria-disabled" (if not item.enabled then "true" else "false"),attribute "data-focus-only" (if item.focusOnly then "true" else "false"),attribute "data-surface-control" item.identity,attribute "role" (if switcherOption then "option" else if popup && snapshot.mode=="menu" then (if item.checked/=Nothing then "menuitemcheckbox" else "menuitem") else "button"),attribute "aria-current" (if (not popup && kind=="control-group" && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)) || (popup && List.member snapshot.mode ["menu","switcher","snap","settings","notifications","system","files","jump"] && (item.detail=="Selected" || (snapshot.mode=="menu" && String.endsWith " • Selected" item.detail) || (settingsToggle && String.startsWith "On" item.detail))) then "true" else "false")] ++ (if overviewFilter then [attribute "aria-pressed" (if item.checked==Just True then "true" else "false")] else (item.checked |> Maybe.map (\checked -> [attribute "aria-checked" (if checked then "true" else "false")]) |> Maybe.withDefault [])) ++ (if String.isEmpty description then [] else [attribute "aria-describedby" descriptionId]) ++ (if popup && snapshot.mode=="settings" && item.identity=="settings:help" then [attribute "aria-expanded" (if item.detail=="Expanded" then "true" else "false")] else []) ++ (if settingsToggle then [attribute "aria-pressed" (if String.startsWith "On" item.detail then "true" else "false")] else []) ++ (if switcherOption then [attribute "aria-selected" (if item.detail=="Selected" then "true" else "false")] else if not popup && kind=="control-group" then [attribute "aria-pressed" (if active then "true" else "false")] else [])) [Preview.decorativeInlineView visual,span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail],if String.isEmpty description then text "" else span [class "preview-description",id descriptionId,hidden True] [text description]]
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
    in if popup then div [attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-popup",attribute "data-mode" snapshot.mode,attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] [h1 [] [text (if snapshot.mode=="applications" then "Applications" else if snapshot.mode=="overview" then "Task View" else if snapshot.mode=="switcher" then "Switch windows" else if snapshot.mode=="snap" then "Snap window" else if snapshot.mode=="jump" then "Application actions" else if snapshot.mode=="files" then "Files" else if snapshot.mode=="system" then "System" else if snapshot.mode=="notifications" then "Notifications" else if snapshot.mode=="settings" then "Settings" else if snapshot.mode=="menu" then "Window actions" else "Choose a window")],p [attribute "role" "status",attribute "aria-live" "off"] [text snapshot.status],(if snapshot.mode=="overview" then div [class "surface-controls",attribute "role" "group"] (overviewRows snapshot.popup) else if snapshot.mode=="switcher" then div [class "surface-controls",attribute "role" "group",attribute "aria-label" "Window switcher controls"] [Keyed.node "div" [attribute "role" "listbox",attribute "aria-label" "Switch windows",attribute "aria-multiselectable" "false"] (snapshot.popup |> List.filter (\item -> String.startsWith "switcher:family:" item.identity) |> List.map (\item -> ("control:" ++ item.identity,control item))),Keyed.node "div" [attribute "role" "group",attribute "aria-label" "Window switcher actions"] (snapshot.popup |> List.filter (\item -> not (String.startsWith "switcher:family:" item.identity)) |> List.map (\item -> ("control:" ++ item.identity,control item)))] else Keyed.node "div" [class "surface-controls",attribute "role" (if snapshot.mode=="menu" then "menu" else "group")] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.popup))]
       else Keyed.node "div" [attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-bar",attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)]
            [("actions",Keyed.node "div" [class "surface-actions",attribute "role" "toolbar",attribute "aria-label" "Warlock taskbar"] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.bar))
            ,("status",span [class (if String.isEmpty snapshot.status || snapshot.status=="Ready" then "surface-status surface-status-idle" else "surface-status"),attribute "role" "status",attribute "aria-live" "off",attribute "aria-atomic" "true",attribute "aria-label" snapshot.status,title snapshot.status] [text snapshot.status])]
