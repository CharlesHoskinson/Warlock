module SurfaceRenderer exposing (enabled, Snapshot, decode, encode, controlIdentities, controlDomId, publication, lease, mode, view, viewBarWithStatusScroll, viewWithPreview, viewWithPreviewPending, action, queryValue, pendingQuery, pendingQueryBlocked, honestPendingQuery, composingPopup, fieldIdentity)

import Html exposing (Html, button, div, h1, input, label, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, for, hidden, id, style, title, type_, value, placeholder)
import Html.Events exposing (on)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Set exposing (Set)
import Settings
import PreviewVisual as Preview
import StatusScroll
import SurfaceSnapshot
import SurfaceTheme
import UInt64 exposing (Counter)

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

pendingQueryBlocked : String -> Bool
pendingQueryBlocked = SurfaceSnapshot.pendingQueryBlocked

honestPendingQuery : String -> Snapshot -> Snapshot
honestPendingQuery = SurfaceSnapshot.honestPendingQuery

composingPopup : Snapshot -> Snapshot
composingPopup = SurfaceSnapshot.composingPopup

fieldIdentity : Snapshot -> String
fieldIdentity = SurfaceSnapshot.fieldIdentity

findNonCollidingPrefix : Set String -> List String -> String -> String
findNonCollidingPrefix used items candidate =
    if List.any (\domValue -> Set.member (candidate ++ domValue) used) items then
        findNonCollidingPrefix used items (candidate ++ "-")
    else
        candidate

controlEscapePrefix : String
controlEscapePrefix =
    "surface-control-"

escapeControlDomId : String -> String
escapeControlDomId rawDomId =
    if StatusScroll.isReservedDomId rawDomId || String.startsWith controlEscapePrefix rawDomId then
        controlEscapePrefix ++ rawDomId
    else
        rawDomId

controlDomId : Snapshot -> String -> String
controlDomId _ rawDomId =
    escapeControlDomId rawDomId

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send current = viewInternal (\_ -> Preview.Hidden) False Nothing popup send current

viewBarWithStatusScroll : Maybe String -> (E.Value -> msg) -> Snapshot -> Html msg
viewBarWithStatusScroll statusScrollDomId send current = viewInternal (\_ -> Preview.Hidden) False statusScrollDomId False send current

viewWithPreview : (String -> Preview.Visual) -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreview preview popup send current = viewInternal preview False Nothing popup send current

viewWithPreviewPending : (String -> Preview.Visual) -> Bool -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreviewPending preview pending popup send current = viewInternal preview pending Nothing popup send current

viewInternal : (String -> Preview.Visual) -> Bool -> Maybe String -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewInternal preview pending statusScrollDomId popup send current =
    let snapshot = SurfaceSnapshot.details current
        -- Statically and injectively exclude StatusScroll.reservedDomPrefix from
        -- every rendered control/description/caption DOM ID independent of snapshot
        -- contents so neither status-scroll tasks nor deferred focus tasks can alias
        -- across frames.
        rawControlIds = List.map .domId (snapshot.bar ++ snapshot.popup)
        mapControlDomId rawDomId = escapeControlDomId rawDomId
        effectiveControlIds = List.map mapControlDomId rawControlIds
        domIds = Set.fromList effectiveControlIds
        safeStatusDomId = if popup then Nothing else statusScrollDomId |> Maybe.andThen (\scrollCandidate -> if StatusScroll.isReservedDomId scrollCandidate then Just scrollCandidate else Nothing)
        statusScrollIdAttrs = safeStatusDomId |> Maybe.map (\scrollId -> [id scrollId]) |> Maybe.withDefault []
        descriptionPrefix = findNonCollidingPrefix domIds effectiveControlIds "preview-description-"
        captionPrefix = findNonCollidingPrefix domIds effectiveControlIds "settings-save-caption-"
        control item =
            let renderedDomId = mapControlDomId item.domId
                visual = preview item.identity
                description = Preview.description visual
                descriptionId = descriptionPrefix ++ renderedDomId
                settingsSave = popup && snapshot.mode=="settings" && List.member item.identity ["settings:save","settings:motion:save","settings:shortcuts:save"]
                captionId = captionPrefix ++ renderedDomId
                describedBy = List.filterMap identity [if String.isEmpty description then Nothing else Just descriptionId,if settingsSave then Just captionId else Nothing]
                settingsToggle = popup && ((snapshot.mode=="settings" && List.member item.identity ["settings:effects-off","settings:reduced-transparency"]) || (snapshot.mode=="notifications" && List.member item.identity ["notifications:dnd","notifications:critical-interrupt"]))
                switcherOption = popup && snapshot.mode=="switcher" && String.startsWith "switcher:family:" item.identity
                overviewFilter = popup && snapshot.mode=="overview" && (item.identity=="overview:all" || String.startsWith "overview:workspace:" item.identity)
                active = not popup && (String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity) && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)
                kind = if String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity then "control-group" else if item.identity=="bar:recovery-refresh" then "control-recovery" else "control-utility"
                windowStateValue = if kind/="control-group" then "none" else if String.contains "Attention; " item.detail then "attention" else if String.contains "Active" item.detail then "active" else if String.contains "Minimized" item.detail then "minimized" else "open"
                controlRole = if switcherOption then "option" else if popup && snapshot.mode=="menu" then (if item.checked/=Nothing then "menuitemcheckbox" else "menuitem") else "button"
                currentFlag = (not popup && kind=="control-group" && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)) || (popup && List.member snapshot.mode ["menu","switcher","snap","settings","notifications","system","files","jump"] && (item.detail=="Selected" || (snapshot.mode=="menu" && String.endsWith " • Selected" item.detail) || (settingsToggle && String.startsWith "On" item.detail)))
                themeSpec = { popup = popup, surfaceMode = snapshot.mode, identity = item.identity, kind = kind, windowState = windowStateValue, isEnabled = item.enabled, isFocusOnly = item.focusOnly, isCurrent = currentFlag, checked = item.checked, isMenuCheckbox = controlRole=="menuitemcheckbox", appearance = snapshot.appearance, motion = snapshot.motion }
                labelAttrs = [class "control-label"] ++ SurfaceTheme.controlLabelStyles popup snapshot.mode item.identity
                detailAttrs = [class "control-detail"] ++ SurfaceTheme.controlDetailStyles themeSpec item.detail
                activation = SurfaceSnapshot.action popup item.identity current |> Maybe.map (\wire -> [on "click" (D.succeed (send wire))]) |> Maybe.withDefault []
            in if popup && snapshot.mode=="settings" && (String.startsWith "settings:help:text:" item.identity || (String.startsWith "settings:shortcuts:" item.identity && String.endsWith ":state" item.identity)) then
                p ([class "notification-text",id renderedDomId,attribute (if String.startsWith "settings:help:text:" item.identity then "data-settings-help" else "data-shortcut-state") item.identity] ++ SurfaceTheme.notificationTextStyles snapshot.appearance) [span labelAttrs [text item.label],span detailAttrs [text item.detail]]
            else if popup && snapshot.mode=="notifications" && (String.endsWith ":summary" item.identity || String.endsWith ":body" item.identity) then
                p ([class "notification-text",id renderedDomId,attribute "data-notification-content" item.identity] ++ SurfaceTheme.notificationTextStyles snapshot.appearance) [span labelAttrs [text item.label],span detailAttrs [text item.detail]]
            else if popup && List.member snapshot.mode ["system","files","jump"] && String.endsWith ":state" item.identity then
                p ([class "notification-text",id renderedDomId,attribute (if snapshot.mode=="jump" then "data-jump-content" else if snapshot.mode=="files" then "data-files-content" else "data-system-content") item.identity] ++ SurfaceTheme.notificationTextStyles snapshot.appearance) [span labelAttrs [text item.label]]
            else if popup && List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then
                let packet inputKind query = send (E.object [("surfaceProtocol",E.int 2),("kind",E.string inputKind),("surface",E.string "popup"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string item.identity),("query",E.string query)])
                    edit = D.map2 (\query composing -> packet (if composing then "surface-preedit" else "surface-query") query) (D.at ["target","value"] D.string) (D.oneOf [D.field "isComposing" D.bool,D.succeed False])
                    composition inputKind = D.map (packet inputKind) (D.at ["target","value"] D.string)
                in input ([class "launcher-search",id renderedDomId,type_ (if snapshot.mode=="files" then "text" else "search"),placeholder (if snapshot.mode=="files" then "/path/to/folder or ~/Documents" else "Search applications"),value item.label,attribute "aria-label" item.ariaLabel,attribute "data-surface-field" item.identity,attribute "autocomplete" "off",disabled (not item.enabled),on "input" edit,on "compositionstart" (composition "surface-composition-start"),on "compositionend" (composition "surface-composition-end")] ++ SurfaceTheme.searchFieldStyles snapshot.appearance item.enabled snapshot.mode snapshot.motion) []
            else (if settingsSave then (\saveButton -> div ([class "settings-save-group"] ++ SurfaceTheme.settingsSaveGroupStyles snapshot.appearance) [saveButton,p ([class "settings-save-caption",id captionId] ++ SurfaceTheme.settingsSaveCaptionStyles snapshot.appearance) [text item.detail]]) else identity) <| button ([class kind,id renderedDomId,attribute "data-window-state" windowStateValue,attribute "aria-label" item.ariaLabel,disabled (not item.enabled && not item.focusOnly),attribute "aria-disabled" (if not item.enabled then "true" else "false"),attribute "data-focus-only" (if item.focusOnly then "true" else "false"),attribute "data-surface-control" item.identity,attribute "role" controlRole,attribute "aria-current" (if currentFlag then "true" else "false")] ++ (if overviewFilter then [attribute "aria-pressed" (if item.checked==Just True then "true" else "false")] else (item.checked |> Maybe.map (\checked -> [attribute "aria-checked" (if checked then "true" else "false")]) |> Maybe.withDefault [])) ++ (if List.isEmpty describedBy then [] else [attribute "aria-describedby" (String.join " " describedBy)]) ++ (if popup && snapshot.mode=="settings" && item.identity=="settings:help" then [attribute "aria-expanded" (if item.detail=="Expanded" then "true" else "false")] else []) ++ (if settingsToggle then [attribute "aria-pressed" (if String.startsWith "On" item.detail then "true" else "false")] else []) ++ (if not popup && kind=="control-group" then [attribute "data-active-application" (if active then "true" else "false")] else []) ++ (if switcherOption then [attribute "aria-selected" (if item.detail=="Selected" then "true" else "false")] else if not popup && kind=="control-group" then [attribute "aria-pressed" (if active then "true" else "false")] else []) ++ SurfaceTheme.controlStyles themeSpec ++ activation) [Preview.decorativeInlineView visual,if controlRole=="menuitemcheckbox" then SurfaceTheme.checkboxIndicator item.checked else text "",span labelAttrs [text item.label],if settingsSave then text "" else span detailAttrs [text item.detail],if String.isEmpty description then text "" else span [class "preview-description",id descriptionId,hidden True,style "display" "none"] [text description]]
        keyedControl item =
            (if popup && List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then [("label:" ++ item.identity,label ([class "launcher-search-label",for (mapControlDomId item.domId)] ++ SurfaceTheme.searchLabelStyles snapshot.appearance snapshot.mode) [text item.ariaLabel])] else [])
                ++ [("control:" ++ item.identity,control item)]
        familyPrefix rows = case rows of
            first :: rest -> if String.startsWith "overview:family:" first.identity then first :: familyPrefix rest else []
            [] -> []
        overviewRows rows =
            case rows of
                [] -> []
                first :: rest ->
                    if String.startsWith "overview:workspace:" first.identity then
                        let members = familyPrefix rest
                        in div ([class "overview-workspace",attribute "role" "group",attribute "aria-labelledby" (mapControlDomId first.domId)] ++ SurfaceTheme.overviewWorkspaceStyles snapshot.appearance) (List.map control (first::members)) :: overviewRows (List.drop (List.length members) rest)
                    else control first :: overviewRows rest
        statusIdle = String.isEmpty snapshot.status || snapshot.status=="Ready"
        displayedStatus = if pending then "Results may not match current input." ++ (if String.isEmpty snapshot.status then "" else " Previous: " ++ snapshot.status) else snapshot.status
    in if popup then div ([attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-popup",attribute "data-mode" snapshot.mode,attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] ++ SurfaceTheme.popupRootStyles snapshot.appearance snapshot.motion) [h1 (SurfaceTheme.popupHeadingStyles snapshot.appearance) [text (if snapshot.mode=="applications" then "Applications" else if snapshot.mode=="overview" then "Task View" else if snapshot.mode=="switcher" then "Switch windows" else if snapshot.mode=="snap" then "Snap window" else if snapshot.mode=="jump" then "Application actions" else if snapshot.mode=="files" then "Files" else if snapshot.mode=="system" then "System" else if snapshot.mode=="notifications" then "Notifications" else if snapshot.mode=="settings" then "Settings" else if snapshot.mode=="menu" then "Window actions" else "Choose a window")],p ([attribute "role" "status",attribute "aria-live" "off"] ++ SurfaceTheme.popupStatusStyles snapshot.appearance snapshot.status) [text displayedStatus],(if snapshot.mode=="overview" then div ([class "surface-controls",attribute "role" "group"] ++ SurfaceTheme.popupControlsStyles snapshot.mode) (overviewRows snapshot.popup) else if snapshot.mode=="switcher" then div ([class "surface-controls",attribute "role" "group",attribute "aria-label" "Window switcher controls"] ++ SurfaceTheme.popupControlsStyles snapshot.mode) [Keyed.node "div" ([attribute "role" "listbox",attribute "aria-label" "Switch windows",attribute "aria-multiselectable" "false"] ++ SurfaceTheme.switcherListboxStyles snapshot.appearance) (snapshot.popup |> List.filter (\item -> String.startsWith "switcher:family:" item.identity) |> List.map (\item -> ("control:" ++ item.identity,control item))),Keyed.node "div" ([attribute "role" "group",attribute "aria-label" "Window switcher actions"] ++ SurfaceTheme.switcherActionsStyles) (snapshot.popup |> List.filter (\item -> not (String.startsWith "switcher:family:" item.identity)) |> List.map (\item -> ("control:" ++ item.identity,control item)))] else Keyed.node "div" ([class "surface-controls",attribute "role" (if snapshot.mode=="menu" then "menu" else "group")] ++ SurfaceTheme.popupControlsStyles snapshot.mode) (List.concatMap keyedControl snapshot.popup))]
       else Keyed.node "div" ([attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-bar",attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] ++ SurfaceTheme.barRootStyles snapshot.appearance snapshot.motion)
            [("actions",Keyed.node "div" ([class "surface-actions",attribute "role" "toolbar",attribute "aria-label" "Warlock taskbar"] ++ SurfaceTheme.barActionsStyles) (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.bar))
             ,("status",span ([class (if statusIdle then "surface-status surface-status-idle" else "surface-status"),attribute "role" "status",attribute "aria-live" "off",attribute "aria-atomic" "true",attribute "aria-label" snapshot.status,title snapshot.status] ++ SurfaceTheme.barStatusStyles snapshot.appearance statusIdle snapshot.status) [span (statusScrollIdAttrs ++ (if statusIdle then [] else [attribute "tabindex" "0"]) ++ SurfaceTheme.barStatusInnerStyles snapshot.appearance snapshot.motion) [text snapshot.status]])]
